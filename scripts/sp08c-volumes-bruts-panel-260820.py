#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sp08c-volumes-bruts-panel-260820.py — volumes BRUTS du panel (avant pipeline de nettoyage).

POURQUOI
--------
Le tableau de couverture compare notre panel au marché mondial Inside Airbnb
(`bnb-inside-study-cont-world.csv`, étude « The Threat of Short-Term Rentals to Housing »).
Or ce comptage mondial est un STOCK BRUT : Inside Airbnb totalise toutes les annonces publiées,
sans filtre prix/disponibilité/type. Comparer notre `vol_n_ann` (941 K, APRÈS nettoyage) à ce
8,3 M revient à mélanger deux définitions et sous-estime mécaniquement la couverture.

Ce script recompte donc les annonces du panel EN BRUT : nombre de lignes des sumlistings 26-06,
sans aucun filtre de nettoyage — seuls les filtres de PÉRIMÈTRE (centre-commune) sont appliqués,
puisqu'ils définissent le territoire étudié et non la qualité de l'annonce.

SORTIE
------
data/interim/panel-volumes-bruts-2606.csv  (UTF-8 BOM)
  continent_detail · n_villes · n_ann_brut · n_ann_clean · retention_pct

Usage : python scripts/sp08c-volumes-bruts-panel-260820.py
"""

import glob
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
KPI_CITY = ROOT / "data/interim/kpi_global_by_city_2606.csv"
OUT = ROOT / "data/interim/panel-volumes-bruts-2606.csv"
SNAP = "26-06"

# Filtres de PÉRIMÈTRE (identiques à sp08) : l'agglo Inside Airbnb déborde la ville étudiée.
# Ce ne sont pas des filtres de nettoyage — ils définissent le territoire.
CENTRE_FILTERS = {
    "bordeaux":     ("neighbourhood_group", ["Bordeaux"]),
    "lisbon":       ("neighbourhood_group", ["Lisboa"]),
    "porto":        ("neighbourhood_group", ["PORTO"]),
    "bergamo":      ("neighbourhood", ["Bergamo"]),
    "los-angeles":  ("neighbourhood_group", ["City of Los Angeles"]),
    "geneva":       ("neighbourhood", ["Commune de Genève"]),
    "thessaloniki": ("neighbourhood", ["Thessaloniki"]),
    "nashville":    ("neighbourhood", [
        "District 19", "District 17", "District 21", "District 5", "District 6",
        "District 2", "District 15", "District 18", "District 7", "District 20",
        "District 16", "District 8",
    ]),
    "brussels":     ("neighbourhood", [
        "Bruxelles", "Ixelles", "Saint-Gilles", "Etterbeek", "Saint-Josse-ten-Noode",
    ]),
    "pays-basque":  ("neighbourhood", ["Biarritz", "Anglet", "Bayonne"]),
}


def main():
    kpi = pd.read_csv(KPI_CITY, encoding="utf-8-sig")
    kpi = kpi[kpi["scope"] == "city"]
    print(f"Panel : {len(kpi)} villes | {int(kpi['vol_n_ann'].sum()):,} annonces nettoyées"
          .replace(",", " "))

    rows, missing = [], []
    for _, r in kpi.iterrows():
        city = r["city"]
        hits = glob.glob(str(ROOT / f"data/raw/**/{city}/{SNAP}-*_sumlistings.csv"), recursive=True)
        if not hits:
            missing.append(city)
            continue
        df = pd.read_csv(hits[0], encoding="utf-8", low_memory=False)
        if city in CENTRE_FILTERS:
            col, vals = CENTRE_FILTERS[city]
            if col in df.columns:
                df = df[df[col].isin(vals)]
        rows.append({
            "continent_detail": r["continent_detail"],
            "n_villes": 1,
            "n_ann_brut": len(df),
            "n_ann_clean": r["vol_n_ann"],
        })

    if missing:
        print(f"[WARN] {len(missing)} ville(s) sans sumlistings {SNAP} : {', '.join(missing)}")

    agg = (pd.DataFrame(rows).groupby("continent_detail", as_index=False)
             .agg(n_villes=("n_villes", "sum"),
                  n_ann_brut=("n_ann_brut", "sum"),
                  n_ann_clean=("n_ann_clean", "sum")))
    agg["retention_pct"] = (agg["n_ann_clean"] / agg["n_ann_brut"] * 100).round(1)
    agg = agg.sort_values("n_ann_brut", ascending=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(OUT, index=False, encoding="utf-8-sig")   # BOM (conv projet)

    print(agg.to_string(index=False))
    tb, tc = int(agg["n_ann_brut"].sum()), int(agg["n_ann_clean"].sum())
    print(f"\nTOTAL brut {tb:,} | nettoyé {tc:,} | rétention {tc / tb * 100:.1f} %"
          .replace(",", " "))
    print(f"-> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
