# &s &RECAP_KPI_GLOBAL_aaMAIN - Génère KPI par ville et par pays (global)

# Calcule TOUS les indicateurs Airbnb depuis le parquet listingfull consolidé.
# Source unique : dblistingfull (déjà nettoyé par sp07b).
# Inclut core KPI + reviews + capacité + host + occupancy (ex-sp08b).
#
# Usage:
#   python scripts/sp08-recap-kpi-global-260212.py [--snapshot 26-06] [--europe-only]
#
# Outputs (SNAP = 2506 défaut, 2606 via --snapshot 26-06):
#   data/interim/kpi_<scope>_by_city_<SNAP>.csv       (+ cols is_proxy / price_invalid)
#   data/interim/kpi_<scope>_by_aggregate_<SNAP>.csv
#
# Date: 2026-02-12 | refacto: 2026-04-26 (pipeline unifié) | param snapshot: 2026-07-15

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
INTERIM_DIR = BASE / "data" / "interim"
REF_CSV = BASE / "data" / "external" / "city-reference-airbnb-260222.csv"

europe_only = "--europe-only" in sys.argv
scope = "europe" if europe_only else "global"

# Snapshot cible paramétrable : --snapshot 26-06 (défaut 25-06 pour rétrocompat)
SNAPSHOT = "25-06"
for _i, _a in enumerate(sys.argv):
    if _a == "--snapshot" and _i + 1 < len(sys.argv):
        SNAPSHOT = sys.argv[_i + 1]
SNAP_TAG = SNAPSHOT.replace("-", "")  # "26-06" -> "2606"

# Ne PAS republier le dashboard (JSON non datés) pour un snapshot non-live -> protège la version en ligne.
# 2506 = live actuel -> publie ; autre snapshot -> seulement si --publish explicite.
WRITE_DASHBOARD = (SNAPSHOT == "25-06") or ("--publish" in sys.argv)

DATA_PATH = INTERIM_DIR / f"dblistingfull_{SNAP_TAG}_cons_{scope}.parquet"

if europe_only and not DATA_PATH.exists():
    DATA_PATH = INTERIM_DIR / f"dblistingfull_{SNAP_TAG}_cons_global.parquet"

# Table de référence
_ref = pd.read_csv(REF_CSV)
_ref_idx = _ref[_ref["city"].notna()].set_index("city")
_fx = _ref.dropna(subset=["country_code", "fx_eur"]).drop_duplicates("country_code")
FX_EUR = dict(zip(_fx["country_code"], _fx["fx_eur"]))
# Override par taux DATÉ du snapshot du run (même table que sp07b) — pour revenue_eur
_CC2CUR = {"GBR": "GBP", "HUN": "HUF", "TUR": "TRY", "DNK": "DKK", "CZE": "CZK", "SWE": "SEK",
           "NOR": "NOK", "CHE": "CHF", "USA": "USD", "CAN": "CAD", "AUS": "AUD", "JPN": "JPY",
           "CHN": "CNY", "TWN": "TWD", "SGP": "SGD", "THA": "THB", "BRA": "BRL", "MEX": "MXN", "ZAF": "ZAR"}
_fxd_path = BASE / "data" / "external" / "fx-by-date-airbnb-260717.csv"
if _fxd_path.exists():
    _fxd = pd.read_csv(_fxd_path)
    _col = f"fx_eur_{SNAP_TAG}"
    if _col in _fxd.columns:
        _cur2fx = dict(zip(_fxd["cur"], _fxd[_col]))
        for _cc, _cur in _CC2CUR.items():
            if _cur in _cur2fx and _cc in FX_EUR:
                FX_EUR[_cc] = round(float(_cur2fx[_cur]), 6)
        print(f"[FX daté] snapshot {SNAP_TAG} : taux BCE appliqués (fallback figé sinon)")
CITY_FR = _ref_idx["city_fr"].fillna("").to_dict()
CITY_REF = _ref_idx[["pop", "housing", "pop_quality"]].to_dict("index")
# &e

# &s &LOAD - Chargement listingfull (déjà nettoyé par sp07b)
print(f"Chargement {DATA_PATH.name}...")
df = pd.read_parquet(DATA_PATH)
# Forcer string pour eviter le cross-product Categorical dans groupby
for col in ["city", "country_code", "continent"]:
    if col in df.columns and hasattr(df[col], "cat"):
        df[col] = df[col].astype(str)

if europe_only and "continent" in df.columns:
    df = df[df["continent"] == "Europe"]

print(f"Données brutes: {len(df):,} lignes, {df['city'].nunique()} villes")

# &s &FILTER_CENTRE - Filtrage centre-commune pour 9 agglos (périmètre homogène)
# Inside Airbnb délimite parfois toute l'agglo (Bordeaux Métropole, LA County, etc.).
# Pour rendre les KPI comparables avec les villes-communes (Paris, Rome...), on filtre
# en amont sur la commune-centre uniquement. TOUS les KPI seront cohérents (centre/centre).
CENTRE_FILTERS = {
    "bordeaux":      {"col": "neighbourhood_group", "values": ["Bordeaux"]},
    "lisbon":        {"col": "neighbourhood_group", "values": ["Lisboa"]},
    "porto":         {"col": "neighbourhood_group", "values": ["PORTO"]},
    "bergamo":       {"col": "neighbourhood",       "values": ["Bergamo"]},
    "los-angeles":   {"col": "neighbourhood_group", "values": ["City of Los Angeles"]},
    "geneva":        {"col": "neighbourhood",       "values": ["Commune de Genève"]},
    "thessaloniki":  {"col": "neighbourhood",       "values": ["Thessaloniki"]},
    "nashville":     {"col": "neighbourhood",       "values": [
        "District 19", "District 17", "District 21", "District 5", "District 6",
        "District 2", "District 15", "District 18", "District 7", "District 20",
        "District 16", "District 8",
    ]},
    "brussels":      {"col": "neighbourhood",       "values": [
        "Bruxelles", "Ixelles", "Saint-Gilles", "Etterbeek", "Saint-Josse-ten-Noode",
    ]},
}

print(f"\nFiltrage centre-commune pour {len(CENTRE_FILTERS)} agglos...")
keep_masks = []
for city_slug, filt in CENTRE_FILTERS.items():
    col, vals = filt["col"], filt["values"]
    if col not in df.columns:
        print(f"  [WARN] {city_slug}: colonne {col} absente, conservé tel quel")
        continue
    mask_city = df["city"] == city_slug
    n_before = mask_city.sum()
    mask_keep = mask_city & df[col].isin(vals)
    n_after = mask_keep.sum()
    # Marquer les lignes hors-centre à drop
    df = df[~mask_city | mask_keep]
    print(f"  {city_slug:<14} {n_before:>6,} -> {n_after:>6,} ({(n_after/n_before*100 if n_before else 0):4.0f}%)")

