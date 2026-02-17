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

# Répertoires à scanner (region_key -> dossier, nesting style)
# europe: europe/{country}/{city}
# usa: usa/united-states/{city}
# world: world/{country}/{city}
SCAN_DIRS = {
    "europe": RAW_BASE / "europe",
    "usa": RAW_BASE / "usa",
    "world": RAW_BASE / "world",
}

# Régions et zones non-urbaines à exclure
REGIONS_EXCLUDE = [
    # Europe
    "sicily", "puglia", "south-aegean", "crete", "girona",
    "mallorca", "pays-basque", "euskadi", "vaud", "trentino", "menorca",
    # USA (counties, MSA, islands)
    "broward-county", "clark-county-nv", "hawaii", "san-mateo-county",
    "santa-clara-county", "santa-cruz-county", "twin-cities-msa",
    "rhode-island", "jersey-city", "newark", "oakland", "cambridge",
    "pacific-grove", "albany", "asheville", "bozeman", "columbus",
    "fort-worth", "rochester", "salem-or",
    # Australia (regions)
    "barossa-valley", "barwon-south-west-vic", "mid-north-coast",
    "mornington-peninsula", "northern-rivers", "sunshine-coast",
    "tasmania", "western-australia",
    # Canada (petites villes/provinces)
    "new-brunswick", "quebec-city", "victoria", "winnipeg", "ottawa",
    # Autres
    "belize", "beijing",
]

MIN_LISTINGS = 3000

# Mapping pays -> code ISO 3166 alpha-3
COUNTRY_CODES = {
    # Europe
    "austria": "AUT", "belgium": "BEL", "czech-republic": "CZE",
    "denmark": "DNK", "france": "FRA", "germany": "DEU",
    "greece": "GRC", "hungary": "HUN", "ireland": "IRL",
    "italy": "ITA", "norway": "NOR", "portugal": "PRT",
    "spain": "ESP", "sweden": "SWE", "switzerland": "CHE",
    "the-netherlands": "NLD", "turkey": "TUR", "united-kingdom": "GBR",
    "latvia": "LVA",
    # Americas
    "united-states": "USA", "canada": "CAN",
    "argentina": "ARG", "chile": "CHL", "mexico": "MEX", "brazil": "BRA",
    # Asia-Pacific
    "japan": "JPN", "china": "CHN", "singapore": "SGP",
    "australia": "AUS", "taiwan": "TWN", "thailand": "THA",
    # Africa
    "south-africa": "ZAF",
}

# Mapping region_key -> continent
REGION_MAP = {
    "europe": "Europe",
    "usa": "Americas",
}
# Pour world/, on mappe par pays
COUNTRY_CONTINENT = {
    "CAN": "Americas", "ARG": "Americas", "CHL": "Americas",
    "MEX": "Americas", "BRA": "Americas",
    "JPN": "Asia-Pacific", "CHN": "Asia-Pacific", "SGP": "Asia-Pacific",
    "AUS": "Asia-Pacific", "TWN": "Asia-Pacific", "THA": "Asia-Pacific",
    "ZAF": "Africa",
    "LVA": "Europe",
}

