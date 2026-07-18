# &s &JCN_KPI_aaMAIN - Helper KPI Airbnb partagé (sp08 / sp10)

# Fonctions factorisées pour calculer les indicateurs KPI Airbnb.
# Réutilisé par sp08 (monde 75 villes) et sp10 (France multi-niveaux).
#
# Usage:
#   from jcn_kpi import compute_core_kpi, compute_concentration, compute_kpi, add_density_ratios
#
# Date: 2026-02-21

import pandas as pd
import numpy as np

# &s &CORE_KPI - Indicateurs de base (volumes, prix, structure, activité)

def compute_core_kpi(df):
    """Calcule les KPI de base depuis un DataFrame de listings nettoyés.

    Attendu: colonnes id, host_id, price_eur, room_type, is_entire_home,
    is_multihost, is_longterm, availability_365, number_of_reviews,
    reviews_per_month, minimum_nights, calculated_host_listings_count.

    Returns: dict de KPI (scalaires).
    """
    n = len(df)
    if n == 0:
        return {}

    kpi = {
        "vol_n_ann": n,
        "str_n_entire": int(df["is_entire_home"].sum()),
        "vol_n_hotes": df["host_id"].nunique(),
        # Prix
        "px_med": round(df["price_eur"].median(), 1),
        "px_moy": round(df["price_eur"].mean(), 1),
        "px_q25": round(df["price_eur"].quantile(0.25), 1),
        "px_q75": round(df["price_eur"].quantile(0.75), 1),
        # Structure
        "str_entire_pct": round(df["is_entire_home"].mean() * 100, 1),
        "pct_multi": round(df["is_multihost"].mean() * 100, 1),
        "str_minnuits30_pct": round(df["is_longterm"].mean() * 100, 1),
        # Activité
        "act_cal_ouvert_med": round(df["availability_365"].median(), 1),
        "act_cal_ouvert_moy": round(df["availability_365"].mean(), 1),
        "actrv_avis": round(df["number_of_reviews"].median(), 1),
        "actrv_avis_mois": round(df["reviews_per_month"].dropna().median(), 1) if df["reviews_per_month"].notna().any() else 0,
    }

    # Dérivés
    kpi["str_ratio_ann_hote"] = round(kpi["vol_n_ann"] / kpi["vol_n_hotes"], 2) if kpi["vol_n_hotes"] > 0 else 0
    kpi["px_iqr"] = round(kpi["px_q75"] - kpi["px_q25"], 0)

    # Prix par type de logement
    entire = df[df["room_type"] == "Entire home/apt"]["price_eur"]
    private = df[df["room_type"] == "Private room"]["price_eur"]
    kpi["px_entire_med"] = round(entire.median(), 1) if len(entire) > 0 else np.nan
    kpi["px_private_med"] = round(private.median(), 1) if len(private) > 0 else np.nan

    return kpi

# &e

# &s &CONCENTRATION - Indicateurs de concentration hôtes (cr_)

def concentration_hosts_for_offre50(df):
    """% d'hôtes nécessaires pour détenir 50% de l'offre (Lorenz, axe X fixé Y=50%)."""
    host_listings = df.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    vol_n_hotes = len(host_listings)
    if vol_n_hotes == 0 or total == 0:
        return 0
    cumsum = host_listings.cumsum()
    hosts_for_50 = (cumsum <= total * 0.5).sum() + 1
    return round(hosts_for_50 / vol_n_hotes * 100, 1)

def gini_coef(values):
    """Indice de Gini d'une distribution (0=égalité, 1=inégalité totale)."""
    arr = np.sort(np.asarray(values, dtype=float))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * (index * arr).sum() - (n + 1) * arr.sum()) / (n * arr.sum()))

