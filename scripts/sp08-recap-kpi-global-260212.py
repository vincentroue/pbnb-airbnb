# &s &RECAP_KPI_GLOBAL_aaMAIN - Génère KPI par ville et par pays (global)

# Calcule indicateurs Airbnb depuis le parquet consolidé global.
# Supporte --europe-only pour ne garder que les villes européennes.
#
# Outputs:
#   data/interim/kpi_global_by_city_2506.csv
#   data/interim/kpi_global_by_country_2506.csv
#
# Date: 2026-02-12

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
INTERIM_DIR = BASE / "data" / "interim"
REF_CSV = BASE / "data" / "external" / "city-reference-airbnb-260217.csv"

europe_only = "--europe-only" in sys.argv
scope = "europe" if europe_only else "global"
DATA_PATH = INTERIM_DIR / f"dbsumlistings_2506_cons_{scope}.parquet"

# Si fichier europe n'existe pas, filtrer depuis global
if europe_only and not DATA_PATH.exists():
    DATA_PATH = INTERIM_DIR / "dbsumlistings_2506_cons_global.parquet"

# Table de référence unique — remplace city_reference_data.py, FX_EUR, CITY_FR
_ref = pd.read_csv(REF_CSV)
_ref_idx = _ref[_ref["city"].notna()].set_index("city")
_fx = _ref.dropna(subset=["country_code", "fx_eur"]).drop_duplicates("country_code")
FX_EUR = dict(zip(_fx["country_code"], _fx["fx_eur"]))
CITY_FR = _ref_idx["city_fr"].fillna("").to_dict()
CITY_REF = _ref_idx[["pop", "housing", "pop_quality"]].to_dict("index")
# &e

# &s &LOAD_CLEAN
print(f"Chargement {DATA_PATH.name}...")
df_raw = pd.read_parquet(DATA_PATH)

if europe_only and "continent" in df_raw.columns:
    df_raw = df_raw[df_raw["continent"] == "Europe"]

print(f"Brut: {len(df_raw):,} lignes, {df_raw['city'].nunique()} villes")

df = df_raw.copy()

# Conversion prix EUR
if "price_eur" not in df.columns:
    df["price_eur"] = df.apply(
        lambda r: r["price"] * FX_EUR.get(r["country_code"], 1.0)
        if pd.notna(r["price"]) else None, axis=1
    )

# Flags
df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(int)
df["is_multihost"] = (df["calculated_host_listings_count"] > 1).astype(int)
df["is_longterm"] = (df["minimum_nights"] >= 30).astype(int)

# Pipeline cleaning
df = df[df["price"].notna()]
df = df[df["availability_365"] > 0]
df = df[df["room_type"] != "Hotel room"]
df = df[(df["price_eur"] >= 10) & (df["price_eur"] <= 1000)]

print(f"Nettoyé: {len(df):,} lignes, {df['city'].nunique()} villes")
# &e

# &s &KPI_CITY - Calcul KPI par ville
print("\nCalcul KPI par ville...")

def concentration_50(group):
    """% hosts nécessaires pour 50% de l'offre."""
    host_listings = group.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    n_hosts = len(host_listings)
    cumsum = host_listings.cumsum()
    hosts_for_50 = (cumsum <= total * 0.5).sum() + 1
    return round(hosts_for_50 / n_hosts * 100, 1) if n_hosts > 0 else 0

def concentration_metrics(group):
    """Indicateurs de concentration cr_ par ville."""
    host_listings = group.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    n_hosts = len(host_listings)
    # CR10 : part de marché des 10 premiers hosts
    cr_top10_pct = round(host_listings.head(10).sum() / total * 100, 1) if total > 0 else 0
    # Profil hôtes : % avec ≥5 et ≥10 listings
    cr_host_5plus = round((host_listings >= 5).sum() / n_hosts * 100, 1) if n_hosts > 0 else 0
    cr_host_10plus = round((host_listings >= 10).sum() / n_hosts * 100, 1) if n_hosts > 0 else 0
    # Emprise marché : % listings détenus par hôtes ≥5 et ≥10
    cr_offre_5plus = round(host_listings[host_listings >= 5].sum() / total * 100, 1) if total > 0 else 0
    cr_offre_10plus = round(host_listings[host_listings >= 10].sum() / total * 100, 1) if total > 0 else 0
    return pd.Series({
        "cr_top10_pct": cr_top10_pct,
        "cr_host_5plus": cr_host_5plus, "cr_host_10plus": cr_host_10plus,
        "cr_offre_5plus": cr_offre_5plus, "cr_offre_10plus": cr_offre_10plus,
    })

