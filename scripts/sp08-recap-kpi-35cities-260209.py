# &s &RECAP_KPI_aaMAIN - Génère 2 fichiers recap KPI (par ville + par pays)

# Calcule tous les indicateurs Airbnb à partir du parquet nettoyé
# et des données population/logements commune propre.
#
# Outputs:
#   data/interim/kpi_35cities_by_city_2506.csv
#   data/interim/kpi_35cities_by_country_2506.csv
#
# Date: 2026-02-09

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
DATA_PATH = BASE / "data" / "interim" / "dbsumlistings_2506_cons35city.parquet"
OUTPUT_DIR = BASE / "data" / "interim"

sys.path.insert(0, str(BASE / "scripts"))
from city_reference_data import CITY_DATA

# Greater Manchester : IA couvre la métropole, pas la commune
# On ajoute avec les données métro (cohérentes avec le périmètre IA)
CITY_DATA["greater-manchester"] = {
    "pop": 2_867_000,
    "housing": 1_200_000,
    "pop_source": "ONS Census 2021 (Greater Manchester Combined Authority)",
    "housing_source": "ONS Census 2021 GMCA: ~1.2M dwellings",
}

# Villes à exclure du rapport (périmètre IA ≠ commune)
# greater-manchester : OK car on utilise pop métro ci-dessus
EXCLUDE_CITIES = []  # aucune exclusion pour l'instant

# Taux conversion EUR
FX_EUR = {
    "GBR": 1.17, "HUN": 0.0026, "TUR": 0.028, "DNK": 0.134, "CZE": 0.040,
    "NOR": 0.085, "SWE": 0.087, "CHE": 1.06,
}

# Noms français
CITY_FR = {
    "london": "Londres", "paris": "Paris", "rome": "Rome",
    "istanbul": "Istanbul", "lisbon": "Lisbonne", "madrid": "Madrid",
    "athens": "Athènes", "barcelona": "Barcelone", "copenhagen": "Copenhague",
    "budapest": "Budapest", "florence": "Florence", "vienna": "Vienne",
    "prague": "Prague", "berlin": "Berlin", "bordeaux": "Bordeaux",
    "venice": "Venise", "amsterdam": "Amsterdam", "brussels": "Bruxelles",
    "dublin": "Dublin", "lyon": "Lyon", "milan": "Milan", "porto": "Porto",
    "oslo": "Oslo", "naples": "Naples", "malaga": "Malaga", "valencia": "Valence",
    "sevilla": "Séville", "greater-manchester": "Manchester (métro)",
    "munich": "Munich", "edinburgh": "Édimbourg", "stockholm": "Stockholm",
    "thessaloniki": "Thessalonique", "bologna": "Bologne",
    "bergamo": "Bergame", "zurich": "Zurich",
}
# &e

# &s &LOAD_CLEAN
print("Chargement données...")
df_raw = pd.read_parquet(DATA_PATH)
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

# Exclure villes si besoin
if EXCLUDE_CITIES:
    df = df[~df["city"].isin(EXCLUDE_CITIES)]

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

# Indicateurs dérivés
city_kpi["ratio_lh"] = (city_kpi["n_listings"] / city_kpi["n_hosts"]).round(2)
city_kpi["prix_iqr"] = (city_kpi["prix_q75"] - city_kpi["prix_q25"]).round(0)
city_kpi["pct_entire"] = (city_kpi["pct_entire"] * 100).round(1)
city_kpi["pct_multi"] = (city_kpi["pct_multi"] * 100).round(1)
city_kpi["pct_longterm"] = (city_kpi["pct_longterm"] * 100).round(1)

# Concentration
conc = df.groupby("city").apply(concentration_50).reset_index(name="cr_hosts_50pct")
city_kpi = city_kpi.merge(conc, on="city")

# Population et logements (commune propre)
city_kpi["pop"] = city_kpi["city"].map(lambda c: CITY_DATA.get(c, {}).get("pop", np.nan))
city_kpi["housing"] = city_kpi["city"].map(lambda c: CITY_DATA.get(c, {}).get("housing", np.nan))
city_kpi["pop_source"] = city_kpi["city"].map(
    lambda c: "confirmed" if "ESTIMATE" not in CITY_DATA.get(c, {}).get("housing_source", "ESTIMATE") else "estimated"
)

# Ratios de pression
city_kpi["listings_1000hab"] = (city_kpi["n_listings"] / city_kpi["pop"] * 1000).round(1)
city_kpi["listings_1000hsg"] = (city_kpi["n_listings"] / city_kpi["housing"] * 1000).round(1)
city_kpi["entire_1000hsg"] = (city_kpi["n_entire"] / city_kpi["housing"] * 1000).round(1)