def compute_concentration(df):
    """Indicateurs de concentration cr_ depuis un DataFrame de listings.

    Schéma de nommage : cr_<axe_mesuré>_<seuil>_pct
      - cr_offre_top10host_pct  : % offre captée par top 10 hôtes absolus
      - cr_offre_top10pct_pct   : % offre captée par top 10 % des hôtes (Lorenz)
      - cr_hosts_offre50_pct    : % hôtes pour atteindre 50 % de l'offre (Lorenz inverse)
      - cr_gini                 : indice de Gini de la distribution hôte/listings
    """
    host_listings = df.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    vol_n_hotes = len(host_listings)

    if vol_n_hotes == 0 or total == 0:
        return {
            "cr_hosts_offre50_pct": 0, "cr_offre_top10host_pct": 0, "cr_offre_top10pct_pct": 0,
            "cr_gini": 0,
            "cr_host_5plus": 0, "cr_host_10plus": 0,
            "cr_offre_5plus": 0, "cr_offre_10plus": 0,
        }

    n_top10pct = max(1, int(np.ceil(vol_n_hotes * 0.10)))

    return {
        # Indicateurs Lorenz-style
        "cr_hosts_offre50_pct": concentration_hosts_for_offre50(df),
        "cr_offre_top10host_pct": round(host_listings.head(10).sum() / total * 100, 1),
        "cr_offre_top10pct_pct": round(host_listings.head(n_top10pct).sum() / total * 100, 1),
        "cr_gini": round(gini_coef(host_listings.values), 3),
        # Seuils cumulés
        "cr_host_1plus": round((host_listings > 1).sum() / vol_n_hotes * 100, 1),
        "cr_host_5plus": round((host_listings >= 5).sum() / vol_n_hotes * 100, 1),
        "cr_host_10plus": round((host_listings >= 10).sum() / vol_n_hotes * 100, 1),
        "cr_offre_1plus": round(host_listings[host_listings > 1].sum() / total * 100, 1),
        "cr_offre_5plus": round(host_listings[host_listings >= 5].sum() / total * 100, 1),
        "cr_offre_10plus": round(host_listings[host_listings >= 10].sum() / total * 100, 1),
        # Classes exclusives (single=1, semipro=2-4, pro=5-9, 10plus=≥10 — somment à 100%)
        "cr_host_single_pct": round((host_listings == 1).sum() / vol_n_hotes * 100, 1),
        "cr_host_semipro_pct": round(((host_listings >= 2) & (host_listings <= 4)).sum() / vol_n_hotes * 100, 1),
        "cr_host_pro_pct": round(((host_listings >= 5) & (host_listings <= 9)).sum() / vol_n_hotes * 100, 1),
        "cr_offre_single_pct": round(host_listings[host_listings == 1].sum() / total * 100, 1),
        "cr_offre_semipro_pct": round(host_listings[(host_listings >= 2) & (host_listings <= 4)].sum() / total * 100, 1),
        "cr_offre_pro_pct": round(host_listings[(host_listings >= 5) & (host_listings <= 9)].sum() / total * 100, 1),
    }

# &e

# &s &COMPUTE_KPI - Fonction combinée core + concentration

def compute_kpi(df):
    """Calcule tous les KPI (core + concentration) pour un groupe de listings.

    Returns: dict complet de KPI.
    """
    kpi = compute_core_kpi(df)
    if kpi:
        kpi.update(compute_concentration(df))
    return kpi

# &e

# &s &GZ_KPI - Indicateurs issus du listings.csv.gz (reviews, occupation, capacité, hôte)

