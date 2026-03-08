# &s &AUDIT_GEO_SCOPE_aaMAIN - Audit périmètre géographique Inside Airbnb vs population

# Détecte les villes dont les listings Inside Airbnb couvrent un
# périmètre plus large (agglomération, province) que la population
# de référence (commune). Produit un CSV d'audit et un résumé console.
#
# Usage:
#   python scripts/util-audit-geo-scope-260221.py
#
# Output:
#   data/interim/audit_geo_scope_2506.csv
#   reports/helpers/geo-scope-audit-summary.csv
#
# Date: 2026-02-21

import pandas as pd
import numpy as np
import math
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
RAW_DIR = BASE / "data" / "raw" / "zudb-inside-airbnbbnb"
KPI_CSV = BASE / "data" / "interim" / "kpi_global_by_city_2506.csv"
REF_CSV = BASE / "data" / "external" / "city-reference-airbnb-260217.csv"
OUTPUT_DETAIL = BASE / "data" / "interim" / "audit_geo_scope_2506.csv"
OUTPUT_SUMMARY = BASE / "reports" / "helpers" / "geo-scope-audit-summary.csv"

# Classification manuelle vérifiée (2026-02-21)
# Clé = slug ville, valeur = dict {type, centre_group, pop_correct, hsg_correct, note}
#
# type:
#   "agglo"   = listings couvrent agglomération, pop = commune → BIAIS
#   "aligned" = listings couvrent agglo mais pop = agglo → OK
#   "intra"   = groups = districts internes de la commune → OK
#   "ok"      = pas de groups multiples → OK
SCOPE_OVERRIDES = {
    # BIAIS CONFIRMÉ
    "bordeaux": {
        "type": "agglo", "centre_group": "Bordeaux",
        "pop_correct": 820_000, "hsg_correct": 432_000,
        "note": "28 communes Bordeaux Métropole. Pop commune = 260K, métropole = 820K."
    },
    "lisbon": {
        "type": "agglo", "centre_group": "Lisboa",
        "pop_correct": 2_870_000, "hsg_correct": 1_350_000,
        "note": "16 communes AML (Área Metropolitana de Lisboa). Pop commune = 545K."
    },
    "porto": {
        "type": "agglo", "centre_group": "PORTO",
        "pop_correct": 1_740_000, "hsg_correct": 780_000,
        "note": "17 communes AMP (Área Metropolitana do Porto). Pop commune = 232K."
    },
    "bergamo": {
        "type": "agglo", "centre_group": "Bergamo",
        "pop_correct": 1_120_000, "hsg_correct": 500_000,
        "note": "~197 communes de la Province de Bergame. Pop commune = 122K."
    },
    "los-angeles": {
        "type": "agglo", "centre_group": "City of Los Angeles",
        "pop_correct": 5_500_000, "hsg_correct": 2_100_000,
        "note": "City + Other Cities + Unincorporated Areas. Pop city = 3.82M."
    },
    # DÉJÀ ALIGNÉ
    "greater-manchester": {
        "type": "aligned", "centre_group": "Manchester",
        "note": "10 boroughs. Pop = 2.87M = Greater Manchester (ONS Census 2021)."
    },
    "victoria": {
        "type": "aligned", "centre_group": "Victoria",
        "note": "16 municipalities CRD. Pop = 420K = CMA StatCan."
    },
    "new-york-city": {
        "type": "intra", "centre_group": None,
        "note": "5 boroughs = NYC proper. Pop = 8.48M = ville."
    },
    # DISTRICTS INTERNES
    "madrid": {"type": "intra", "centre_group": None, "note": "21 distritos municipaux."},
    "barcelona": {"type": "intra", "centre_group": None, "note": "10 districtes municipaux."},
    "berlin": {"type": "intra", "centre_group": None, "note": "12 Bezirke (ville-État)."},
    "valencia": {"type": "intra", "centre_group": None, "note": "19 distritos municipaux."},
    "sevilla": {"type": "intra", "centre_group": None, "note": "11 distritos municipaux."},
    "zurich": {"type": "intra", "centre_group": None, "note": "12 Kreise."},
    "venice": {"type": "intra", "centre_group": None, "note": "2 zones (Isole + Terraferma), Comune di Venezia."},
    "seattle": {"type": "intra", "centre_group": None, "note": "17 neighbourhoods internes."},
    "singapore": {"type": "intra", "centre_group": None, "note": "5 régions."},
}
# &e

