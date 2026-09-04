# &s &SP10_KPI_FRANCE_aaMAIN - KPI France multi-niveaux (ref/country/city/arr/iris)

# Produit un CSV unique multi-niveaux pour le rapport France.
# Niveaux ref_monde, ref_europe importés de kpi_global_by_aggregate.
# Niveaux city (Paris/Lyon/Bordeaux) importés de kpi_global_by_city.
# Niveaux city (Biarritz/Bayonne/Anglet), arr, iris calculés depuis dblistingfull.
# Helper jcn-kpi.py pour les formules partagées avec sp08.
#
# Inputs:
#   data/interim/kpi_global_by_city_2506.csv
#   data/interim/kpi_global_by_aggregate_2506.csv
#   data/interim/dblistingfull_2506_cons_global.parquet
#   data/external/insee_iris_pop_log_3villes.csv
#   data/external/insee_tourisme_3villes.csv
#   CONTOURS-IRIS GPKG (IGN)
#
# Output:
#   data/interim/kpi_france_byterr_2506.csv
#
# Date: 2026-02-21 | Refacto: 2026-04-28

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
import importlib.util
import sys

# &s &CONFIG

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
INTERIM_DIR = BASE / "data" / "interim"
EXT_DIR = BASE / "data" / "external"

# Snapshot cible paramétrable : --snapshot 26-06 (défaut 25-06 pour rétrocompat)
SNAPSHOT = "25-06"
for _i, _a in enumerate(sys.argv):
    if _a == "--snapshot" and _i + 1 < len(sys.argv):
        SNAPSHOT = sys.argv[_i + 1]
SNAP_TAG = SNAPSHOT.replace("-", "")  # "26-06" -> "2606"

LISTINGFULL_PATH = INTERIM_DIR / f"dblistingfull_{SNAP_TAG}_cons_global.parquet"
KPI_CITY_PATH = INTERIM_DIR / f"kpi_global_by_city_{SNAP_TAG}.csv"
KPI_AGG_PATH = INTERIM_DIR / f"kpi_global_by_aggregate_{SNAP_TAG}.csv"
INSEE_IRIS_PATH = EXT_DIR / "insee_iris_pop_log_3villes.csv"
INSEE_TOUR_PATH = EXT_DIR / "insee_tourisme_3villes.csv"
GPKG_PATH = Path(r"C:\Users\vince\DBD-datab\TDC-ref\geo-shape-raw\CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2025-01-01\iris.gpkg")

OUTPUT_PATH = INTERIM_DIR / f"kpi_france_byterr_{SNAP_TAG}.csv"

# Villes France dans le pipeline
FRANCE_CITIES = ["paris", "lyon", "bordeaux", "pays-basque"]

# Mapping arrondissements Paris
ARR_MAP_PARIS = {
    "Louvre": "1er", "Bourse": "2e", "Temple": "3e",
    "Hôtel-de-Ville": "4e", "Panthéon": "5e", "Luxembourg": "6e",
    "Palais-Bourbon": "7e", "Élysée": "8e", "Opéra": "9e",
    "Entrepôt": "10e", "Popincourt": "11e", "Reuilly": "12e",
    "Gobelins": "13e", "Observatoire": "14e", "Vaugirard": "15e",
    "Passy": "16e", "Batignolles-Monceau": "17e", "Buttes-Montmartre": "18e",
    "Buttes-Chaumont": "19e", "Ménilmontant": "20e",
}

# Mapping arrondissements Lyon
ARR_MAP_LYON = {f"{i}e Arrondissement": f"{i}e" for i in range(2, 10)}
ARR_MAP_LYON["1er Arrondissement"] = "1er"

# BAB sous-villes (neighbourhood_group dans pays-basque)
BAB_COMMUNES = {
    "Biarritz": {"code_insee": "64122", "city_slug": "biarritz"},
    "Anglet":   {"code_insee": "64024", "city_slug": "anglet"},
    "Bayonne":  {"code_insee": "64102", "city_slug": "bayonne"},
}

# Centre-commune pour agglos
CENTRE_FILTERS = {
    "bordeaux": {"col": "neighbourhood_group", "values": ["Bordeaux"]},
}

