# &s &SP10_KPI_FRANCE_aaMAIN - KPI France multi-niveaux (country/city/arr/iris)

# Calcule les indicateurs Airbnb pour la France à 4 niveaux géographiques :
#   country → city → arr (arrondissement) → iris
# Utilise le helper jcn-kpi.py pour les formules partagées avec sp08.
# Jointure spatiale IRIS via geopandas + GPKG IGN.
#
# Inputs:
#   data/interim/dbsumlistings_2506_cons_global.parquet
#   data/external/insee_iris_pop_log_3villes.csv (ou 4villes avec BAB)
#   data/external/insee_tourisme_3villes.csv
#   CONTOURS-IRIS GPKG (IGN)
#
# Output:
#   data/interim/kpi_france_byterr_2506.csv
#
# Date: 2026-02-21

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
import sys
import importlib.util

# &s &CONFIG

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
INTERIM_DIR = BASE / "data" / "interim"
EXT_DIR = BASE / "data" / "external"

DATA_PATH = INTERIM_DIR / "dbsumlistings_2506_cons_global.parquet"
INSEE_IRIS_PATH = EXT_DIR / "insee_iris_pop_log_3villes.csv"
INSEE_TOUR_PATH = EXT_DIR / "insee_tourisme_3villes.csv"
GPKG_PATH = Path(r"C:\Users\vince\DBD-datab\TDC-ref\geo-shape-raw\CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2025-01-01\iris.gpkg")

OUTPUT_PATH = INTERIM_DIR / "kpi_france_byterr_2506.csv"

# Villes France dans le pipeline
FRANCE_CITIES = ["paris", "lyon", "bordeaux", "pays-basque"]

# Mapping arrondissements Paris (neighbourhood → arr label)
ARR_MAP_PARIS = {
    "Louvre": "1er", "Bourse": "2e", "Temple": "3e",
    "Hôtel-de-Ville": "4e", "Panthéon": "5e", "Luxembourg": "6e",
    "Palais-Bourbon": "7e", "Élysée": "8e", "Opéra": "9e",
    "Entrepôt": "10e", "Popincourt": "11e", "Reuilly": "12e",
    "Gobelins": "13e", "Observatoire": "14e", "Vaugirard": "15e",
    "Passy": "16e", "Batignolles-Monceau": "17e", "Buttes-Montmartre": "18e",
    "Buttes-Chaumont": "19e", "Ménilmontant": "20e",
}

# Mapping arrondissements Lyon (neighbourhood → arr label)
# Format Inside Airbnb: "1er Arrondissement", "2e Arrondissement", ...
ARR_MAP_LYON = {f"{i}e Arrondissement": f"{i}e" for i in range(2, 10)}
ARR_MAP_LYON["1er Arrondissement"] = "1er"

# BAB sous-villes (neighbourhood_group dans pays-basque)
BAB_CITIES = ["Biarritz", "Anglet", "Bayonne"]

# Correction centre commune pour agglos (Inside Airbnb couvre la métropole)
# Même logique que CENTRE_FILTERS dans sp08
CENTRE_FILTERS = {
    "bordeaux": {"col": "neighbourhood_group", "values": ["Bordeaux"]},
}

# IRIS filter patterns par ville (préfixe code_iris)
IRIS_FILTERS = {
    "paris": "75%",
    "lyon": "6938%",
    "bordeaux": "33063%",
    "pays-basque": ("64102%", "64122%", "64024%"),  # Bayonne, Biarritz, Anglet
}

# Seuil minimum listings par IRIS pour inclure dans output
IRIS_MIN_LISTINGS = 20

# &e

# &s &LOAD_HELPER - Import helper KPI

_spec = importlib.util.spec_from_file_location("jcn_kpi", BASE / "src" / "jcn-kpi.py")
jcn_kpi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jcn_kpi)

# &e

# &s &LOAD_DATA - Chargement listings + INSEE

print("=" * 60)
print("sp10 — KPI France multi-niveaux (country/city/arr/iris)")
print("=" * 60)