city_kpi = df.groupby(["country_code", "city"]).agg(
    n_listings=("id", "count"),
    n_entire=("is_entire_home", "sum"),
    n_hosts=("host_id", "nunique"),
    prix_med=("price_eur", "median"),
    prix_moy=("price_eur", "mean"),
    prix_q25=("price_eur", lambda x: x.quantile(0.25)),
    prix_q75=("price_eur", lambda x: x.quantile(0.75)),
    pct_entire=("is_entire_home", "mean"),
    pct_multi=("is_multihost", "mean"),
    pct_longterm=("is_longterm", "mean"),
    dispo_med=("availability_365", "median"),
    dispo_moy=("availability_365", "mean"),
    reviews_med=("number_of_reviews", "median"),
    rpm_med=("reviews_per_month", lambda x: x.dropna().median()),
).reset_index()

# Prix médian par type de logement
entire_prix = df[df["room_type"] == "Entire home/apt"].groupby(["country_code", "city"]).agg(
    prix_med_entire=("price_eur", "median"),
).reset_index()
private_prix = df[df["room_type"] == "Private room"].groupby(["country_code", "city"]).agg(
    prix_med_private=("price_eur", "median"),
).reset_index()
city_kpi = city_kpi.merge(entire_prix, on=["country_code", "city"], how="left")
city_kpi = city_kpi.merge(private_prix, on=["country_code", "city"], how="left")

# Continent
if "continent" in df.columns:
    cont_map = df.groupby("city")["continent"].first()
    city_kpi["continent"] = city_kpi["city"].map(cont_map)

# Indicateurs dérivés
city_kpi["ratio_lh"] = (city_kpi["n_listings"] / city_kpi["n_hosts"]).round(2)
city_kpi["prix_iqr"] = (city_kpi["prix_q75"] - city_kpi["prix_q25"]).round(0)
city_kpi["pct_entire"] = (city_kpi["pct_entire"] * 100).round(1)
city_kpi["pct_multi"] = (city_kpi["pct_multi"] * 100).round(1)
city_kpi["pct_longterm"] = (city_kpi["pct_longterm"] * 100).round(1)

# Concentration
conc = df.groupby("city").apply(concentration_50, include_groups=False).reset_index(name="cr_hosts_50pct")
city_kpi = city_kpi.merge(conc, on="city")

# Indicateurs cr_ (concentration détaillée)
cr = df.groupby("city").apply(concentration_metrics, include_groups=False).reset_index()
city_kpi = city_kpi.merge(cr, on="city")

# Population et logements — depuis CSV de référence unique
city_kpi["pop"] = city_kpi["city"].map(
    lambda c: CITY_REF.get(c, {}).get("pop", np.nan)
)
city_kpi["housing"] = city_kpi["city"].map(
    lambda c: CITY_REF.get(c, {}).get("housing", np.nan)
)
city_kpi["pop_source"] = city_kpi["city"].map(
    lambda c: CITY_REF.get(c, {}).get("pop_quality", "")
)

# Correction centre pour agglos — filtre les listings au périmètre commune-centre
# Pour les villes où Inside Airbnb couvre une agglo/province plus large que la commune
CENTRE_FILTERS = {
    "bordeaux":      {"col": "neighbourhood_group", "values": ["Bordeaux"]},
    "lisbon":        {"col": "neighbourhood_group", "values": ["Lisboa"]},
    "porto":         {"col": "neighbourhood_group", "values": ["PORTO"]},
    "bergamo":       {"col": "neighbourhood",       "values": ["Bergamo"]},
    "los-angeles":   {"col": "neighbourhood_group", "values": ["City of Los Angeles"]},
    "geneva":        {"col": "neighbourhood",       "values": ["Commune de Genève"]},
    "thessaloniki":  {"col": "neighbourhood",       "values": ["Thessaloniki"]},
}

def count_centre_listings(city_slug, df_clean):
    """Compte les listings nettoyés dans le périmètre centre (commune) pour les agglos."""
    filt = CENTRE_FILTERS.get(city_slug)
    if not filt:
        return len(df_clean[df_clean["city"] == city_slug])
    col, vals = filt["col"], filt["values"]
    mask = (df_clean["city"] == city_slug) & (df_clean[col].isin(vals))
    return int(mask.sum())

# n_listings_centre pour chaque ville
city_kpi["n_listings_centre"] = city_kpi["city"].map(lambda c: count_centre_listings(c, df))