# IRIS filter patterns par ville
IRIS_FILTERS = {
    "paris": "75%",
    "lyon": "6938%",
    "bordeaux": "33063%",
    "pays-basque": ("64102%", "64122%", "64024%"),
}

# 20 -> 5 (260824) : a 20, les IRIS sous le seuil n'etaient PAS emis du tout, donc leur
# infobulle de carte n'avait rien a afficher ("— annonces · — logements"). A 5, ils portent
# leurs valeurs ; c'est la CARTE qui les grise via MIN_OCC_IRIS. Garde-fou deplace au bon
# endroit : le seuil de production n'est pas le seuil d'affichage.
IRIS_MIN_LISTINGS = 5
# Minimum de résidences principales : un IRIS n'entre dans l'analyse que s'il est
# réellement résidentiel. En deçà de 20 RP, les ratios /1 000 RP explosent (division
# par ~0) sur des IRIS non résidentiels — parcs, cimetières, monuments, quartiers
# d'affaires — où le brouillage des coordonnées Inside Airbnb (~150 m) snape des
# annonces (12 IRIS parisiens avaient plus d'annonces que de logements totaux : artefact).
IRIS_MIN_RP = 20

# &e

# &s &LOAD_HELPER - Import helper KPI

_spec = importlib.util.spec_from_file_location("jcn_kpi", BASE / "src" / "jcn-kpi.py")
jcn_kpi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jcn_kpi)

# &e

# &s &LOAD_DATA - Chargement données

print("=" * 60)
print("sp10 — KPI France multi-niveaux (ref/country/city/arr/iris)")
print("=" * 60)

# 1. KPI city importés (Paris, Lyon, Bordeaux — PAS pays-basque car éclaté en 3)
print(f"\nImport kpi_global_by_city ({KPI_CITY_PATH.name})...")
kpi_city_all = pd.read_csv(KPI_CITY_PATH)
kpi_city_fra = kpi_city_all[
    (kpi_city_all["country_code"] == "FRA") &
    (kpi_city_all["city"].isin(["paris", "lyon", "bordeaux"]))
].copy()
kpi_city_fra["level"] = "city"
kpi_city_fra["territory"] = kpi_city_fra["city"]
print(f"  {len(kpi_city_fra)} villes importées: {kpi_city_fra['city'].tolist()}")

# 2. KPI aggregate (refs monde, europe, country FRA)
print(f"\nImport kpi_global_by_aggregate ({KPI_AGG_PATH.name})...")
kpi_agg = pd.read_csv(KPI_AGG_PATH)

ref_monde = kpi_agg[kpi_agg["level"] == "world"].copy()
ref_monde["level"] = "ref_monde"
ref_monde["territory"] = "monde"

ref_europe = kpi_agg[(kpi_agg["level"] == "continent") & (kpi_agg["continent"] == "Europe")].copy()
ref_europe["level"] = "ref_europe"
ref_europe["territory"] = "europe"

ref_fra = kpi_agg[(kpi_agg["level"] == "country") & (kpi_agg["country_code"] == "FRA")].copy()
ref_fra["level"] = "country"
ref_fra["territory"] = "france"

print(f"  Refs importées: monde ({len(ref_monde)}), europe ({len(ref_europe)}), france ({len(ref_fra)})")

# 3. Listings France depuis dblistingfull
print(f"\nChargement {LISTINGFULL_PATH.name}...")
df_raw = pd.read_parquet(LISTINGFULL_PATH)
df_raw = df_raw[df_raw["city"].isin(FRANCE_CITIES)].copy()
print(f"France brut: {len(df_raw):,} lignes, {df_raw['city'].nunique()} villes")

# Flags + cleaning
if "price_eur" not in df_raw.columns:
    df_raw["price_eur"] = df_raw["price"]
jcn_kpi.add_flags(df_raw)
df = jcn_kpi.clean_listings(df_raw)
print(f"France nettoyé: {len(df):,} lignes")

# Arrondissements
df.loc[df["city"] == "paris", "arr"] = df.loc[df["city"] == "paris", "neighbourhood"].map(ARR_MAP_PARIS)
df.loc[df["city"] == "lyon", "arr"] = df.loc[df["city"] == "lyon", "neighbourhood"].map(ARR_MAP_LYON)
df.loc[df["city"] == "pays-basque", "bab_commune"] = df.loc[df["city"] == "pays-basque", "neighbourhood_group"]