# Listings France
print(f"\nChargement {DATA_PATH.name}...")
df_raw = pd.read_parquet(DATA_PATH)
df_raw = df_raw[df_raw["city"].isin(FRANCE_CITIES)].copy()
print(f"France brut: {len(df_raw):,} lignes, {df_raw['city'].nunique()} villes")

# Flags + cleaning
if "price_eur" not in df_raw.columns:
    df_raw["price_eur"] = df_raw["price"]  # France = EUR, pas de conversion
jcn_kpi.add_flags(df_raw)
df = jcn_kpi.clean_listings(df_raw)
print(f"France nettoyé: {len(df):,} lignes")

# Arrondissements Paris (neighbourhood = "Louvre", "Bourse", etc.)
df.loc[df["city"] == "paris", "arr"] = df.loc[df["city"] == "paris", "neighbourhood"].map(ARR_MAP_PARIS)
# Arrondissements Lyon (neighbourhood = "1er Arrondissement", "2e Arrondissement", etc.)
df.loc[df["city"] == "lyon", "arr"] = df.loc[df["city"] == "lyon", "neighbourhood"].map(ARR_MAP_LYON)
# BAB : sous-ville = neighbourhood_group
df.loc[df["city"] == "pays-basque", "bab_commune"] = df.loc[df["city"] == "pays-basque", "neighbourhood_group"]

# INSEE IRIS
print(f"Chargement INSEE IRIS ({INSEE_IRIS_PATH.name})...")
insee_iris = pd.read_csv(INSEE_IRIS_PATH, dtype={"code_iris": str, "code_insee": str})
print(f"  {len(insee_iris)} IRIS, villes: {insee_iris['city'].value_counts().to_dict()}")

# INSEE tourisme
insee_tour = pd.read_csv(INSEE_TOUR_PATH)

# &e

# &s &FILTER_CENTRE - Filtre centre commune pour agglos

# Appliquer CENTRE_FILTERS pour aligner numérateur (listings) et dénominateur (INSEE commune)
# df reste le jeu complet (utilisé pour IRIS spatial join), df_centre pour KPI city/country
df_centre = df.copy()
for city_name, filt in CENTRE_FILTERS.items():
    col, vals = filt["col"], filt["values"]
    mask_city = df_centre["city"] == city_name
    mask_centre = df_centre[col].isin(vals)
    n_before = mask_city.sum()
    df_centre = df_centre[~mask_city | (mask_city & mask_centre)]
    n_after = (df_centre["city"] == city_name).sum()
    print(f"Filtre centre {city_name}: {n_before:,} -> {n_after:,} ({col}={vals})")

# &e

# &s &KPI_COUNTRY - Niveau country (agrégat France)

print("\n--- Niveau country ---")
kpi_fr = jcn_kpi.compute_kpi(df_centre)
kpi_fr["level"] = "country"
kpi_fr["territory"] = "france"
kpi_fr["city"] = "france"

# Agrégation INSEE par ville (réutilisé pour country, city, arr)
INSEE_COLS = {
    "pop": "pop_2022", "logements": "log_2022", "rp": "rp_2022",
    "res_sec": "rsecocc_2022", "rp_prop": "rp_prop_2022",
    "nper_prop": "nper_rp_prop_2022", "log_vacants": "logvac_2022",
}
insee_agg = insee_iris.groupby("city").agg(
    **{k: (v, "sum") for k, v in INSEE_COLS.items()}
).reset_index()
# Arrondir à l'entier (données INSEE = estimations statistiques)
for c in INSEE_COLS:
    insee_agg[c] = insee_agg[c].round(0)

def add_insee_cols(kpi_row, insee_sub):
    """Ajoute colonnes INSEE brutes + ratios de densité à une ligne KPI."""
    totals = {c: insee_sub[c].sum() for c in INSEE_COLS}
    for c, v in totals.items():
        kpi_row[c] = round(v)
    if totals["pop"] > 0:
        jcn_kpi.add_density_ratios(
            kpi_row, pop=totals["pop"], rp=totals["rp"],
            nper_prop=totals["nper_prop"], res_sec=totals["res_sec"],
        )

