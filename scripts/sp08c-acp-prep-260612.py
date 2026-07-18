"""
sp08c-acp-prep — Prépare le CSV ACP-ready depuis kpi_global_by_city_2506.csv

Sortie : data/interim/kpi_acp_city_2506.csv — consommable TEL QUEL par le
template ACP (tpljcn-dml-ACPHCPC-fd.qmd) en mode CSV-driven, SANS aucune greffe.

3 nettoyages (le delta pbnb autrefois greffé dans le QMD) :
  1. Filtre scope == 'city'      → exclut les sub_cities BAB
  2. city_fr fallback = city     → villes sans label FR (Winnipeg…)
  3. is_capital → "Capitale" / "Non-capitale"  (au lieu de True/False/NaN)

Usage : python scripts/sp08c-acp-prep-260612.py
"""
from pathlib import Path
import pandas as pd

BASE = Path("C:/Users/vince/hh/pq/PDS/pbnb-airbnb-log-jrr-jpy")
SRC = BASE / "data/interim/kpi_global_by_city_2506.csv"
OUT = BASE / "data/interim/kpi_acp_city_2506.csv"


def enc_capital(v):
    """True/False/NaN → Capitale/Non-capitale (modalités propres pour quali.sup)."""
    if pd.isna(v):
        return "Non-capitale"
    return "Capitale" if str(v) in ("True", "true", "1", "1.0") else "Non-capitale"


def main():
    df = pd.read_csv(SRC, encoding="utf-8-sig")

    # 1. Filtre scope == city
    df = df[df["scope"] == "city"].copy()

    # 2. city_fr fallback = city
    miss = df["city_fr"].isna() | (df["city_fr"] == "")
    df.loc[miss, "city_fr"] = df.loc[miss, "city"]

    # 3. is_capital encodé
    df["is_capital"] = df["is_capital"].apply(enc_capital)

    # 4. Traitement NA contexte (PAS de médiane : sémantiquement faux).
    #    Le helper heatmap individus (jcn-dml-hcpc-typo.R) n'a pas de guard
    #    is.na → un z-score NA sur une sup quanti fait planter typo_individus_rt.
    #    Il faut donc zéro NA sur les sup quanti, MAIS avec des valeurs justes.
    #
    #    4a. UNESCO = comptage de sites → NA signifie "aucun site recensé" = 0
    #        (pays-basque/BAB et Oakland : périmètre sans site classé apparié).
    df["ctx_static_unesco_50km"] = df["ctx_static_unesco_50km"].fillna(0)

    #    4b. IDH non renseigné pour Hong-Kong/Taipei (hors base UCDB IDH) → la
    #        config ddict utilise plutôt le PIB/hab UCDB (mieux couvert). L'IDH
    #        est laissé tel quel (non sélectionné en sup quanti).
    #
    #    4c. 2 villes "edge" (Oakland, pays-basque/BAB) ne sont pas des cités
    #        UCDB autonomes → tout leur contexte UCDB manque. Remplissage par la
    #        ville VOISINE du panel (même aire/région), pas par médiane globale.
    NEIGHBOR = {"oakland": "san-francisco", "pays-basque": "bordeaux"}
    ctx_ucdb = [c for c in df.columns
                if c.startswith("ctx_ucdb_") and df[c].dtype.kind in "fi"]
    filled = {}
    for city, ref in NEIGHBOR.items():
        m_city = df["city"] == city
        m_ref = df["city"] == ref
        if not m_city.any() or not m_ref.any():
            continue
        for c in ctx_ucdb:
            if df.loc[m_city, c].isna().any() and df.loc[m_ref, c].notna().any():
                df.loc[m_city, c] = df.loc[m_ref, c].values[0]
                filled[f"{city}.{c.replace('ctx_ucdb_', '')}"] = ref

    # UTF-8 BOM (Excel-friendly)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"OK  {OUT.name} : {len(df)} villes")
    print(f"    is_capital  : {df['is_capital'].value_counts().to_dict()}")
    print(f"    city_fr vides : {(df['city_fr'].isna() | (df['city_fr'] == '')).sum()}")
    print(f"    UNESCO NA->0 + UCDB voisins remplis : {filled}")


if __name__ == "__main__":
    main()