print(f"Données après filtre centre: {len(df):,} lignes, {df['city'].nunique()} villes")
# &e

# Flags complémentaires (pas dans sp07b)
df["is_longterm90"] = (df["minimum_nights"] >= 90).astype(np.int8)

# Revenue en EUR (estimated_revenue_l365d est en devise locale)
fx_map = df["country_code"].map(FX_EUR).fillna(1.0)
df["revenue_eur"] = (df["estimated_revenue_l365d"] * fx_map).round(0)
# &e

# &s &KPI_CITY - Calcul KPI par ville
print("\nCalcul KPI par ville...")

def _gini(values):
    """Indice de Gini d'une distribution (0=égalité, 1=inégalité totale)."""
    arr = np.sort(np.asarray(values, dtype=float))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * (idx * arr).sum() - (n + 1) * arr.sum()) / (n * arr.sum()))

def concentration_50(group):
    """% hôtes nécessaires pour 50% de l'offre (Lorenz inverse)."""
    host_listings = group.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    vol_n_hotes = len(host_listings)
    cumsum = host_listings.cumsum()
    hosts_for_50 = (cumsum <= total * 0.5).sum() + 1
    return round(hosts_for_50 / vol_n_hotes * 100, 1) if vol_n_hotes > 0 else 0

def concentration_metrics(group):
    """Indicateurs de concentration cr_ par ville.

    Schéma de nommage : cr_<axe_mesuré>_<seuil>_pct
      - cr_offre_top10host_pct  : % offre captée par top 10 hôtes absolus (effet d'échelle)
      - cr_offre_top10pct_pct   : % offre captée par top 10 % des hôtes (comparable inter-échelles)
      - cr_gini                 : indice de Gini de la distribution hôte/listings
    """
    host_listings = group.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    vol_n_hotes = len(host_listings)
    n_top10pct = max(1, int(np.ceil(vol_n_hotes * 0.10))) if vol_n_hotes > 0 else 0

    cr_offre_top10host_pct = round(host_listings.head(10).sum() / total * 100, 1) if total > 0 else 0
    cr_offre_top10pct_pct = round(host_listings.head(n_top10pct).sum() / total * 100, 1) if total > 0 else 0
    cr_gini = round(_gini(host_listings.values), 3) if vol_n_hotes > 0 else 0

    cr_host_1plus = round((host_listings > 1).sum() / vol_n_hotes * 100, 1) if vol_n_hotes > 0 else 0
    cr_host_5plus = round((host_listings >= 5).sum() / vol_n_hotes * 100, 1) if vol_n_hotes > 0 else 0
    cr_host_10plus = round((host_listings >= 10).sum() / vol_n_hotes * 100, 1) if vol_n_hotes > 0 else 0
    cr_offre_1plus = round(host_listings[host_listings > 1].sum() / total * 100, 1) if total > 0 else 0
    cr_offre_5plus = round(host_listings[host_listings >= 5].sum() / total * 100, 1) if total > 0 else 0
    cr_offre_10plus = round(host_listings[host_listings >= 10].sum() / total * 100, 1) if total > 0 else 0
    # Classes exclusives (single=1, semipro=2-4, pro=5-9, 10plus=≥10 — somment à 100%)
    cr_host_single_pct = round((host_listings == 1).sum() / vol_n_hotes * 100, 1) if vol_n_hotes > 0 else 0
    cr_host_semipro_pct = round(((host_listings >= 2) & (host_listings <= 4)).sum() / vol_n_hotes * 100, 1) if vol_n_hotes > 0 else 0
    cr_host_pro_pct = round(((host_listings >= 5) & (host_listings <= 9)).sum() / vol_n_hotes * 100, 1) if vol_n_hotes > 0 else 0
    cr_offre_single_pct = round(host_listings[host_listings == 1].sum() / total * 100, 1) if total > 0 else 0
    cr_offre_semipro_pct = round(host_listings[(host_listings >= 2) & (host_listings <= 4)].sum() / total * 100, 1) if total > 0 else 0
    cr_offre_pro_pct = round(host_listings[(host_listings >= 5) & (host_listings <= 9)].sum() / total * 100, 1) if total > 0 else 0
    # Grille croisée Adamiak (type × mono/multi, somme 100% des annonces)
    n = len(group)
    if n > 0:
        is_ent = group["is_entire_home"] == 1
        is_mul = group["is_multihost"] == 1
        crt_ada_single_home_pct = round((is_ent & ~is_mul).sum() / n * 100, 1)
        crt_ada_multi_home_pct = round((is_ent & is_mul).sum() / n * 100, 1)
        crt_ada_single_room_pct = round((~is_ent & ~is_mul).sum() / n * 100, 1)
        crt_ada_multi_room_pct = round((~is_ent & is_mul).sum() / n * 100, 1)
    else:
        crt_ada_single_home_pct = crt_ada_multi_home_pct = crt_ada_single_room_pct = crt_ada_multi_room_pct = 0
    return pd.Series({
        "cr_offre_top10host_pct": cr_offre_top10host_pct,
        "cr_offre_top10pct_pct": cr_offre_top10pct_pct,
        "cr_gini": cr_gini,
        "cr_host_1plus": cr_host_1plus, "cr_host_5plus": cr_host_5plus, "cr_host_10plus": cr_host_10plus,
        "cr_offre_1plus": cr_offre_1plus, "cr_offre_5plus": cr_offre_5plus, "cr_offre_10plus": cr_offre_10plus,
        "cr_host_single_pct": cr_host_single_pct, "cr_host_semipro_pct": cr_host_semipro_pct, "cr_host_pro_pct": cr_host_pro_pct,
        "cr_offre_single_pct": cr_offre_single_pct, "cr_offre_semipro_pct": cr_offre_semipro_pct, "cr_offre_pro_pct": cr_offre_pro_pct,
        "crt_ada_single_home_pct": crt_ada_single_home_pct, "crt_ada_multi_home_pct": crt_ada_multi_home_pct,
        "crt_ada_single_room_pct": crt_ada_single_room_pct, "crt_ada_multi_room_pct": crt_ada_multi_room_pct,
    })

# Core KPI (identique à l'ancien sp08)
city_kpi = df.groupby(["country_code", "city"]).agg(
    vol_n_ann=("id", "count"),
    str_n_entire=("is_entire_home", "sum"),
    vol_n_hotes=("host_id", "nunique"),
    px_med=("price_eur", "median"),
    str_entire_pct=("is_entire_home", "mean"),
    str_minnuits30_pct=("is_longterm", "mean"),
    str_minnuits90_pct=("is_longterm90", "mean"),
    act_cal_ouvert_med=("availability_365", "median"),
    act_cal_ouvert_moy=("availability_365", "mean"),
    act_cal_180j_pct=("availability_365", lambda x: round((x >= 180).mean() * 100, 1)),
    actrv_avis=("number_of_reviews", "median"),
    actrv_avis_mois=("reviews_per_month", lambda x: x.dropna().median()),
).reset_index()

