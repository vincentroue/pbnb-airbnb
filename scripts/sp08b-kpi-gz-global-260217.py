# &s &KPI_GZ_GLOBAL_aaMAIN - KPI depuis listings.csv.gz (reviews, capacité, host, occupancy)

# Extrait les indicateurs non disponibles dans sumlistings :
# review scores, capacité, profil hôte, occupancy estimée.
# Scanne les gz 25-06 pour toutes les villes intégrées.
#
# Usage:
#   python scripts/sp08b-kpi-gz-global-260217.py [--europe-only]
#
# Outputs:
#   data/interim/kpi_gz_global_by_city_2506.csv
#   data/interim/kpi_gz_europe_by_city_2506.csv (si --europe-only)
#
# Fichier: sp08b-kpi-gz-global-260217.py | dcr: 26-02-17 | dup: 26-02-17

import pandas as pd
import numpy as np
from pathlib import Path
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

# Colonnes à extraire du gz (minimise mémoire)
GZ_USECOLS = [
    "id", "host_id", "host_is_superhost",
    "room_type", "price", "minimum_nights",
    "accommodates", "bedrooms",
    "instant_bookable",
    "review_scores_rating", "review_scores_accuracy",
    "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location",
    "review_scores_value",
    "calculated_host_listings_count",
    "availability_365",
]

# Colonnes optionnelles (pas dans tous les snapshots)
GZ_OPTIONAL = ["estimated_occupancy_l365d", "estimated_revenue_l365d"]

# Table de référence
_ref = pd.read_csv(REF_CSV)
_ref_int = _ref[_ref["status"] == "integrated"]
if europe_only:
    _ref_int = _ref_int[_ref_int["continent"] == "Europe"]
CITIES = _ref_int.set_index("city")[["raw_folder", "raw_country", "country_code", "continent"]].to_dict("index")

# Taux FX
_fx = _ref.dropna(subset=["country_code", "fx_eur"]).drop_duplicates("country_code")
FX_EUR = dict(zip(_fx["country_code"], _fx["fx_eur"]))

# Filtres par neighbourhood — sous-sélection géographique pour certaines villes
CITY_NBH_FILTERS = {
    "pays-basque": ["Biarritz", "Anglet", "Bayonne"],
}
# &e

# &s &LOAD_GZ
def find_gz(city, meta, snapshot=SNAPSHOT):
    """Trouve le listings.csv.gz pour une ville et un snapshot."""
    folder = meta["raw_folder"]
    country = meta["raw_country"]
    gz_path = RAW_BASE / folder / country / city / snapshot / "listings.csv.gz"
    return gz_path if gz_path.exists() else None


def load_gz(gz_path, usecols):
    """Charge un gz avec seulement les colonnes nécessaires."""
    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        # Lire header pour détecter colonnes dispo
        header = f.readline().strip().split(",")
    # Filtrer aux colonnes existantes + ajouter neighbourhood pour filtres géo
    nbh_cols = ["neighbourhood_group_cleansed", "neighbourhood_cleansed"]
    extra = [c for c in nbh_cols if c in header]
    cols_present = [c for c in usecols if c in header] + extra
    cols_present = list(dict.fromkeys(cols_present))  # déduplique
    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f, usecols=cols_present, low_memory=False)
    return df
# &e

# &s &KPI_COMPUTE
def compute_gz_kpi(df, country_code):
    """Calcule les KPI gz pour une ville."""
    fx = FX_EUR.get(country_code, 1.0)

    # Cleaning minimal (même pipeline que sp08)
    if "price" in df.columns:
        # Prix gz = string "$135.00" → float
        df["price"] = df["price"].replace(r'[\$,]', '', regex=True).astype(float)
        df["price_eur"] = df["price"] * fx
        df = df[df["price"].notna() & (df["availability_365"] > 0)]
        df = df[df["room_type"] != "Hotel room"]
        df = df[(df["price_eur"] >= 10) & (df["price_eur"] <= 1000)]

    n = len(df)
    if n == 0:
        return None

    kpi = {"n_gz": n}

    # Reviews (échelle 0-5)
    for col_short in ["rating", "accuracy", "cleanliness", "checkin",
                      "communication", "location", "value"]:
        col = f"review_scores_{col_short}"
        if col in df.columns:
            vals = df[col].dropna()
            kpi[f"rev_{col_short}_med"] = round(vals.median(), 2) if len(vals) > 0 else np.nan
            kpi[f"rev_{col_short}_n"] = len(vals)

    # Taux de couverture reviews
    if "review_scores_rating" in df.columns:
        kpi["rev_coverage_pct"] = round(df["review_scores_rating"].notna().mean() * 100, 1)

    # Capacité
    if "accommodates" in df.columns:
        kpi["accommodates_med"] = round(df["accommodates"].median(), 1)
        kpi["accommodates_moy"] = round(df["accommodates"].mean(), 1)
    if "bedrooms" in df.columns:
        vals = df["bedrooms"].dropna()
        kpi["bedrooms_med"] = round(vals.median(), 1) if len(vals) > 0 else np.nan

    # Prix par bedrooms (entire home uniquement)
    if "bedrooms" in df.columns and "price_eur" in df.columns:
        entire = df[df["room_type"] == "Entire home/apt"]
        for seg, mask_fn in [("1br", lambda d: d["bedrooms"] == 1),
                             ("2br", lambda d: d["bedrooms"] == 2),
                             ("3br_plus", lambda d: d["bedrooms"] >= 3)]:
            sub = entire[mask_fn(entire)]
            if len(sub) >= 10:
                kpi[f"prix_med_{seg}"] = round(sub["price_eur"].median(), 1)

    # Profil hôte
    if "host_is_superhost" in df.columns:
        sh = df["host_is_superhost"].map({"t": 1, "f": 0}).dropna()
        kpi["pct_superhost"] = round(sh.mean() * 100, 1) if len(sh) > 0 else np.nan

    # Instant book
    if "instant_bookable" in df.columns:
        ib = df["instant_bookable"].map({"t": 1, "f": 0}).dropna()
        kpi["pct_instant_book"] = round(ib.mean() * 100, 1) if len(ib) > 0 else np.nan

    # Occupancy et revenue estimés
    if "estimated_occupancy_l365d" in df.columns:
        occ = df["estimated_occupancy_l365d"].dropna()
        if len(occ) > 0:
            kpi["occupancy_est_med"] = round(occ.median(), 0)
            kpi["occupancy_est_moy"] = round(occ.mean(), 1)

    if "estimated_revenue_l365d" in df.columns:
        rev = df["estimated_revenue_l365d"].dropna()
        if len(rev) > 0:
            kpi["revenue_est_med"] = round(rev.median() * fx, 0)  # Convertir en EUR
            kpi["revenue_est_moy"] = round(rev.mean() * fx, 0)

    return kpi