# Nom français
city_kpi["city_fr"] = city_kpi["city"].map(lambda c: CITY_FR.get(c, c.title()))

# Arrondir
for col in ["prix_med", "prix_moy", "prix_q25", "prix_q75", "dispo_med", "dispo_moy",
            "reviews_med", "rpm_med"]:
    city_kpi[col] = city_kpi[col].round(1)

# Ordre des colonnes
cols_city = [
    "country_code", "city", "city_fr", "pop_source",
    # Volume
    "n_listings", "n_entire", "n_hosts",
    # Population & pression
    "pop", "housing",
    "listings_1000hab", "listings_1000hsg", "entire_1000hsg",
    # Prix
    "prix_med", "prix_moy", "prix_q25", "prix_q75", "prix_iqr",
    # Structure
    "pct_entire", "pct_multi", "pct_longterm", "ratio_lh",
    # Concentration
    "cr_hosts_50pct",
    # Activité
    "dispo_med", "dispo_moy", "reviews_med", "rpm_med",
]
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

# Indicateurs dérivés
country_kpi["ratio_lh"] = (country_kpi["n_listings"] / country_kpi["n_hosts"]).round(2)
country_kpi["prix_iqr"] = (country_kpi["prix_q75"] - country_kpi["prix_q25"]).round(0)
country_kpi["pct_entire"] = (country_kpi["pct_entire"] * 100).round(1)
country_kpi["pct_multi"] = (country_kpi["pct_multi"] * 100).round(1)
country_kpi["pct_longterm"] = (country_kpi["pct_longterm"] * 100).round(1)

# Pop et housing agrégés depuis city_kpi
pop_country = city_kpi.groupby("country_code").agg(
    pop_total=("pop", "sum"),
    housing_total=("housing", "sum"),
).reset_index()
country_kpi = country_kpi.merge(pop_country, on="country_code")

country_kpi["listings_1000hab"] = (country_kpi["n_listings"] / country_kpi["pop_total"] * 1000).round(1)
country_kpi["listings_1000hsg"] = (country_kpi["n_listings"] / country_kpi["housing_total"] * 1000).round(1)
country_kpi["entire_1000hsg"] = (country_kpi["n_entire"] / country_kpi["housing_total"] * 1000).round(1)

# Arrondir
for col in ["prix_med", "prix_moy", "prix_q25", "prix_q75", "dispo_med", "dispo_moy",
            "reviews_med", "rpm_med"]:
    country_kpi[col] = country_kpi[col].round(1)

cols_country = [
    "country_code", "n_villes",
    "n_listings", "n_entire", "n_hosts",
    "pop_total", "housing_total",
    "listings_1000hab", "listings_1000hsg", "entire_1000hsg",
    "prix_med", "prix_moy", "prix_q25", "prix_q75", "prix_iqr",
    "pct_entire", "pct_multi", "pct_longterm", "ratio_lh",
    "dispo_med", "dispo_moy", "reviews_med", "rpm_med",
]
country_kpi = country_kpi[cols_country].sort_values("n_listings", ascending=False)
# &e

# &s &EXPORT
out_city = OUTPUT_DIR / "kpi_35cities_by_city_2506.csv"
out_country = OUTPUT_DIR / "kpi_35cities_by_country_2506.csv"

city_kpi.to_csv(out_city, index=False, encoding="utf-8-sig")
country_kpi.to_csv(out_country, index=False, encoding="utf-8-sig")

print(f"\n{'='*60}")
print(f"Export ville:  {out_city.name} ({len(city_kpi)} villes)")
print(f"Export pays:   {out_country.name} ({len(country_kpi)} pays)")
print(f"{'='*60}")

# Aperçu
print(f"\n--- TOP 10 villes (volume) ---")
top = city_kpi.head(10)[["city_fr", "country_code", "n_listings", "pop",
                          "listings_1000hab", "entire_1000hsg", "prix_med",
                          "pct_multi", "pct_longterm", "dispo_med"]]
print(top.to_string(index=False))

print(f"\n--- Par pays ---")
print(country_kpi[["country_code", "n_villes", "n_listings",
                    "listings_1000hab", "entire_1000hsg", "prix_med",
                    "pct_multi", "ratio_lh"]].to_string(index=False))

# Moyennes globales
print(f"\n--- Moyennes globales (35 villes) ---")
print(f"Listings total: {city_kpi['n_listings'].sum():,}")
print(f"Prix médian global: {df['price_eur'].median():.0f} EUR")
print(f"Moy. listings/1000 hab: {city_kpi['listings_1000hab'].mean():.1f}")
print(f"Moy. listings/1000 hsg: {city_kpi['listings_1000hsg'].mean():.1f}")
print(f"Moy. entire/1000 hsg: {city_kpi['entire_1000hsg'].mean():.1f}")
# &e

# &e
