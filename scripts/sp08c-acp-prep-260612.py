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
import sys
import pandas as pd

BASE = Path("C:/Users/vince/hh/pq/PDS/pbnb-airbnb-log-jrr-jpy")
# Snapshot en argument (défaut 2506). Ex: python sp08c-acp-prep-260612.py 2606
SNAP = sys.argv[1] if len(sys.argv) > 1 else "2506"
SRC = BASE / f"data/interim/kpi_global_by_city_{SNAP}.csv"
OUT = BASE / f"data/interim/kpi_acp_city_{SNAP}.csv"


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
    #        Villes hors UCDB (Victoria, Fort Worth) → voisin métropolitain du
    #        panel ; Asheville sans voisin proche → médiane (fallback ci-dessous).
    NEIGHBOR = {"oakland": "san-francisco", "pays-basque": "bordeaux",
                "fort-worth": "dallas", "victoria": "vancouver"}
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
    # Fallback médiane pour tout ctx_ucdb_* encore NA (ville sans voisin panel,
    # ex Asheville) — sup quanti illustrative, zéro impact sur la typo, mais évite
    # le crash heatmap individus (helper sans garde is.na).
    ucdb_med = {}
    for c in ctx_ucdb:
        if df[c].isna().any():
            ucdb_med[c] = int(df[c].isna().sum())
            df[c] = df[c].fillna(df[c].median())

    # 4d. Colonnes d'évolution (_vevol/_vdifp/_vabs) : NA = pas de baseline (ville
    #     nouvelle ou snapshot échoué, ex Berlin 2606) → 0 (neutre « pas de
    #     variation »). Évite le crash heatmap individus (z-score NA sur sup quanti)
    #     et projette la ville à l'origine des trajectoires, sans la distordre.
    evol_cols = [c for c in df.columns
                 if any(s in c for s in ("_vevol_", "_vdifp_", "_vabs_"))
                 and df[c].dtype.kind in "fi"]
    evol_na = {c: int(df[c].isna().sum()) for c in evol_cols if df[c].isna().any()}
    for c in evol_cols:
        df[c] = df[c].fillna(0)

    # 4e. Prix px_* manquant (NIVEAU, pas évolution) : le prix est SUPPLÉMENTAIRE
    #     dans l'ACP (illustratif, zéro impact typo). Fallback sur le prix 2025 de la
    #     MÊME ville (niveau valide — CHF stable pour Zurich/Genève, chers à tort
    #     rabaissés par une médiane), sinon médiane 2606 (ville sans prix réel, ex
    #     Buenos Aires). L'évolution prix reste INTERDITE (base->total cassée).
    px_fb = {}
    if SNAP != "2506":
        prev = BASE / "data/interim/kpi_global_by_city_2506.csv"
        if prev.exists():
            dprev = pd.read_csv(prev, encoding="utf-8-sig")
            dprev = dprev[dprev["scope"] == "city"].drop_duplicates("city").set_index("city")
            for col in ("px_entire_med", "px_private_med"):
                if col in df.columns and df[col].isna().any():
                    m = df[col].isna()
                    n0 = int(m.sum())
                    if col in dprev.columns:
                        df.loc[m, col] = df.loc[m, "city"].map(dprev[col])
                    n_fb = n0 - int(df[col].isna().sum())
                    df[col] = df[col].fillna(df[col].median())
                    px_fb[col] = f"{n_fb}/{n0} via 2025, reste médiane"

    # UTF-8 BOM (Excel-friendly)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    if evol_na:
        print(f"    évolutions NA->0 : {evol_na}")
    if px_fb:
        print(f"    prix NA fallback : {px_fb}")
    print(f"OK  {OUT.name} : {len(df)} villes")
    print(f"    is_capital  : {df['is_capital'].value_counts().to_dict()}")
    print(f"    city_fr vides : {(df['city_fr'].isna() | (df['city_fr'] == '')).sum()}")
    print(f"    UNESCO NA->0 + UCDB voisins remplis : {filled}")


if __name__ == "__main__":
    main()