# Country : somme toutes villes
add_insee_cols(kpi_fr, insee_agg)

# Tourisme
tour_total = insee_tour[["htch25", "rtuh25"]].sum()
kpi_fr["htch"] = int(tour_total["htch25"])
kpi_fr["rtuh"] = int(tour_total["rtuh25"])
kpi_fr["ratio_airbnb_hotel"] = round(kpi_fr["n_listings"] / tour_total["htch25"], 1)

rows = [kpi_fr]
print(f"  France: {kpi_fr['n_listings']} listings")

# &e

# &s &KPI_CITY - Niveau city (4 villes)

print("\n--- Niveau city ---")
for city_name in FRANCE_CITIES:
    df_city = df_centre[df_centre["city"] == city_name]
    kpi = jcn_kpi.compute_kpi(df_city)
    kpi["level"] = "city"
    kpi["territory"] = city_name
    kpi["city"] = city_name

    # INSEE colonnes brutes + densité
    city_insee = insee_agg[insee_agg["city"] == city_name]
    if len(city_insee) > 0:
        add_insee_cols(kpi, city_insee)

    # Tourisme
    tour_city = insee_tour[insee_tour["city"] == city_name]
    if len(tour_city) > 0:
        kpi["htch"] = int(tour_city.iloc[0]["htch25"])
        kpi["rtuh"] = int(tour_city.iloc[0]["rtuh25"])
        kpi["ratio_airbnb_hotel"] = round(kpi["n_listings"] / tour_city.iloc[0]["htch25"], 1)

    rows.append(kpi)
    print(f"  {city_name}: {kpi['n_listings']} listings")

# &e

# &s &KPI_ARR - Niveau arrondissement (Paris 20 + Lyon 9)

print("\n--- Niveau arr ---")

# Helper : agréger INSEE IRIS → arr
def insee_by_arr(city_name, code_to_arr):
    """Agrège les IRIS INSEE au niveau arrondissement."""
    sub = insee_iris[insee_iris["city"] == city_name].copy()
    sub["arr"] = sub["code_insee"].map(code_to_arr)
    return sub.groupby("arr").agg(
        **{k: (v, "sum") for k, v in INSEE_COLS.items()}
    ).reset_index()

# Paris arrondissements
df_paris = df[df["city"] == "paris"]
paris_arr_from_code = {f"751{i:02d}": (f"{i}er" if i == 1 else f"{i}e") for i in range(1, 21)}
paris_insee_by_arr = insee_by_arr("paris", paris_arr_from_code)

for arr_label in sorted(ARR_MAP_PARIS.values(), key=lambda x: int(x.replace("er", "").replace("e", ""))):
    df_arr = df_paris[df_paris["arr"] == arr_label]
    if len(df_arr) == 0:
        continue
    kpi = jcn_kpi.compute_kpi(df_arr)
    kpi["level"] = "arr"
    kpi["territory"] = f"paris_{arr_label}"
    kpi["city"] = "paris"
    kpi["arr"] = arr_label

    arr_insee = paris_insee_by_arr[paris_insee_by_arr["arr"] == arr_label]
    if len(arr_insee) > 0:
        add_insee_cols(kpi, arr_insee)

    rows.append(kpi)

print(f"  Paris: {len([r for r in rows if r.get('city')=='paris' and r['level']=='arr'])} arrondissements")

# Lyon arrondissements
df_lyon = df[df["city"] == "lyon"]
lyon_arr_from_code = {f"6938{i}": (f"{i}er" if i == 1 else f"{i}e") for i in range(1, 10)}
lyon_insee_by_arr = insee_by_arr("lyon", lyon_arr_from_code)

for arr_label in sorted(ARR_MAP_LYON.values(), key=lambda x: int(x.replace("er", "").replace("e", ""))):
    df_arr = df_lyon[df_lyon["arr"] == arr_label]
    if len(df_arr) == 0:
        continue
    kpi = jcn_kpi.compute_kpi(df_arr)
    kpi["level"] = "arr"
    kpi["territory"] = f"lyon_{arr_label}"
    kpi["city"] = "lyon"
    kpi["arr"] = arr_label

    arr_insee = lyon_insee_by_arr[lyon_insee_by_arr["arr"] == arr_label]
    if len(arr_insee) > 0:
        add_insee_cols(kpi, arr_insee)

    rows.append(kpi)