# Centre-commune
df_centre = df.copy()
for city_name, filt in CENTRE_FILTERS.items():
    col, vals = filt["col"], filt["values"]
    mask_city = df_centre["city"] == city_name
    mask_centre = df_centre[col].isin(vals)
    n_before = mask_city.sum()
    df_centre = df_centre[~mask_city | (mask_city & mask_centre)]
    n_after = (df_centre["city"] == city_name).sum()
    print(f"Filtre centre {city_name}: {n_before:,} -> {n_after:,}")

# INSEE IRIS
print(f"\nChargement INSEE IRIS ({INSEE_IRIS_PATH.name})...")
insee_iris = pd.read_csv(INSEE_IRIS_PATH, dtype={"code_iris": str, "code_insee": str})
print(f"  {len(insee_iris)} IRIS")

INSEE_COLS = {
    "pop": "pop_2022", "logements": "log_2022", "rp": "rp_2022",
    "res_sec": "rsecocc_2022", "rp_prop": "rp_prop_2022",
    "nper_prop": "nper_rp_prop_2022", "log_vacants": "logvac_2022",
}
insee_agg = insee_iris.groupby("city").agg(
    **{k: (v, "sum") for k, v in INSEE_COLS.items()}
).reset_index()
for c in INSEE_COLS:
    insee_agg[c] = insee_agg[c].round(0)

# INSEE tourisme
insee_tour = pd.read_csv(INSEE_TOUR_PATH)

# &e

# &s &HELPER_INSEE - Fonctions INSEE

def add_insee_cols(kpi_row, insee_sub):
    """Ajoute colonnes INSEE brutes + ratios de densité."""
    totals = {c: insee_sub[c].sum() for c in INSEE_COLS}
    for c, v in totals.items():
        kpi_row[c] = round(v)
    if totals["pop"] > 0:
        jcn_kpi.add_density_ratios(
            kpi_row, pop=totals["pop"], rp=totals["rp"],
            res_sec=totals["res_sec"], housing=totals["logements"],
        )

def add_tourisme(kpi_row, city_name):
    """Ajoute indicateurs tourisme si dispo."""
    tour_city = insee_tour[insee_tour["city"] == city_name]
    if len(tour_city) > 0:
        kpi_row["htch"] = int(tour_city.iloc[0]["htch25"])
        kpi_row["rtuh"] = int(tour_city.iloc[0]["rtuh25"])
        kpi_row["ratio_airbnb_hotel"] = round(kpi_row["vol_n_ann"] / tour_city.iloc[0]["htch25"], 1)

def insee_by_arr(city_name, code_to_arr):
    """Agrège INSEE IRIS → arrondissement."""
    sub = insee_iris[insee_iris["city"] == city_name].copy()
    sub["arr"] = sub["code_insee"].map(code_to_arr)
    return sub.groupby("arr").agg(
        **{k: (v, "sum") for k, v in INSEE_COLS.items()}
    ).reset_index()

# &e

# &s &ENRICH_INSEE - Enrichir villes importées + ref france avec INSEE

print("\n--- Enrichissement INSEE sur villes importées ---")

def enrich_df_insee(df_rows, city_col="city"):
    """Ajoute colonnes INSEE brutes + ratios sur un DataFrame importé (city ou country)."""
    for idx in df_rows.index:
        city_name = df_rows.loc[idx, city_col] if city_col in df_rows.columns else None
        if city_name == "france" or pd.isna(city_name):
            # Agrégat France : somme toutes villes INSEE
            insee_sub = insee_agg
        else:
            insee_sub = insee_agg[insee_agg["city"] == city_name]
        if len(insee_sub) == 0:
            continue
        totals = {c: insee_sub[c].sum() for c in INSEE_COLS}
        for c, v in totals.items():
            df_rows.loc[idx, c] = round(v)
        n_list = df_rows.loc[idx, "vol_n_ann"]
        str_n_entire = df_rows.loc[idx, "str_n_entire"] if "str_n_entire" in df_rows.columns else 0
        if totals["pop"] > 0 and pd.notna(n_list):
            n_list = int(n_list)
            # listings_1000log STANDBY (recalcul cohérent en cours)
            # if totals["logements"] > 0:
            #     df_rows.loc[idx, "listings_1000log"] = round(n_list / totals["logements"] * 1000, 1)
            if totals["rp"] > 0:
                df_rows.loc[idx, "prsf_listings_1000rp"] = round(n_list / totals["rp"] * 1000, 1)
            if totals["rp"] > 0 and totals.get("res_sec", 0) is not None:
                log_occ = totals["rp"] + totals.get("res_sec", 0)
                if log_occ > 0:
                    df_rows.loc[idx, "prsf_listings_1000rps"] = round(n_list / log_occ * 1000, 1)
        city_label = city_name if city_name != "france" else "ALL"
        print(f"  {city_label}: prsf_listings_1000rp={df_rows.loc[idx, 'prsf_listings_1000rp'] if 'prsf_listings_1000rp' in df_rows.columns else '?'}")