# Population et logements (metro comme fallback, overridé par city_reference_data.py)
# Sources: city_reference_data.py (city proper) > Eurostat, UN WUP 2024 (metro)
CITY_META = {
    # --- Europe (35 villes) ---
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
    "riga": {"pop": 615_000, "housing": 300_000, "lat": 56.9496, "lon": 24.1052},
    # --- USA (7-14 villes) ---
    "new-york-city": {"pop": 8_260_000, "housing": 3_500_000, "lat": 40.7128, "lon": -74.0060},
    "los-angeles": {"pop": 3_900_000, "housing": 1_500_000, "lat": 34.0522, "lon": -118.2437},
    "chicago": {"pop": 2_700_000, "housing": 1_200_000, "lat": 41.8781, "lon": -87.6298},
    "san-francisco": {"pop": 870_000, "housing": 400_000, "lat": 37.7749, "lon": -122.4194},
    "washington-dc": {"pop": 690_000, "housing": 350_000, "lat": 38.9072, "lon": -77.0369},
    "boston": {"pop": 680_000, "housing": 300_000, "lat": 42.3601, "lon": -71.0589},
    "seattle": {"pop": 750_000, "housing": 370_000, "lat": 47.6062, "lon": -122.3321},
    "austin": {"pop": 1_020_000, "housing": 430_000, "lat": 30.2672, "lon": -97.7431},
    "san-diego": {"pop": 1_390_000, "housing": 530_000, "lat": 32.7157, "lon": -117.1611},
    "nashville": {"pop": 690_000, "housing": 310_000, "lat": 36.1627, "lon": -86.7816},
    "denver": {"pop": 715_000, "housing": 320_000, "lat": 39.7392, "lon": -104.9903},
    "portland": {"pop": 650_000, "housing": 290_000, "lat": 45.5152, "lon": -122.6784},
    "dallas": {"pop": 1_340_000, "housing": 560_000, "lat": 32.7767, "lon": -96.7970},
    "new-orleans": {"pop": 380_000, "housing": 190_000, "lat": 29.9511, "lon": -90.0715},
    # --- Canada ---
    "toronto": {"pop": 2_800_000, "housing": 1_200_000, "lat": 43.6532, "lon": -79.3832},
    "vancouver": {"pop": 680_000, "housing": 310_000, "lat": 49.2827, "lon": -123.1207},
    "montreal": {"pop": 1_760_000, "housing": 800_000, "lat": 45.5017, "lon": -73.5673},
    # --- Asia-Pacific ---
    "tokyo": {"pop": 14_000_000, "housing": 7_500_000, "lat": 35.6762, "lon": 139.6503},
    "sydney": {"pop": 5_300_000, "housing": 2_100_000, "lat": -33.8688, "lon": 151.2093},
    "melbourne": {"pop": 5_000_000, "housing": 1_900_000, "lat": -37.8136, "lon": 144.9631},
    "brisbane": {"pop": 2_500_000, "housing": 950_000, "lat": -27.4698, "lon": 153.0251},
    "hong-kong": {"pop": 7_500_000, "housing": 2_800_000, "lat": 22.3193, "lon": 114.1694},
    "singapore": {"pop": 5_900_000, "housing": 1_400_000, "lat": 1.3521, "lon": 103.8198},
    "taipei": {"pop": 2_600_000, "housing": 1_000_000, "lat": 25.0330, "lon": 121.5654},
    "bangkok": {"pop": 10_700_000, "housing": 3_500_000, "lat": 13.7563, "lon": 100.5018},
    # --- Americas (hors USA/CAN) ---
    "mexico-city": {"pop": 9_200_000, "housing": 3_000_000, "lat": 19.4326, "lon": -99.1332},
    "rio-de-janeiro": {"pop": 6_750_000, "housing": 2_500_000, "lat": -22.9068, "lon": -43.1729},
    "santiago": {"pop": 5_600_000, "housing": 2_100_000, "lat": -33.4489, "lon": -70.6693},
    "buenos-aires": {"pop": 3_100_000, "housing": 1_400_000, "lat": -34.6037, "lon": -58.3816},
    # --- Africa ---
    "cape-town": {"pop": 4_800_000, "housing": 1_500_000, "lat": -33.9249, "lon": 18.4241},
}

# Override CITY_META pop/housing with city_reference_data (city proper, not metro)
from city_reference_data import CITY_DATA
for city_key, ref in CITY_DATA.items():
    # Map manchester→greater-manchester for Inside Airbnb naming
    meta_key = "greater-manchester" if city_key == "manchester" else city_key
    if meta_key in CITY_META:
        CITY_META[meta_key]["pop"] = ref["pop"]
        CITY_META[meta_key]["housing"] = ref["housing"]
    else:
        # City in reference data but not in CITY_META → add with coords from CITY_META or defaults
        CITY_META[meta_key] = {"pop": ref["pop"], "housing": ref["housing"], "lat": 0, "lon": 0}
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

                if city_name in REGIONS_EXCLUDE:
                    continue

                csv_file = find_sumlistings(city_dir, snapshot)
                if csv_file is None:
                    continue

                try:
                    df = pd.read_csv(csv_file)
                    n = len(df)

                    if n < MIN_LISTINGS:
                        print(f"  [SKIP] {city_name} ({n:,} < {MIN_LISTINGS:,})")
                        continue

                    df["city"] = city_name
                    df["country"] = country_name
                    df["country_code"] = country_code

                    # Continent
                    if region_key in REGION_MAP:
                        df["continent"] = REGION_MAP[region_key]
                    else:
                        df["continent"] = COUNTRY_CONTINENT.get(country_code, "Other")

                    meta = CITY_META.get(city_name, {})
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
    print(f"Régions exclues: {len(REGIONS_EXCLUDE)}")

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
