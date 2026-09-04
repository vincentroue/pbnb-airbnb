#!/usr/bin/env python3
"""
sp11 — Export JSON dashboard Observable (EXPORTEUR UNIQUE)
Produit TOUS les fichiers JSON pour dashboard/src/data/ depuis les données pipeline.
Paramétré --snapshot (défaut 26-06) comme sp07b/sp08/sp12.

Inputs (millésime SNAP_TAG, ex 2606):
  - data/interim/kpi_global_by_city_{SNAP}.csv       (KPI villes monde + scope + évol)
  - data/interim/kpi_global_by_aggregate_{SNAP}.csv  (KPI agrégats monde/continent/pays)
  - data/interim/kpi_france_byterr_{SNAP}.csv         (KPI France multi-niveaux + évol)
  - data/interim/dblistingfull_{SNAP}_cons_global.parquet (listings nettoyés → quartiers)
  - data/external/city-reference-airbnb-260217.csv    (coords villes)
  - reports/helpers/ddict-airbnb.json                 (dictionnaire → copié dans dashboard)

Outputs (dashboard/src/data/):
  - kpi_city.json        world by-city (scope city|sub_city + évol) ← dash-france cellules FR
  - kpi_city_geo.json    world by-city + coords lat/lon             ← carte/table/scatter monde
  - kpi_agg.json         agrégats monde/continent/continent_detail/pays
  - kpi_neighbourhood.json  ~4200 quartiers × KPI (noms colonnes 2606)
  - kpi_fr_city.json     France byterr level=city (namespacé, PAS de collision avec kpi_city)
  - kpi_country/arr/iris/ref_europe/ref_monde.json  France byterr autres niveaux
  - ddict-airbnb.json    copie du dictionnaire à jour

Résout la COLLISION historique : sp08 (world) et sp11 (France) écrivaient tous deux
kpi_city.json. Désormais France level=city → kpi_fr_city.json ; kpi_city.json = world only.

Usage: python scripts/sp11-export-dashboard-json-260501.py --snapshot 26-06
"""

# &s &SETUP
import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

# Console Windows : forcer UTF-8 (flèches/accents dans les prints)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent.parent
INTERIM = BASE / "data" / "interim"
DASH_DIR = BASE / "dashboard" / "src" / "data"

parser = argparse.ArgumentParser(description="Export JSON dashboard Observable")
parser.add_argument("--snapshot", default="26-06",
                    help="Millésime snapshot (défaut 26-06 → SNAP_TAG 2606)")
args = parser.parse_args()
SNAP_TAG = args.snapshot.replace("-", "")   # "26-06" → "2606"

if not DASH_DIR.exists():
    print(f"[SKIP] Dashboard dir not found: {DASH_DIR}")
    sys.exit(0)

print(f"sp11 — Export dashboard JSON (snapshot {args.snapshot} → tag {SNAP_TAG}) → {DASH_DIR}")


def write_json(df, name):
    """Écrit un DataFrame en JSON records UTF-8 (pas de whitelist : toutes colonnes gardées)."""
    (DASH_DIR / name).write_text(
        df.to_json(orient="records", force_ascii=False), encoding="utf-8"
    )
# &e

# &s &WORLD_KPI - Export KPI villes monde + agrégats (from kpi_global_by_city/aggregate)
REF_CSV = BASE / "data" / "external" / "city-reference-airbnb-260222.csv"
city_csv = INTERIM / f"kpi_global_by_city_{SNAP_TAG}.csv"
agg_csv = INTERIM / f"kpi_global_by_aggregate_{SNAP_TAG}.csv"

city_kpi = pd.read_csv(city_csv)
agg_kpi = pd.read_csv(agg_csv)
ref = pd.read_csv(REF_CSV)

# kpi_city.json = world by-city TEL QUEL (garde scope + toutes colonnes évol)
write_json(city_kpi, "kpi_city.json")

# kpi_city_geo.json = world by-city + coords (pour la carte / scatter)
coords = ref[["city", "lat", "lon"]].dropna()
city_geo = city_kpi.merge(coords, on="city", how="left")
write_json(city_geo, "kpi_city_geo.json")

write_json(agg_kpi, "kpi_agg.json")