# Prix médian par type de logement
entire_prix = df[df["room_type"] == "Entire home/apt"].groupby(["country_code", "city"]).agg(
    px_entire_med=("price_eur", "median"),
    px_entire_q25=("price_eur", lambda x: x.quantile(0.25)),
    px_entire_q75=("price_eur", lambda x: x.quantile(0.75)),
).reset_index()
entire_prix["px_entire_iqr"] = (entire_prix["px_entire_q75"] - entire_prix["px_entire_q25"]).round(0)
private_prix = df[df["room_type"] == "Private room"].groupby(["country_code", "city"]).agg(
    px_private_med=("price_eur", "median"),
).reset_index()
shared_prix = df[df["room_type"] == "Shared room"].groupby(["country_code", "city"]).agg(
    prix_med_shared=("price_eur", "median"),
).reset_index()
city_kpi = city_kpi.merge(entire_prix, on=["country_code", "city"], how="left")
city_kpi = city_kpi.merge(private_prix, on=["country_code", "city"], how="left")
city_kpi = city_kpi.merge(shared_prix, on=["country_code", "city"], how="left")

# Review scores (ex-sp08b)
print("  Reviews, capacité, host, occupancy...")
_SUB_NOTES = {"rating": "glb", "accuracy": "exact", "cleanliness": "proprete",
              "checkin": "arrivee", "communication": "communic", "location": "emplacem", "value": "qprix"}
rev_kpi = df.groupby("city").agg(**{
    **{f"actrv_note_{fr}": (f"review_scores_{en}", lambda x, en=en: round(x.dropna().median(), 2) if x.dropna().shape[0] > 0 else np.nan)
       for en, fr in _SUB_NOTES.items()},
    **{f"actrv_note_{fr}_n": (f"review_scores_{en}", lambda x, en=en: x.dropna().shape[0])
       for en, fr in _SUB_NOTES.items()},
}).reset_index()
# Taux de couverture reviews
rev_cov = df.groupby("city").agg(
    actrv_listing_ac_avis_pct=("review_scores_rating", lambda x: round(x.notna().mean() * 100, 1))
).reset_index()
city_kpi = city_kpi.merge(rev_kpi, on="city", how="left")
city_kpi = city_kpi.merge(rev_cov, on="city", how="left")

# Capacité
cap_kpi = df.groupby("city").agg(
    str_cap_pers_med=("accommodates", "median"),
    str_cap_pers_moy=("accommodates", lambda x: round(x.mean(), 1)),
    str_cap_chbr_med=("bedrooms", lambda x: round(x.dropna().median(), 1) if x.dropna().shape[0] > 0 else np.nan),
).reset_index()
city_kpi = city_kpi.merge(cap_kpi, on="city", how="left")

# Prix par nombre de chambres (entire home uniquement, seuil 10 listings)
entire_df = df[df["room_type"] == "Entire home/apt"]
prix_br = entire_df.groupby("city").apply(
    lambda g: pd.Series({
        "px_1br_med": round(g.loc[g["bedrooms"] == 1, "price_eur"].median(), 1) if (g["bedrooms"] == 1).sum() >= 10 else np.nan,
        "px_2br_med": round(g.loc[g["bedrooms"] == 2, "price_eur"].median(), 1) if (g["bedrooms"] == 2).sum() >= 10 else np.nan,
        "px_3brplus_med": round(g.loc[g["bedrooms"] >= 3, "price_eur"].median(), 1) if (g["bedrooms"] >= 3).sum() >= 10 else np.nan,
    }), include_groups=False
).reset_index()
city_kpi = city_kpi.merge(prix_br, on="city", how="left")

