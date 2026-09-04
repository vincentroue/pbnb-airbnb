# &s &DENSE_RECOUNT_aaMAIN - Recompte annonces en zone dense par snapshot
#
# Le polygone dense (GHS-POP >=1500 hab/km2 intra-perimetre IA) et pop_dense/aire_dense
# sont INVARIANTS entre snapshots (raster epoch 2025 + perimetre IA figes). Seul le
# NUMERATEUR n_listings_dense change avec les volumes. Ce script reutilise les polygones
# deja exportes (dense_intra_ia_geojsons) + les denominateurs figes de l'audit 2506, et
# recompte n_listings_dense sur le parquet du snapshot -> audit_dense_intra_ia_{TAG}.csv.
#
# Bien plus rapide que le generateur complet (point-in-polygon, pas de masquage raster).
#
# Usage: python scripts/sp08d-dense-recount-260719.py [--snapshot 26-06]

import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
import sys

# &s &CONFIG
SNAPSHOT = "26-06"
for _i, _a in enumerate(sys.argv):
    if _a == "--snapshot" and _i + 1 < len(sys.argv):
        SNAPSHOT = sys.argv[_i + 1]
SNAP_TAG = SNAPSHOT.replace("-", "")

PBNB = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
GHS = Path(r"C:\Users\vince\DBD-datab\dbd_glb\GHS-POP-raster")
GEO_DIR = GHS / "outputs" / "dense_intra_ia_geojsons"
BASE_CSV = GHS / "outputs" / "audit_dense_intra_ia_75villes.csv"   # denominateurs figes (build 2506)
OUT_CSV = GHS / "outputs" / f"audit_dense_intra_ia_{SNAP_TAG}.csv"
PARQUET = PBNB / "data" / "interim" / f"dblistingfull_{SNAP_TAG}_cons_global.parquet"

# Sous-villes BAB : listings filtres sur le parent pays-basque + neighbourhood
BAB = {"biarritz": "Biarritz", "anglet": "Anglet", "bayonne": "Bayonne"}
# &e

# &s &LOAD
print("=" * 60)
print(f"sp08d - Recompte dense, snapshot {SNAPSHOT} (TAG {SNAP_TAG})")
print("=" * 60)

base = pd.read_csv(BASE_CSV)
print(f"Audit base (denominateurs figes) : {len(base)} villes")

df = pq.read_table(PARQUET, columns=["city", "neighbourhood", "latitude", "longitude"]).to_pandas()
df = df.dropna(subset=["latitude", "longitude"])
gdf_all = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
)
print(f"Listings {SNAP_TAG} : {len(df):,}")
# &e

# &s &RECOUNT - Point-in-polygon sur polygones figes
rows = []
missing = []
for _, r in base.iterrows():
    city = r["city"]
    gj = GEO_DIR / f"{city}_dense_intra_ia.geojson"

    if city in BAB:
        cl = gdf_all[(gdf_all.city == "pays-basque") & (gdf_all.neighbourhood == BAB[city])]
    else:
        cl = gdf_all[gdf_all.city == city]
    n_total = len(cl)

    n_dense = 0
    if gj.exists() and n_total > 0:
        poly = gpd.read_file(gj).to_crs("EPSG:4326")
        n_dense = len(gpd.sjoin(cl, poly, predicate="within"))
    elif not gj.exists():
        missing.append(city)

    pop_dense = r["pop_dense"]
    aire = r["aire_dense_km2"]
    pop_ia = r["pop_ghsl_ia"]
    pop_ref = r["pop_ref"]

    row = r.to_dict()  # garde les denominateurs figes (pop_dense, aire, densite_pop, top5km2, pct_pop_dense, n_pixels)
    row["n_listings_total"] = n_total
    row["n_listings_dense"] = n_dense
    row["ratio_listings_par_hab"] = round(n_dense / pop_dense * 1000, 1) if pop_dense > 1000 else None
    row["densite_listings_km2"] = round(n_dense / aire, 1) if aire > 1 else None
    row["pct_listings_dense"] = round(n_dense / n_total * 100, 1) if n_total > 0 else 0
    row["ratio_ia_total"] = round(n_total / pop_ia * 1000, 1) if pop_ia > 1000 else None
    row["ratio_ref"] = round(n_total / pop_ref * 1000, 1) if pop_ref > 0 else 0

    # Flag fiabilite recalcule (depend de n_listings_dense)
    if aire < 5 or n_dense < 200:
        row["flag_fiabilite"] = "fragile"
    elif row["pct_listings_dense"] < 30:
        row["flag_fiabilite"] = "partiel"
    else:
        row["flag_fiabilite"] = "fiable"

    rows.append(row)

out = pd.DataFrame(rows)
out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"\n{len(out)} villes -> {OUT_CSV.name}")
if missing:
    print(f"[WARN] geojson dense manquant ({len(missing)}) : {missing}")

# Controle : quelques villes cle
print("\n--- Controle (ratio annonces/1000hab zone dense) ---")
show = out[out.city.isin(["paris", "lisbon", "barcelona", "berlin", "amsterdam", "rome"])]
print(show[["city", "pop_dense", "n_listings_dense", "ratio_listings_par_hab", "pct_listings_dense", "flag_fiabilite"]].to_string(index=False))
# &e
# &e &DENSE_RECOUNT_aaMAIN