print(f"  Lyon: {len([r for r in rows if r.get('city')=='lyon' and r['level']=='arr'])} arrondissements")

# BAB communes (pas d'arrondissements, mais 3 sous-villes)
df_bab = df[df["city"] == "pays-basque"]
bab_insee = insee_iris[insee_iris["city"] == "pays-basque"] if "pays-basque" in insee_iris["city"].values else pd.DataFrame()

for commune in BAB_CITIES:
    df_com = df_bab[df_bab["bab_commune"] == commune]
    if len(df_com) == 0:
        continue
    kpi = jcn_kpi.compute_kpi(df_com)
    kpi["level"] = "arr"  # Traité comme arr pour homogénéité
    kpi["territory"] = f"bab_{commune.lower()}"
    kpi["city"] = "pays-basque"
    kpi["arr"] = commune

    # INSEE BAB : filtrer par code_insee commune, agréger IRIS → commune
    bab_codes = {"Bayonne": "64102", "Biarritz": "64122", "Anglet": "64024"}
    com_insee_raw = insee_iris[insee_iris["code_insee"] == bab_codes.get(commune, "")]
    if len(com_insee_raw) > 0:
        com_agg = pd.DataFrame([{c: com_insee_raw[v].sum() for c, v in INSEE_COLS.items()}])
        add_insee_cols(kpi, com_agg)

    rows.append(kpi)

print(f"  BAB: {len([r for r in rows if r.get('city')=='pays-basque' and r['level']=='arr'])} communes")

# &e

# &s &KPI_IRIS - Niveau IRIS (jointure spatiale geopandas)

print("\n--- Niveau IRIS (jointure spatiale) ---")

if not GPKG_PATH.exists():
    print(f"  [SKIP] GPKG non trouvé: {GPKG_PATH}")
