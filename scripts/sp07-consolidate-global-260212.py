# &s &CONSOLIDATE_GLOBAL_aaMAIN - Consolidation ~54 villes monde (hors régions)
# Fichier: sp07-consolidate-global-260212.py | dcr: 26-02-12 | dup: 26-02-12
# Usage: python sp07-consolidate-global-260212.py [--europe-only]
# Scanne europe/ + usa/ + world/ — exclut régions et counties

from pathlib import Path
import pandas as pd
import numpy as np
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
RAW_BASE = BASE / "data" / "raw" / "zudb-inside-airbnbbnb"
INTERIM_DIR = BASE / "data" / "interim"
REF_CSV = BASE / "data" / "external" / "city-reference-airbnb-260217.csv"

SCAN_DIRS = {
    "europe": RAW_BASE / "europe",
    "usa": RAW_BASE / "usa",
    "world": RAW_BASE / "world",
}

MIN_LISTINGS = 2000

# Table de référence unique — remplace CITY_META, REGIONS_EXCLUDE, COUNTRY_CODES, etc.
_ref = pd.read_csv(REF_CSV)
REGIONS = set(_ref[_ref["type"] == "region"]["city"])
CITY_META = _ref[_ref["city"].notna()].set_index("city")[
    ["country_code", "continent", "pop", "housing", "lat", "lon"]
].to_dict("index")
COUNTRY_CODES = dict(zip(_ref["raw_country"].dropna(), _ref["country_code"].dropna()))
# Fallback continent par dossier racine (pour villes non référencées)
FOLDER_CONTINENT = {"europe": "Europe", "usa": "Americas"}

# Filtres par neighbourhood_group — pour les villes dont Inside Airbnb couvre
# un périmètre plus large que la ville cible (régions, agglomérations).
# Clé = slug ville, valeur = liste de neighbourhood_groups à GARDER.
CITY_NBH_FILTERS = {
    "pays-basque": ["Biarritz", "Anglet", "Bayonne"],  # BAB uniquement (45% du total)
}
# &e

# &s &LOAD_CITIES
def find_sumlistings(city_dir, snapshot="25-06"):
    """Trouve le fichier sumlistings pour un snapshot donné."""
    for f in city_dir.glob(f"*{snapshot}*sumlistings.csv"):
        return f
    return None


def load_all_cities(snapshot="25-06", europe_only=False):
    """Charge toutes les villes des répertoires configurés."""
    all_dfs = []

    scan = {"europe": SCAN_DIRS["europe"]} if europe_only else SCAN_DIRS

    for region_key, region_dir in scan.items():
        if not region_dir.exists():
            print(f"  [WARN] Répertoire absent: {region_dir}")
            continue

        print(f"\n--- {region_key.upper()} ---")

        for country_dir in sorted(region_dir.iterdir()):
            if not country_dir.is_dir():
                continue
            country_name = country_dir.name
            country_code = COUNTRY_CODES.get(country_name, country_name[:3].upper())

            for city_dir in sorted(country_dir.iterdir()):
                if not city_dir.is_dir():
                    continue
                city_name = city_dir.name

                if city_name in REGIONS:
                    continue

                csv_file = find_sumlistings(city_dir, snapshot)
                if csv_file is None:
                    continue

                try:
                    df = pd.read_csv(csv_file)

                    # Filtre neighbourhood_group si la ville a un périmètre restreint
                    if city_name in CITY_NBH_FILTERS:
                        keep_groups = CITY_NBH_FILTERS[city_name]
                        n_before = len(df)
                        df = df[df["neighbourhood_group"].isin(keep_groups)]
                        print(f"  [FILT] {city_name}: {n_before:,} -> {len(df):,} "
                              f"(garder {', '.join(keep_groups)})")

                    n = len(df)

                    if n < MIN_LISTINGS:
                        print(f"  [SKIP] {city_name} ({n:,} < {MIN_LISTINGS:,})")
                        continue

                    df["city"] = city_name
                    df["country"] = country_name
                    df["country_code"] = country_code

                    # Continent : CSV ref > fallback par dossier racine
                    meta = CITY_META.get(city_name, {})
                    cont = meta.get("continent", "")
                    if not cont or (isinstance(cont, float) and np.isnan(cont)):
                        cont = FOLDER_CONTINENT.get(region_key, "Other")
                    df["continent"] = cont

                    df["city_pop"] = meta.get("pop", np.nan)
                    df["city_housing"] = meta.get("housing", np.nan)
                    df["city_lat"] = meta.get("lat", np.nan)
                    df["city_lon"] = meta.get("lon", np.nan)

                    all_dfs.append(df)
                    print(f"  [OK]   {city_name}: {n:,} listings ({country_code})")

                except Exception as e:
                    print(f"  [ERR]  {city_name}: {e}")

    if not all_dfs:
        raise ValueError("Aucune ville chargée!")

    return pd.concat(all_dfs, ignore_index=True)
# &e

# &s &MAIN
if __name__ == "__main__":
    europe_only = "--europe-only" in sys.argv
    scope = "EUROPE ONLY" if europe_only else "GLOBAL"

    print("=" * 60)
    print(f"CONSOLIDATION {scope}")
    print("=" * 60)
    print(f"Seuil: {MIN_LISTINGS:,} listings minimum")
    print(f"Régions exclues: {len(REGIONS)}")

    df = load_all_cities("25-06", europe_only=europe_only)

    n_cities = df["city"].nunique()
    n_countries = df["country_code"].nunique()
    n_continents = df["continent"].nunique()

    print()
    print("=" * 60)
    print("RÉSULTAT")
    print("=" * 60)
    print(f"Total listings: {len(df):,}")
    print(f"Villes: {n_cities}")
    print(f"Pays: {n_countries}")
    print(f"Continents: {n_continents}")

    # Stats par ville
    stats = df.groupby(["continent", "country_code", "city"]).agg(
        n=("id", "count"),
        pop=("city_pop", "first"),
        housing=("city_housing", "first"),
    ).reset_index().sort_values("n", ascending=False)

    stats["listings_per_1000hab"] = (stats["n"] / stats["pop"] * 1000).round(1)

    print()
    for cont in sorted(stats["continent"].unique()):
        sub = stats[stats["continent"] == cont]
        print(f"\n--- {cont} ({len(sub)} villes) ---")
        print(sub[["country_code", "city", "n", "listings_per_1000hab"]].to_string(index=False))

    # Uniformiser types object avant export parquet
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).replace("nan", pd.NA)

    # Sauvegarder
    suffix = "europe" if europe_only else "global"
    out_path = INTERIM_DIR / f"dbsumlistings_2506_cons_{suffix}.parquet"
    df.to_parquet(out_path, index=False)
    print(f"\n[EXPORT] {out_path.name}: {len(df):,} lignes, {n_cities} villes")

    out_stats = INTERIM_DIR / f"recap_stats_{suffix}_2506.csv"
    stats.to_csv(out_stats, index=False, encoding="utf-8-sig")
    print(f"[EXPORT] {out_stats.name}")

    print("\nDone!")
# &e

# &e &CONSOLIDATE_GLOBAL_aaMAIN
