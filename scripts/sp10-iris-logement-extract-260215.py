"""
sp10 — Extraction données logement IRIS pour Airbnb France
============================================================
Extrait les ratios propriétaires/locataires par IRIS depuis le dossier complet INSEE.
Joint avec la géographie IRIS pour créer un dataset prêt à cartographier.

Sources :
- Dossier complet INSEE (RP 2021/2022) : propriétaires, locataires, HLM, vacances
- CONTOURS-IRIS GPKG (Lambert 93) : géométries IRIS

Usage :
    python scripts/sp10-iris-logement-extract-260215.py
    python scripts/sp10-iris-logement-extract-260215.py --scope airbnb   # Paris+Lyon+Bordeaux
    python scripts/sp10-iris-logement-extract-260215.py --scope idf      # Île-de-France
    python scripts/sp10-iris-logement-extract-260215.py --scope france   # France entière
    python scripts/sp10-iris-logement-extract-260215.py --with-geo       # Joindre géométries
    python scripts/sp10-iris-logement-extract-260215.py --inspect        # Explorer colonnes

Output :
    data/interim/iris_logement_airbnb.parquet   (scope=airbnb, ~7K IRIS)
    data/interim/iris_logement_france.parquet    (scope=france, ~53K IRIS)
    data/geo/iris_airbnb_logement.geojson        (--with-geo)
"""

# &s &IRIS_LOGEMENT_aaMAIN - Pipeline extraction logement IRIS