def compute_gz_kpi(df, min_n=10):
    """Calcule les KPI gz depuis un DataFrame contenant les colonnes gz.

    Colonnes attendues (optionnelles — skip si absentes) :
        review_scores_rating, review_scores_accuracy, review_scores_cleanliness,
        review_scores_checkin, review_scores_communication, review_scores_location,
        review_scores_value, estimated_occupancy_l365d, estimated_revenue_l365d,
        accommodates, bedrooms, host_is_superhost, instant_bookable.

    Returns: dict de KPI gz (scalaires).
    """
    kpi = {}
    n = len(df)
    if n == 0:
        return kpi

    def _med(col):
        if col not in df.columns:
            return np.nan
        v = df[col].dropna()
        return round(v.median(), 2) if len(v) >= min_n else np.nan

    def _mean(col):
        if col not in df.columns:
            return np.nan
        v = df[col].dropna()
        return round(v.mean(), 2) if len(v) >= min_n else np.nan

    def _pct(col, true_val=1):
        if col not in df.columns:
            return np.nan
        v = df[col].dropna()
        if len(v) < min_n:
            return np.nan
        return round((v == true_val).mean() * 100, 1)

    def _n_valid(col):
        if col not in df.columns:
            return 0
        return int(df[col].notna().sum())

    # Reviews
    kpi["actrv_note_glb"] = _med("review_scores_rating")
    kpi["actrv_note_glb_n"] = _n_valid("review_scores_rating")
    SUB_NOTES = {
        "accuracy": "exact", "cleanliness": "proprete", "checkin": "arrivee",
        "communication": "communic", "location": "emplacem", "value": "qprix",
    }
    for sub_en, sub_fr in SUB_NOTES.items():
        col = f"review_scores_{sub_en}"
        kpi[f"actrv_note_{sub_fr}"] = _med(col)
        kpi[f"actrv_note_{sub_fr}_n"] = _n_valid(col)
    kpi["actrv_listing_ac_avis_pct"] = round(_n_valid("review_scores_rating") / n * 100, 1) if n > 0 else 0

    # Occupation & revenus (revenus arrondis à l'euro pour cohérence avec sp08)
    kpi["act_reserv_j_med"] = _med("estimated_occupancy_l365d")
    kpi["act_reserv_j_moy"] = _mean("estimated_occupancy_l365d")
    _rev_med = _med("estimated_revenue_l365d")
    _rev_moy = _mean("estimated_revenue_l365d")
    kpi["act_revenu_med"] = round(_rev_med, 0) if pd.notna(_rev_med) else _rev_med
    kpi["act_revenu_moy"] = round(_rev_moy, 0) if pd.notna(_rev_moy) else _rev_moy

    # Taux d'occupation = occupancy / 365 * 100 (cappe 70% par Inside Airbnb)
    if "estimated_occupancy_l365d" in df.columns:
        taux = df["estimated_occupancy_l365d"].dropna() / 365 * 100
        if len(taux) >= min_n:
            kpi["act_reserv_taux"] = round(taux.median(), 1)

    # Occupation bins
    if "estimated_occupancy_l365d" in df.columns:
        occ = df["estimated_occupancy_l365d"].dropna()
        if len(occ) >= min_n:
            kpi["act_reserv_30j_pct"] = round((occ >= 30).mean() * 100, 1)
            kpi["act_reserv_180j_pct"] = round((occ >= 180).mean() * 100, 1)

    # Disponibilité bins
    if "availability_365" in df.columns:
        disp = df["availability_365"].dropna()
        if len(disp) >= min_n:
            kpi["act_cal_180j_pct"] = round((disp >= 180).mean() * 100, 1)

    # Capacité
    kpi["str_cap_pers_med"] = _med("accommodates")
    kpi["str_cap_pers_moy"] = _mean("accommodates")
    kpi["str_cap_chbr_med"] = _med("bedrooms")

    # Prix par nombre de chambres (logements entiers seulement)
    entire = df[df["room_type"] == "Entire home/apt"] if "room_type" in df.columns else pd.DataFrame()
    if "bedrooms" in entire.columns and len(entire) > 0:
        for nbr, label in [(1, "1br"), (2, "2br")]:
            sub = entire[entire["bedrooms"] == nbr]["price_eur"]
            kpi[f"px_{label}_med"] = round(sub.median(), 1) if len(sub) >= min_n else np.nan
        sub3 = entire[entire["bedrooms"] >= 3]["price_eur"]
        kpi["px_3brplus_med"] = round(sub3.median(), 1) if len(sub3) >= min_n else np.nan

    # Profil hôte
    kpi["act_superhost_pct"] = _pct("host_is_superhost", true_val=1)
    kpi["str_instantbook_pct"] = _pct("instant_bookable", true_val=1)

    # Longterm 90
    if "minimum_nights" in df.columns:
        mn = df["minimum_nights"].dropna()
        if len(mn) >= min_n:
            kpi["str_minnuits90_pct"] = round((mn >= 90).mean() * 100, 1)

    return kpi