# &e

# &s &MAIN
if __name__ == "__main__":
    print("=" * 60)
    print(f"KPI GZ — {scope.upper()} (snapshot {SNAPSHOT})")
    print("=" * 60)
    print(f"Villes cibles: {len(CITIES)}")

    usecols = GZ_USECOLS + GZ_OPTIONAL
    results = []
    errors = []

    for city, meta in sorted(CITIES.items()):
        gz_path = find_gz(city, meta)
        if gz_path is None:
            print(f"  [MISS] {city}: pas de gz {SNAPSHOT}")
            errors.append(city)
            continue

        try:
            df = load_gz(gz_path, usecols)
            # Filtre neighbourhood si périmètre restreint
            if city in CITY_NBH_FILTERS:
                keep = CITY_NBH_FILTERS[city]
                if "neighbourhood_group_cleansed" in df.columns:
                    df = df[df["neighbourhood_group_cleansed"].isin(keep)]
                elif "neighbourhood_cleansed" in df.columns:
                    df = df[df["neighbourhood_cleansed"].isin(keep)]
            kpi = compute_gz_kpi(df, meta["country_code"])
            if kpi is None:
                print(f"  [SKIP] {city}: 0 listings après cleaning")
                continue
            kpi["city"] = city
            kpi["country_code"] = meta["country_code"]
            kpi["continent"] = meta["continent"]
            results.append(kpi)
            print(f"  [OK]   {city}: {kpi['n_gz']:,} listings, "
                  f"rev={kpi.get('rev_rating_med', 'N/A')}, "
                  f"coverage={kpi.get('rev_coverage_pct', 'N/A')}%")
        except Exception as e:
            print(f"  [ERR]  {city}: {e}")
            errors.append(city)

    if not results:
        print("\nAucun résultat!")
        sys.exit(1)

    # Assembler
    kpi_gz = pd.DataFrame(results)

    # Ordre colonnes
    cols_meta = ["continent", "country_code", "city"]
    cols_rev = [c for c in kpi_gz.columns if c.startswith("rev_")]
    cols_cap = [c for c in kpi_gz.columns if c.startswith("accommodates") or c.startswith("bedrooms")]
    cols_host = [c for c in kpi_gz.columns if c.startswith("pct_super") or c.startswith("pct_instant")]
    cols_prix_br = [c for c in kpi_gz.columns if c.startswith("prix_med_")]
    cols_occ = [c for c in kpi_gz.columns if c.startswith("occupancy") or c.startswith("revenue")]
    cols_order = cols_meta + ["n_gz"] + sorted(cols_rev) + sorted(cols_cap) + sorted(cols_prix_br) + sorted(cols_host) + sorted(cols_occ)
    cols_order = [c for c in cols_order if c in kpi_gz.columns]
    kpi_gz = kpi_gz[cols_order].sort_values("n_gz", ascending=False)

    # Export
    out_path = INTERIM_DIR / f"kpi_gz_{scope}_by_city_2506.csv"
    kpi_gz.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT: {out_path.name}")
    print(f"{'=' * 60}")
    print(f"Villes: {len(kpi_gz)}")
    print(f"Erreurs/manquants: {len(errors)}")

    if errors:
        print(f"  → {', '.join(errors)}")

    print(f"\n--- TOP 15 (volume gz) ---")
    top_cols = ["city", "n_gz", "rev_rating_med", "rev_value_med",
                "accommodates_med", "pct_superhost", "pct_instant_book"]
    top_cols = [c for c in top_cols if c in kpi_gz.columns]
    print(kpi_gz[top_cols].head(15).to_string(index=False))

    print(f"\n--- Moyennes globales ---")
    for col in ["rev_rating_med", "rev_value_med", "accommodates_med",
                "pct_superhost", "pct_instant_book", "rev_coverage_pct"]:
        if col in kpi_gz.columns:
            print(f"  {col}: {kpi_gz[col].mean():.1f}")

    if "occupancy_est_med" in kpi_gz.columns:
        print(f"  occupancy_est_med: {kpi_gz['occupancy_est_med'].mean():.0f} jours")
    if "revenue_est_med" in kpi_gz.columns:
        print(f"  revenue_est_med: {kpi_gz['revenue_est_med'].mean():.0f} EUR")
# &e

# &e &KPI_GZ_GLOBAL_aaMAIN
