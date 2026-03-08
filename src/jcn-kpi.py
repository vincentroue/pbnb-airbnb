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
        "n_listings": n,
        "n_entire": int(df["is_entire_home"].sum()),
        "n_hosts": df["host_id"].nunique(),
        # Prix
        "prix_med": round(df["price_eur"].median(), 1),
        "prix_moy": round(df["price_eur"].mean(), 1),
        "prix_q25": round(df["price_eur"].quantile(0.25), 1),
        "prix_q75": round(df["price_eur"].quantile(0.75), 1),
        # Structure
        "pct_entire": round(df["is_entire_home"].mean() * 100, 1),
        "pct_multi": round(df["is_multihost"].mean() * 100, 1),
        "pct_longterm": round(df["is_longterm"].mean() * 100, 1),
        # Activité
        "dispo_med": round(df["availability_365"].median(), 1),
        "dispo_moy": round(df["availability_365"].mean(), 1),
        "reviews_med": round(df["number_of_reviews"].median(), 1),
        "rpm_med": round(df["reviews_per_month"].dropna().median(), 1) if df["reviews_per_month"].notna().any() else 0,
    }

    # Dérivés
    kpi["ratio_lh"] = round(kpi["n_listings"] / kpi["n_hosts"], 2) if kpi["n_hosts"] > 0 else 0
    kpi["prix_iqr"] = round(kpi["prix_q75"] - kpi["prix_q25"], 0)

    # Prix par type de logement
    entire = df[df["room_type"] == "Entire home/apt"]["price_eur"]
    private = df[df["room_type"] == "Private room"]["price_eur"]
    kpi["prix_med_entire"] = round(entire.median(), 1) if len(entire) > 0 else np.nan
    kpi["prix_med_private"] = round(private.median(), 1) if len(private) > 0 else np.nan

    return kpi

# &e

# &s &CONCENTRATION - Indicateurs de concentration hôtes (cr_)

def concentration_50(df):
    """% d'hôtes nécessaires pour détenir 50% de l'offre (Lorenz)."""
    host_listings = df.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    n_hosts = len(host_listings)
    if n_hosts == 0 or total == 0:
        return 0
    cumsum = host_listings.cumsum()
    hosts_for_50 = (cumsum <= total * 0.5).sum() + 1
    return round(hosts_for_50 / n_hosts * 100, 1)

def compute_concentration(df):
    """Indicateurs de concentration cr_ depuis un DataFrame de listings.

    Returns: dict avec cr_hosts_50pct, cr_top10_pct, cr_host_5plus,
             cr_host_10plus, cr_offre_5plus, cr_offre_10plus.
    """
    host_listings = df.groupby("host_id").size().sort_values(ascending=False)
    total = host_listings.sum()
    n_hosts = len(host_listings)

    if n_hosts == 0 or total == 0:
        return {
            "cr_hosts_50pct": 0, "cr_top10_pct": 0,
            "cr_host_5plus": 0, "cr_host_10plus": 0,
            "cr_offre_5plus": 0, "cr_offre_10plus": 0,
        }

    return {
        "cr_hosts_50pct": concentration_50(df),
        "cr_top10_pct": round(host_listings.head(10).sum() / total * 100, 1),
        "cr_host_5plus": round((host_listings >= 5).sum() / n_hosts * 100, 1),
        "cr_host_10plus": round((host_listings >= 10).sum() / n_hosts * 100, 1),
        "cr_offre_5plus": round(host_listings[host_listings >= 5].sum() / total * 100, 1),
        "cr_offre_10plus": round(host_listings[host_listings >= 10].sum() / total * 100, 1),
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

# &s &DENSITY_RATIOS - Ratios de pression (population, logement, propriétaires)

def add_density_ratios(kpi, pop=None, rp=None, nper_prop=None, res_sec=None, housing=None):
    """Ajoute les ratios de densité/pression à un dict KPI.

    Args:
        kpi: dict de KPI (doit contenir n_listings, n_entire)
        pop: population totale (commune/territoire)
        rp: résidences principales
        nper_prop: nombre de personnes propriétaires
        res_sec: résidences secondaires et logements occasionnels
        housing: logements totaux (legacy, =rp si absent)
    """
    n = kpi.get("n_listings", 0)
    n_entire = kpi.get("n_entire", 0)

    if pop and pop > 0:
        kpi["listings_1000hab"] = round(n / (pop / 1000), 1)
    if rp and rp > 0:
        kpi["listings_1000rp"] = round(n / (rp / 1000), 1)
        kpi["entire_1000rp"] = round(n_entire / (rp / 1000), 1)
    if rp and res_sec is not None:
        log_occ = rp + res_sec
        if log_occ > 0:
            kpi["listings_1000rps"] = round(n / (log_occ / 1000), 1)
    if nper_prop and nper_prop > 0:
        kpi["listings_1000prop"] = round(n / (nper_prop / 1000), 1)
    if housing and housing > 0:
        kpi["listings_1000hsg"] = round(n / (housing / 1000), 1)
        kpi["entire_1000hsg"] = round(n_entire / (housing / 1000), 1)

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
    """Pipeline cleaning standard (prix notna, dispo>0, pas hotel, prix 10-1000 EUR).

    Retourne un DataFrame filtré (copie).
    """
    out = df[df["price_eur"].notna()].copy()
    out = out[out["availability_365"] > 0]
    out = out[out["room_type"] != "Hotel room"]
    out = out[(out["price_eur"] >= 10) & (out["price_eur"] <= 1000)]
    return out

# &e

# &e