# Enrichir Paris/Lyon/Bordeaux (importés de kpi_global)
enrich_df_insee(kpi_city_fra, city_col="city")

# Enrichir ref france (importé de kpi_aggregate)
ref_fra["city"] = "france"
enrich_df_insee(ref_fra, city_col="city")

# Tourisme sur ref france
tour_total = insee_tour[["htch25", "rtuh25"]].sum()
ref_fra["htch"] = int(tour_total["htch25"])
ref_fra["rtuh"] = int(tour_total["rtuh25"])
if tour_total["htch25"] > 0:
    ref_fra["ratio_airbnb_hotel"] = round(ref_fra["vol_n_ann"].iloc[0] / tour_total["htch25"], 1)

# Tourisme sur villes importées
for idx in kpi_city_fra.index:
    city_name = kpi_city_fra.loc[idx, "city"]
    add_tourisme(kpi_city_fra.loc[idx], city_name)

# &e

# &s &KPI_BAB_CITIES - Calcul Biarritz / Bayonne / Anglet (level=city)

print("\n--- Niveau city (BAB détail) ---")
rows_computed = []
df_bab = df_centre[df_centre["city"] == "pays-basque"]

for commune_name, info in BAB_COMMUNES.items():
    df_com = df_bab[df_bab["bab_commune"] == commune_name]
    if len(df_com) == 0:
        print(f"  {commune_name}: SKIP (0 listings)")
        continue
    kpi = jcn_kpi.compute_all_kpi(df_com)
    kpi["level"] = "city"
    kpi["territory"] = info["city_slug"]
    kpi["city"] = info["city_slug"]
    kpi["country_code"] = "FRA"
    kpi["continent"] = "Europe"

    # INSEE
    com_insee = insee_iris[insee_iris["code_insee"] == info["code_insee"]]
    if len(com_insee) > 0:
        com_agg = pd.DataFrame([{c: com_insee[v].sum() for c, v in INSEE_COLS.items()}])
        add_insee_cols(kpi, com_agg)

    rows_computed.append(kpi)
    print(f"  {commune_name}: {kpi['vol_n_ann']} listings, pop={kpi.get('pop', '?')}")

# &e

# &s &KPI_ARR - Niveau arrondissement (Paris 20 + Lyon 9)

print("\n--- Niveau arr ---")

# Paris
df_paris = df[df["city"] == "paris"]
paris_arr_from_code = {f"751{i:02d}": (f"{i}er" if i == 1 else f"{i}e") for i in range(1, 21)}
paris_insee_by_arr = insee_by_arr("paris", paris_arr_from_code)

for arr_label in sorted(ARR_MAP_PARIS.values(), key=lambda x: int(x.replace("er", "").replace("e", ""))):
    df_arr = df_paris[df_paris["arr"] == arr_label]
    if len(df_arr) == 0:
        continue
    kpi = jcn_kpi.compute_all_kpi(df_arr)
    kpi["level"] = "arr"
    kpi["territory"] = f"paris_{arr_label}"
    kpi["city"] = "paris"
    kpi["arr"] = arr_label

    arr_insee = paris_insee_by_arr[paris_insee_by_arr["arr"] == arr_label]
    if len(arr_insee) > 0:
        add_insee_cols(kpi, arr_insee)

    rows_computed.append(kpi)