# &s &LOAD_DATA
print(">>> Chargement données...")
df_kpi = pd.read_csv(KPI_CSV)
df_ref = pd.read_csv(REF_CSV)
kpi_cities = list(df_kpi["city"].values)
print(f"    {len(kpi_cities)} villes dans le KPI")
# &e

# &s &SCAN_CITIES - Scan systématique de toutes les villes
print(">>> Scan des neighbourhood_groups...")
results = []

for city in kpi_cities:
    kpi = df_kpi[df_kpi["city"] == city].iloc[0]
    ref = df_ref[df_ref["city"] == city]
    ref_row = ref.iloc[0] if len(ref) > 0 else None

    # Trouver le sumlistings juin 2025
    matches = list(RAW_DIR.rglob(f"25-06-*-{city}_sumlistings.csv"))
    matches += list((BASE / "data" / "raw").glob(f"25-06-*-{city}_sumlistings.csv"))

    # Données de base
    row = {
        "city": city,
        "city_fr": kpi.get("city_fr", city),
        "country_code": kpi["country_code"],
        "continent": kpi["continent"],
        "pop": kpi["pop"],
        "housing": kpi.get("housing", np.nan),
        "n_listings": kpi["n_listings"],
        "l_1000hab": kpi["listings_1000hab"],
        "l_1000hsg": kpi.get("listings_1000hsg", np.nan),
        "pop_source": ref_row["pop_source"] if ref_row is not None else "",
    }

    if not matches:
        row.update({
            "n_groups": 0, "n_brut": 0, "n_centre": 0, "pct_centre": 100.0,
            "spread_km": 0, "scope_type": "ok", "scope_note": "Pas de fichier sumlistings",
        })
        results.append(row)
        continue

    try:
        df = pd.read_csv(matches[0])
    except Exception as e:
        row.update({
            "n_groups": -1, "n_brut": 0, "n_centre": 0, "pct_centre": 100.0,
            "spread_km": 0, "scope_type": "error", "scope_note": f"Erreur lecture: {e}",
        })
        results.append(row)
        continue

    n_brut = len(df)

    # Neighbourhood groups
    has_groups = "neighbourhood_group" in df.columns
    if has_groups:
        grps = df["neighbourhood_group"].dropna().unique()
        n_groups = len(grps)
    else:
        n_groups = 0

    # Spread géographique (km)
    spread_km = 0
    if "latitude" in df.columns and "longitude" in df.columns:
        lat_range = df["latitude"].max() - df["latitude"].min()
        lon_range = df["longitude"].max() - df["longitude"].min()
        lat_km = lat_range * 111.0
        lon_km = lon_range * 111.0 * math.cos(math.radians(df["latitude"].mean()))
        spread_km = round(max(lat_km, lon_km), 1)

    # Classification
    override = SCOPE_OVERRIDES.get(city)
    if override:
        scope_type = override["type"]
        scope_note = override["note"]
        centre_group = override.get("centre_group")

        if centre_group and has_groups and n_groups > 0:
            n_centre = len(df[df["neighbourhood_group"] == centre_group])
        elif centre_group and "neighbourhood" in df.columns:
            n_centre = len(df[df["neighbourhood"] == centre_group])
        else:
            n_centre = n_brut

        pct_centre = n_centre / n_brut * 100 if n_brut > 0 else 100

        # Ratios corrigés pour les agglos
        if scope_type == "agglo":
            pop_correct = override.get("pop_correct", kpi["pop"])
            hsg_correct = override.get("hsg_correct")
            clean_ratio = kpi["n_listings"] / n_brut if n_brut > 0 else 1
            n_centre_clean = int(n_centre * clean_ratio)
            l_1000hab_commune = round(n_centre_clean / kpi["pop"] * 1000, 1) if kpi["pop"] > 0 else 0
            l_1000hab_metro = round(kpi["n_listings"] / pop_correct * 1000, 1)
            bias_factor = round(pop_correct / kpi["pop"], 1) if kpi["pop"] > 0 else 1
            row["pop_correct"] = pop_correct
            row["hsg_correct"] = hsg_correct
            row["l_1000hab_commune"] = l_1000hab_commune
            row["l_1000hab_metro"] = l_1000hab_metro
            row["bias_factor"] = bias_factor
    else:
        scope_type = "ok"
        scope_note = ""
        n_centre = n_brut
        pct_centre = 100.0

    row.update({
        "n_groups": n_groups,
        "n_brut": n_brut,
        "n_centre": n_centre,
        "pct_centre": round(pct_centre, 1),
        "spread_km": spread_km,
        "scope_type": scope_type,
        "scope_note": scope_note,
    })
    results.append(row)

