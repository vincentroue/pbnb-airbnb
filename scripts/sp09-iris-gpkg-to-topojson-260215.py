"""
sp09 — Conversion IRIS GPKG Lambert 93 → TopoJSON WGS84
=========================================================
Pipeline: iris.gpkg (167 MB, L93) → GeoJSON (WGS84) → TopoJSON (simplifié)

Usage (depuis terminal PowerShell) :
    # 1. Installer dépendances si besoin
    pip install geopandas topojson pyproj

    # 2. Lancer
    python scripts/sp09-iris-gpkg-to-topojson-260215.py

    # 3. Options
    python scripts/sp09-iris-gpkg-to-topojson-260215.py --scope france     # France entière (~53K IRIS)
    python scripts/sp09-iris-gpkg-to-topojson-260215.py --scope airbnb     # Paris+Lyon+Bordeaux (~7K IRIS)
    python scripts/sp09-iris-gpkg-to-topojson-260215.py --scope idf        # Île-de-France (~5K IRIS)
    python scripts/sp09-iris-gpkg-to-topojson-260215.py --inspect          # Juste inspecter le GPKG

Output :
    data/geo/iris_france_wgs84.topojson          (scope=france)
    data/geo/iris_airbnb3villes_wgs84.topojson   (scope=airbnb)
    data/geo/iris_idf_wgs84.topojson             (scope=idf)
"""

# &s &IRIS_TOPOJSON_aaMAIN - Pipeline IRIS GPKG → TopoJSON

import argparse
import sys
import time
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
GPKG_PATH = Path(r"C:\Users\vince\DBD-datab\TDC-ref\geo-shape-raw"
                 r"\CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2025-01-01\iris.gpkg")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "geo"

# Départements par scope
DEPS_AIRBNB = {
    "75": "Paris",
    "69": "Lyon (Rhône)",
    "33": "Bordeaux (Gironde)",
}
DEPS_IDF = ["75", "77", "78", "91", "92", "93", "94", "95"]

# Simplification tolerance (en degrés WGS84, ~50m)
SIMPLIFY_TOLERANCE = 0.0005


# &s &INSPECT - Inspection du GeoPackage
def inspect_gpkg(gpkg_path: Path):
    """Inspecte le contenu du GPKG sans conversion."""
    import fiona
    import geopandas as gpd

    print(f"\n{'='*60}")
    print(f"INSPECTION: {gpkg_path.name}")
    print(f"Taille: {gpkg_path.stat().st_size / 1e6:.1f} MB")
    print(f"{'='*60}")

    layers = fiona.listlayers(str(gpkg_path))
    print(f"\nLayers: {layers}")

    for layer_name in layers:
        print(f"\n--- Layer: {layer_name} ---")
        gdf = gpd.read_file(str(gpkg_path), layer=layer_name, rows=5)
        print(f"CRS: {gdf.crs}")
        print(f"Colonnes: {list(gdf.columns)}")
        print(f"Types:\n{gdf.dtypes}\n")
        print("Échantillon (sans géométrie):")
        print(gdf.drop(columns="geometry").head())

        # Count total rows via SQL
        import sqlite3
        conn = sqlite3.connect(str(gpkg_path))
        count = conn.execute(f'SELECT COUNT(*) FROM "{layer_name}"').fetchone()[0]
        conn.close()
        print(f"\nTotal lignes: {count:,}")

        # Départements uniques (si colonne INSEE_COM ou CODE_IRIS)
        iris_col = None
        for c in ["CODE_IRIS", "code_iris", "INSEE_COM", "insee_com"]:
            if c in gdf.columns:
                iris_col = c
                break

        if iris_col:
            gdf_all = gpd.read_file(str(gpkg_path), layer=layer_name,
                                     columns=[iris_col])
            dep_codes = gdf_all[iris_col].str[:2].unique()
            print(f"Départements ({len(dep_codes)}): {sorted(dep_codes)[:20]}...")

    print(f"\n{'='*60}\n")
# &e


