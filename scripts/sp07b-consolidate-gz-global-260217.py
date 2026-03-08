# &s &CONSOLIDATE_GZ_aaMAIN - Consolidation listings.csv.gz pour villes intégrées

# Charge les listings.csv.gz (79 cols) pour toutes les villes intégrées,
# ne garde que ~30 cols utiles, applique le cleaning pipeline, exporte parquet.
# Utilise city-reference-airbnb-260217.csv comme source de vérité.
#
# Usage:
#   python scripts/sp07b-consolidate-gz-global-260217.py [--europe-only]
#
# Outputs:
#   data/interim/dblistingfull_2506_cons_global.parquet
#   data/interim/dblistingfull_2506_cons_europe.parquet (si --europe-only)
#
# Fichier: sp07b-consolidate-gz-global-260217.py | dcr: 26-02-17 | dup: 26-02-17

from pathlib import Path
import pandas as pd
import numpy as np
import gzip
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
RAW_BASE = BASE / "data" / "raw" / "zudb-inside-airbnbbnb"
INTERIM_DIR = BASE / "data" / "interim"
REF_CSV = BASE / "data" / "external" / "city-reference-airbnb-260217.csv"

europe_only = "--europe-only" in sys.argv
scope = "europe" if europe_only else "global"
SNAPSHOT = "25-06"

# Colonnes à garder (sur ~79 disponibles)
KEEP_COLS = [
    # Identifiants
    "id", "host_id",
    # Géo
    "latitude", "longitude", "neighbourhood_cleansed",
    # Logement
    "property_type", "room_type", "accommodates", "bedrooms", "bathrooms_text",
    # Prix et dispo
    "price", "minimum_nights", "maximum_nights",
    "availability_365",
    # Activité
    "number_of_reviews", "number_of_reviews_ltm",
    "reviews_per_month", "first_review", "last_review",
    # Review scores
    "review_scores_rating", "review_scores_accuracy",
    "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location",
    "review_scores_value",
    # Host profil
    "host_is_superhost", "host_response_time", "host_response_rate",
    "host_identity_verified", "host_since",
    "calculated_host_listings_count",
    # Booking
    "instant_bookable", "license",
    # Estimations Inside Airbnb
    "estimated_occupancy_l365d", "estimated_revenue_l365d",
]

# Table de référence
_ref = pd.read_csv(REF_CSV)
_ref_int = _ref[_ref["status"] == "integrated"]
if europe_only:
    _ref_int = _ref_int[_ref_int["continent"] == "Europe"]
CITIES = _ref_int.set_index("city")[
    ["raw_folder", "raw_country", "country_code", "continent", "pop", "housing"]
].to_dict("index")

# Taux FX
_fx = _ref.dropna(subset=["country_code", "fx_eur"]).drop_duplicates("country_code")
FX_EUR = dict(zip(_fx["country_code"], _fx["fx_eur"]))

# Filtres par neighbourhood — sous-sélection géographique pour certaines villes
CITY_NBH_FILTERS = {
    "pays-basque": ["Biarritz", "Anglet", "Bayonne"],
}
# &e

# &s &LOAD_GZ
def load_gz_city(city, meta):
    """Charge un gz avec colonnes sélectionnées + métadonnées."""
    gz_path = RAW_BASE / meta["raw_folder"] / meta["raw_country"] / city / SNAPSHOT / "listings.csv.gz"
    if not gz_path.exists():
        return None, f"pas de gz {SNAPSHOT}"

    # Lire header pour filtrer aux colonnes existantes
    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    cols_present = [c for c in KEEP_COLS if c in header]

    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f, usecols=cols_present, low_memory=False)

    # Parser prix "$135.00" -> float
    if "price" in df.columns:
        df["price"] = df["price"].replace(r'[\$,]', '', regex=True).astype(float)

    # Filtre neighbourhood_group si périmètre restreint
    if city in CITY_NBH_FILTERS:
        keep = CITY_NBH_FILTERS[city]
        # gz utilise neighbourhood_cleansed, pas neighbourhood_group
        # On filtre aussi sur neighbourhood_group si elle existe dans le header
        n_before = len(df)
        if "neighbourhood_group_cleansed" in df.columns:
            df = df[df["neighbourhood_group_cleansed"].isin(keep)]
        elif "neighbourhood_cleansed" in df.columns:
            df = df[df["neighbourhood_cleansed"].isin(keep)]

    # Métadonnées
    df["city"] = city
    df["country_code"] = meta["country_code"]
    df["continent"] = meta["continent"]

    # Prix EUR
    fx = FX_EUR.get(meta["country_code"], 1.0)
    df["price_eur"] = (df["price"] * fx).round(2)

    # Flags
    df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(np.int8)
    df["is_multihost"] = (df["calculated_host_listings_count"] > 1).astype(np.int8)
    df["is_longterm"] = (df["minimum_nights"] >= 30).astype(np.int8)

    # Booleans t/f -> int8
    for col in ["host_is_superhost", "host_identity_verified", "instant_bookable"]:
        if col in df.columns:
            df[col] = df[col].map({"t": 1, "f": 0}).astype("Int8")

    # host_response_rate "95%" -> float
    if "host_response_rate" in df.columns:
        df["host_response_rate"] = (
            df["host_response_rate"].str.rstrip("%").astype(float) / 100
        ).round(3)

    # Population et logements
    df["city_pop"] = meta.get("pop", np.nan)
    df["city_housing"] = meta.get("housing", np.nan)

    return df, None
