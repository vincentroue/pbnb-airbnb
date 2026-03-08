# &s &HOSTS_GLOBAL_aaMAIN - Agrégation hôtes depuis listings.csv.gz consolidé

# Crée un fichier host-level (1 ligne = 1 hôte × 1 ville) à partir du
# parquet gz consolidé. Capture le mix de portefeuille (room_type),
# les notes moyennes, la dispersion géographique, le type Adamiak.
#
# Usage:
#   python scripts/sp09-hosts-global-260222.py
#
# Input:
#   data/interim/dblistingfull_2506_cons_global.parquet
#
# Output:
#   data/interim/dbhosts_2506_cons_global.parquet
#   data/interim/dbhosts_2506_cons_global.csv (top 500 pour inspection)
#
# Fichier: sp09-hosts-global-260222.py | dcr: 26-02-22 | dup: 26-02-22

import pandas as pd
import numpy as np
from pathlib import Path

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
INTERIM_DIR = BASE / "data" / "interim"
INPUT_PATH = INTERIM_DIR / "dblistingfull_2506_cons_global.parquet"
# &e

# &s &LOAD
print("=" * 60)
print("AGRÉGATION HÔTES — GLOBAL")
print("=" * 60)

df = pd.read_parquet(INPUT_PATH)
print(f"Chargé : {len(df):,} listings, {df['host_id'].nunique():,} hôtes uniques")
print(f"Villes : {df['city'].nunique()}")
# &e

# &s &AGGREGATE
def classify_host_type(row):
    """Type Adamiak : single-room / single-home / multi-room / multi-home / mixed."""
    if row["n_listings"] == 1:
        if row["n_entire"] == 1:
            return "single-home"
        else:
            return "single-room"
    else:
        if row["n_entire"] == 0:
            return "multi-room"
        elif row["n_private"] == 0 and row["n_shared"] == 0:
            return "multi-home"
        else:
            return "mixed"


def classify_host_category_simple(n):
    """3 bins : mono / multi / pro."""
    if n == 1:
        return "mono"
    elif n <= 9:
        return "multi"
    else:
        return "pro"


def classify_host_category_detail(n):
    """5 bins : mono / small_multi / multi / large / mega."""
    if n == 1:
        return "mono"
    elif n <= 4:
        return "small_multi"
    elif n <= 9:
        return "multi"
    elif n <= 49:
        return "large"
    else:
        return "mega"


# Préparer les flags room_type
df["is_private"] = (df["room_type"] == "Private room").astype(int)
df["is_shared"] = (df["room_type"] == "Shared room").astype(int)

# Agrégation par host × ville
agg = df.groupby(["host_id", "city"]).agg(
    # Volume
    n_listings=("id", "count"),
    n_entire=("is_entire_home", "sum"),
    n_private=("is_private", "sum"),
    n_shared=("is_shared", "sum"),
    # Prix
    prix_med=("price_eur", "median"),
    prix_min=("price_eur", "min"),
    prix_max=("price_eur", "max"),
    prix_moy=("price_eur", "mean"),
    # Reviews
    rev_rating_med=("review_scores_rating", lambda x: x.dropna().median() if x.notna().any() else np.nan),
    rev_nb_total=("number_of_reviews", "sum"),
    rpm_med=("reviews_per_month", lambda x: x.dropna().median() if x.notna().any() else np.nan),
    rpm_total=("reviews_per_month", lambda x: x.dropna().sum()),
    # Capacité
    accommodates_total=("accommodates", "sum"),
    accommodates_med=("accommodates", "median"),
    bedrooms_total=("bedrooms", lambda x: x.dropna().sum()),
    # Disponibilité
    dispo_med=("availability_365", "median"),
    dispo_moy=("availability_365", "mean"),
    pct_yearround=("availability_365", lambda x: round((x > 180).mean() * 100, 1)),
    # Géo
    n_quartiers=("neighbourhood_cleansed", "nunique"),
    # Profil
    host_since=("host_since", "first"),
    is_superhost=("host_is_superhost", "first"),
    # Revenue estimé
    revenue_est_total=("estimated_revenue_l365d", lambda x: x.dropna().sum() if x.notna().any() else np.nan),
    occupancy_est_med=("estimated_occupancy_l365d", lambda x: x.dropna().median() if x.notna().any() else np.nan),
    # Méta
    country_code=("country_code", "first"),
    continent=("continent", "first"),
).reset_index()

# Colonnes dérivées
agg["pct_entire"] = (agg["n_entire"] / agg["n_listings"] * 100).round(1)
agg["host_type"] = agg.apply(classify_host_type, axis=1)
agg["host_cat_simple"] = agg["n_listings"].apply(classify_host_category_simple)
agg["host_cat_detail"] = agg["n_listings"].apply(classify_host_category_detail)
agg["prix_range"] = (agg["prix_max"] - agg["prix_min"]).round(1)
# &e

# &s &MULTI_CITY
# Hôtes multi-villes (opèrent dans plusieurs villes)
host_cities = df.groupby("host_id")["city"].nunique().reset_index(name="n_cities")
agg = agg.merge(host_cities, on="host_id", how="left")
# &e

# &s &EXPORT
# Tri par volume décroissant
agg = agg.sort_values(["n_listings", "rev_nb_total"], ascending=[False, False])

# Export parquet complet
out_parquet = INTERIM_DIR / "dbhosts_2506_cons_global.parquet"
agg.to_parquet(out_parquet, index=False)

# Export CSV top 500 pour inspection
out_csv = INTERIM_DIR / "dbhosts_top500_2506.csv"
agg.head(500).to_csv(out_csv, index=False, encoding="utf-8-sig")

n_hosts = len(agg)
n_cities = agg["city"].nunique()

print(f"\n{'=' * 60}")
print(f"RÉSULTAT")
print(f"{'=' * 60}")
print(f"Hôtes : {n_hosts:,} (host × ville)")
print(f"Villes : {n_cities}")
print(f"Colonnes : {len(agg.columns)}")
print(f"Export : {out_parquet.name} ({out_parquet.stat().st_size / 1024 / 1024:.1f} MB)")
print(f"Export : {out_csv.name} (top 500)")

# Stats par type
print(f"\n--- Répartition host_type (Adamiak) ---")
type_stats = agg["host_type"].value_counts()
for t, n in type_stats.items():
    print(f"  {t:<15s} {n:>8,} ({n/n_hosts*100:>5.1f}%)")

print(f"\n--- Répartition host_cat_detail ---")
cat_stats = agg["host_cat_detail"].value_counts()
for c, n in cat_stats.items():
    print(f"  {c:<15s} {n:>8,} ({n/n_hosts*100:>5.1f}%)")

# Multi-villes
multi_city = agg[agg["n_cities"] > 1]
print(f"\n--- Hôtes multi-villes ---")
print(f"  {len(multi_city):,} hôtes opèrent dans 2+ villes ({len(multi_city)/n_hosts*100:.1f}%)")
if len(multi_city) > 0:
    top_multi = multi_city.nlargest(10, "n_listings")[["host_id", "city", "n_listings", "n_cities", "host_type"]]
    print(f"\n  Top 10 multi-villes :")
    print(top_multi.to_string(index=False))

# Top 15 par volume
print(f"\n--- Top 15 hôtes (volume) ---")
top_cols = ["host_id", "city", "n_listings", "host_type", "prix_med", "rev_rating_med", "revenue_est_total"]
top_cols = [c for c in top_cols if c in agg.columns]
print(agg[top_cols].head(15).to_string(index=False))

print(f"\nDone!")
# &e

# &e &HOSTS_GLOBAL_aaMAIN