# &s &CONVERT - Conversion GPKG → TopoJSON
def convert_to_topojson(gpkg_path: Path, scope: str, tolerance: float):
    """Convertit GPKG Lambert93 → TopoJSON WGS84 simplifié."""
    import geopandas as gpd
    import topojson as tp

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Lecture GPKG ──
    t0 = time.time()
    print(f"\n[1/5] Lecture {gpkg_path.name}...")

    # Déterminer filtre spatial/attributaire
    if scope == "france":
        gdf = gpd.read_file(str(gpkg_path))
        out_name = "iris_france_wgs84"
    elif scope == "airbnb":
        gdf = gpd.read_file(str(gpkg_path))
        # Filtrer sur les 3 départements
        iris_col = _find_iris_col(gdf)
        dep_col = gdf[iris_col].str[:2]
        mask = dep_col.isin(DEPS_AIRBNB.keys())
        gdf = gdf[mask].copy()
        out_name = "iris_airbnb3villes_wgs84"
    elif scope == "idf":
        gdf = gpd.read_file(str(gpkg_path))
        iris_col = _find_iris_col(gdf)
        dep_col = gdf[iris_col].str[:2]
        mask = dep_col.isin(DEPS_IDF)
        gdf = gdf[mask].copy()
        out_name = "iris_idf_wgs84"
    else:
        raise ValueError(f"Scope inconnu: {scope}")

    print(f"    {len(gdf):,} IRIS chargés ({time.time()-t0:.1f}s)")
    print(f"    CRS source: {gdf.crs}")

    # ── 2. Reprojection Lambert 93 → WGS84 ──
    t1 = time.time()
    print(f"[2/5] Reprojection EPSG:2154 → EPSG:4326...")
    gdf = gdf.to_crs(epsg=4326)
    print(f"    OK ({time.time()-t1:.1f}s)")

    # ── 3. Nettoyage colonnes ──
    print(f"[3/5] Nettoyage colonnes...")
    # Garder uniquement les colonnes utiles
    keep_cols = []
    for c in gdf.columns:
        cl = c.lower()
        if cl in ["geometry"]:
            keep_cols.append(c)
        elif cl in ["code_iris", "nom_iris", "insee_com", "nom_com",
                     "typ_iris", "code_iris_2", "iris",
                     "inseecom2025", "nomcom2025", "codeiris2025",
                     "nomiris2025", "typiris"]:
            keep_cols.append(c)
    # If no standard cols found, keep all non-geometry
    if len(keep_cols) <= 1:
        keep_cols = list(gdf.columns)
    gdf = gdf[keep_cols]
    print(f"    Colonnes gardées: {[c for c in keep_cols if c != 'geometry']}")

    # ── 4. Simplification géométrie ──
    t2 = time.time()
    print(f"[4/5] Simplification (tolerance={tolerance})...")
    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)
    print(f"    OK ({time.time()-t2:.1f}s)")

    # ── 5. Export TopoJSON ──
    t3 = time.time()
    out_topojson = OUTPUT_DIR / f"{out_name}.topojson"
    out_geojson = OUTPUT_DIR / f"{out_name}.geojson"

    print(f"[5/5] Export TopoJSON...")

    # Export via topojson library
    topo = tp.Topology(gdf, prequantize=True, presimplify=tolerance)
    topo.to_json(str(out_topojson))

    # Also export GeoJSON for reference
    gdf.to_file(str(out_geojson), driver="GeoJSON")

    t_total = time.time() - t0
    size_topo = out_topojson.stat().st_size / 1e6
    size_geojson = out_geojson.stat().st_size / 1e6

    print(f"\n{'='*60}")
    print(f"RÉSULTAT — scope={scope}")
    print(f"  IRIS: {len(gdf):,}")
    print(f"  TopoJSON: {out_topojson.name} ({size_topo:.1f} MB)")
    print(f"  GeoJSON:  {out_geojson.name} ({size_geojson:.1f} MB)")
    print(f"  Ratio compression: {size_geojson/size_topo:.1f}x")
    print(f"  Temps total: {t_total:.1f}s")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    return out_topojson
# &e


# &s &HELPERS - Fonctions utilitaires
def _find_iris_col(gdf) -> str:
    """Trouve la colonne contenant le code IRIS."""
    candidates = ["CODE_IRIS", "code_iris", "CODEIRIS2025", "codeiris2025",
                   "CODE_IRIS_2", "IRIS", "iris"]
    for c in candidates:
        if c in gdf.columns:
            return c
    # Fallback: chercher colonne avec codes 9 chiffres
    for c in gdf.columns:
        if c == "geometry":
            continue
        sample = gdf[c].dropna().head(10).astype(str)
        if sample.str.match(r"^\d{9}$").all():
            print(f"    Colonne IRIS détectée: {c}")
            return c
    # Last resort: INSEE_COM (5 chiffres)
    for c in ["INSEE_COM", "insee_com", "INSEECOM2025", "inseecom2025"]:
        if c in gdf.columns:
            return c
    raise ValueError(f"Colonne IRIS introuvable. Colonnes: {list(gdf.columns)}")
# &e


# &s &CLI - Interface ligne de commande
def main():
    parser = argparse.ArgumentParser(
        description="Conversion IRIS GPKG Lambert93 → TopoJSON WGS84"
    )
    parser.add_argument("--scope", choices=["france", "airbnb", "idf"],
                        default="airbnb",
                        help="Périmètre: france (tout), airbnb (Paris+Lyon+Bordeaux), idf")
    parser.add_argument("--inspect", action="store_true",
                        help="Inspecter le GPKG sans convertir")
    parser.add_argument("--tolerance", type=float, default=SIMPLIFY_TOLERANCE,
                        help=f"Tolérance simplification en degrés (défaut: {SIMPLIFY_TOLERANCE})")
    parser.add_argument("--gpkg", type=str, default=str(GPKG_PATH),
                        help="Chemin vers le fichier GPKG")
    args = parser.parse_args()

    gpkg = Path(args.gpkg)
    if not gpkg.exists():
        print(f"ERREUR: Fichier introuvable: {gpkg}")
        sys.exit(1)

    if args.inspect:
        inspect_gpkg(gpkg)
    else:
        # Vérifier dépendances
        try:
            import geopandas
            import topojson
        except ImportError as e:
            print(f"ERREUR: Package manquant: {e}")
            print("  → pip install geopandas topojson pyproj")
            sys.exit(1)

        convert_to_topojson(gpkg, args.scope, args.tolerance)


if __name__ == "__main__":
    main()
# &e

# &e (FIN-du module IRIS_TOPOJSON_aaMAIN)
