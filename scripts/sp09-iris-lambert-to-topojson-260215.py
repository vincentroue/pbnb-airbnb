# &s &IRIS_TOPOJSON_aaMAIN - Conversion IRIS Lambert93 GPKG -> TopoJSON
#
# Source: CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2025-01-01/iris.gpkg (167 MB)
# Output: nodom_iris_2025.topojson + .geojson dans geo-shape-ok/
# Pipeline: GPKG(Lambert93) -> reproject WGS84 -> filtrer DOM -> simplifier -> export
#
# Note: tp.Topology() trop lent sur 46K polygones -> shapely simplify + json direct

from pathlib import Path
import geopandas as gpd
import json
import time

# &s &PATHS - Chemins source/destination
SRC_GPKG = Path(r"C:\Users\vince\DBD-datab\TDC-ref\geo-shape-raw"
                r"\CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2025-01-01\iris.gpkg")
OUT_DIR = Path(r"C:\Users\vince\DBD-datab\TDC-ref\fr\geo-shape-ok")
OUT_GEOJSON = OUT_DIR / "nodom_iris_2025.geojson"
OUT_TOPOJSON = OUT_DIR / "nodom_iris_2025.topojson"

DOM_DEP = {"971", "972", "973", "974", "976"}
# &e

# &s &LOAD_REPROJECT - Lecture GPKG + reprojection WGS84
print(f"[1/5] Lecture {SRC_GPKG.name} ...")
t0 = time.time()
gdf = gpd.read_file(SRC_GPKG)
print(f"       {len(gdf):,} IRIS charges en {time.time()-t0:.1f}s")
print(f"       CRS: {gdf.crs}")
print(f"       Colonnes: {list(gdf.columns)}")

print("[2/5] Reprojection Lambert93 -> WGS84 (EPSG:4326) ...")
t1 = time.time()
gdf = gdf.to_crs(epsg=4326)
print(f"       OK en {time.time()-t1:.1f}s")
# &e

# &s &FILTER_DOM - Filtrer DOM
print("[3/5] Filtrage DOM-TOM ...")
dep_col = gdf["code_iris"].astype(str).str[:2]
mask_dom = dep_col.isin(DOM_DEP) | dep_col.str.startswith("97")
n_dom = mask_dom.sum()
gdf = gdf[~mask_dom].copy()
print(f"       {n_dom:,} IRIS DOM exclus -> {len(gdf):,} IRIS metropole")
# &e

# &s &SIMPLIFY - Simplification shapely (rapide)
print("[4/5] Simplification polygones (shapely) ...")
t2 = time.time()

# Tolerance en degres : ~50m = 0.0005 deg lat
TOLERANCE = 0.0005
gdf["geometry"] = gdf["geometry"].simplify(tolerance=TOLERANCE, preserve_topology=True)

# Supprimer geometries vides apres simplification
n_empty = gdf.geometry.is_empty.sum()
if n_empty > 0:
    gdf = gdf[~gdf.geometry.is_empty]
    print(f"       {n_empty} geometries vides supprimees")

print(f"       Simplification en {time.time()-t2:.1f}s -> {len(gdf):,} IRIS")
# &e

# &s &EXPORT - Export GeoJSON + TopoJSON
print("[5/5] Export ...")
t3 = time.time()

# Colonnes a garder (nettoyer les colonnes techniques)
KEEP_COLS = ["code_iris", "nom_iris", "code_insee", "nom_commune", "type_iris", "geometry"]
gdf_out = gdf[[c for c in KEEP_COLS if c in gdf.columns]].copy()

# GeoJSON
gdf_out.to_file(OUT_GEOJSON, driver="GeoJSON")
size_geo = OUT_GEOJSON.stat().st_size / (1024 * 1024)
print(f"       GeoJSON: {size_geo:.1f} MB -> {OUT_GEOJSON.name}")

# TopoJSON via topojson lib (sur GDF deja simplifie = rapide)
try:
    import topojson as tp
    print("       Construction TopoJSON (partage aretes) ...")
    t4 = time.time()
    topo = tp.Topology(gdf_out, prequantize=1e6)
    topo_str = topo.to_json()
    OUT_TOPOJSON.write_text(topo_str, encoding="utf-8")
    size_topo = OUT_TOPOJSON.stat().st_size / (1024 * 1024)
    print(f"       TopoJSON: {size_topo:.1f} MB -> {OUT_TOPOJSON.name} ({time.time()-t4:.0f}s)")
except Exception as e:
    print(f"       WARN: TopoJSON echoue ({e}), GeoJSON seul disponible")

print(f"\n=== Termine en {time.time()-t0:.0f}s ===")
print(f"    IRIS metropole: {len(gdf_out):,}")
print(f"    GeoJSON:  {OUT_GEOJSON}")
if OUT_TOPOJSON.exists():
    print(f"    TopoJSON: {OUT_TOPOJSON}")
# &e

# &e (FIN IRIS_TOPOJSON_aaMAIN)
