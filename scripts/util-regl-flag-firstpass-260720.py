# &s &REGL_FLAG_FIRSTPASS_aaMAIN - Premier jet flag régulation ville par ville
#
# Combine 3 proxies data (license%, min≥30, cal_ouvert) -> classification provisoire
# regl_niveau/type/echelle/annee, PUIS override par ~14 villes documentées (PDF Threat + web).
# Sortie = point de départ pour un deepsearch qui n'a plus qu'à corriger/dater/sourcer.
#
# Sortie: data/external/regl-flag-pbnb-cities-260720.csv

import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
KPI = BASE / "data" / "interim" / "kpi_global_by_city_2606.csv"
PARQUET = BASE / "data" / "interim" / "dblistingfull_2606_cons_global.parquet"
OUT = BASE / "data" / "external" / "regl-flag-pbnb-cities-260720.csv"

# &s &PROXIES
cc = pd.read_csv(KPI)
cc = cc[cc["scope"] == "city"].copy()

lic = pq.read_table(PARQUET, columns=["city", "license"]).to_pandas()
def _has_num(x):
    x = str(x).strip()
    return any(c.isdigit() for c in x)
def _engage(x):  # numéro OU Exempt = l'hôte a répondu à une obligation d'enregistrement
    x = str(x).strip().lower()
    return _has_num(x) or "exempt" in x
lic["num"] = lic["license"].map(_has_num)
lic["eng"] = lic["license"].map(_engage)
g = lic.groupby("city").agg(pct_license=("num", "mean"), pct_reg_engage=("eng", "mean")).reset_index()
g[["pct_license", "pct_reg_engage"]] = (g[["pct_license", "pct_reg_engage"]] * 100).round(1)
cc = cc.merge(g, on="city", how="left")

# &s &CLASSIF_DATA - premier jet depuis les proxies
def classify(r):
    m30, eng, cal = r["str_minnuits30_pct"], r.get("pct_reg_engage", 0) or 0, r["act_cal_ouvert_med"]
    if m30 >= 45:
        return 3, "min-stay/interdiction", "data"
    if eng >= 80:
        return 2, "registration", "data"
    if m30 >= 25 or eng >= 40:
        return 2, "registration/min-stay", "data"
    if eng >= 15:
        return 1, "registration partielle", "data"
    if cal < 100:
        return 2, "night-cap serré ?", "à vérifier"
    return 0, "aucune ?", "à vérifier"

cc[["regl_niveau", "regl_type", "regl_confiance"]] = cc.apply(lambda r: pd.Series(classify(r)), axis=1)
cc["regl_annee"] = ""
cc["regl_echelle"] = "ville"
cc["regl_source"] = ""
# &e

# &s &CURATED - override villes documentées (PDF Threat + recherche) -> date/echelle/type/source
# niveau, type, annee, echelle, source
CURATED = {
    "new-york-city": (3, "interdiction (unhosted <30j, LL18)", "2023", "ville", "NYC Local Law 18"),
    "los-angeles":   (2, "registration + résidence princ. (HSO)", "2019", "ville", "LA Home-Sharing Ordinance"),
    "san-francisco": (2, "registration + résidence princ.", "2015", "ville", "SF Office STR"),
    "montreal":      (2, "registration provinciale (Bill 25)", "2023", "province", "Québec Bill 25"),
    "toronto":       (2, "registration + résidence princ.", "2021", "ville", "Toronto STR by-law"),
    "quebec-city":   (2, "registration provinciale (CITQ)", "2016", "province", "Québec CITQ / Bill 25"),
    "amsterdam":     (3, "registration + plafond 30 nuits", "2019", "ville+national", "Gemeente Amsterdam / loi NL 2021"),
    "paris":         (2, "registration + plafond 90 nuits (Le Meur)", "2024", "ville+national", "Loi Le Meur 2024 (cadre 2014/2019)"),
    "barcelona":     (3, "moratoire licences, fin LCD 2028", "2024", "ville+province", "Decret-Llei 9/2024 Catalunya"),
    "berlin":        (2, "permis anti-détournement (Zweckentfremdung)", "2018", "ville", "Zweckentfremdungsverbot Berlin"),
    "london":        (2, "plafond 90 nuits (SANS enregistrement)", "2015", "national", "Deregulation Act 2015 — POINT AVEUGLE data"),
    "singapore":     (3, "min-séjour 3 mois (privé) / 6 mois (HDB)", "2017", "national", "URA Short-Term Accommodation"),
    "hong-kong":     (3, "licence guesthouse obligatoire <28j", "2003", "territorial", "Hotel & Guesthouse Ordinance Cap.349 — POINT AVEUGLE data"),
    "tokyo":         (2, "registration + plafond 180 nuits (Minpaku)", "2018", "national", "Loi Minpaku (Housing Accommodation Business Act)"),
    "lisbon":        (2, "registration (RNAL) + zones de contention", "2018", "ville+national", "RNAL / zonas de contenção"),
    "vienna":        (2, "registration + zones résidentielles", "2024", "ville", "Wien STR Novelle 2024"),
}
for city, (niv, typ, an, ech, src) in CURATED.items():
    m = cc["city"] == city
    if m.any():
        cc.loc[m, ["regl_niveau", "regl_type", "regl_annee", "regl_echelle", "regl_source", "regl_confiance"]] = \
            [niv, typ, an, ech, src, "curé"]
# &e

# &s &EXPORT
cols = ["city", "city_fr", "continent", "regl_niveau", "regl_type", "regl_annee", "regl_echelle",
        "regl_source", "regl_confiance", "pct_license", "pct_reg_engage", "str_minnuits30_pct",
        "act_cal_ouvert_med", "vol_n_ann"]
out = cc[cols].sort_values(["regl_niveau", "str_minnuits30_pct"], ascending=[False, False])
out.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"-> {OUT.relative_to(BASE)} ({len(out)} villes)")
print(f"\nRépartition regl_niveau : {out['regl_niveau'].value_counts().sort_index().to_dict()}")
print(f"Confiance : {out['regl_confiance'].value_counts().to_dict()}")
print("\n--- Villes 'à vérifier' (le deepsearch doit trancher) ---")
av = out[out.regl_confiance == "à vérifier"]
print(av[["city_fr", "regl_niveau", "regl_type", "pct_reg_engage", "str_minnuits30_pct"]].head(20).to_string(index=False))
# &e
# &e &REGL_FLAG_FIRSTPASS_aaMAIN
