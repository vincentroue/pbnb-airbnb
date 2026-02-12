"""
sp08-consolidate-10cities-260108.py
Consolide sumlistings + listings.gz pour 10 villes Europe (3 snapshots)
Output: data/interim/
"""

import pandas as pd
from pathlib import Path
import gzip
import re

# =======&s CONFIG =======
BASE_PATH = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
RAW_PATH = BASE_PATH / "data" / "raw" / "zudb-inside-airbnbbnb"
INTERIM_PATH = BASE_PATH / "data" / "interim"

# 10 villes cibles avec leurs chemins relatifs et codes pays
CITIES = {
    "paris": {"path": "europe/france/paris", "country": "FRA", "country_name": "France"},
    "london": {"path": "europe/united-kingdom/london", "country": "GBR", "country_name": "United Kingdom"},
    "rome": {"path": "europe/italy/rome", "country": "ITA", "country_name": "Italy"},
    "berlin": {"path": "europe/germany/berlin", "country": "DEU", "country_name": "Germany"},
    "florence": {"path": "europe/italy/florence", "country": "ITA", "country_name": "Italy"},
    "budapest": {"path": "europe/hungary/budapest", "country": "HUN", "country_name": "Hungary"},
    "bordeaux": {"path": "europe/france/bordeaux", "country": "FRA", "country_name": "France"},
    "lyon": {"path": "europe/france/lyon", "country": "FRA", "country_name": "France"},
    "venice": {"path": "europe/italy/venice", "country": "ITA", "country_name": "Italy"},
    "brussels": {"path": "europe/belgium/brussels", "country": "BEL", "country_name": "Belgium"},
}

SNAPSHOTS = ["25-03", "25-06", "25-09"]
# =======&e CONFIG =======


# =======&s LOAD_SUMLISTINGS =======
def load_sumlistings(city: str, info: dict) -> list:
    """Load all sumlistings for a city"""
    city_path = RAW_PATH / info["path"]
    dfs = []

    for snap in SNAPSHOTS:
        # Pattern: 25-03-FRA-paris_sumlistings.csv
        pattern = f"{snap}-{info['country']}-{city}_sumlistings.csv"
        filepath = city_path / pattern

        if filepath.exists():
            df = pd.read_csv(filepath, low_memory=False)
            df["city"] = city
            df["country_code"] = info["country"]
            df["country_name"] = info["country_name"]
            df["date_snapshot"] = f"20{snap.replace('-', '-')}"  # 2025-03
            dfs.append(df)
            print(f"  ✓ {pattern}: {len(df):,} lignes")
        else:
            print(f"  ✗ {pattern}: NOT FOUND")

    return dfs
# =======&e LOAD_SUMLISTINGS =======


# =======&s LOAD_LISTINGS_GZ =======
def load_listings_gz(city: str, info: dict) -> list:
    """Load all listings.gz for a city"""
    city_path = RAW_PATH / info["path"]
    dfs = []

    for snap in SNAPSHOTS:
        # Path: 25-03/listings.csv.gz
        gz_path = city_path / snap / "listings.csv.gz"

        if gz_path.exists():
            try:
                with gzip.open(gz_path, 'rt', encoding='utf-8') as f:
                    df = pd.read_csv(f, low_memory=False)
                df["city"] = city
                df["country_code"] = info["country"]
                df["country_name"] = info["country_name"]
                df["date_snapshot"] = f"20{snap.replace('-', '-')}"
                dfs.append(df)
                print(f"  ✓ {snap}/listings.csv.gz: {len(df):,} lignes, {len(df.columns)} cols")
            except Exception as e:
                print(f"  ✗ {snap}/listings.csv.gz: ERROR - {e}")
        else:
            print(f"  ✗ {snap}/listings.csv.gz: NOT FOUND")

    return dfs
# =======&e LOAD_LISTINGS_GZ =======


