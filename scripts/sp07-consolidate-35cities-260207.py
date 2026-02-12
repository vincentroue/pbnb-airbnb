# &s &CONSOLIDATE_35CITIES - Consolidation 35 villes européennes (hors régions)
# Fichier: sp07-consolidate-35cities-260207.py | dcr: 26-02-07 | dup: 26-02-07
# Usage: python sp07-consolidate-35cities-260207.py
# Exclut les régions (sicily, puglia, crete, etc.) pour comparabilité ACP

from pathlib import Path
import pandas as pd
import numpy as np

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
RAW_DIR = BASE / "data" / "raw" / "zudb-inside-airbnbbnb" / "europe"
INTERIM_DIR = BASE / "data" / "interim"

# Régions à exclure (pas comparables aux villes)
REGIONS_EXCLUDE = [
    "sicily", "puglia", "south-aegean", "crete", "girona",
    "mallorca", "pays-basque", "euskadi", "vaud", "trentino", "menorca"
]

# Seuil minimum listings
MIN_LISTINGS = 3000

# Mapping pays -> code ISO
COUNTRY_CODES = {
    "austria": "AUT", "belgium": "BEL", "czech-republic": "CZE",
    "denmark": "DNK", "france": "FRA", "germany": "DEU",
    "greece": "GRC", "hungary": "HUN", "ireland": "IRL",
    "italy": "ITA", "norway": "NOR", "portugal": "PRT",
    "spain": "ESP", "sweden": "SWE", "switzerland": "CHE",
    "the-netherlands": "NLD", "turkey": "TUR", "united-kingdom": "GBR"
}

# Population et logements approximatifs (2024, agglomération)
# Sources: Eurostat, UN, Wikipedia
CITY_META = {
    "london": {"pop": 9_648_000, "housing": 3_600_000, "lat": 51.5074, "lon": -0.1278},
    "paris": {"pop": 11_017_000, "housing": 5_100_000, "lat": 48.8566, "lon": 2.3522},
    "rome": {"pop": 4_355_000, "housing": 1_800_000, "lat": 41.9028, "lon": 12.4964},
    "istanbul": {"pop": 15_840_000, "housing": 5_500_000, "lat": 41.0082, "lon": 28.9784},
    "madrid": {"pop": 6_750_000, "housing": 2_900_000, "lat": 40.4168, "lon": -3.7038},
    "lisbon": {"pop": 2_986_000, "housing": 1_200_000, "lat": 38.7223, "lon": -9.1393},
    "copenhagen": {"pop": 1_366_000, "housing": 650_000, "lat": 55.6761, "lon": 12.5683},
    "milan": {"pop": 3_250_000, "housing": 1_500_000, "lat": 45.4642, "lon": 9.1900},
    "barcelona": {"pop": 5_700_000, "housing": 2_300_000, "lat": 41.3851, "lon": 2.1734},
    "athens": {"pop": 3_154_000, "housing": 1_400_000, "lat": 37.9838, "lon": 23.7275},
    "porto": {"pop": 1_320_000, "housing": 550_000, "lat": 41.1579, "lon": -8.6291},
    "vienna": {"pop": 1_982_000, "housing": 950_000, "lat": 48.2082, "lon": 16.3738},
    "berlin": {"pop": 3_677_000, "housing": 2_000_000, "lat": 52.5200, "lon": 13.4050},
    "florence": {"pop": 383_000, "housing": 180_000, "lat": 43.7696, "lon": 11.2558},
    "budapest": {"pop": 1_768_000, "housing": 850_000, "lat": 47.4979, "lon": 19.0402},
    "bordeaux": {"pop": 1_247_000, "housing": 580_000, "lat": 44.8378, "lon": -0.5792},
    "oslo": {"pop": 1_064_000, "housing": 480_000, "lat": 59.9139, "lon": 10.7522},
    "naples": {"pop": 2_187_000, "housing": 900_000, "lat": 40.8518, "lon": 14.2681},
    "prague": {"pop": 1_357_000, "housing": 620_000, "lat": 50.0755, "lon": 14.4378},
    "amsterdam": {"pop": 1_174_000, "housing": 540_000, "lat": 52.3676, "lon": 4.9041},
    "malaga": {"pop": 1_025_000, "housing": 450_000, "lat": 36.7213, "lon": -4.4214},
    "lyon": {"pop": 2_323_000, "housing": 1_050_000, "lat": 45.7640, "lon": 4.8357},
    "valencia": {"pop": 1_581_000, "housing": 700_000, "lat": 39.4699, "lon": -0.3763},
    "sevilla": {"pop": 1_107_000, "housing": 480_000, "lat": 37.3891, "lon": -5.9845},
    "venice": {"pop": 261_000, "housing": 140_000, "lat": 45.4408, "lon": 12.3155},
    "greater-manchester": {"pop": 2_867_000, "housing": 1_200_000, "lat": 53.4808, "lon": -2.2426},
    "munich": {"pop": 1_558_000, "housing": 780_000, "lat": 48.1351, "lon": 11.5820},
    "dublin": {"pop": 1_263_000, "housing": 530_000, "lat": 53.3498, "lon": -6.2603},
    "brussels": {"pop": 1_222_000, "housing": 560_000, "lat": 50.8503, "lon": 4.3517},
    "edinburgh": {"pop": 558_000, "housing": 260_000, "lat": 55.9533, "lon": -3.1883},
    "stockholm": {"pop": 1_679_000, "housing": 780_000, "lat": 59.3293, "lon": 18.0686},
    "thessaloniki": {"pop": 1_110_000, "housing": 480_000, "lat": 40.6401, "lon": 22.9444},
    "bologna": {"pop": 1_017_000, "housing": 450_000, "lat": 44.4949, "lon": 11.3426},
    "bergamo": {"pop": 522_000, "housing": 230_000, "lat": 45.6983, "lon": 9.6773},
    "zurich": {"pop": 1_395_000, "housing": 620_000, "lat": 47.3769, "lon": 8.5417},
    "bristol": {"pop": 724_000, "housing": 320_000, "lat": 51.4545, "lon": -2.5879},
    "geneva": {"pop": 613_000, "housing": 280_000, "lat": 46.2044, "lon": 6.1432},
    "antwerp": {"pop": 1_055_000, "housing": 460_000, "lat": 51.2194, "lon": 4.4025},
}
# &e

