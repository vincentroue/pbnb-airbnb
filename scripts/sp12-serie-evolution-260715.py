# &s &SERIE_EVOLUTION_aaMAIN - Panel série (coffre-fort) + colonnes d'évolution YoY

# Empile les snapshots KPI (kpi_bnb_serie_panel = coffre-fort, col snapshot) et injecte
# les colonnes d'évolution dans le fichier plat COURANT (celui que lisent ACP + rapports).
#
# Convention (validée 2026-07-14/15) :
#   {base}_vevol_{per} = évolution relative %   (niveaux, prix, comptages, ratios)
#   {base}_vdifp_{per} = variation en points    (indicateurs déjà en %)
#   {base}_vabs_{per}  = variation absolue       (indice borné : cr_gini)
#   {base}_{ref2}      = valeur de référence n-1 (pour tables « 2025 · 2026 · Δ »)
#   per = ref2+cur2 (ex 2526) ; ref2 = 2 chiffres du snapshot de référence (25)
# Flags : is_proxy=1 (Berlin)      -> TOUTE l'évolution -> NA
#         price_invalid=1 (Zurich/Geneva) -> évolution PRIX -> NA
# prs_listings_1000hab_dense EXCLU (dense encore calculé sur 2506, à re-auditer).
#
# Usage: python scripts/sp12-serie-evolution-260715.py [--cur 2606] [--ref 2506]
#
# Fichier: sp12-serie-evolution-260715.py | dcr: 26-07-15

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
INTERIM = BASE / "data" / "interim"

def _arg(flag, default):
    for i, a in enumerate(sys.argv):
        if a == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default

SNAP_CUR = _arg("--cur", "2606")
SNAP_REF = _arg("--ref", "2506")
REF2 = SNAP_REF[:2]                 # "25"
PER = SNAP_REF[:2] + SNAP_CUR[:2]   # "2526"

# Indicateurs clés & type d'évolution
VEVOL = ["vol_n_ann", "vol_n_hotes", "px_med", "px_entire_med", "str_ratio_ann_hote",
         "act_reserv_j_med", "actrv_avis_mois", "act_revenu_med"]
VDIFP = ["str_entire_pct", "str_minnuits30_pct", "cr_host_single_pct", "cr_host_pro_pct",
         "cr_offre_top10pct_pct", "act_reserv_taux", "act_superhost_pct",
         "str_instantbook_pct", "cr_host_1plus"]
VABS = ["cr_gini"]
PRICE_COLS = ["px_med", "px_entire_med", "act_revenu_med"]  # -> NA si price_invalid
# &e

# &s &HELPERS
def _evol_colnames():
    """Noms EXACTS des colonnes générées par ce run (période PER + réf REF2)."""
    names = set()
    for base in VEVOL:
        names.add(f"{base}_vevol_{PER}")
    for base in VDIFP:
        names.add(f"{base}_vdifp_{PER}")
    for base in VABS:
        names.add(f"{base}_vabs_{PER}")
    for base in VEVOL + VDIFP + VABS:
        names.add(f"{base}_{REF2}")
    return names

def levels_only(df):
    """Retire UNIQUEMENT les colonnes d'évolution de CE run (idempotence + panel propre).

    Ne touche pas aux colonnes d'évolution d'autres périodes déjà présentes
    (ex. ctx_tour_nights_total_vevol_2224, contexte externe).
    """
    drop = _evol_colnames()
    return df.drop(columns=[c for c in df.columns if c in drop], errors="ignore")