# Ratios de pression — listings_1000hab = centre (référence), _agglo = total périmètre IA
city_kpi["listings_1000hab"] = (city_kpi["n_listings_centre"] / city_kpi["pop"] * 1000).round(1)
city_kpi["listings_1000hab_agglo"] = np.where(
    city_kpi["city"].isin(CENTRE_FILTERS),
    (city_kpi["n_listings"] / city_kpi["pop"] * 1000).round(1),
    np.nan
)
city_kpi["listings_1000hsg"] = (city_kpi["n_listings"] / city_kpi["housing"] * 1000).round(1)
city_kpi["entire_1000hsg"] = (city_kpi["n_entire"] / city_kpi["housing"] * 1000).round(1)

# Densité annonces / km² — depuis area_centre_km2 du fichier référence enrichi
_ref_area = _ref.set_index("city")["area_geo_centre_km2"].to_dict() if "area_geo_centre_km2" in _ref.columns else {}
if not _ref_area:
    # Fallback : lire depuis audit si pas dans ref
    _audit_path = INTERIM_DIR / "audit_geo_scope_2506.csv"
    if _audit_path.exists():
        _audit = pd.read_csv(_audit_path)
        _ref_area = _audit.set_index("city")["area_centre_km2"].to_dict()
city_kpi["area_centre_km2"] = city_kpi["city"].map(_ref_area)
city_kpi["density_l_km2"] = (city_kpi["n_listings_centre"] / city_kpi["area_centre_km2"]).round(1)

# Log agglos corrigées
agglo_cities = city_kpi[city_kpi["city"].isin(CENTRE_FILTERS)]
if len(agglo_cities) > 0:
    print(f"\nCorrection centre ({len(CENTRE_FILTERS)} agglos):")
    for _, r in agglo_cities.iterrows():
        print(f"  {r['city']:20s} L={r['n_listings']:>6d}  L_centre={r['n_listings_centre']:>6d}  "
              f"L/1Kh={r['listings_1000hab']:>5.1f} (agglo={r['listings_1000hab_agglo']:.1f})")

# Nom français
city_kpi["city_fr"] = city_kpi["city"].map(lambda c: CITY_FR.get(c, c.replace("-", " ").title()))

# Arrondir
for col in ["prix_med", "prix_med_entire", "prix_med_private",
            "prix_moy", "prix_q25", "prix_q75",
            "dispo_med", "dispo_moy", "reviews_med", "rpm_med"]:
    if col in city_kpi.columns:
        city_kpi[col] = city_kpi[col].round(1)

# Swap n_listings -> n_listings_agglo, n_listings_centre -> n_listings
# Le dashboard et les rapports affichent n_listings = commune centre (coherent avec listings_1000hab)
# n_listings_agglo conserve le scope complet Inside Airbnb (pour reference)
city_kpi = city_kpi.rename(columns={"n_listings": "n_listings_agglo", "n_listings_centre": "n_listings"})

# Ordre des colonnes
cols_city = [
    "continent", "country_code", "city", "city_fr", "pop_source",
    "n_listings", "n_listings_agglo", "n_entire", "n_hosts",
    "pop", "housing",
    "listings_1000hab", "listings_1000hab_agglo", "density_l_km2",
    "listings_1000hsg", "entire_1000hsg",
    "area_centre_km2",
    "prix_med", "prix_med_entire", "prix_med_private",
    "prix_moy", "prix_q25", "prix_q75", "prix_iqr",
    "pct_entire", "pct_multi", "pct_longterm", "ratio_lh",
    "cr_hosts_50pct",
    "cr_top10_pct", "cr_host_5plus", "cr_host_10plus",
    "cr_offre_5plus", "cr_offre_10plus",
    "dispo_med", "dispo_moy", "reviews_med", "rpm_med",
]
# Filtrer colonnes existantes
cols_city = [c for c in cols_city if c in city_kpi.columns]
city_kpi = city_kpi[cols_city].sort_values("n_listings", ascending=False)
# &e

# &s &KPI_COUNTRY - Calcul KPI par pays
print("Calcul KPI par pays...")

country_kpi = df.groupby("country_code").agg(
    n_villes=("city", "nunique"),
    n_listings=("id", "count"),
    n_entire=("is_entire_home", "sum"),
    n_hosts=("host_id", "nunique"),
    prix_med=("price_eur", "median"),
    prix_moy=("price_eur", "mean"),
    prix_q25=("price_eur", lambda x: x.quantile(0.25)),
    prix_q75=("price_eur", lambda x: x.quantile(0.75)),
    pct_entire=("is_entire_home", "mean"),
    pct_multi=("is_multihost", "mean"),
    pct_longterm=("is_longterm", "mean"),
    dispo_med=("availability_365", "median"),
    dispo_moy=("availability_365", "mean"),
    reviews_med=("number_of_reviews", "median"),
    rpm_med=("reviews_per_month", lambda x: x.dropna().median()),
).reset_index()

