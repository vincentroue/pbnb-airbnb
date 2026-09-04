# &s &REGL_COMPLETE13_aaMAIN - Complète les 13 dernières villes (recherche) + re-dérive les binaires
# Rend le flag régul complet sur 76/76, homogène (confiance recherche partout où recherché).
import pandas as pd, re
from pathlib import Path

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
FLAG = BASE / "data" / "external" / "regl-flag-pbnb-cities-260720.csv"

R13 = {
 "singapore": (3,"ban+min-stay","2019","national","oui","Interdiction de fait : séjour min. 3 mois (92 nuits) résidentiel privé, 6 mois logement public HDB, amendes 200000 S$","ura.gov.sg/short-term-accommodation"),
 "ottawa": (2,"registration+primary-residence+licence","2021/2024","ville","oui","Location courte durée limitée à la résidence principale, permis-hôte obligatoire (100$/an), amendes jusqu'à 100000$/jour","ottawa.ca/short-term-rentals"),
 "pays-basque": (3,"registration+primary-residence+night-cap+licence","2023","ville","oui","Compensation logement-pour-logement dans 24 communes tendues (Biarritz/Anglet/Bayonne) : -92% d'autorisations, résidence principale 120 nuits/an","communaute-paysbasque.fr/meubles-de-tourisme-reglement"),
 "bordeaux": (2,"registration+primary-residence+night-cap+licence","2025","ville","oui","Cadre Le Meur : enregistrement + résidence principale 120 nuits/an (90 préparé) + changement d'usage/compensation pour secondaire","bordeaux.fr/location-touristique-guide"),
 "bologna": (2,"registration+licence","2024/2025","national","partiel","CIN national obligatoire (01/2025) + SCIA ; règle municipale B3 (min 50 m²) annulée fin 2025 par le Conseil d'État","cittametropolitana.bo.it/CIN"),
 "denver": (2,"licence+primary-residence","2016","ville","oui","Licence courte durée réservée à la résidence principale (≥183 jours/an) ; enforcement fort (850+ citations, ~200 fermetures 2024)","denvergov.org/short-term-rentals"),
 "thessaloniki": (3,"registration+moratoire","2025/2026","national","oui","Registre AMA national (loi 5170/2025) + gel des nouvelles inscriptions dans le 1er district central dès 03/2026","news.gtp.gr/greece-str-restrictions-2026"),
 "boston": (2,"registration+primary-residence+licence","2019","ville","oui","Location courte durée limitée aux logements occupés par le propriétaire (résidence ≥9 mois/an), enregistrement annuel obligatoire","boston.gov/short-term-rentals"),
 "portland": (2,"registration+primary-residence+night-cap","2015","ville","partiel","Permis ASTR : résidence principale (≥270 jours/an), plafond 95 nuits/an d'absence de l'hôte ; enforcement perfectible","portland.gov/bds/astr-permits"),
 "victoria": (3,"primary-residence+registration","2024","état/province","oui","BC Short-Term Rental Act (05/2024) : courte durée restreinte à la résidence principale + 1 unité, licence, amendes 250-500$/jour","gov.bc.ca/short-term-rentals-principal-residence"),
 "columbus": (1,"registration+licence","2019","ville","oui","Permis STR obligatoire (Chapitre 598, <30 nuits) affiché sur l'annonce ; pas d'obligation stricte de résidence principale","columbus.gov/short-term-rental"),
 "quebec-city": (2,"registration+primary-residence+night-cap+moratoire","2024/2025","état/province","oui","Enregistrement CITQ (loi provinciale) + résidence principale 90 nuitées/an + gel temporaire des nouveaux établissements","citq.qc.ca"),
 "bergamo": (1,"registration+licence","2024/2025","national","partiel","CIN national (01/2025) + CIR régional + SCIA ; règlement communal qualité (11/2025) ; pas de plafond de nuits","comune.bergamo.it/locazione-breve-turistica"),
}

df = pd.read_csv(FLAG)
df["regl_annee"] = df["regl_annee"].astype("string")
for slug, (niv, typ, an, ech, enf, res, src) in R13.items():
    m = df["city"] == slug
    if m.any():
        df.loc[m, ["regl_niveau","regl_type","regl_annee","regl_echelle","regl_enforce","regl_resume","regl_source","regl_confiance"]] = \
            [niv, typ, an, ech, enf, res, src, "recherche"]

# Re-dérive TOUS les binaires depuis regl_type (idempotent) + re-extrait le plafond
t = df["regl_type"].fillna("").astype(str).str.lower()
df["regl_registration"] = t.str.contains("registration").astype(int)
df["regl_licence"]      = t.str.contains("licence").astype(int)
df["regl_night_cap"]    = t.str.contains("night-cap").astype(int)
df["regl_primary_res"]  = t.str.contains("primary-residence").astype(int)
df["regl_ban_zone"]     = (t.str.contains("ban") | t.str.contains("moratoire")).astype(int)
df["regl_min_stay30"]   = t.str.contains("min-stay").astype(int)
df["regl_levy"]         = t.str.contains("levy").astype(int)
def cap(s):
    nums = re.findall(r"(\d+)\s*(?:nuit(?:s|ées)?|jours|j)(?:/an|/année)?", str(s))
    return int(nums[-1]) if nums else pd.NA
df["regl_cap_nights"] = df["regl_resume"].map(cap).astype("Int64")
df["regl_niveau"] = df["regl_niveau"].astype(int)

cols = ["city","city_fr","continent","regl_niveau","regl_echelle","regl_annee","regl_enforce",
        "regl_registration","regl_licence","regl_night_cap","regl_cap_nights",
        "regl_primary_res","regl_ban_zone","regl_min_stay30","regl_levy",
        "regl_type","regl_resume","regl_source","regl_confiance",
        "pct_license","pct_reg_engage","str_minnuits30_pct","act_cal_ouvert_med","vol_n_ann"]
df = df[cols].sort_values(["regl_niveau","vol_n_ann"], ascending=[False, False])
df.to_csv(FLAG, index=False, encoding="utf-8-sig")

print(f"Flag complet : {len(df)} villes | confiance = {df['regl_confiance'].value_counts().to_dict()}")
print(f"Niveau : {df['regl_niveau'].value_counts().sort_index().to_dict()}")
print(f"Villes restées NON recherchées : {df[df.regl_confiance!='recherche'].city_fr.tolist() or 'AUCUNE'}")
print("\nMécanismes (villes) :", {c.replace('regl_',''): int(df[c].sum()) for c in ['regl_registration','regl_licence','regl_night_cap','regl_primary_res','regl_ban_zone','regl_min_stay30','regl_levy']})
print("\n--- Niveau 3 final ---")
print(", ".join(df[df.regl_niveau==3].city_fr.tolist()))
# &e &REGL_COMPLETE13_aaMAIN