# &e

# &s &CLEANING
def clean_gz(df):
    """Pipeline cleaning identique à sp08."""
    n_before = len(df)
    df = df[df["price"].notna()]
    df = df[df["availability_365"] > 0]
    df = df[df["room_type"] != "Hotel room"]
    df = df[(df["price_eur"] >= 10) & (df["price_eur"] <= 1000)]
    n_after = len(df)
    return df, n_before, n_after
# &e

# &s &MAIN
if __name__ == "__main__":
    print("=" * 60)
    print(f"CONSOLIDATION GZ — {scope.upper()} (snapshot {SNAPSHOT})")
    print("=" * 60)
    print(f"Villes cibles: {len(CITIES)}")
    print(f"Colonnes sélectionnées: {len(KEEP_COLS)}")

    all_dfs = []
    errors = []

    for city, meta in sorted(CITIES.items()):
        df, err = load_gz_city(city, meta)
        if err:
            print(f"  [MISS] {city}: {err}")
            errors.append(city)
            continue

        df, n_raw, n_clean = clean_gz(df)
        pct = round(n_clean / n_raw * 100, 1) if n_raw > 0 else 0
        all_dfs.append(df)
        print(f"  [OK]   {city}: {n_raw:,} -> {n_clean:,} ({pct}%) "
              f"| {meta['country_code']} | {len(df.columns)} cols")

    if not all_dfs:
        print("\nAucune ville chargée!")
        sys.exit(1)

    print(f"\nConcaténation...")
    df_all = pd.concat(all_dfs, ignore_index=True)

    # Uniformiser types object avant parquet
    for col in df_all.select_dtypes(include=["object"]).columns:
        df_all[col] = df_all[col].astype(str).replace("nan", pd.NA)
        if df_all[col].nunique() < 50:
            df_all[col] = df_all[col].astype("category")

    n_cities = df_all["city"].nunique()
    n_countries = df_all["country_code"].nunique()

    # Export
    out_path = INTERIM_DIR / f"dblistingfull_2506_cons_{scope}.parquet"
    df_all.to_parquet(out_path, index=False)
    size_mb = out_path.stat().st_size / 1024 / 1024

    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT")
    print(f"{'=' * 60}")
    print(f"Total: {len(df_all):,} listings nettoyés")
    print(f"Villes: {n_cities} | Pays: {n_countries}")
    print(f"Colonnes: {len(df_all.columns)}")
    print(f"Export: {out_path.name} ({size_mb:.0f} MB)")

    if errors:
        print(f"\nManquants ({len(errors)}): {', '.join(errors)}")

    # Stats par continent
    print(f"\n--- Par continent ---")
    stats = df_all.groupby("continent").agg(
        villes=("city", "nunique"),
        listings=("id", "count"),
    ).sort_values("listings", ascending=False)
    print(stats.to_string())

    # Top 15 par volume
    print(f"\n--- Top 15 villes ---")
    top = df_all.groupby(["continent", "country_code", "city"]).agg(
        n=("id", "count"),
        prix_med=("price_eur", "median"),
        rev_med=("review_scores_rating", lambda x: x.dropna().median()),
        pct_super=("host_is_superhost", lambda x: round(x.mean() * 100, 1)),
    ).sort_values("n", ascending=False).head(15)
    print(top.to_string())

    print(f"\nColonnes: {list(df_all.columns)}")
    print("\nDone!")
# &e

# &e &CONSOLIDATE_GZ_aaMAIN
