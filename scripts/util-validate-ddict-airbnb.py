# &s &VALIDATE_DDICT_aaMAIN - Valide ddict-airbnb.json vs CSV réels

# Croise le dictionnaire d'indicateurs (JSON) avec les colonnes
# réellement présentes dans les CSV KPI (sum + gz). Produit un rapport
# de validation (CSV) pour identifier écarts et indicateurs planifiés.
#
# Usage:
#   python scripts/util-validate-ddict-airbnb.py
#   python scripts/util-validate-ddict-airbnb.py --csv data/interim/kpi_global_by_city_2506.csv
#
# Output:
#   reports/helpers/ddict-validation-airbnb.csv
#
# Date: 2026-02-18

import json
import pandas as pd
from pathlib import Path
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
DDICT_PATH = BASE / "reports" / "helpers" / "ddict-airbnb.json"
DEFAULT_CSV = BASE / "data" / "interim" / "kpi_global_by_city_2506.csv"
OUTPUT_PATH = BASE / "reports" / "helpers" / "ddict-validation-airbnb.csv"

# CLI: --csv override
csv_path = DEFAULT_CSV
for i, arg in enumerate(sys.argv):
    if arg == "--csv" and i + 1 < len(sys.argv):
        csv_path = Path(sys.argv[i + 1])
# &e

# &s &PARSE_DDICT
print(f">>> Lecture ddict: {DDICT_PATH.name}")
with open(DDICT_PATH, "r", encoding="utf-8") as f:
    ddict = json.load(f)

indicators = ddict.get("indicators", {})
themes = ddict.get("themes", {})
meta_columns = ddict.get("meta_columns", {})

# Filtrer les _comment entries
indic_keys = [k for k in indicators if not k.startswith("_")]
print(f"    {len(indic_keys)} indicateurs dans ddict.json")
print(f"    {len(themes)} thèmes définis")

# Construire dataframe des indicateurs
rows = []
# Mapping csv_col -> ddict_name (pour croiser les noms divergents)
csv_col_to_ddict = {}
for key in indic_keys:
    ind = indicators[key]
    csv_col = ind.get("csv_col", "")
    if csv_col:
        csv_col_to_ddict[csv_col] = key
    rows.append({
        "variable": key,
        "csv_col": csv_col,
        "theme": ind.get("theme", ""),
        "short": ind.get("short", ""),
        "medium": ind.get("medium", ""),
        "long": ind.get("long", ""),
        "label": ind.get("label", ""),
        "type": ind.get("type", ""),
        "unit": ind.get("unit", ""),
        "polarity": ind.get("polarity", 0),
        "order": ind.get("order", 99),
        "status_ddict": ind.get("status", ""),
        "source": ind.get("source", ""),
        "gz_col": ind.get("gz_col", ""),
        "formula": ind.get("formula", ""),
        "description": ind.get("description", ""),
    })

df_ddict = pd.DataFrame(rows)
# &e

# &s &LOAD_CSV
print(f">>> Lecture CSV sum: {csv_path.name}")
if csv_path.exists():
    df_csv = pd.read_csv(csv_path, nrows=1)
    csv_cols = list(df_csv.columns)
    print(f"    {len(csv_cols)} colonnes dans CSV")
else:
    print(f"    ⚠ CSV non trouvé: {csv_path}")
    csv_cols = []

# CSV gz (kpi_gz_*_by_city_*.csv)
GZ_CSV = BASE / "data" / "interim" / "kpi_gz_global_by_city_2506.csv"
gz_cols = []
if GZ_CSV.exists():
    df_gz = pd.read_csv(GZ_CSV, nrows=1)
    gz_cols = list(df_gz.columns)
    print(f">>> Lecture CSV gz: {GZ_CSV.name} ({len(gz_cols)} colonnes)")

# Séparer méta vs indicateurs dans le CSV
meta_keys = set(meta_columns.keys()) if meta_columns else set()
csv_indic_cols = [c for c in csv_cols if c not in meta_keys and not c.startswith("_")]
csv_meta_cols = [c for c in csv_cols if c in meta_keys]
print(f"    {len(csv_meta_cols)} colonnes méta, {len(csv_indic_cols)} colonnes indicateurs")

# Construire reverse map : csv_col alias → ddict key (depuis le ddict lui-même)
# Pour les indicateurs dont csv_col != key (ex: review_rating → rev_rating_med)
gz_indic_cols = [c for c in gz_cols if c not in meta_keys and not c.startswith("_")]
# Map gz col names to ddict keys via csv_col_to_ddict
gz_ddict_cols = set()
for c in gz_indic_cols:
    if c in csv_col_to_ddict:
        gz_ddict_cols.add(csv_col_to_ddict[c])
    else:
        gz_ddict_cols.add(c)
if gz_cols:
    print(f"    {len(gz_ddict_cols)} indicateurs gz mappés")
# &e

# &s &CROSS_VALIDATION
print(">>> Croisement ddict × CSV...")