df_audit = pd.DataFrame(results)
# &e

# &s &EXPORT
# Export détaillé
df_audit.to_csv(OUTPUT_DETAIL, index=False, encoding="utf-8-sig")
print(f">>> Export détaillé: {OUTPUT_DETAIL.name}")

# Export résumé (uniquement les villes avec biais ou classification spéciale)
df_summary = df_audit[df_audit["scope_type"] != "ok"].copy()
df_summary = df_summary.sort_values(["scope_type", "pct_centre"])
df_summary.to_csv(OUTPUT_SUMMARY, index=False, encoding="utf-8-sig")
print(f">>> Export résumé: {OUTPUT_SUMMARY.name}")
# &e

# &s &REPORT
print()
print("=" * 90)
print("AUDIT PÉRIMÈTRE GÉOGRAPHIQUE — Inside Airbnb vs Population")
print("=" * 90)

# Résumé par type
type_counts = df_audit["scope_type"].value_counts()
print(f"\nClassification ({len(df_audit)} villes):")
for t in ["agglo", "aligned", "intra", "ok"]:
    n = type_counts.get(t, 0)
    labels = {"agglo": "⚠️  Biais confirmé", "aligned": "✅ Déjà aligné",
              "intra": "✅ Districts internes", "ok": "✅ Sans groups"}
    print(f"  {labels.get(t, t):30s}: {n:3d} villes")

# Détail biais
agglo = df_audit[df_audit["scope_type"] == "agglo"].sort_values("bias_factor")
if len(agglo) > 0:
    print(f"\n{'─'*90}")
    print(f"BIAIS CONFIRMÉ — {len(agglo)} villes")
    print(f"{'─'*90}")
    print(f"{'Ville':20s} {'Pop act.':>9s} {'Pop corr.':>10s} {'×biais':>7s} {'L/1Kh':>6s} {'L/1Kh*':>7s} {'% ctr':>6s}  Note")
    for _, r in agglo.iterrows():
        print(f"{r['city_fr']:20s} {r['pop']/1000:>8.0f}K {r['pop_correct']/1000:>9.0f}K "
              f"{r.get('bias_factor',1):>6.1f}× {r['l_1000hab']:>6.1f} {r.get('l_1000hab_metro',0):>6.1f}* "
              f"{r['pct_centre']:>5.1f}%  {r['scope_note'][:50]}")

# Villes alignées / intra
for scope_type, label in [("aligned", "DÉJÀ ALIGNÉ"), ("intra", "DISTRICTS INTERNES")]:
    subset = df_audit[df_audit["scope_type"] == scope_type]
    if len(subset) > 0:
        print(f"\n{label} — {len(subset)} villes")
        for _, r in subset.iterrows():
            print(f"  {r['city_fr']:20s} {r['l_1000hab']:>6.1f} L/1Kh  {r['scope_note']}")

print(f"\nOutputs: {OUTPUT_DETAIL.name}, {OUTPUT_SUMMARY.name}")
# &e

# &e