_paris = city_kpi[city_kpi["city"] == "paris"]
_pv = _paris.iloc[0]["vol_n_ann"] if len(_paris) else "?"
print(f"  kpi_city.json:     {len(city_kpi)} villes (scope) · Paris vol_n_ann={_pv}")
print(f"  kpi_city_geo.json: {len(city_geo)} villes + coords")
print(f"  kpi_agg.json:      {len(agg_kpi)} agrégats")
# &e

# &s &NEIGHBOURHOOD_KPI - Agrégation par quartier (noms colonnes 2606)
LISTING_PQ = INTERIM / f"dblistingfull_{SNAP_TAG}_cons_global.parquet"

df = pd.read_parquet(LISTING_PQ, columns=[
    "city", "neighbourhood", "neighbourhood_group",
    "latitude", "longitude", "price_eur", "room_type",
    "minimum_nights", "availability_365",
    "number_of_reviews", "reviews_per_month",
    "calculated_host_listings_count"
])

# Cleaning (mêmes critères que sp08)
df = df[
    (df["price_eur"].notna()) & (df["price_eur"] > 0) &
    (df["availability_365"] > 0) &
    (df["room_type"] != "Hotel room") &
    (df["price_eur"] >= 10) & (df["price_eur"] <= 2000)
]

print(f"  Listings clean: {len(df):,}")


def agg_nbh(grp):
    n = len(grp)
    entire = grp[grp["room_type"] == "Entire home/apt"]
    multi = grp[grp["calculated_host_listings_count"] > 1]
    # Noms de colonnes = convention 2606 (vol_n_ann, px_*, str_*, cr_*, act_*, actrv_*)
    return pd.Series({
        "vol_n_ann": n,
        "vol_n_hotes": grp["calculated_host_listings_count"].nunique(),
        "px_med": round(grp["price_eur"].median(), 0),
        "px_entire_med": round(entire["price_eur"].median(), 0) if len(entire) > 0 else None,
        "str_entire_pct": round(len(entire) / n * 100, 1),
        "cr_offre_1plus": round(len(multi) / n * 100, 1),
        "str_minnuits30_pct": round((grp["minimum_nights"] >= 30).mean() * 100, 1),
        "act_cal_ouvert_med": round(grp["availability_365"].median(), 0),
        "actrv_avis": round(grp["number_of_reviews"].median(), 0),
        "actrv_avis_mois": round(grp["reviews_per_month"].median(), 1)
            if grp["reviews_per_month"].notna().any() else None,
        "lat": round(grp["latitude"].median(), 4),
        "lon": round(grp["longitude"].median(), 4),
    })


nbh_kpi = df.groupby(["city", "neighbourhood"]).apply(agg_nbh).reset_index()
write_json(nbh_kpi, "kpi_neighbourhood.json")
print(f"  kpi_neighbourhood.json: {len(nbh_kpi)} quartiers, {nbh_kpi['city'].nunique()} villes (cols 2606)")
# &e

# &s &FRANCE_LEVELS - KPI France split par level (level=city → kpi_fr_city, PAS kpi_city)
fr_csv = INTERIM / f"kpi_france_byterr_{SNAP_TAG}.csv"
if fr_csv.exists():
    kpi_fr = pd.read_csv(fr_csv)
    for lvl in ["ref_monde", "ref_europe", "country", "city", "arr", "iris"]:
        sub = kpi_fr[kpi_fr["level"] == lvl].copy()
        if "code_iris" in sub.columns:
            sub["code_iris"] = sub["code_iris"].apply(
                lambda x: str(int(x)) if pd.notna(x) else None
            )
        # level=city → namespace kpi_fr_city.json pour NE PAS écraser le world kpi_city.json
        out_name = "kpi_fr_city.json" if lvl == "city" else f"kpi_{lvl}.json"
        write_json(sub, out_name)
    print("  France levels: " + ", ".join(
        f"{lvl}({len(kpi_fr[kpi_fr.level == lvl])})"
        for lvl in ["country", "city", "arr", "iris"]
    ) + "  [city → kpi_fr_city.json]")
else:
    print(f"  [WARN] France byterr introuvable: {fr_csv}")
# &e

# &s &DDICT - Copie du dictionnaire indicateurs à jour
ddict_src = BASE / "reports" / "helpers" / "ddict-airbnb.json"
if ddict_src.exists():
    shutil.copyfile(ddict_src, DASH_DIR / "ddict-airbnb.json")
    print(f"  ddict-airbnb.json: copié depuis {ddict_src.relative_to(BASE)}")
# &e

print("\nDone.")