print(f"  Paris: {len([r for r in rows_computed if r.get('city')=='paris' and r['level']=='arr'])} arrondissements")

# Lyon
df_lyon = df[df["city"] == "lyon"]
lyon_arr_from_code = {f"6938{i}": (f"{i}er" if i == 1 else f"{i}e") for i in range(1, 10)}
lyon_insee_by_arr = insee_by_arr("lyon", lyon_arr_from_code)

for arr_label in sorted(ARR_MAP_LYON.values(), key=lambda x: int(x.replace("er", "").replace("e", ""))):
    df_arr = df_lyon[df_lyon["arr"] == arr_label]
    if len(df_arr) == 0:
        continue
    kpi = jcn_kpi.compute_all_kpi(df_arr)
    kpi["level"] = "arr"
    kpi["territory"] = f"lyon_{arr_label}"
    kpi["city"] = "lyon"
    kpi["arr"] = arr_label

    arr_insee = lyon_insee_by_arr[lyon_insee_by_arr["arr"] == arr_label]
    if len(arr_insee) > 0:
        add_insee_cols(kpi, arr_insee)

    rows_computed.append(kpi)

print(f"  Lyon: {len([r for r in rows_computed if r.get('city')=='lyon' and r['level']=='arr'])} arrondissements")

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

        iris_filter = IRIS_FILTERS.get(city_name)
        if iris_filter is None:
            continue

        if isinstance(iris_filter, tuple):
            conditions = " OR ".join([f"code_iris LIKE '{p}'" for p in iris_filter])
            query = f'SELECT * FROM "{lyr}" WHERE {conditions}'
        else:
            query = f'SELECT * FROM "{lyr}" WHERE code_iris LIKE \'{iris_filter}\''

        try:
            iris_gdf = gpd.read_file(GPKG_PATH, layer=lyr, where=query.split("WHERE ")[1])
        except Exception:
            iris_gdf = gpd.read_file(str(GPKG_PATH), sql=query)

        if iris_gdf.crs and iris_gdf.crs.to_epsg() != 4326:
            iris_gdf = iris_gdf.to_crs(4326)

        pts_gdf = gpd.GeoDataFrame(
            df_city,
            geometry=gpd.points_from_xy(df_city["longitude"], df_city["latitude"]),
            crs=4326,
        )

        joined = gpd.sjoin(pts_gdf, iris_gdf[["code_iris", "nom_iris", "geometry"]], how="left", predicate="within")
        joined_valid = joined[joined["code_iris"].notna()]

        # Taille du portefeuille de l'hote a l'echelle de la VILLE (pas de l'IRIS).
        # Sans ca, compute_all_kpi recompte les annonces par hote DANS l'IRIS : un hote qui
        # gere 5 annonces reparties sur 5 IRIS ressort "mono-annonce" dans chacun. Le biais
        # de fragmentation est massif (Paris : 41,4 % au niveau ville, 14,3 % en mediane
        # d'IRIS) et il varie avec l'etalement des portefeuilles, donc il n'est meme pas
        # constant entre territoires. Colonnes suffixees _ville = definition portee ville.
        joined_valid = joined_valid.assign(
            _host_n_ville=joined_valid.groupby("host_id")["host_id"].transform("size"))

        n_iris = 0
        for code_iris, grp in joined_valid.groupby("code_iris"):
            if len(grp) < IRIS_MIN_LISTINGS:
                continue
            kpi = jcn_kpi.compute_all_kpi(grp)
            for seuil in (1, 5, 10):
                kpi[f"cr_offre_{seuil}plus_ville"] = round(
                    (grp["_host_n_ville"] > seuil).mean() * 100, 1) if seuil == 1 else round(
                    (grp["_host_n_ville"] >= seuil).mean() * 100, 1)
            kpi["level"] = "iris"
            kpi["territory"] = code_iris
            kpi["city"] = city_name
            kpi["code_iris"] = code_iris
            kpi["nom_iris"] = grp["nom_iris"].iloc[0] if "nom_iris" in grp.columns else ""

            if city_name == "paris" and "arr" in grp.columns:
                kpi["arr"] = grp["arr"].iloc[0] if grp["arr"].notna().any() else ""
            elif city_name == "lyon" and "arr" in grp.columns:
                kpi["arr"] = grp["arr"].iloc[0] if grp["arr"].notna().any() else ""
            elif city_name == "pays-basque" and "bab_commune" in grp.columns:
                kpi["arr"] = grp["bab_commune"].iloc[0] if grp["bab_commune"].notna().any() else ""

            # INSEE IRIS
            iris_insee = insee_iris[insee_iris["code_iris"] == code_iris]
            if len(iris_insee) > 0:
                row_i = iris_insee.iloc[0]
                kpi["pop"] = round(row_i["pop_2022"])
                kpi["rp"] = round(row_i["rp_2022"])
                kpi["res_sec"] = round(row_i["rsecocc_2022"])
                kpi["logements"] = round(row_i["log_2022"])
                kpi["rp_prop"] = round(row_i["rp_prop_2022"])
                kpi["nper_prop"] = round(row_i["nper_rp_prop_2022"])
                kpi["log_vacants"] = round(row_i["logvac_2022"])
                if row_i["pop_2022"] > 0:
                    jcn_kpi.add_density_ratios(
                        kpi, pop=row_i["pop_2022"], rp=row_i["rp_2022"],
                        res_sec=row_i["rsecocc_2022"], housing=row_i["log_2022"],
                    )

            # IRIS non résidentiel (rp < seuil, ou hors INSEE) : ratios /1 000 RP non
            # fiables -> exclu de l'analyse IRIS. get(...,0) exclut aussi les IRIS sans match.
            if kpi.get("rp", 0) < IRIS_MIN_RP:
                continue
            rows_computed.append(kpi)
            n_iris += 1

        n_matched = len(joined_valid)
        n_total = len(df_city)
        print(f"  {city_name}: {n_iris} IRIS (>= {IRIS_MIN_LISTINGS}), "
              f"{n_matched}/{n_total} matchés ({n_matched/n_total*100:.0f}%)")