ddict_vars = set(df_ddict["variable"])
csv_vars = set(csv_indic_cols)
# csv_col aliases: colonnes CSV qui correspondent a un indicateur ddict via csv_col
csv_col_aliases = set(csv_col_to_ddict.keys())
all_available = csv_vars | gz_ddict_cols

# Variables ddict presentes dans CSV (directement ou via csv_col)
in_both = (ddict_vars & csv_vars) | {csv_col_to_ddict[c] for c in csv_col_aliases if c in csv_vars}
in_gz = ddict_vars & gz_ddict_cols - csv_vars - in_both
in_ddict_only = ddict_vars - in_both - in_gz
# CSV_ONLY: colonnes CSV non documentees (ni directement ni via csv_col)
in_csv_only = csv_vars - ddict_vars - csv_col_aliases

# Statut croise
def cross_status(row):
    var = row["variable"]
    csv_col = row.get("csv_col", "")
    ddict_status = row["status_ddict"]
    if var in csv_vars or (csv_col and csv_col in csv_vars):
        return "OK"
    elif var in gz_ddict_cols:
        return "OK_GZ"
    elif ddict_status == "planned":
        return "PLANNED"
    elif var in in_ddict_only:
        return "DDICT_ONLY"
    else:
        return "UNKNOWN"

df_ddict["status_csv"] = df_ddict.apply(cross_status, axis=1)

# Colonnes gz non documentées (pas dans ddict, pas dans sum)
in_gz_only = gz_ddict_cols - ddict_vars - csv_col_aliases if gz_cols else set()

# Ajouter colonnes CSV (sum + gz) non documentées
all_csv_only = in_csv_only | in_gz_only
if all_csv_only:
    extra_rows = []
    for col in sorted(all_csv_only):
        src = "sum" if col in in_csv_only else "gz"
        extra_rows.append({
            "variable": col,
            "csv_col": "",
            "theme": "?",
            "short": "",
            "medium": "[Non documenté]",
            "long": "",
            "label": "[Non documenté]",
            "type": "",
            "unit": "",
            "polarity": 0,
            "order": 99,
            "status_ddict": "missing",
            "source": src,
            "gz_col": "",
            "formula": "",
            "description": f"Présent dans CSV {src} mais absent du ddict.json",
            "status_csv": "CSV_ONLY",
        })
    df_extra = pd.DataFrame(extra_rows)
    df_ddict = pd.concat([df_ddict, df_extra], ignore_index=True)

# Tri par thème puis order
theme_order = list(themes.keys()) + ["?"]
df_ddict["theme_rank"] = df_ddict["theme"].map(
    {t: i for i, t in enumerate(theme_order)}
).fillna(99).astype(int)
df_ddict = df_ddict.sort_values(["theme_rank", "order", "variable"]).drop(columns=["theme_rank"])
# &e

# &s &EXPORT
print(f">>> Export: {OUTPUT_PATH.name}")
df_ddict.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

# Résumé
print(f"\n{'='*60}")
print(f"RÉSUMÉ VALIDATION ddict-airbnb.json")
print(f"{'='*60}")
print(f"  Indicateurs ddict:  {len(indic_keys)}")
print(f"  Colonnes CSV sum:   {len(csv_indic_cols)}")
if gz_cols:
    print(f"  Colonnes CSV gz:    {len(gz_ddict_cols)}")
print()

status_counts = df_ddict["status_csv"].value_counts()
for status in ["OK", "OK_GZ", "PLANNED", "DDICT_ONLY", "CSV_ONLY"]:
    n = status_counts.get(status, 0)
    if n > 0:
        print(f"  {status:15s}: {n:3d}")

print()
# Détail par thème (themes v4 = dict d'objets {label, order})
print("Par thème:")
for theme_code, theme_obj in themes.items():
    theme_label = theme_obj.get("label", theme_code) if isinstance(theme_obj, dict) else str(theme_obj)
    mask = df_ddict["theme"] == theme_code
    n_ok = ((df_ddict[mask]["status_csv"].isin(["OK", "OK_GZ"]))).sum()
    n_planned = ((df_ddict[mask]["status_csv"] == "PLANNED")).sum()
    n_total = mask.sum()
    if n_total > 0:
        status_str = f"{n_ok} ok"
        if n_planned > 0:
            status_str += f", {n_planned} planned"
        print(f"  {theme_code:6s} {theme_label[:40]:40s} {status_str}")

# CSV_ONLY
csv_only = df_ddict[df_ddict["status_csv"] == "CSV_ONLY"]
if len(csv_only) > 0:
    print(f"\n[WARN] Non documentées ({len(csv_only)}):")
    for _, row in csv_only.iterrows():
        src = row.get("source", "?")
        print(f"  - {row['variable']} ({src})")

# DDICT_ONLY (dans ddict mais pas dans les CSV)
ddict_only = df_ddict[df_ddict["status_csv"] == "DDICT_ONLY"]
if len(ddict_only) > 0:
    print(f"\n[INFO] Dans ddict mais pas dans CSV ({len(ddict_only)}):")
    for _, row in ddict_only.iterrows():
        print(f"  - {row['variable']} (source={row.get('source', '?')})")

print(f"\nOutput: {OUTPUT_PATH}")
# &e

# &e
