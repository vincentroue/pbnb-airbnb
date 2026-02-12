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

europe_only = "--europe-only" in sys.argv
scope = "europe" if europe_only else "global"
DATA_PATH = INTERIM_DIR / f"dbsumlistings_2506_cons_{scope}.parquet"

# Si fichier europe n'existe pas, filtrer depuis global
if europe_only and not DATA_PATH.exists():
    DATA_PATH = INTERIM_DIR / "dbsumlistings_2506_cons_global.parquet"

sys.path.insert(0, str(BASE / "scripts"))
from city_reference_data import CITY_DATA

# Greater Manchester : IA couvre la métropole
CITY_DATA["greater-manchester"] = {
    "pop": 2_867_000, "housing": 1_200_000,
    "pop_source": "ONS Census 2021 (Greater Manchester Combined Authority)",
    "housing_source": "ONS Census 2021 GMCA: ~1.2M dwellings",
}

# Taux conversion EUR (mi-2025)
FX_EUR = {
    # Europe (hors zone euro)
    "GBR": 1.17, "HUN": 0.0026, "TUR": 0.028, "DNK": 0.134, "CZE": 0.040,
    "NOR": 0.085, "SWE": 0.087, "CHE": 1.06, "LVA": 1.0,  # Lettonie = EUR
    # Americas
    "USA": 0.92, "CAN": 0.67, "BRA": 0.17, "MEX": 0.052, "ARG": 0.001, "CHL": 0.0010,
    # Asia-Pacific
    "JPN": 0.0062, "AUS": 0.60, "SGP": 0.69, "CHN": 0.13,  # HKD
    "TWN": 0.029, "THA": 0.027,
    # Africa
    "ZAF": 0.050,
}

# Noms français
CITY_FR = {
    # Europe
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
    "bergamo": "Bergame", "zurich": "Zurich", "riga": "Riga",
    # USA
    "new-york-city": "New York", "los-angeles": "Los Angeles",
    "chicago": "Chicago", "san-francisco": "San Francisco",
    "washington-dc": "Washington DC", "boston": "Boston", "seattle": "Seattle",
    "austin": "Austin", "san-diego": "San Diego", "nashville": "Nashville",
    "denver": "Denver", "portland": "Portland", "dallas": "Dallas",
    "new-orleans": "La Nouvelle-Orléans",
    # Canada
    "toronto": "Toronto", "vancouver": "Vancouver", "montreal": "Montréal",
    # Asia-Pacific
    "tokyo": "Tokyo", "sydney": "Sydney", "melbourne": "Melbourne",
    "brisbane": "Brisbane", "hong-kong": "Hong Kong", "singapore": "Singapour",
    "taipei": "Taipei", "bangkok": "Bangkok",
    # Americas (hors USA/CAN)
    "mexico-city": "Mexico", "rio-de-janeiro": "Rio de Janeiro",
    "santiago": "Santiago", "buenos-aires": "Buenos Aires",
    # Africa
    "cape-town": "Le Cap",
}
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
conc = df.groupby("city").apply(concentration_50, include_groups=False).reset_index(name="pct_hosts_50pct")
city_kpi = city_kpi.merge(conc, on="city")

# Population et logements
# Priorité : city_reference_data.py (commune propre, Europe) > sp07 CITY_META (parquet)
pop_from_parquet = df.groupby("city")[["city_pop", "city_housing"]].first()

city_kpi["pop"] = city_kpi["city"].map(
    lambda c: CITY_DATA.get(c, {}).get("pop", np.nan)
)
city_kpi["housing"] = city_kpi["city"].map(
    lambda c: CITY_DATA.get(c, {}).get("housing", np.nan)
)
city_kpi["pop_source"] = city_kpi["city"].map(
    lambda c: "confirmed" if c in CITY_DATA and "ESTIMATE" not in CITY_DATA.get(c, {}).get("housing_source", "ESTIMATE") else "estimated"
)

# Fallback vers données sp07 (metro) pour villes non-européennes
for idx, row in city_kpi.iterrows():
    if pd.isna(row["pop"]) and row["city"] in pop_from_parquet.index:
        city_kpi.at[idx, "pop"] = pop_from_parquet.loc[row["city"], "city_pop"]
        city_kpi.at[idx, "housing"] = pop_from_parquet.loc[row["city"], "city_housing"]
        city_kpi.at[idx, "pop_source"] = "metro_estimate"

# Ratios de pression
city_kpi["listings_1000hab"] = (city_kpi["n_listings"] / city_kpi["pop"] * 1000).round(1)
city_kpi["listings_1000hsg"] = (city_kpi["n_listings"] / city_kpi["housing"] * 1000).round(1)
city_kpi["entire_1000hsg"] = (city_kpi["n_entire"] / city_kpi["housing"] * 1000).round(1)

# Nom français
city_kpi["city_fr"] = city_kpi["city"].map(lambda c: CITY_FR.get(c, c.replace("-", " ").title()))

# Arrondir
for col in ["prix_med", "prix_moy", "prix_q25", "prix_q75", "dispo_med", "dispo_moy",
            "reviews_med", "rpm_med"]:
    city_kpi[col] = city_kpi[col].round(1)

# Ordre des colonnes
cols_city = [
    "continent", "country_code", "city", "city_fr", "pop_source",
    "n_listings", "n_entire", "n_hosts",
    "pop", "housing",
    "listings_1000hab", "listings_1000hsg", "entire_1000hsg",
    "prix_med", "prix_moy", "prix_q25", "prix_q75", "prix_iqr",
    "pct_entire", "pct_multi", "pct_longterm", "ratio_lh",
    "pct_hosts_50pct",
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