# &e

# &s &COMPUTE_ALL - Fonction combinée core + concentration + gz

def compute_all_kpi(df, min_n_gz=10):
    """Calcule tous les KPI (core + concentration + gz) pour un groupe de listings.

    Returns: dict complet de KPI.
    """
    kpi = compute_core_kpi(df)
    if kpi:
        kpi.update(compute_concentration(df))
        kpi.update(compute_gz_kpi(df, min_n=min_n_gz))
    return kpi

# &e

# &s &DENSITY_RATIOS - Ratios de pression (population, logement, propriétaires)

def add_density_ratios(kpi, pop=None, rp=None, res_sec=None, housing=None, **_):
    """Ajoute les ratios de pression à un dict KPI.

    Ratios actifs (France) :
        prsf_listings_1000rp   — annonces / 1000 résidences principales
        prsf_listings_1000rps  — annonces / 1000 logements occupés (RP + rés. secondaires)

    STANDBY (recalcul cohérent en cours, gardés dans ddict) :
        listings_1000hab  — annonces / 1000 habitants
        listings_1000log  — annonces / 1000 logements (parc total)
    """
    n = kpi.get("vol_n_ann", 0)

    # STANDBY — recalcul cohérent à venir
    # if pop and pop > 0:
    #     kpi["listings_1000hab"] = round(n / (pop / 1000), 1)
    # if housing and housing > 0:
    #     kpi["listings_1000log"] = round(n / (housing / 1000), 1)
    if rp and rp > 0:
        kpi["prsf_listings_1000rp"] = round(n / (rp / 1000), 1)
    if rp and res_sec is not None:
        log_occ = rp + res_sec
        if log_occ > 0:
            kpi["prsf_listings_1000rps"] = round(n / (log_occ / 1000), 1)

    return kpi

# &e

# &s &CLEAN_FLAGS - Ajout flags standard sur DataFrame listings

def add_flags(df):
    """Ajoute les colonnes flags standard (is_entire_home, is_multihost, is_longterm).

    Modifie df in-place et retourne df.
    """
    if "is_entire_home" not in df.columns:
        df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(int)
    if "is_multihost" not in df.columns:
        df["is_multihost"] = (df["calculated_host_listings_count"] > 1).astype(int)
    if "is_longterm" not in df.columns:
        df["is_longterm"] = (df["minimum_nights"] >= 30).astype(int)
    return df

def clean_listings(df):
    """Nettoyage : ACTIVITÉ (comptage) = dispo>0 + pas hôtel, INDÉPENDANT du prix.

    Prix null / hors [10,2000] -> NA (exclus des stats de prix) mais l'annonce reste COMPTÉE.
    Cohérent avec clean_gz de sp07b (fix volume 2026-07-17) : le taux de prix-null change entre
    snapshots via le mécanisme price_quote d'Inside Airbnb -> filtrer sur le prix fausse le volume.
    Retourne un DataFrame filtré (copie).
    """
    active = (df["availability_365"] > 0) | (df["number_of_reviews_ltm"] > 0)
    out = df[active & (df["room_type"] != "Hotel room")].copy()
    bad = out["price_eur"].isna() | (out["price_eur"] < 10) | (out["price_eur"] > 2000)
    for _c in ("price", "price_eur"):
        if _c in out.columns:
            out.loc[bad, _c] = np.nan
    return out

# &e

# &e