# =======&s MAIN =======
def main():
    print("=" * 70)
    print("CONSOLIDATION 10 VILLES EUROPE - AIRBNB")
    print("=" * 70)

    INTERIM_PATH.mkdir(parents=True, exist_ok=True)

    # -------&s sumlistings -------
    print("\n[1/4] CHARGEMENT SUMLISTINGS...")
    all_sum = []
    for city, info in CITIES.items():
        print(f"\n{city.upper()} ({info['country']}):")
        dfs = load_sumlistings(city, info)
        all_sum.extend(dfs)

    df_sum = pd.concat(all_sum, ignore_index=True)
    print(f"\n→ Total sumlistings: {len(df_sum):,} lignes")
    # -------&e sumlistings -------

    # -------&s listings_gz -------
    print("\n[2/4] CHARGEMENT LISTINGS.GZ...")
    all_full = []
    for city, info in CITIES.items():
        print(f"\n{city.upper()} ({info['country']}):")
        dfs = load_listings_gz(city, info)
        all_full.extend(dfs)

    df_full = pd.concat(all_full, ignore_index=True)
    print(f"\n→ Total listings full: {len(df_full):,} lignes")
    # -------&e listings_gz -------

    # -------&s save_parquet -------
    print("\n[3/4] SAUVEGARDE PARQUET (3 snapshots)...")

    # Sumlistings
    out_sum = INTERIM_PATH / "dbsumlistings_snaps_cons10city.parquet"
    df_sum.to_parquet(out_sum, index=False)
    print(f"  ✓ {out_sum.name}: {out_sum.stat().st_size/1024/1024:.1f} MB")

    # Listings full
    out_full = INTERIM_PATH / "dblistingfull_snap_cons10city.parquet"
    df_full.to_parquet(out_full, index=False)
    print(f"  ✓ {out_full.name}: {out_full.stat().st_size/1024/1024:.1f} MB")
    # -------&e save_parquet -------

    # -------&s excel_recap -------
    print("\n[4/4] EXPORT EXCEL RECAP...")

    # Pivot table: city x snapshot
    recap_sum = df_sum.groupby(["country_name", "city", "date_snapshot"]).size().unstack(fill_value=0)
    recap_sum.columns = [f"snap_{c[-2:]}" for c in recap_sum.columns]  # snap_03, snap_06, snap_09
    recap_sum = recap_sum.reset_index()
    recap_sum["total"] = recap_sum[[c for c in recap_sum.columns if c.startswith("snap_")]].sum(axis=1)
    recap_sum = recap_sum.sort_values("total", ascending=False)

    excel_path = INTERIM_PATH / "recap_volumes_10cities.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        recap_sum.to_excel(writer, sheet_name="volumes_par_snap", index=False)

        # Ajout résumé par pays
        recap_country = df_sum.groupby(["country_name", "date_snapshot"]).size().unstack(fill_value=0)
        recap_country.columns = [f"snap_{c[-2:]}" for c in recap_country.columns]
        recap_country["total"] = recap_country.sum(axis=1)
        recap_country = recap_country.reset_index().sort_values("total", ascending=False)
        recap_country.to_excel(writer, sheet_name="volumes_par_pays", index=False)

    print(f"  ✓ {excel_path.name}")
    # -------&e excel_recap -------

    # -------&s filter_june -------
    print("\n[5/5] EXPORT FILTRE JUIN 2025...")

    # Filter juin
    df_sum_june = df_sum[df_sum["date_snapshot"] == "2025-06"].copy()
    df_full_june = df_full[df_full["date_snapshot"] == "2025-06"].copy()

    out_sum_june = INTERIM_PATH / "dbsumlistings_2506.parquet"
    out_full_june = INTERIM_PATH / "dblistingfull_2506_cons.parquet"

    df_sum_june.to_parquet(out_sum_june, index=False)
    df_full_june.to_parquet(out_full_june, index=False)

    print(f"  ✓ {out_sum_june.name}: {len(df_sum_june):,} lignes, {out_sum_june.stat().st_size/1024/1024:.1f} MB")
    print(f"  ✓ {out_full_june.name}: {len(df_full_june):,} lignes, {out_full_june.stat().st_size/1024/1024:.1f} MB")
    # -------&e filter_june -------

    # -------&s summary -------
    print("\n" + "=" * 70)
    print("RÉSUMÉ FINAL")
    print("=" * 70)
    print(f"\nFichiers créés dans {INTERIM_PATH}:")
    print(f"  1. dbsumlistings_snaps_cons10city.parquet ({len(df_sum):,} lignes)")
    print(f"  2. dblistingfull_snap_cons10city.parquet ({len(df_full):,} lignes)")
    print(f"  3. recap_volumes_10cities.xlsx")
    print(f"  4. dbsumlistings_2506.parquet ({len(df_sum_june):,} lignes)")
    print(f"  5. dblistingfull_2506_cons.parquet ({len(df_full_june):,} lignes)")

    print("\n--- VOLUMES PAR VILLE (Juin 2025) ---")
    print(df_sum_june.groupby(["country_name", "city"]).size().sort_values(ascending=False).to_string())
    # -------&e summary -------

if __name__ == "__main__":
    main()
# =======&e MAIN =======