else:
    import fiona
    layers = fiona.listlayers(str(GPKG_PATH))
    lyr = layers[0]

    for city_name in FRANCE_CITIES:
        df_city = df[df["city"] == city_name]
        if len(df_city) == 0:
            continue

        # Charger IRIS géometries
        iris_filter = IRIS_FILTERS.get(city_name)
        if iris_filter is None:
            continue

        if isinstance(iris_filter, tuple):
            # BAB : multiple préfixes
            conditions = " OR ".join([f'code_iris LIKE \'{p}\'' for p in iris_filter])
            query = f'SELECT * FROM "{lyr}" WHERE {conditions}'
        else:
            query = f'SELECT * FROM "{lyr}" WHERE code_iris LIKE \'{iris_filter}\''

        try:
            iris_gdf = gpd.read_file(GPKG_PATH, layer=lyr, where=query.split("WHERE ")[1] if "WHERE" in query else None)
        except Exception:
            # Fallback: read with SQL-like query via fiona
            iris_gdf = gpd.read_file(str(GPKG_PATH), sql=query)

        if iris_gdf.crs and iris_gdf.crs.to_epsg() != 4326:
            iris_gdf = iris_gdf.to_crs(4326)

        # Points listings → jointure spatiale
        pts_gdf = gpd.GeoDataFrame(
            df_city,
            geometry=gpd.points_from_xy(df_city["longitude"], df_city["latitude"]),
            crs=4326,
        )

        joined = gpd.sjoin(pts_gdf, iris_gdf[["code_iris", "nom_iris", "geometry"]], how="left", predicate="within")
        joined_valid = joined[joined["code_iris"].notna()]

        # KPI par IRIS
        n_iris = 0
        for code_iris, grp in joined_valid.groupby("code_iris"):
            if len(grp) < IRIS_MIN_LISTINGS:
                continue
            kpi = jcn_kpi.compute_kpi(grp)
            kpi["level"] = "iris"
            kpi["territory"] = code_iris
            kpi["city"] = city_name
            kpi["code_iris"] = code_iris
            nom = grp["nom_iris"].iloc[0] if "nom_iris" in grp.columns else ""
            kpi["nom_iris"] = nom

            # Arrondissement (pour Paris/Lyon)
            if city_name == "paris" and "arr" in grp.columns:
                kpi["arr"] = grp["arr"].iloc[0] if grp["arr"].notna().any() else ""
            elif city_name == "lyon" and "arr" in grp.columns:
                kpi["arr"] = grp["arr"].iloc[0] if grp["arr"].notna().any() else ""
            elif city_name == "pays-basque" and "bab_commune" in grp.columns:
                kpi["arr"] = grp["bab_commune"].iloc[0] if grp["bab_commune"].notna().any() else ""

            # INSEE IRIS — colonnes brutes + ratios de densité
            iris_insee = insee_iris[insee_iris["code_iris"] == code_iris]
            if len(iris_insee) > 0:
                row_insee = iris_insee.iloc[0]
                # Colonnes brutes INSEE (arrondi 0 décimales)
                kpi["pop"] = round(row_insee["pop_2022"])
                kpi["rp"] = round(row_insee["rp_2022"])
                kpi["res_sec"] = round(row_insee["rsecocc_2022"])
                kpi["logements"] = round(row_insee["log_2022"])
                kpi["rp_prop"] = round(row_insee["rp_prop_2022"])
                kpi["nper_prop"] = round(row_insee["nper_rp_prop_2022"])
                kpi["log_vacants"] = round(row_insee["logvac_2022"])
                # Ratios de densité (skip si pop=0)
                if row_insee["pop_2022"] > 0:
                    jcn_kpi.add_density_ratios(
                        kpi,
                        pop=row_insee["pop_2022"],
                        rp=row_insee["rp_2022"],
                        nper_prop=row_insee["nper_rp_prop_2022"],
                        res_sec=row_insee["rsecocc_2022"],
                    )

            rows.append(kpi)
            n_iris += 1

        n_matched = len(joined_valid)
        n_total = len(df_city)
        print(f"  {city_name}: {n_iris} IRIS (>= {IRIS_MIN_LISTINGS} listings), "
              f"{n_matched}/{n_total} listings matchés ({n_matched/n_total*100:.0f}%)")

# &e

# &s &EXPORT - Assemblage DataFrame + export CSV

print("\n--- Export ---")
result = pd.DataFrame(rows)

# Colonnes ordonnées
cols_order = [
    "level", "territory", "city", "arr", "code_iris", "nom_iris",
    "pop", "logements", "rp", "res_sec", "rp_prop", "nper_prop", "log_vacants",
    "n_listings", "n_entire", "n_hosts",
    "listings_1000hab", "entire_1000rp", "listings_1000rps", "listings_1000prop", "listings_1000hsg",
    "prix_med", "prix_med_entire", "prix_med_private",
    "prix_moy", "prix_q25", "prix_q75", "prix_iqr",
    "pct_entire", "pct_multi", "pct_longterm", "ratio_lh",
    "cr_hosts_50pct", "cr_top10_pct",
    "cr_host_5plus", "cr_host_10plus",
    "cr_offre_5plus", "cr_offre_10plus",
    "dispo_med", "dispo_moy", "reviews_med", "rpm_med",
    "htch", "rtuh", "ratio_airbnb_hotel",
]
cols_present = [c for c in cols_order if c in result.columns]
extra_cols = [c for c in result.columns if c not in cols_order]
result = result[cols_present + extra_cols]

result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

# Résumé
print(f"\nExport: {OUTPUT_PATH.name}")
print(f"  {len(result)} lignes total")
for lvl in ["country", "city", "arr", "iris"]:
    n = len(result[result["level"] == lvl])
    if n > 0:
        print(f"  - {lvl}: {n} territoires")
print(f"  {len(result.columns)} colonnes")

print(f"\n{'='*60}")
print("sp10 terminé.")
print(f"{'='*60}")

# &e

# &e