# &s &LOAD_CITIES
def find_sumlistings(city_dir, snapshot="25-06"):
    """Trouve le fichier sumlistings pour un snapshot donné."""
    for f in city_dir.glob(f"*{snapshot}*sumlistings.csv"):
        return f
    return None

def load_all_cities(snapshot="25-06"):
    """Charge toutes les villes (hors régions) avec seuil minimum."""
    all_dfs = []

    for country_dir in RAW_DIR.iterdir():
        if not country_dir.is_dir():
            continue
        country_name = country_dir.name
        country_code = COUNTRY_CODES.get(country_name, country_name[:3].upper())

        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            city_name = city_dir.name

            # Exclure régions
            if city_name in REGIONS_EXCLUDE:
                print(f"  [SKIP] {city_name} (région)")
                continue

            # Trouver fichier
            csv_file = find_sumlistings(city_dir, snapshot)
            if csv_file is None:
                print(f"  [MISS] {city_name} (pas de snapshot {snapshot})")
                continue

            # Charger
            try:
                df = pd.read_csv(csv_file)
                n = len(df)

                # Seuil minimum
                if n < MIN_LISTINGS:
                    print(f"  [SKIP] {city_name} ({n:,} < {MIN_LISTINGS:,})")
                    continue

                # Ajouter métadonnées
                df["city"] = city_name
                df["country"] = country_name
                df["country_code"] = country_code

                # Ajouter population si disponible
                meta = CITY_META.get(city_name, {})
                df["city_pop"] = meta.get("pop", np.nan)
                df["city_housing"] = meta.get("housing", np.nan)
                df["city_lat"] = meta.get("lat", np.nan)
                df["city_lon"] = meta.get("lon", np.nan)

                all_dfs.append(df)
                print(f"  [OK]   {city_name}: {n:,} listings")

            except Exception as e:
                print(f"  [ERR]  {city_name}: {e}")

    if not all_dfs:
        raise ValueError("Aucune ville chargée!")

    return pd.concat(all_dfs, ignore_index=True)
# &e

# &s &MAIN
if __name__ == "__main__":
    print("=" * 60)
    print("CONSOLIDATION 35 VILLES EUROPÉENNES")
    print("=" * 60)
    print(f"Source: {RAW_DIR}")
    print(f"Seuil: {MIN_LISTINGS:,} listings minimum")
    print(f"Régions exclues: {len(REGIONS_EXCLUDE)}")
    print()

    # Charger
    print("Chargement des villes...")
    df = load_all_cities("25-06")

    print()
    print("=" * 60)
    print("RÉSULTAT")
    print("=" * 60)
    print(f"Total listings: {len(df):,}")
    print(f"Villes: {df['city'].nunique()}")
    print(f"Pays: {df['country_code'].nunique()}")

    # Stats par ville
    stats = df.groupby(["country_code", "city"]).agg(
        n=("id", "count"),
        pop=("city_pop", "first"),
        housing=("city_housing", "first"),
    ).reset_index().sort_values("n", ascending=False)

    stats["listings_per_1000hab"] = (stats["n"] / stats["pop"] * 1000).round(1)
    stats["listings_per_1000housing"] = (stats["n"] / stats["housing"] * 1000).round(1)

    print()
    print(stats.to_string(index=False))

    # Sauvegarder
    out_sumlistings = INTERIM_DIR / "dbsumlistings_2506_cons35city.parquet"
    df.to_parquet(out_sumlistings, index=False)
    print(f"\n[EXPORT] {out_sumlistings.name}: {len(df):,} lignes")

    out_stats = INTERIM_DIR / "recap_stats_35cities_2506.csv"
    stats.to_csv(out_stats, index=False, encoding="utf-8-sig")
    print(f"[EXPORT] {out_stats.name}")

    print()
    print("Done!")
# &e

# &e &CONSOLIDATE_35CITIES