# Profil hôte
host_kpi = df.groupby("city").agg(
    act_superhost_pct=("host_is_superhost", lambda x: round(x.dropna().mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
    str_instantbook_pct=("instant_bookable", lambda x: round(x.dropna().mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
).reset_index()
city_kpi = city_kpi.merge(host_kpi, on="city", how="left")

# Occupancy et revenue estimés
occ_kpi = df.groupby("city").agg(
    act_reserv_j_med=("estimated_occupancy_l365d", lambda x: round(x.dropna().median(), 0) if x.dropna().shape[0] > 0 else np.nan),
    act_reserv_j_moy=("estimated_occupancy_l365d", lambda x: round(x.dropna().mean(), 1) if x.dropna().shape[0] > 0 else np.nan),
    act_reserv_30j_pct=("estimated_occupancy_l365d", lambda x: round((x.dropna() >= 30).mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
    act_reserv_180j_pct=("estimated_occupancy_l365d", lambda x: round((x.dropna() >= 180).mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
    act_revenu_med=("revenue_eur", lambda x: round(x.dropna().median(), 0) if x.dropna().shape[0] > 0 else np.nan),
    act_revenu_moy=("revenue_eur", lambda x: round(x.dropna().mean(), 0) if x.dropna().shape[0] > 0 else np.nan),
    act_reserv_taux=("estimated_occupancy_l365d", lambda x: round((x.dropna() / 365 * 100).median(), 1) if x.dropna().shape[0] > 0 else np.nan),
).reset_index()
city_kpi = city_kpi.merge(occ_kpi, on="city", how="left")

# Continent + continent_detail (split Americas et Asia-Pacific)
if "continent" in df.columns:
    cont_map = df.groupby("city")["continent"].first()
    city_kpi["continent"] = city_kpi["city"].map(cont_map)
    cc_map = df.groupby("city")["country_code"].first()
    city_kpi["_cc"] = city_kpi["city"].map(cc_map)
    city_kpi["continent_detail"] = city_kpi["continent"]
    # Americas
    city_kpi.loc[(city_kpi["continent"] == "Americas") & (city_kpi["_cc"].isin(["USA", "CAN"])), "continent_detail"] = "North America"
    city_kpi.loc[(city_kpi["continent"] == "Americas") & (city_kpi["_cc"].isin(["MEX", "BRA", "ARG"])), "continent_detail"] = "Latin America"
    # Asia-Pacific
    city_kpi.loc[(city_kpi["continent"] == "Asia-Pacific") & (city_kpi["_cc"].isin(["AUS", "NZL"])), "continent_detail"] = "Oceania"
    city_kpi.loc[(city_kpi["continent"] == "Asia-Pacific") & (~city_kpi["_cc"].isin(["AUS", "NZL"])), "continent_detail"] = "Asia"
    # Europe
    _EU_WEST_NORTH = ["GBR", "IRL", "FRA", "BEL", "NLD", "DEU", "AUT", "CHE", "DNK", "SWE", "NOR"]
    city_kpi.loc[(city_kpi["continent"] == "Europe") & (city_kpi["_cc"].isin(_EU_WEST_NORTH)), "continent_detail"] = "Europe West & North"
    city_kpi.loc[(city_kpi["continent"] == "Europe") & (~city_kpi["_cc"].isin(_EU_WEST_NORTH)), "continent_detail"] = "Europe South & East"
    city_kpi.drop(columns=["_cc"], inplace=True)

# Indicateurs dérivés
city_kpi["str_ratio_ann_hote"] = (city_kpi["vol_n_ann"] / city_kpi["vol_n_hotes"]).round(2)
city_kpi["str_entire_pct"] = (city_kpi["str_entire_pct"] * 100).round(1)
city_kpi["str_minnuits30_pct"] = (city_kpi["str_minnuits30_pct"] * 100).round(1)
city_kpi["str_minnuits90_pct"] = (city_kpi["str_minnuits90_pct"] * 100).round(1)

# Concentration
conc = df.groupby("city").apply(concentration_50, include_groups=False).reset_index(name="cr_hosts_offre50_pct")
city_kpi = city_kpi.merge(conc, on="city")

cr = df.groupby("city").apply(concentration_metrics, include_groups=False).reset_index()
city_kpi = city_kpi.merge(cr, on="city")

# Population et logements
city_kpi["pop"] = city_kpi["city"].map(
    lambda c: CITY_REF.get(c, {}).get("pop", np.nan)
)
city_kpi["housing"] = city_kpi["city"].map(
    lambda c: CITY_REF.get(c, {}).get("housing", np.nan)
)
city_kpi["pop_source"] = city_kpi["city"].map(
    lambda c: CITY_REF.get(c, {}).get("pop_quality", "")
)

# Ratios de pression — STANDBY (recalcul cohérent en cours, gardés dans ddict)
# city_kpi["listings_1000hab"] = (city_kpi["vol_n_ann"] / city_kpi["pop"] * 1000).round(1)
# city_kpi["listings_1000log"] = (city_kpi["vol_n_ann"] / city_kpi["housing"] * 1000).round(1)
# city_kpi["entire_1000log"] = (city_kpi["str_n_entire"] / city_kpi["housing"] * 1000).round(1)

# Densité annonces / km² (périmètre déjà filtré centre en amont)
_ref_area = _ref.set_index("city")["area_geo_centre_km2"].to_dict() if "area_geo_centre_km2" in _ref.columns else {}
if not _ref_area:
    _audit_path = INTERIM_DIR / f"audit_geo_scope_{SNAP_TAG}.csv"
    if _audit_path.exists():
        _audit = pd.read_csv(_audit_path)
        _ref_area = _audit.set_index("city")["area_centre_km2"].to_dict()
city_kpi["area_centre_km2"] = city_kpi["city"].map(_ref_area)
city_kpi["density_l_km2"] = (city_kpi["vol_n_ann"] / city_kpi["area_centre_km2"]).round(1)

# Nom français
city_kpi["city_fr"] = city_kpi["city"].map(lambda c: CITY_FR.get(c, c.replace("-", " ").title()))

# Arrondir
for col in ["px_med", "px_entire_med", "px_private_med", "prix_med_shared",
            "px_entire_q25", "px_entire_q75",
            "act_cal_ouvert_med", "act_cal_ouvert_moy", "actrv_avis", "actrv_avis_mois"]:
    if col in city_kpi.columns:
        city_kpi[col] = city_kpi[col].round(1)

# Ordre des colonnes
cols_city = [
    "continent", "continent_detail", "country_code", "city", "city_fr", "pop_source",
    "vol_n_ann", "str_n_entire", "vol_n_hotes",
    "pop", "housing",
    # "listings_1000hab", "listings_1000log", "entire_1000log",  # STANDBY
    "density_l_km2", "area_centre_km2",
    "px_med", "px_entire_med", "px_entire_q25", "px_entire_q75", "px_entire_iqr",
    "px_private_med",
    "str_entire_pct", "str_minnuits30_pct", "str_minnuits90_pct", "str_ratio_ann_hote",
    "cr_hosts_offre50_pct",
    "cr_offre_top10host_pct", "cr_offre_top10pct_pct", "cr_gini",
    "cr_host_1plus", "cr_host_5plus", "cr_host_10plus",
    "cr_offre_1plus", "cr_offre_5plus", "cr_offre_10plus",
    "cr_host_single_pct", "cr_host_semipro_pct", "cr_host_pro_pct",
    "cr_offre_single_pct", "cr_offre_semipro_pct", "cr_offre_pro_pct",
    "crt_ada_single_home_pct", "crt_ada_multi_home_pct",
    "crt_ada_single_room_pct", "crt_ada_multi_room_pct",
    "act_cal_ouvert_med", "act_cal_ouvert_moy", "act_cal_180j_pct",
    "actrv_avis", "actrv_avis_mois",
    # Ex-sp08b : reviews, capacité, host, occupancy
    "actrv_note_exact", "actrv_note_exact_n",
    "actrv_note_arrivee", "actrv_note_arrivee_n",
    "actrv_note_proprete", "actrv_note_proprete_n",
    "actrv_note_communic", "actrv_note_communic_n",
    "actrv_listing_ac_avis_pct",
    "actrv_note_emplacem", "actrv_note_emplacem_n",
    "actrv_note_glb", "actrv_note_glb_n",
    "actrv_note_qprix", "actrv_note_qprix_n",
    "str_cap_pers_med", "str_cap_pers_moy", "str_cap_chbr_med",
    "px_1br_med", "px_2br_med", "px_3brplus_med",
    "str_instantbook_pct", "act_superhost_pct",
    "act_reserv_j_med", "act_reserv_j_moy",
    "act_reserv_180j_pct", "act_reserv_30j_pct",
    "act_reserv_taux",
    "act_revenu_med", "act_revenu_moy",
    # GHS-POP densité
    "ctx_pop_dense", "ctx_aire_dense_km2",
    "prs_listings_1000hab_dense", "prs_density_l_km2_dense",
    "prs_pct_listings_dense", "ctx_densite_pop_dense", "ctx_densite_top_5km2",
    "ctx_pop_dense_flag",
    # Contexte externe (panel v2)
    "is_capital", "income_group", "region",
    "ctx_tour_nights_total_24", "ctx_tour_pct_foreign_24", "ctx_tour_nights_total_vevol_2224",
    "ctx_static_gawc_score", "ctx_static_unesco_50km",
    "ctx_ucdb_hdi_latest", "ctx_ucdb_gdp_avg_20", "ctx_ucdb_pop_ghsl_20",
    "ctx_ucdb_pop_cagr_20", "ctx_ucdb_temp_mean_latest",
    "ctx_ucdb_green_pct_latest", "ctx_ucdb_bldg_height_20",
]
cols_city = [c for c in cols_city if c in city_kpi.columns]
city_kpi["scope"] = "city"
city_kpi = city_kpi[["scope"] + cols_city].sort_values("vol_n_ann", ascending=False)
# &e

# &s &SUB_CITY - KPI sous-villes (BAB éclaté)
SUB_CITIES = {
    "biarritz": {"parent": "pays-basque", "neighbourhood": "Biarritz",
                 "pop": 26000, "housing": 21000, "city_fr": "Biarritz"},
    "anglet":   {"parent": "pays-basque", "neighbourhood": "Anglet",
                 "pop": 40000, "housing": 20000, "city_fr": "Anglet"},
    "bayonne":  {"parent": "pays-basque", "neighbourhood": "Bayonne",
                 "pop": 52000, "housing": 28000, "city_fr": "Bayonne"},
}
sub_rows = []
for sub_city, meta in SUB_CITIES.items():
    parent = meta["parent"]
    sub_df = df[(df["city"] == parent) & (df["neighbourhood"] == meta["neighbourhood"])]
    if len(sub_df) == 0:
        continue
    entire = sub_df[sub_df["room_type"] == "Entire home/apt"]
    vol_n_hotes = sub_df["host_id"].nunique()
    row = {
        "scope": "sub_city",
        "continent": "Europe", "country_code": "FRA",
        "city": sub_city, "city_fr": meta["city_fr"], "pop_source": "confirmed",
        "vol_n_ann": len(sub_df),
        "str_n_entire": len(entire), "vol_n_hotes": vol_n_hotes,
        "pop": meta["pop"], "housing": meta["housing"],
        # listings_1000hab / listings_1000log / entire_1000log STANDBY
        "px_med": round(sub_df["price_eur"].median(), 1),
        "px_entire_med": round(entire["price_eur"].median(), 1) if len(entire) > 0 else np.nan,
        "px_entire_q25": round(entire["price_eur"].quantile(0.25), 1) if len(entire) > 0 else np.nan,
        "px_entire_q75": round(entire["price_eur"].quantile(0.75), 1) if len(entire) > 0 else np.nan,
        "str_entire_pct": round(len(entire) / len(sub_df) * 100, 1),
        "str_minnuits30_pct": round(sub_df["is_longterm"].mean() * 100, 1),
        "str_ratio_ann_hote": round(len(sub_df) / vol_n_hotes, 2) if vol_n_hotes > 0 else np.nan,
        "act_cal_ouvert_med": round(sub_df["availability_365"].median(), 0),
        "actrv_avis": round(sub_df["number_of_reviews"].median(), 0),
        "actrv_avis_mois": round(sub_df["reviews_per_month"].dropna().median(), 1),
        "actrv_note_glb": round(sub_df["review_scores_rating"].dropna().median(), 2) if sub_df["review_scores_rating"].notna().any() else np.nan,
        "act_superhost_pct": round(sub_df["host_is_superhost"].mean() * 100, 1) if sub_df["host_is_superhost"].notna().any() else np.nan,
        "act_revenu_med": round(sub_df["revenue_eur"].dropna().median(), 0) if "revenue_eur" in sub_df.columns else np.nan,
    }
    row["px_entire_iqr"] = round(row["px_entire_q75"] - row["px_entire_q25"], 0) if pd.notna(row["px_entire_q75"]) else np.nan
    sub_rows.append(row)
    print(f"  sub_city {sub_city}: {len(sub_df)} listings, px_med={row['px_med']}€")

if sub_rows:
    sub_kpi = pd.DataFrame(sub_rows)
    city_kpi = pd.concat([city_kpi, sub_kpi], ignore_index=True)
    print(f"  {len(sub_rows)} sub_cities ajoutées (total {len(city_kpi)} lignes)")
# &e

# &s &MERGE_GHSPOP - Merge variables densité GHS-POP (après sub_cities)
GHSPOP_CSV = Path(r"C:\Users\vince\DBD-datab\dbd_glb\GHS-POP-raster\outputs\audit_dense_intra_ia_75villes.csv")
if GHSPOP_CSV.exists():
    ghspop = pd.read_csv(GHSPOP_CSV)
    ghspop_cols = {
        "ratio_listings_par_hab": "prs_listings_1000hab_dense",
        "densite_listings_km2": "prs_density_l_km2_dense",
        "pct_listings_dense": "prs_pct_listings_dense",
        "pop_dense": "ctx_pop_dense",
        "aire_dense_km2": "ctx_aire_dense_km2",
        "densite_pop_dense": "ctx_densite_pop_dense",
        "densite_top_5km2": "ctx_densite_top_5km2",
        "flag_fiabilite": "ctx_pop_dense_flag",
        "n_listings_dense": "_n_listings_dense",  # interne pour agrégation
        "n_listings_total": "_n_listings_total_ia",  # interne — périmètre IA cohérent
    }
    ghspop_merge = ghspop[["city"] + list(ghspop_cols.keys())].rename(columns=ghspop_cols)
    city_kpi = city_kpi.merge(ghspop_merge, on="city", how="left")
    n_matched = city_kpi["prs_listings_1000hab_dense"].notna().sum()
    print(f"  GHS-POP: {n_matched}/{len(city_kpi)} villes enrichies")
else:
    print(f"  [WARN] GHS-POP non trouvé: {GHSPOP_CSV}")
# &e

# &s &CTX_MERGE - Enrichissement contexte (panel externe: tourisme, UCDB, statique)
CTX_CSV = BASE / "data" / "external" / "kpi-ctx-city-panel-v2.csv"
if CTX_CSV.exists():
    ctx_df = pd.read_csv(CTX_CSV, encoding="utf-8-sig")
    # Colonnes indicateurs ctx_* à merger
    ctx_indic = [c for c in ctx_df.columns if c.startswith("ctx_")]
    # Colonnes méta à merger (is_capital, income_group, region)
    ctx_meta = [c for c in ["is_capital", "income_group", "region"] if c in ctx_df.columns]
    ctx_merge = ctx_df[["panel_city_slug"] + ctx_meta + ctx_indic].copy()
    ctx_merge = ctx_merge.rename(columns={"panel_city_slug": "city"})
    city_kpi = city_kpi.merge(ctx_merge, on="city", how="left")
    n_ctx = city_kpi[ctx_indic[0]].notna().sum() if ctx_indic else 0
    print(f"  Contexte: {n_ctx}/{len(city_kpi)} villes enrichies ({len(ctx_indic)} indic + {len(ctx_meta)} méta)")
else:
    print(f"  [WARN] Contexte non trouvé: {CTX_CSV}")
# &e

# &s &KPI_AGGREGATE - KPI par pays, continent, monde
print("Calcul KPI agrégats...")

def compute_aggregate_kpi(df_sub, groupby_col=None):
    """Calcule KPI agrégés depuis les listings bruts via re-pooling complet (option 1).

    Tous les indicateurs (concentration Gini/CR, classes exclusives, Adamiak,
    reviews, capacité, host, occupancy) sont recalculés sur le pool complet du groupe,
    pas moyennés depuis les KPI ville.
    """
    if groupby_col:
        grp = df_sub.groupby(groupby_col)
    else:
        df_sub = df_sub.assign(_all="world")
        grp = df_sub.groupby("_all")
    gcol = groupby_col or "_all"

    # === Core (volumes, prix médian global, structure, activité, avis) ===
    agg_kpi = grp.agg(
        n_villes=("city", "nunique"),
        vol_n_ann=("id", "count"),
        str_n_entire=("is_entire_home", "sum"),
        vol_n_hotes=("host_id", "nunique"),
        px_med=("price_eur", "median"),
        str_entire_pct=("is_entire_home", "mean"),
        str_minnuits30_pct=("is_longterm", "mean"),
        str_minnuits90_pct=("is_longterm90", "mean"),
        act_cal_ouvert_med=("availability_365", "median"),
        act_cal_ouvert_moy=("availability_365", "mean"),
        act_cal_180j_pct=("availability_365", lambda x: round((x >= 180).mean() * 100, 1)),
        actrv_avis=("number_of_reviews", "median"),
        actrv_avis_mois=("reviews_per_month", lambda x: x.dropna().median()),
    ).reset_index()

    # === Prix par type de logement ===
    entire = df_sub[df_sub["room_type"] == "Entire home/apt"]
    private = df_sub[df_sub["room_type"] == "Private room"]

    entire_px = entire.groupby(gcol).agg(
        px_entire_med=("price_eur", "median"),
        px_entire_q25=("price_eur", lambda x: x.quantile(0.25)),
        px_entire_q75=("price_eur", lambda x: x.quantile(0.75)),
    ).reset_index()
    entire_px["px_entire_iqr"] = (entire_px["px_entire_q75"] - entire_px["px_entire_q25"]).round(0)
    private_px = private.groupby(gcol).agg(px_private_med=("price_eur", "median")).reset_index()
    agg_kpi = agg_kpi.merge(entire_px, on=gcol, how="left")
    agg_kpi = agg_kpi.merge(private_px, on=gcol, how="left")

    # === Concentration (re-pooling complet sur tous les hôtes du groupe) ===
    conc_50 = df_sub.groupby(gcol).apply(concentration_50, include_groups=False).reset_index(name="cr_hosts_offre50_pct")
    conc_metrics = df_sub.groupby(gcol).apply(concentration_metrics, include_groups=False).reset_index()
    agg_kpi = agg_kpi.merge(conc_50, on=gcol, how="left")
    agg_kpi = agg_kpi.merge(conc_metrics, on=gcol, how="left")

    # === Reviews (re-pooling) ===
    rev_agg = df_sub.groupby(gcol).agg(**{
        **{f"actrv_note_{fr}": (f"review_scores_{en}", lambda x, en=en: round(x.dropna().median(), 2) if x.dropna().shape[0] > 0 else np.nan)
           for en, fr in _SUB_NOTES.items()},
        **{f"actrv_note_{fr}_n": (f"review_scores_{en}", lambda x, en=en: x.dropna().shape[0])
           for en, fr in _SUB_NOTES.items()},
    }).reset_index()
    rev_cov_agg = df_sub.groupby(gcol).agg(
        actrv_listing_ac_avis_pct=("review_scores_rating", lambda x: round(x.notna().mean() * 100, 1))
    ).reset_index()
    agg_kpi = agg_kpi.merge(rev_agg, on=gcol, how="left")
    agg_kpi = agg_kpi.merge(rev_cov_agg, on=gcol, how="left")

    # === Capacité ===
    cap_agg = df_sub.groupby(gcol).agg(
        str_cap_pers_med=("accommodates", "median"),
        str_cap_pers_moy=("accommodates", lambda x: round(x.mean(), 1)),
        str_cap_chbr_med=("bedrooms", lambda x: round(x.dropna().median(), 1) if x.dropna().shape[0] > 0 else np.nan),
    ).reset_index()
    agg_kpi = agg_kpi.merge(cap_agg, on=gcol, how="left")

    # === Host ===
    host_agg = df_sub.groupby(gcol).agg(
        act_superhost_pct=("host_is_superhost", lambda x: round(x.dropna().mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
        str_instantbook_pct=("instant_bookable", lambda x: round(x.dropna().mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
    ).reset_index()
    agg_kpi = agg_kpi.merge(host_agg, on=gcol, how="left")

    # === Occupancy / revenus ===
    occ_agg = df_sub.groupby(gcol).agg(
        act_reserv_j_med=("estimated_occupancy_l365d", lambda x: round(x.dropna().median(), 0) if x.dropna().shape[0] > 0 else np.nan),
        act_reserv_j_moy=("estimated_occupancy_l365d", lambda x: round(x.dropna().mean(), 1) if x.dropna().shape[0] > 0 else np.nan),
        act_reserv_30j_pct=("estimated_occupancy_l365d", lambda x: round((x.dropna() >= 30).mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
        act_reserv_180j_pct=("estimated_occupancy_l365d", lambda x: round((x.dropna() >= 180).mean() * 100, 1) if x.dropna().shape[0] > 0 else np.nan),
        act_revenu_med=("revenue_eur", lambda x: round(x.dropna().median(), 0) if x.dropna().shape[0] > 0 else np.nan),
        act_revenu_moy=("revenue_eur", lambda x: round(x.dropna().mean(), 0) if x.dropna().shape[0] > 0 else np.nan),
        act_reserv_taux=("estimated_occupancy_l365d", lambda x: round((x.dropna() / 365 * 100).median(), 1) if x.dropna().shape[0] > 0 else np.nan),
    ).reset_index()
    agg_kpi = agg_kpi.merge(occ_agg, on=gcol, how="left")

    # === Ratios dérivés + arrondis ===
    agg_kpi["str_ratio_ann_hote"] = (agg_kpi["vol_n_ann"] / agg_kpi["vol_n_hotes"]).round(2)
    for col in ["str_entire_pct", "str_minnuits30_pct", "str_minnuits90_pct"]:
        agg_kpi[col] = (agg_kpi[col] * 100).round(1)
    for col in ["px_med", "px_entire_med", "px_private_med",
                "px_entire_q25", "px_entire_q75",
                "act_cal_ouvert_med", "act_cal_ouvert_moy", "actrv_avis", "actrv_avis_mois"]:
        if col in agg_kpi.columns:
            agg_kpi[col] = agg_kpi[col].round(1)

    if groupby_col is None:
        agg_kpi = agg_kpi.drop(columns=["_all"])
    return agg_kpi

# Pays
country_kpi = compute_aggregate_kpi(df, "country_code")
pop_country = city_kpi[city_kpi["scope"] == "city"].groupby("country_code").agg(
    pop_total=("pop", "sum"), housing_total=("housing", "sum"),
).reset_index()
country_kpi = country_kpi.merge(pop_country, on="country_code")
# listings_1000hab / listings_1000log / entire_1000log STANDBY
country_kpi["level"] = "country"
# Ajouter continent_detail au niveau pays
_cd_map = city_kpi[city_kpi["scope"] == "city"].groupby("country_code")["continent_detail"].first()
country_kpi["continent_detail"] = country_kpi["country_code"].map(_cd_map)
country_kpi = country_kpi.sort_values("vol_n_ann", ascending=False)

# Continent (4 groupes bruts)
continent_kpi = compute_aggregate_kpi(df, "continent")
pop_continent = city_kpi[city_kpi["scope"] == "city"].groupby("continent").agg(
    pop_total=("pop", "sum"), housing_total=("housing", "sum"),
    n_countries=("country_code", "nunique"),
).reset_index()
continent_kpi = continent_kpi.merge(pop_continent, on="continent")
# listings_1000hab / listings_1000log / entire_1000log STANDBY
continent_kpi["level"] = "continent"

# Continent_detail (7 groupes affinés)
_cities_scope = city_kpi[city_kpi["scope"] == "city"]
df_cd = df.merge(_cities_scope[["city", "continent_detail"]].drop_duplicates(), on="city", how="left")
contdet_kpi = compute_aggregate_kpi(df_cd, "continent_detail")
pop_contdet = _cities_scope.groupby("continent_detail").agg(
    pop_total=("pop", "sum"), housing_total=("housing", "sum"),
    n_countries=("country_code", "nunique"),
).reset_index()
contdet_kpi = contdet_kpi.merge(pop_contdet, on="continent_detail")
# listings_1000hab / listings_1000log / entire_1000log STANDBY
contdet_kpi["level"] = "continent_detail"
contdet_kpi["continent"] = contdet_kpi["continent_detail"]

# Monde
world_kpi = compute_aggregate_kpi(df)
_cities = city_kpi[city_kpi["scope"] == "city"]
world_kpi["n_countries"] = df["country_code"].nunique()
world_kpi["pop_total"] = _cities["pop"].sum()
world_kpi["housing_total"] = _cities["housing"].sum()
# listings_1000hab / listings_1000log / entire_1000log STANDBY
world_kpi["level"] = "world"
world_kpi["continent"] = "World"

# Concaténer
agg_kpi = pd.concat([world_kpi, continent_kpi, contdet_kpi, country_kpi], ignore_index=True)
cols_agg = ["level", "continent", "continent_detail", "country_code", "n_villes", "n_countries",
    "vol_n_ann", "str_n_entire", "vol_n_hotes", "pop_total", "housing_total",
    # "listings_1000hab", "listings_1000log", "entire_1000log",  # STANDBY
    "px_med", "px_entire_med", "px_entire_q25", "px_entire_q75", "px_entire_iqr",
    "px_private_med",
    "str_entire_pct", "str_minnuits30_pct", "str_minnuits90_pct", "str_ratio_ann_hote",
    "cr_hosts_offre50_pct",
    "cr_offre_top10host_pct", "cr_offre_top10pct_pct", "cr_gini",
    "cr_host_1plus", "cr_host_5plus", "cr_host_10plus",
    "cr_offre_1plus", "cr_offre_5plus", "cr_offre_10plus",
    "cr_host_single_pct", "cr_host_semipro_pct", "cr_host_pro_pct",
    "cr_offre_single_pct", "cr_offre_semipro_pct", "cr_offre_pro_pct",
    "crt_ada_single_home_pct", "crt_ada_multi_home_pct",
    "crt_ada_single_room_pct", "crt_ada_multi_room_pct",
    "act_cal_ouvert_med", "act_cal_ouvert_moy", "act_cal_180j_pct",
    "actrv_avis", "actrv_avis_mois",
    "actrv_note_exact", "actrv_note_exact_n",
    "actrv_note_arrivee", "actrv_note_arrivee_n",
    "actrv_note_proprete", "actrv_note_proprete_n",
    "actrv_note_communic", "actrv_note_communic_n",
    "actrv_listing_ac_avis_pct",
    "actrv_note_emplacem", "actrv_note_emplacem_n",
    "actrv_note_glb", "actrv_note_glb_n",
    "actrv_note_qprix", "actrv_note_qprix_n",
    "str_cap_pers_med", "str_cap_pers_moy", "str_cap_chbr_med",
    "str_instantbook_pct", "act_superhost_pct",
    "act_reserv_j_med", "act_reserv_j_moy",
    "act_reserv_180j_pct", "act_reserv_30j_pct",
    "act_reserv_taux",
    "act_revenu_med", "act_revenu_moy",
    # Pression GHS-POP agrégée (méthodologie cohérente continent/pays/monde)
    "ctx_pop_dense_total", "ctx_aire_dense_km2_total",
    "prs_listings_1000hab_dense", "prs_density_l_km2_dense", "prs_pct_listings_dense",
]

# === &PRESS_DENSE_AGG - Pression dense recalculée par sommation GHS-POP ===
# Sommer ctx_pop_dense + aire_dense_km2 + n_listings_dense + n_listings_total par groupe puis recalculer.
# Méthodologie cohérente = même calcul GHS-POP (cellules ≥1500 hab/km², périmètre Inside Airbnb).
# IMPORTANT : dénominateur du pct = n_listings_total IA (cohérent avec n_listings_dense),
# PAS vol_n_ann city_kpi (swappé centre-commune pour 9 agglos → incohérent avec n_listings_dense).
_cities_dense = city_kpi[city_kpi["scope"] == "city"].copy()

def _agg_dense(df_grp, group_col, group_val):
    """Calcule les 3 ratios dense + totaux pour un sous-ensemble de villes."""
    sub = df_grp.dropna(subset=["ctx_pop_dense", "ctx_aire_dense_km2"])
    if len(sub) == 0:
        return {}
    pop_d = sub["ctx_pop_dense"].sum()
    aire_d = sub["ctx_aire_dense_km2"].sum()
    n_d = sub["_n_listings_dense"].sum() if "_n_listings_dense" in sub.columns else 0
    n_total_ia = sub["_n_listings_total_ia"].sum() if "_n_listings_total_ia" in sub.columns else 0
    return {
        "ctx_pop_dense_total": int(pop_d),
        "ctx_aire_dense_km2_total": round(aire_d, 1),
        "prs_listings_1000hab_dense": round(n_d / pop_d * 1000, 2) if pop_d > 0 else None,
        "prs_density_l_km2_dense": round(n_d / aire_d, 1) if aire_d > 0 else None,
        "prs_pct_listings_dense": round(n_d / n_total_ia * 100, 1) if n_total_ia > 0 else None,
    }

# Construire un dict {level, key} -> dict de ratios
dense_rows = []
# world
d = _agg_dense(_cities_dense, "_all", "world")
dense_rows.append({"level": "world", **d})
# continent
for cont, sub in _cities_dense.groupby("continent"):
    d = _agg_dense(sub, "continent", cont)
    dense_rows.append({"level": "continent", "continent": cont, **d})
# continent_detail
for cont_d, sub in _cities_dense.groupby("continent_detail"):
    d = _agg_dense(sub, "continent_detail", cont_d)
    dense_rows.append({"level": "continent_detail", "continent_detail": cont_d, **d})
# country
for cc, sub in _cities_dense.groupby("country_code"):
    d = _agg_dense(sub, "country_code", cc)
    dense_rows.append({"level": "country", "country_code": cc, **d})

dense_df = pd.DataFrame(dense_rows)
# Merge sur agg_kpi par (level + clé adéquate)
for lvl, key in [("world", None), ("continent", "continent"),
                 ("continent_detail", "continent_detail"), ("country", "country_code")]:
    sub_dense = dense_df[dense_df["level"] == lvl].drop(columns=["level"])
    if key is None:
        # Une seule ligne world : injection directe
        mask = agg_kpi["level"] == "world"
        for col in ["ctx_pop_dense_total", "ctx_aire_dense_km2_total",
                    "prs_listings_1000hab_dense", "prs_density_l_km2_dense", "prs_pct_listings_dense"]:
            if col in sub_dense.columns:
                agg_kpi.loc[mask, col] = sub_dense.iloc[0][col]
    else:
        for _, r in sub_dense.iterrows():
            mask = (agg_kpi["level"] == lvl) & (agg_kpi[key] == r[key])
            for col in ["ctx_pop_dense_total", "ctx_aire_dense_km2_total",
                        "prs_listings_1000hab_dense", "prs_density_l_km2_dense", "prs_pct_listings_dense"]:
                if col in r.index and pd.notna(r[col]):
                    agg_kpi.loc[mask, col] = r[col]

cols_agg = [c for c in cols_agg if c in agg_kpi.columns]
agg_kpi = agg_kpi[cols_agg]

print(f"  {len(country_kpi)} pays + {len(continent_kpi)} continents + 1 monde = {len(agg_kpi)} lignes")
print(f"  Pression dense GHS-POP: {agg_kpi['prs_listings_1000hab_dense'].notna().sum()}/{len(agg_kpi)} agrégats enrichis")
# &e

# &s &EXPORT
# Flags proxy / prix-invalide propagés par ville (depuis le parquet, comme continent).
# is_proxy=1 (Berlin) -> exclure de TOUTE l'évolution ; price_invalid=1 (Zurich/Geneva) -> exclure évolution PRIX.
for _flag in ["is_proxy", "price_invalid"]:
    if _flag in df.columns:
        city_kpi[_flag] = city_kpi["city"].map(df.groupby("city")[_flag].first()).fillna(0).astype(int)
    else:
        city_kpi[_flag] = 0

out_city = INTERIM_DIR / f"kpi_{scope}_by_city_{SNAP_TAG}.csv"
out_agg = INTERIM_DIR / f"kpi_{scope}_by_aggregate_{SNAP_TAG}.csv"

city_kpi.drop(columns=["_n_listings_dense", "_n_listings_total_ia"], errors="ignore").to_csv(out_city, index=False, encoding="utf-8-sig")
agg_kpi.to_csv(out_agg, index=False, encoding="utf-8-sig")

print(f"\n{'='*60}")
print(f"Export ville:  {out_city.name} ({len(city_kpi)} lignes, {len(city_kpi.columns)} cols)")
print(f"Export agrégat: {out_agg.name} ({len(agg_kpi)} lignes)")
print(f"{'='*60}")

print(f"\n--- TOP 15 villes (volume) ---")
top_cols = ["city_fr", "continent", "vol_n_ann", "density_l_km2",
            "px_entire_med", "cr_offre_1plus", "actrv_note_glb", "act_revenu_med"]
top_cols = [c for c in top_cols if c in city_kpi.columns]
print(city_kpi.head(15)[top_cols].to_string(index=False))

_cities_only = city_kpi[city_kpi["scope"] == "city"]
_sub_only = city_kpi[city_kpi["scope"] == "sub_city"]
print(f"\n--- Totaux ({len(_cities_only)} villes + {len(_sub_only)} sub_cities) ---")
print(f"Listings total: {_cities_only['vol_n_ann'].sum():,}")
print(f"Prix médian global: {df['price_eur'].median():.0f} EUR")
# &e

# &s &SYNC_DDICT - Propagation auto du ddict source vers les caches locaux
# Source de verite : reports/helpers/ddict-airbnb.json
# Copies : dashboard/src/data/ + rpt-bis/helpers/
import shutil
_DDICT_SRC = BASE / "reports" / "helpers" / "ddict-airbnb.json"
_DDICT_TARGETS = [
    BASE / "dashboard" / "src" / "data" / "ddict-airbnb.json",
    BASE / "rpt-bis" / "helpers" / "ddict-airbnb.json",
]
if _DDICT_SRC.exists():
    n_sync = 0
    for tgt in _DDICT_TARGETS:
        if tgt.parent.exists():
            shutil.copy2(_DDICT_SRC, tgt)
            n_sync += 1
    print(f"\nddict propage: {n_sync}/{len(_DDICT_TARGETS)} copies synchronisees")
# &e

# &s &EXPORT_DASHBOARD_JSON - Export JSON pour dashboard Observable
DASH_DIR = BASE / "dashboard" / "src" / "data"
if DASH_DIR.exists() and WRITE_DASHBOARD:
    import json

    # City KPI JSON (toutes les villes)
    city_kpi.to_json(DASH_DIR / "kpi_city.json", orient="records", force_ascii=False)

    # Aggregates JSON (monde/continent/country)
    agg_kpi.to_json(DASH_DIR / "kpi_agg.json", orient="records", force_ascii=False)

    # City reference with coords for world map
    ref = pd.read_csv(REF_CSV)
    coords = ref[["city", "lat", "lon"]].dropna()
    city_with_coords = city_kpi.merge(coords, on="city", how="left")
    city_with_coords.to_json(DASH_DIR / "kpi_city_geo.json", orient="records", force_ascii=False)

    print(f"\nDashboard JSON: {DASH_DIR}")
    print(f"  kpi_city.json ({len(city_kpi)} villes)")
    print(f"  kpi_agg.json ({len(agg_kpi)} agrégats)")
    print(f"  kpi_city_geo.json ({len(city_with_coords)} villes + coords)")
elif not WRITE_DASHBOARD:
    print(f"\n[SKIP] Dashboard JSON non réécrit (snapshot {SNAPSHOT} != live 25-06 ; ajouter --publish pour forcer)")
else:
    print(f"\n[SKIP] Dashboard dir not found: {DASH_DIR}")
# &e

# &e