def enrich(cur, ref, key="city"):
    """Ajoute _ref2 + colonne d'évolution au bon type, puis applique les flags."""
    ref_idx = ref.drop_duplicates(key).set_index(key)
    out = cur.copy()
    for base in VEVOL + VDIFP + VABS:
        if base not in out.columns or base not in ref_idx.columns:
            continue
        v_ref = out[key].map(ref_idx[base])
        out[f"{base}_{REF2}"] = v_ref
        if base in VEVOL:
            out[f"{base}_vevol_{PER}"] = ((out[base] - v_ref) / v_ref.replace(0, np.nan) * 100).round(1)
        elif base in VDIFP:
            out[f"{base}_vdifp_{PER}"] = (out[base] - v_ref).round(1)
        else:  # VABS (cr_gini) : delta absolu en points d'indice
            out[f"{base}_vabs_{PER}"] = (out[base] - v_ref).round(3)

    evol_cols = [c for c in out.columns if c.endswith(f"_{PER}")]
    # is_proxy=1 -> toute l'évolution NA (valeurs = n-1, delta trompeur)
    if "is_proxy" in out.columns:
        out.loc[out["is_proxy"] == 1, evol_cols] = np.nan
    # price_invalid=1 -> évolution PRIX NA (le niveau prix courant est déjà NA de toute façon)
    if "price_invalid" in out.columns:
        price_evol = [f"{b}_vevol_{PER}" for b in PRICE_COLS if f"{b}_vevol_{PER}" in out.columns]
        out.loc[out["price_invalid"] == 1, price_evol] = np.nan
    return out
# &e

# &s &MAIN
if __name__ == "__main__":
    print("=" * 64)
    print(f"SÉRIE + ÉVOLUTION — ref {SNAP_REF} -> cur {SNAP_CUR} (période {PER})")
    print("=" * 64)

    cur_path = INTERIM / f"kpi_global_by_city_{SNAP_CUR}.csv"
    ref_path = INTERIM / f"kpi_global_by_city_{SNAP_REF}.csv"
    cur_city = levels_only(pd.read_csv(cur_path))
    ref_city = levels_only(pd.read_csv(ref_path))
    print(f"Villes : {SNAP_REF}={len(ref_city)} | {SNAP_CUR}={len(cur_city)}")

    # 1) PANEL coffre-fort (niveaux empilés, col snapshot)
    p_ref = ref_city.assign(snapshot=SNAP_REF)
    p_cur = cur_city.assign(snapshot=SNAP_CUR)
    panel = pd.concat([p_ref, p_cur], ignore_index=True, sort=False)
    for f in ["is_proxy", "price_invalid"]:
        if f in panel.columns:
            panel[f] = panel[f].fillna(0).astype(int)
    panel_path = INTERIM / "kpi_bnb_serie_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"Panel   : {panel_path.name} ({len(panel)} lignes = {panel['snapshot'].nunique()} snapshots)")

    # 2) Enrichir le fichier plat COURANT (lu par ACP + rapports)
    enriched = enrich(cur_city, ref_city, key="city")
    enriched.to_csv(cur_path, index=False, encoding="utf-8-sig")
    n_evol = len([c for c in enriched.columns if c.endswith(f"_{PER}")])
    n_ref = len([c for c in enriched.columns if c.endswith(f"_{REF2}")])
    print(f"Enrichi : {cur_path.name} (+{n_evol} cols évol, +{n_ref} cols _{REF2})")

    # 3) Aperçu
    ev_vol = f"vol_n_ann_vevol_{PER}"
    ev_px = f"px_med_vevol_{PER}"
    print(f"\n--- Top 8 hausses de volume (vol_n_ann_vevol_{PER}) ---")
    show = ["city_fr", "vol_n_ann", f"vol_n_ann_{REF2}", ev_vol, ev_px, "is_proxy", "price_invalid"]
    show = [c for c in show if c in enriched.columns]
    print(enriched.dropna(subset=[ev_vol]).nlargest(8, ev_vol)[show].to_string(index=False))
    print(f"\n--- Contrôle flags (évol doit être NA) ---")
    chk = enriched[enriched["city"].isin(["berlin", "zurich", "geneva"])]
    print(chk[[c for c in ["city", ev_vol, ev_px, "is_proxy", "price_invalid"] if c in enriched.columns]].to_string(index=False))
    print("\nDone!")
# &e

# &e &SERIE_EVOLUTION_aaMAIN