# &e

# &s &EXPORT - Assemblage + export CSV

print("\n--- Assemblage ---")

# Convertir rows calculés en DataFrame
df_computed = pd.DataFrame(rows_computed)

# Pression zone dense des communes basques : sp08 la calcule bien (scope=sub_city dans
# kpi_global_by_city) mais sp10 recalculait ces 3 lignes localement, sans le denominateur
# GHS-POP -> colonne vide. On la recupere au lieu de laisser un "—" dans le rapport.
_DENSE_COLS = ["ctx_pop_dense", "ctx_pop_dense_total", "prs_listings_1000hab_dense",
               "ctx_densite_pop_dense", "n_listings_dense"]
_sub = kpi_city_all[kpi_city_all.get("scope", "") == "sub_city"]
if len(_sub) and len(df_computed):
    _cols = [c for c in _DENSE_COLS if c in _sub.columns]
    _src = _sub.set_index("city")[_cols]
    for i in df_computed.index:
        terr = df_computed.loc[i, "territory"]
        if df_computed.loc[i, "level"] == "city" and terr in _src.index:
            for c in _cols:
                df_computed.loc[i, c] = _src.loc[terr, c]
    print(f"  Pression dense récupérée (sp08 sub_city) pour : "
          f"{[t for t in df_computed.territory if t in _src.index]}")

# Empiler : refs (monde/europe/france) + cities importées + computed
frames = [ref_monde, ref_europe, ref_fra, kpi_city_fra, df_computed]
result = pd.concat([f for f in frames if len(f) > 0], ignore_index=True)

# Ordre des niveaux
level_order = {"ref_monde": 0, "ref_europe": 1, "country": 2, "city": 3, "arr": 4, "iris": 5}
result["_sort"] = result["level"].map(level_order).fillna(9)
result = result.sort_values(["_sort", "city", "territory"]).drop(columns="_sort")

