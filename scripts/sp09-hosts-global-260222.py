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
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
INTERIM_DIR = BASE / "data" / "interim"

# Snapshot cible paramétrable : --snapshot 26-06 (défaut 25-06 pour rétrocompat)
SNAPSHOT = "25-06"
for _i, _a in enumerate(sys.argv):
    if _a == "--snapshot" and _i + 1 < len(sys.argv):
        SNAPSHOT = sys.argv[_i + 1]
SNAP_TAG = SNAPSHOT.replace("-", "")  # "26-06" -> "2606"

INPUT_PATH = INTERIM_DIR / f"dblistingfull_{SNAP_TAG}_cons_global.parquet"
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
    if row["vol_n_ann"] == 1:
        if row["str_n_entire"] == 1:
            return "single-home"
        else:
            return "single-room"
    else:
        if row["str_n_entire"] == 0:
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
    vol_n_ann=("id", "count"),
    str_n_entire=("is_entire_home", "sum"),
    n_private=("is_private", "sum"),
    n_shared=("is_shared", "sum"),
    # Prix
    px_med=("price_eur", "median"),
    prix_min=("price_eur", "min"),
    prix_max=("price_eur", "max"),
    px_moy=("price_eur", "mean"),
    # Reviews
    actrv_note_glb=("review_scores_rating", lambda x: x.dropna().median() if x.notna().any() else np.nan),
    rev_nb_total=("number_of_reviews", "sum"),
    actrv_avis_mois=("reviews_per_month", lambda x: x.dropna().median() if x.notna().any() else np.nan),
    rpm_total=("reviews_per_month", lambda x: x.dropna().sum()),
    # Capacité
    accommodates_total=("accommodates", "sum"),
    str_cap_pers_med=("accommodates", "median"),
    bedrooms_total=("bedrooms", lambda x: x.dropna().sum()),
    # Disponibilité
    act_cal_ouvert_med=("availability_365", "median"),
    act_cal_ouvert_moy=("availability_365", "mean"),
    pct_yearround=("availability_365", lambda x: round((x > 180).mean() * 100, 1)),
    # Géo
    n_quartiers=("neighbourhood_cleansed", "nunique"),
    # Profil
    host_since=("host_since", "first"),
    is_superhost=("host_is_superhost", "first"),
    # Revenue estimé
    revenue_est_total=("estimated_revenue_l365d", lambda x: x.dropna().sum() if x.notna().any() else np.nan),
    act_reserv_j_med=("estimated_occupancy_l365d", lambda x: x.dropna().median() if x.notna().any() else np.nan),
    # Méta
    country_code=("country_code", "first"),
    continent=("continent", "first"),
).reset_index()

# Colonnes dérivées
agg["str_entire_pct"] = (agg["str_n_entire"] / agg["vol_n_ann"] * 100).round(1)
agg["host_type"] = agg.apply(classify_host_type, axis=1)
agg["host_cat_simple"] = agg["vol_n_ann"].apply(classify_host_category_simple)
agg["host_cat_detail"] = agg["vol_n_ann"].apply(classify_host_category_detail)
agg["prix_range"] = (agg["prix_max"] - agg["prix_min"]).round(1)
# &e

# &s &MULTI_CITY
# Hôtes multi-villes (opèrent dans plusieurs villes)
host_cities = df.groupby("host_id")["city"].nunique().reset_index(name="n_cities")
agg = agg.merge(host_cities, on="host_id", how="left")
# &e

# &s &EXPORT
# Tri par volume décroissant
agg = agg.sort_values(["vol_n_ann", "rev_nb_total"], ascending=[False, False])

# Export parquet complet
out_parquet = INTERIM_DIR / f"dbhosts_{SNAP_TAG}_cons_global.parquet"
agg.to_parquet(out_parquet, index=False)

# Export CSV top 500 pour inspection
out_csv = INTERIM_DIR / f"dbhosts_top500_{SNAP_TAG}.csv"
agg.head(500).to_csv(out_csv, index=False, encoding="utf-8-sig")

vol_n_hotes = len(agg)
n_cities = agg["city"].nunique()

print(f"\n{'=' * 60}")
print(f"RÉSULTAT")
print(f"{'=' * 60}")
print(f"Hôtes : {vol_n_hotes:,} (host × ville)")
print(f"Villes : {n_cities}")
print(f"Colonnes : {len(agg.columns)}")
print(f"Export : {out_parquet.name} ({out_parquet.stat().st_size / 1024 / 1024:.1f} MB)")
print(f"Export : {out_csv.name} (top 500)")

# Stats par type
print(f"\n--- Répartition host_type (Adamiak) ---")
type_stats = agg["host_type"].value_counts()
for t, n in type_stats.items():
    print(f"  {t:<15s} {n:>8,} ({n/vol_n_hotes*100:>5.1f}%)")

print(f"\n--- Répartition host_cat_detail ---")
cat_stats = agg["host_cat_detail"].value_counts()
for c, n in cat_stats.items():
    print(f"  {c:<15s} {n:>8,} ({n/vol_n_hotes*100:>5.1f}%)")

# Multi-villes
multi_city = agg[agg["n_cities"] > 1]
print(f"\n--- Hôtes multi-villes ---")
print(f"  {len(multi_city):,} hôtes opèrent dans 2+ villes ({len(multi_city)/vol_n_hotes*100:.1f}%)")
if len(multi_city) > 0:
    top_multi = multi_city.nlargest(10, "vol_n_ann")[["host_id", "city", "vol_n_ann", "n_cities", "host_type"]]
    print(f"\n  Top 10 multi-villes :")
    print(top_multi.to_string(index=False))

# Top 15 par volume
print(f"\n--- Top 15 hôtes (volume) ---")
top_cols = ["host_id", "city", "vol_n_ann", "host_type", "px_med", "actrv_note_glb", "revenue_est_total"]
top_cols = [c for c in top_cols if c in agg.columns]
print(agg[top_cols].head(15).to_string(index=False))

print(f"\nDone!")
# &e

# &e &HOSTS_GLOBAL_aaMAIN