import argparse
import sys
import time
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
DOSSIER_COMPLET = Path(
    r"C:\Users\vince\DBD-datab\pobs-fr-datafull"
    r"\unzipped_dossier_complet_31_12_2024\dossier_complet.csv"
)
META_DOSSIER = Path(
    r"C:\Users\vince\DBD-datab\pobs-fr-datafull"
    r"\unzipped_dossier_complet_31_12_2024\meta_dossier_complet.csv"
)
GPKG_PATH = Path(
    r"C:\Users\vince\DBD-datab\TDC-ref\geo-shape-raw"
    r"\CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2025-01-01\iris.gpkg"
)
DBCLN_COMMUNES = Path(
    r"C:\Users\vince\hh\pq\PDS\ptod-ttrajObserDev"
    r"\data\output\parquet\dbcln-communes-vf.parquet"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_INTERIM = PROJECT_ROOT / "data" / "interim"
OUTPUT_GEO = PROJECT_ROOT / "data" / "geo"

# Départements
DEPS_AIRBNB = {"75", "69", "33"}
DEPS_IDF = {"75", "77", "78", "91", "92", "93", "94", "95"}

# Colonnes logement du dossier complet
# P21 = RP 2021 (dernière année dispo dans dossier complet 2024)
LOG_COLS = [
    "CODGEO",           # Code commune ou IRIS
    "LIBGEO",           # Libellé
    "P21_LOG",          # Total logements
    "P21_RP",           # Résidences principales
    "P21_RSECOCC",      # Résidences secondaires
    "P21_LOGVAC",       # Logements vacants
    "P21_RP_PROP",      # RP propriétaires
    "P21_RP_LOC",       # RP locataires (tous)
    "P21_RP_LOCHLMV",   # RP locataires HLM
    "P21_RP_GRAT",      # RP logés gratuitement
]


# &s &INSPECT - Exploration colonnes disponibles
def inspect_dossier_complet():
    """Explore les colonnes logement du dossier complet."""
    import pandas as pd

    print(f"\n{'='*60}")
    print(f"INSPECTION: Dossier complet INSEE")
    print(f"{'='*60}")

    # Lire métadonnées
    if META_DOSSIER.exists():
        meta = pd.read_csv(str(META_DOSSIER), sep=";", encoding="utf-8")
        print(f"\nMétadonnées: {len(meta)} variables")
        # Filtrer logement
        log_meta = meta[meta.iloc[:, 0].str.contains("P21_RP|P21_LOG|P21_RSECOCC|P21_LOGVAC",
                                                       case=False, na=False)]
        if len(log_meta) > 0:
            print("\nVariables logement (P21_*) :")
            for _, row in log_meta.iterrows():
                print(f"  {row.iloc[0]:25s} | {row.iloc[1] if len(row) > 1 else ''}")
    else:
        print(f"  Métadonnées non trouvées: {META_DOSSIER}")

    # Lire échantillon
    print(f"\nLecture échantillon (100 lignes)...")
    df = pd.read_csv(str(DOSSIER_COMPLET), sep=";", nrows=100, low_memory=False)
    print(f"Colonnes ({len(df.columns)}): {list(df.columns)[:30]}...")

    # Colonnes logement trouvées
    found = [c for c in LOG_COLS if c in df.columns]
    missing = [c for c in LOG_COLS if c not in df.columns]
    print(f"\nColonnes logement trouvées: {found}")
    if missing:
        print(f"Colonnes manquantes: {missing}")
        # Chercher alternatives
        alt = [c for c in df.columns if "RP_PROP" in c or "RP_LOC" in c or "_LOG" in c]
        print(f"Alternatives potentielles: {alt[:20]}")

    # Niveaux géographiques
    if "CODGEO" in df.columns:
        lens = df["CODGEO"].str.len().value_counts()
        print(f"\nLongueur CODGEO: {dict(lens)}")
        print(f"  5 chars = commune, 9 chars = IRIS")

    print(f"\n{'='*60}\n")
# &e


# &s &EXTRACT - Extraction des données logement IRIS
def extract_logement_iris(scope: str, with_geo: bool = False):
    """Extrait les ratios propriétaires/locataires par IRIS."""
    import pandas as pd
    import numpy as np

    OUTPUT_INTERIM.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    deps = DEPS_AIRBNB if scope == "airbnb" else (DEPS_IDF if scope == "idf" else None)

    # ── 1. Lecture dossier complet ──
    print(f"\n[1/4] Lecture dossier complet INSEE...")

    # D'abord détecter le séparateur et les colonnes disponibles
    sample = pd.read_csv(str(DOSSIER_COMPLET), sep=";", nrows=5, low_memory=False)

    # Identifier les colonnes propriétaires disponibles
    avail_cols = list(sample.columns)
    use_cols = [c for c in LOG_COLS if c in avail_cols]
    if "CODGEO" not in use_cols:
        # Chercher alternative
        for alt in ["IRIS", "CODE_IRIS", "codgeo"]:
            if alt in avail_cols:
                use_cols = [alt] + [c for c in use_cols if c != "CODGEO"]
                break

    print(f"    Colonnes sélectionnées: {use_cols}")

    df = pd.read_csv(
        str(DOSSIER_COMPLET),
        sep=";",
        usecols=use_cols,
        low_memory=False,
        dtype={"CODGEO": str}
    )
    print(f"    {len(df):,} lignes chargées ({time.time()-t0:.1f}s)")

    # ── 2. Filtrer IRIS (9 caractères) ──
    print(f"[2/4] Filtrage IRIS...")
    geo_col = "CODGEO" if "CODGEO" in df.columns else df.columns[0]
    df[geo_col] = df[geo_col].str.strip()

    # IRIS = 9 chiffres, commune = 5 chiffres
    is_iris = df[geo_col].str.len() == 9
    df_iris = df[is_iris].copy()
    print(f"    {len(df_iris):,} IRIS (sur {len(df):,} lignes)")

    # Filtrer par département
    if deps:
        df_iris["dep"] = df_iris[geo_col].str[:2]
        df_iris = df_iris[df_iris["dep"].isin(deps)].copy()
        df_iris.drop(columns=["dep"], inplace=True)
        print(f"    Après filtre départements {deps}: {len(df_iris):,} IRIS")

    # ── 3. Calculer ratios ──
    print(f"[3/4] Calcul des ratios...")

    # Renommer pour clarté
    df_iris = df_iris.rename(columns={geo_col: "code_iris"})

    # Calculer % si les colonnes existent
    rp_col = next((c for c in ["P21_RP", "P21_RP_PROP"] if c in df_iris.columns), None)

    if "P21_RP" in df_iris.columns:
        rp = pd.to_numeric(df_iris["P21_RP"], errors="coerce")

        if "P21_RP_PROP" in df_iris.columns:
            prop = pd.to_numeric(df_iris["P21_RP_PROP"], errors="coerce")
            df_iris["pct_proprietaire"] = np.where(rp > 0, (prop / rp * 100).round(1), np.nan)

        if "P21_RP_LOC" in df_iris.columns:
            loc_ = pd.to_numeric(df_iris["P21_RP_LOC"], errors="coerce")
            df_iris["pct_locataire"] = np.where(rp > 0, (loc_ / rp * 100).round(1), np.nan)

        if "P21_RP_LOCHLMV" in df_iris.columns:
            hlm = pd.to_numeric(df_iris["P21_RP_LOCHLMV"], errors="coerce")
            df_iris["pct_hlm"] = np.where(rp > 0, (hlm / rp * 100).round(1), np.nan)

    if "P21_LOG" in df_iris.columns and "P21_LOGVAC" in df_iris.columns:
        total = pd.to_numeric(df_iris["P21_LOG"], errors="coerce")
        vac = pd.to_numeric(df_iris["P21_LOGVAC"], errors="coerce")
        df_iris["pct_vacant"] = np.where(total > 0, (vac / total * 100).round(1), np.nan)

    if "P21_LOG" in df_iris.columns and "P21_RSECOCC" in df_iris.columns:
        total = pd.to_numeric(df_iris["P21_LOG"], errors="coerce")
        sec = pd.to_numeric(df_iris["P21_RSECOCC"], errors="coerce")
        df_iris["pct_res_secondaire"] = np.where(total > 0, (sec / total * 100).round(1), np.nan)

    # Ajouter code commune (5 premiers chiffres)
    df_iris["code_commune"] = df_iris["code_iris"].str[:5]

    # Statistiques
    for col in ["pct_proprietaire", "pct_locataire", "pct_hlm", "pct_vacant", "pct_res_secondaire"]:
        if col in df_iris.columns:
            print(f"    {col}: médiane={df_iris[col].median():.1f}%, "
                  f"min={df_iris[col].min():.1f}%, max={df_iris[col].max():.1f}%")

    # ── 4. Export ──
    print(f"[4/4] Export...")
    scope_suffix = scope if scope != "airbnb" else "airbnb3villes"
    out_path = OUTPUT_INTERIM / f"iris_logement_{scope_suffix}.parquet"
    df_iris.to_parquet(str(out_path), index=False)
    size_mb = out_path.stat().st_size / 1e6
    print(f"    → {out_path.name} ({size_mb:.1f} MB, {len(df_iris):,} IRIS)")

    # CSV pour vérification
    out_csv = OUTPUT_INTERIM / f"iris_logement_{scope_suffix}.csv"
    df_iris.to_csv(str(out_csv), index=False, encoding="utf-8-sig")
    print(f"    → {out_csv.name} (CSV UTF-8 BOM)")

    # ── Optionnel: joindre géométries ──
    if with_geo:
        _join_geometry(df_iris, scope_suffix)

    t_total = time.time() - t0
    print(f"\n{'='*60}")
    print(f"RÉSULTAT — scope={scope}")
    print(f"  IRIS: {len(df_iris):,}")
    print(f"  Output: {out_path}")
    print(f"  Temps: {t_total:.1f}s")
    print(f"{'='*60}\n")
# &e


# &s &JOIN_GEO - Jointure avec géométries IRIS
def _join_geometry(df_iris, scope_suffix: str):
    """Joint les données logement avec les géométries IRIS."""
    import geopandas as gpd

    OUTPUT_GEO.mkdir(parents=True, exist_ok=True)

    print(f"\n    Jointure géométries IRIS...")
    gdf = gpd.read_file(str(GPKG_PATH))
    print(f"    {len(gdf):,} géométries IRIS chargées")

    # Trouver colonne IRIS dans le GPKG
    iris_col_gpkg = None
    for c in gdf.columns:
        if c.lower() in ["code_iris", "codeiris2025", "iris"]:
            iris_col_gpkg = c
            break
    if iris_col_gpkg is None:
        # Chercher colonne 9 chiffres
        for c in gdf.columns:
            if c == "geometry":
                continue
            sample = gdf[c].dropna().head(10).astype(str)
            if sample.str.match(r"^\d{9}$").all():
                iris_col_gpkg = c
                break

    if iris_col_gpkg is None:
        print("    ERREUR: Colonne IRIS introuvable dans le GPKG")
        return

    print(f"    Colonne IRIS GPKG: {iris_col_gpkg}")

    # Reprojection Lambert 93 → WGS84
    gdf = gdf.to_crs(epsg=4326)

    # Simplifier géométrie
    gdf["geometry"] = gdf["geometry"].simplify(0.0005, preserve_topology=True)

    # Jointure
    gdf_merged = gdf.merge(
        df_iris,
        left_on=iris_col_gpkg,
        right_on="code_iris",
        how="inner"
    )
    print(f"    {len(gdf_merged):,} IRIS après jointure")

    # Export GeoJSON
    out_geojson = OUTPUT_GEO / f"iris_{scope_suffix}_logement.geojson"
    gdf_merged.to_file(str(out_geojson), driver="GeoJSON")
    size_mb = out_geojson.stat().st_size / 1e6
    print(f"    → {out_geojson.name} ({size_mb:.1f} MB)")
# &e


# &s &CLI - Interface ligne de commande
def main():
    parser = argparse.ArgumentParser(
        description="Extraction données logement IRIS pour Airbnb France"
    )
    parser.add_argument("--scope", choices=["france", "airbnb", "idf"],
                        default="airbnb",
                        help="Périmètre: france, airbnb (Paris+Lyon+Bordeaux), idf")
    parser.add_argument("--inspect", action="store_true",
                        help="Explorer colonnes du dossier complet")
    parser.add_argument("--with-geo", action="store_true",
                        help="Joindre géométries IRIS (nécessite geopandas)")
    args = parser.parse_args()

    if args.inspect:
        inspect_dossier_complet()
    else:
        extract_logement_iris(args.scope, args.with_geo)


if __name__ == "__main__":
    main()
# &e

# &e (FIN-du module IRIS_LOGEMENT_aaMAIN)