# &s &EVOLUTION_PREV - Evolution vs snapshot precedent, a TOUS les niveaux (dont IRIS)
# sp12 ne descend pas sous la ville : les colonnes _vevol_ etaient donc vides a l'IRIS et a
# l'arrondissement. Or sp10 produit un CSV par snapshot avec le MEME code, donc la definition
# d'annonce active est identique de part et d'autre : il suffit d'apparier sur (level, territory).
# Fait ICI plutot que cote R pour que le CSV *et* les JSON dashboard portent la colonne.
PREV_TAG = {"2606": "2506", "2506": "2412"}.get(SNAP_TAG)
PREV_PATH = INTERIM_DIR / f"kpi_france_byterr_{PREV_TAG}.csv" if PREV_TAG else None
EVOL_COLS = ["vol_n_ann", "vol_n_hotes"]          # volumes uniquement : le PRIX n'est PAS
# comparable entre 2025 et 2026 (Inside Airbnb a bascule `price` de base -> total, frais inclus).
if PREV_PATH is not None and PREV_PATH.exists():
    prev = pd.read_csv(PREV_PATH, dtype={"code_iris": str})
    keep = ["level", "territory"] + [c for c in EVOL_COLS if c in prev.columns]
    prev = prev[keep].rename(columns={c: f"{c}_prev" for c in EVOL_COLS if c in prev.columns})
    result = result.merge(prev, on=["level", "territory"], how="left")
    n_ok = 0
    for c in EVOL_COLS:
        pc = f"{c}_prev"
        if c in result.columns and pc in result.columns:
            base = pd.to_numeric(result[pc], errors="coerce")
            cur = pd.to_numeric(result[c], errors="coerce")
            result[f"{c}_{PREV_TAG[:2]}"] = base
            result[f"{c}_vevol_{PREV_TAG[:2]}{SNAP_TAG[:2]}"] = (
                (cur / base.where(base > 0) - 1) * 100).round(1)
            n_ok = int(result[f"{c}_vevol_{PREV_TAG[:2]}{SNAP_TAG[:2]}"].notna().sum())
    result = result.drop(columns=[f"{c}_prev" for c in EVOL_COLS if f"{c}_prev" in result.columns])
    print(f"Evolution vs {PREV_TAG}: {n_ok} territoires appariés, "
          f"dont {int(result['level'].eq('iris').sum())} IRIS")
else:
    print(f"[SKIP] Evolution : snapshot précédent introuvable ({PREV_PATH})")
# &e

result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

# Résumé
print(f"\nExport: {OUTPUT_PATH.name}")
print(f"  {len(result)} lignes, {len(result.columns)} colonnes")
for lvl in ["ref_monde", "ref_europe", "country", "city", "arr", "iris"]:
    n = len(result[result["level"] == lvl])
    if n > 0:
        cities = result[result["level"] == lvl]["territory"].tolist()
        if n <= 6:
            print(f"  - {lvl}: {n} ({', '.join(str(c) for c in cities)})")
        else:
            print(f"  - {lvl}: {n} territoires")

print(f"\n{'='*60}")
print("sp10 terminé.")
print(f"{'='*60}")

# &s &EXPORT_DASHBOARD_JSON - Export JSON pour dashboard Observable France
# NB: level=city → kpi_fr_city.json (namespacé) pour NE PAS écraser kpi_city.json (= world by-city,
#     écrit par sp11). Voir chantier "JSON dashboard 2606" : sp11 = exporteur unique, sp10 non-colisionnant.
DASH_DIR = BASE / "dashboard" / "src" / "data"
if DASH_DIR.exists():
    # Split by level
    for lvl in ["ref_monde", "ref_europe", "country", "city", "arr", "iris"]:
        sub = result[result["level"] == lvl].copy()
        # Fix code_iris: float→string
        if "code_iris" in sub.columns:
            sub["code_iris"] = sub["code_iris"].apply(lambda x: str(int(x)) if pd.notna(x) else None)
        out_name = "kpi_fr_city.json" if lvl == "city" else f"kpi_{lvl}.json"
        sub.to_json(DASH_DIR / out_name, orient="records", force_ascii=False)

    print(f"\nDashboard JSON: {DASH_DIR}")
    for lvl in ["ref_monde", "ref_europe", "country", "city", "arr", "iris"]:
        n = len(result[result["level"] == lvl])
        tag = " → kpi_fr_city.json" if lvl == "city" else ""
        print(f"  kpi_{lvl}.json ({n} lignes){tag}")
else:
    print(f"\n[SKIP] Dashboard dir not found: {DASH_DIR}")
# &e

# &e

# &e