# Prix médian par type de logement — par pays
entire_prix_c = df[df["room_type"] == "Entire home/apt"].groupby("country_code").agg(
    prix_med_entire=("price_eur", "median"),
).reset_index()
private_prix_c = df[df["room_type"] == "Private room"].groupby("country_code").agg(
    prix_med_private=("price_eur", "median"),
).reset_index()
country_kpi = country_kpi.merge(entire_prix_c, on="country_code", how="left")
country_kpi = country_kpi.merge(private_prix_c, on="country_code", how="left")

country_kpi["ratio_lh"] = (country_kpi["n_listings"] / country_kpi["n_hosts"]).round(2)
country_kpi["prix_iqr"] = (country_kpi["prix_q75"] - country_kpi["prix_q25"]).round(0)
country_kpi["pct_entire"] = (country_kpi["pct_entire"] * 100).round(1)
country_kpi["pct_multi"] = (country_kpi["pct_multi"] * 100).round(1)
country_kpi["pct_longterm"] = (country_kpi["pct_longterm"] * 100).round(1)

pop_country = city_kpi.groupby("country_code").agg(
    pop_total=("pop", "sum"), housing_total=("housing", "sum"),
).reset_index()
country_kpi = country_kpi.merge(pop_country, on="country_code")

country_kpi["listings_1000hab"] = (country_kpi["n_listings"] / country_kpi["pop_total"] * 1000).round(1)
country_kpi["listings_1000hsg"] = (country_kpi["n_listings"] / country_kpi["housing_total"] * 1000).round(1)
country_kpi["entire_1000hsg"] = (country_kpi["n_entire"] / country_kpi["housing_total"] * 1000).round(1)

for col in ["prix_med", "prix_med_entire", "prix_med_private", "prix_moy",
            "prix_q25", "prix_q75", "dispo_med", "dispo_moy", "reviews_med", "rpm_med"]:
    if col in country_kpi.columns:
        country_kpi[col] = country_kpi[col].round(1)

cols_country = [
    "country_code", "n_villes",
    "n_listings", "n_entire", "n_hosts",
    "pop_total", "housing_total",
    "listings_1000hab", "listings_1000hsg", "entire_1000hsg",
    "prix_med", "prix_med_entire", "prix_med_private",
    "prix_moy", "prix_q25", "prix_q75", "prix_iqr",
    "pct_entire", "pct_multi", "pct_longterm", "ratio_lh",
    "dispo_med", "dispo_moy", "reviews_med", "rpm_med",
]
cols_country = [c for c in cols_country if c in country_kpi.columns]
country_kpi = country_kpi[cols_country].sort_values("n_listings", ascending=False)
# &e

# &s &MERGE_GZ - Fusion KPI gz (reviews, capacité, host, occupancy)
gz_path = INTERIM_DIR / f"kpi_gz_{scope}_by_city_2506.csv"
if gz_path.exists():
    print(f"\nFusion KPI gz ({gz_path.name})...")
    kpi_gz = pd.read_csv(gz_path)
    # Colonnes à fusionner (exclure meta déjà présentes)
    gz_merge_cols = [c for c in kpi_gz.columns if c not in ["continent", "country_code", "n_gz"]]
    city_kpi = city_kpi.merge(kpi_gz[gz_merge_cols], on="city", how="left")
    print(f"  {len(kpi_gz)} villes gz fusionnées, {len(city_kpi.columns)} colonnes total")
else:
    print(f"\n[INFO] Pas de KPI gz ({gz_path.name}), lancer sp08b d'abord")
# &e

# &s &EXPORT
out_city = INTERIM_DIR / f"kpi_{scope}_by_city_2506.csv"
out_country = INTERIM_DIR / f"kpi_{scope}_by_country_2506.csv"

city_kpi.to_csv(out_city, index=False, encoding="utf-8-sig")
country_kpi.to_csv(out_country, index=False, encoding="utf-8-sig")

print(f"\n{'='*60}")
print(f"Export ville:  {out_city.name} ({len(city_kpi)} villes)")
print(f"Export pays:   {out_country.name} ({len(country_kpi)} pays)")
print(f"{'='*60}")

print(f"\n--- TOP 15 villes (volume) ---")
top = city_kpi.head(15)[["city_fr", "continent", "country_code", "n_listings",
                          "listings_1000hab", "prix_med", "pct_multi", "dispo_med"]]
print(top.to_string(index=False))

print(f"\n--- Moyennes globales ({len(city_kpi)} villes) ---")
print(f"Listings total: {city_kpi['n_listings'].sum():,}")
print(f"Prix médian global: {df['price_eur'].median():.0f} EUR")
print(f"Moy. listings/1000 hab: {city_kpi['listings_1000hab'].mean():.1f}")
# &e

# &e
