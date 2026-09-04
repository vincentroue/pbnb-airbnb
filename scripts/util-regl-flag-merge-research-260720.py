# &s &REGL_MERGE_RESEARCH_aaMAIN - Fusionne la recherche agents (63 villes) dans le flag régul
# Écrase le premier jet data par les données recherchées (sourcées) ; garde le data-proxy pour le reste.
# Ajoute colonnes regl_enforce + regl_resume. confiance = "recherche" pour les 63.
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
FLAG = BASE / "data" / "external" / "regl-flag-pbnb-cities-260720.csv"

# slug: (niveau, type, annee, echelle, enforce, resume, source)
R = {
 # --- Europe Sud ---
 "rome": (2,"registration+licence","2024/2025","national+ville","partiel","CIN national obligatoire 01/2025 (amendes 800-8000€) ; durcissement centre annoncé, pas en vigueur","taxing.it/national-identification-code-cin"),
 "milan": (2,"registration+licence","2024/2025","national+ville","partiel","CIN + CIR Lombardie ; interdiction key-box et check-in en personne dès 2026","euronews.com/travel/2025/12/05/milan-bans-key-boxes"),
 "madrid": (3,"primary-residence+licence+ban","2025","ville","oui","Plan RESIDE 08/2025 : VUT dispersés interdits centre intra-M30, 3053 logements radiés","iberian.property/madrid-reside-plan"),
 "lisbon": (3,"registration+moratoire","2024/2025","ville","oui","AL national ; suspension nouveaux AL depuis 11/2024 + plafond containment 10 %/quartier","realestate-lisbon.com/lisbon-suspension-al"),
 "athens": (3,"registration+ban","2025/2026","national+ville","oui","Registre AMA ; gel nouvelles immat. centre (1/2/3 arr.) jusqu'à 12/2026, amendes 40000€","greekcitytimes.com/2025/09/25/greece-airbnb-ban"),
 "barcelona": (3,"licence+ban","2024/2028","ville+région","oui","Aucune nouvelle licence HUT + non-renouvellement des ~10000 licences en 11/2028","idealista.com/barcelona-2028-deadline"),
 "florence": (3,"ban","2024/2025","ville","oui","Interdiction nouvelles LCD centre historique UNESCO (07/2024) + CIN national","magentaflorence.com/florence-airbnb-stop"),
 "budapest": (3,"ban","2024/2026","ville (6e arr.)","oui","Interdiction totale LCD dans le 6e arr. (Terézváros) dès 01/2026 suite référendum","balkaninsight.com/budapest-district-airbnb-ban"),
 "naples": (2,"registration+licence","2024/2025","national+ville+région","partiel","CIN + CIR Campanie + SCIA ; règle 70/30 par immeuble en périmètre UNESCO","en.ilsole24ore.com/naples-30-per-cent"),
 "prague": (1,"registration","2025/2026","national+UE","partiel","e-Turista (numéro unique) 2025, obligatoire 2026 ; pouvoirs locaux pas encore effectifs","expats.cz/prague-limit-airbnb-2025"),
 "porto": (2,"registration+moratoire","2024/2025","national+ville","oui","AL national ; containment 15 % paroisses centre historique ; ~1413 annulés","guestready.com/new-al-rules-porto"),
 "malaga": (3,"ban+moratoire","2024/2025","ville","oui","Interdiction nouvelles licences 43 quartiers + moratoire 3 ans (Décret 31/2024 Andalousie)","idealista.com/malaga-bans-43-neighbourhoods"),
 "venice": (3,"night-cap+registration","2024/2025","ville+national","partiel","CIN + seuil 120 nuits/an au-delà régime strict + check-in en personne obligatoire","campaignforalivingvenice.org/new-rules-str"),
 "sevilla": (3,"ban","2024","ville","oui","Plafond 10 %/quartier → aucune nouvelle licence Centro/Santa Cruz/Triana ; ~2100 retirées","theolivepress.es/sevilla-crackdown-tourist-flats"),
 "valencia": (3,"ban+moratoire","2024/2025","ville","oui","Interdiction de fait centre historique + moratoire 1 an ; règlement 05/2026 le plus restrictif d'Espagne","thelocal.es/valencia-holiday-let-limits"),
 "riga": (1,"registration","2024","national","non","Peu régulé : déclaration fiscale + taxe séjour, pas de plafond ni licence ; cadre en projet","em.gov.lv/short-term-rental-regulations"),
 "istanbul": (2,"licence+night-cap+primary-residence","2023/2024","national","oui","Loi 7464 (01/2024) : permis Tourisme + consentement copro unanime + cap 100 nuits/an","gvw.com/new-airbnb-law-turkey"),
 # --- Europe Ouest/Nord ---
 "london": (2,"night-cap+primary-residence","2015","ville (Greater London)","oui","Plafond 90 nuits/an logement entier (Deregulation Act 2015), SANS enregistrement","airbnb.com/help/article/1340"),
 "paris": (2,"primary-residence+night-cap+registration","2024/2025","ville+national","oui","Loi Le Meur 2024 : résidence principale 90 nuits/an + numéro d'enregistrement","welkeys.com/reglementation-airbnb-paris-2026"),
 "copenhagen": (2,"night-cap+primary-residence+registration","2019/2025","national","partiel","Logement entier 70 nuits/an (→100 municipalité) + résidence principale + CPR/fisc","airbtics.com/airbnb-rules-copenhagen"),
 "oslo": (2,"night-cap","2019","national","partiel","Plafond 90 nuits/an en copropriété (30 en coopérative d'habitation)","airbtics.com/airbnb-rules-oslo"),
 "vienna": (3,"night-cap+licence+registration","2024","ville","oui","Depuis 07/2024 : interdit zone résidentielle >90j sans licence d'exception ; amendes 50000€","fwp.at/new-rules-str-vienna-2024"),
 "berlin": (2,"primary-residence+registration+licence","2013/2018","ville","oui","Zweckentfremdungsverbot : résidence principale 90j/an + numéro ; secondaire souvent refusé","berlin.de/zweckentfremdungsverbot"),
 "amsterdam": (3,"night-cap+registration+licence+primary-residence","2021/2025","ville","oui","Plafond 30 nuits/an (15 au centre) + permis + numéro + notification/séjour + max 4 pers","amsterdam.nl/holiday-rentals-permit"),
 "greater-manchester": (0,"none","","ville/national (à venir)","non","Aucun plafond ni licence ; registre national anglais (classe C5) pas en vigueur","houst.com/short-term-regulation-manchester"),
 "dublin": (3,"primary-residence+night-cap+licence+registration","2019/2025","ville (RPZ)+national","partiel","Zone pression : logement entier 90j/an, au-delà permis rarement accordé ; registre Fáilte 05/2026","guestready.com/short-term-letting-dublin"),
 "lyon": (2,"primary-residence+night-cap+registration","2018/2026","ville","oui","Résidence principale 120→90 nuits (01/2026) + numéro ; changement d'usage hypercentre","keynest.com/reglementation-airbnb-lyon"),
 "edinburgh": (3,"licence+primary-residence+registration","2022/2024","ville+national (Écosse)","oui","Licence obligatoire toute LCD (échéance 01/2025) + zone de contrôle STL depuis 2022","gov.scot/publications/short-term-lets"),
 "munich": (2,"night-cap+registration+primary-residence","2017/2025","ville","oui","Zweckentfremdung : logement entier ~56j/an sans permis + numéro ; amendes 100000€","checkin-muenchen.de/landlord-info"),
 "stockholm": (0,"none","","national/coopératives","non","Pas de plafond ni licence municipale ; restrictions via coopératives (brf)","thelocal.se/airbnb-rules-sweden"),
 "brussels": (2,"registration+licence","2016/2024","région (Bruxelles-Capitale)","partiel","Enregistrement + déclaration dès la 1ère nuit ; campagne de régularisation 2023-2025","brussels.be/register-tourist-accommodation"),
 "zurich": (1,"registration","","ville (canton Zurich)","partiel","Peu de restrictions : déclaration hôtes ; plafond 90j seulement au stade d'initiative populaire","iamexpat.ch/zurich-restrictions-airbnb"),
 "bristol": (0,"none","","ville/national (à venir)","non","Aucun registre local ni plafond ; classe C5 + registre national anglais pas en vigueur","houst.com/airbnb-rules/bristol"),
 "antwerp": (1,"registration","2016/2025","région (Flandre)","partiel","Décret Logement flamand : déclaration Visit Flanders + numéro ; application faible","airbtics.com/airbnb-rules-antwerpen"),
 "geneva": (2,"night-cap+licence","2018","région (canton Genève, LDTR)","partiel","Plafond 90 nuits/an → au-delà professionnel + autorisation PCTN ; enforcement faible","ge.ch/rent-my-accommodation-airbnb"),
 # --- Amériques ---
 "rio-de-janeiro": (1,"registration","2025","ville","non","Enregistrement municipal (PL 372/2025) + autorisation copro ; application quasi nulle","riotimesonline.com/rio-airbnb-bill-2026"),
 "mexico-city": (2,"registration+night-cap","2024","ville","partiel","Loi Airbnb 2024 : registre + plafond 180 nuits/an (≤50 % de l'année)","mexiconewsdaily.com/airbnb-180-days"),
 "buenos-aires": (1,"registration","2025","ville","non","Loi 6255 : registre ATT + taxe touristique 02/2025 ; ~0 % enregistrés","infobae.com/registro-alquiler-temporario"),
 "new-york-city": (3,"registration+primary-residence+ban","2023","ville","oui","LL18 (09/2023) : hôte présent, pas de logement entier <30j ; offre ~38000→3000","nyc.gov/registration-law"),
 "los-angeles": (2,"registration+primary-residence+night-cap","2019","ville","oui","Home-Sharing Ordinance : résidence principale + plafond 120 nuits/an ; amendes lourdes","planning.lacity.gov/home-sharing"),
 "toronto": (2,"registration+primary-residence+night-cap","2020","ville","oui","Enregistrement + résidence principale ; logement entier 180 nuits/an","toronto.ca/short-term-rentals"),
 "san-diego": (2,"registration+licence+night-cap","2023","ville","oui","Licence STRO 4 paliers (2023) : logement entier ~1 % du parc via loterie","sandiego.gov/short-term-residential-occupancy"),
 "austin": (1,"registration+licence","2016","ville","partiel","Licence STR mais restrictions Type 2 invalidées par tribunaux (Texas), contrôle faible","austintexas.gov/short-term-rentals"),
 "montreal": (2,"registration+primary-residence","2023","province","oui","Loi 25 (Québec) : enregistrement CITQ ; hors résidence principale zonage ; conformité ~90 %","citq.qc.ca"),
 "nashville": (1,"registration+licence","2018","ville","partiel","Permis STRP ; nouveaux non-occupant interdits zones résid. mais droits acquis (Tennessee)","nashville.gov/short-term-rentals"),
 "chicago": (1,"registration+licence","2016","ville","oui","Shared Housing Ordinance : numéro d'enregistrement ; pas de plafond de nuits général","chicago.gov/shared-housing"),
 "seattle": (2,"registration+licence","2019","ville","oui","Licence opérateur (numéro affiché) plafonnant à 2 logements/hôte sauf legacy/Downtown","seattle.gov/short-term-rentals"),
 "new-orleans": (3,"licence+primary-residence+moratoire","2023","ville","oui","Ordonnance 2023 : occupant du lot, 1 permis/îlot via loterie, moratoire commercial","nola.gov/short-term-rental-administration"),
 "san-francisco": (2,"registration+primary-residence+night-cap","2015","ville","oui","Registre ; résidence principale ≥275j ; plafond 90 nuits/an non hébergé","sfplanning.org/str"),
 "washington-dc": (2,"licence+primary-residence+night-cap","2019","ville","oui","Licence depuis résidence principale + plafond 90 nuits/an non hébergé","dlcp.dc.gov/short-term-rental"),
 "dallas": (1,"registration","2023","ville","non","Interdiction 2023 bloquée par injonction (Cour suprême Texas) ; enregistrement seul","keranews.org/dallas-str-ban-block"),
 "vancouver": (3,"registration+licence+primary-residence","2024","province","oui","Loi provinciale C.-B. (05/2024) : résidence principale + double licence (ville+province)","vancouver.ca/short-term-rentals"),
 "asheville": (3,"ban+primary-residence","2018","ville","oui","Logement entier interdit hors zones resort depuis 2018 ; homestays occupés seulement","ashevillenc.gov/short-term-rental-violations"),
 "fort-worth": (3,"ban+registration","2023","ville","oui","Interdiction STR zones résidentielles (2023), validée en justice 2025","fortworthtexas.gov/short-term-rentals"),
 "oakland": (0,"none","","ville","non","Pas d'ordonnance STR dédiée (TOT 14 %) ; règlement en préparation 2026","oaklandca.gov/short-term-rental-regulations"),
 # --- APAC + Afrique ---
 "tokyo": (2,"registration+night-cap","2018","national/territorial","oui","Loi Minpaku (2018) : enregistrement + plafond 180 nuits/an ; enforcement forte","airbnb.com/help/article/3819"),
 "bangkok": (3,"ban+min-stay+licence","2004","national","partiel","Hotel Act : <30j illégal sans licence hôtel ; contournement min 30 nuits","reproperty.co.th/airbnb-legal-thailand"),
 "melbourne": (2,"night-cap-levy","2025","état/région","oui","Victoria : prélèvement 7,5 % sur réservations <28j depuis 01/2025 ; copro peut interdire","parliament.vic.gov.au/short-stay-levy"),
 "sydney": (2,"registration+night-cap","2021","état/région","oui","STRA NSW : enregistrement + plafond 180 nuits/an non hébergé (Grand Sydney)","planning.nsw.gov.au/short-term-rental-accommodation"),
 "hong-kong": (3,"licence+ban","1991","territorial","oui","Ordinance Cap.349 : licence obligatoire <28j ; sans = illégal (amende 200000 HKD + prison)","elegislation.gov.hk/hk/cap349"),
 "taipei": (3,"ban+licence","2001","national/territorial","partiel","<30j interdit sans licence hôtel/minsu ; contrôles renforcés 2025-2026","travel.taipei/news/details/67191"),
 "brisbane": (1,"registration","2022","ville","partiel","Permissif : surtaxe foncière ~+50 % usage court ; projet de permis abandonné","houst.com/brisbane-short-stay-rules"),
 "cape-town": (1,"registration","2019","ville","non","By-law 2019 (max 30j/hôte) via zonage, quasi non appliqué ; enregistrement prévu mi-2026","houst.com/short-term-regulation-cape-town"),
}

df = pd.read_csv(FLAG)
for col in ["regl_enforce", "regl_resume"]:
    if col not in df.columns:
        df[col] = ""
df["regl_annee"] = df["regl_annee"].astype("string")

n = 0
for slug, (niv, typ, an, ech, enf, res, src) in R.items():
    m = df["city"] == slug
    if m.any():
        df.loc[m, "regl_niveau"] = niv
        df.loc[m, "regl_type"] = typ
        df.loc[m, "regl_annee"] = an
        df.loc[m, "regl_echelle"] = ech
        df.loc[m, "regl_enforce"] = enf
        df.loc[m, "regl_resume"] = res
        df.loc[m, "regl_source"] = src
        df.loc[m, "regl_confiance"] = "recherche"
        n += 1

df["regl_niveau"] = df["regl_niveau"].astype(int)
cols = ["city", "city_fr", "continent", "regl_niveau", "regl_type", "regl_annee", "regl_echelle",
        "regl_enforce", "regl_resume", "regl_source", "regl_confiance",
        "pct_license", "pct_reg_engage", "str_minnuits30_pct", "act_cal_ouvert_med", "vol_n_ann"]
df = df[cols].sort_values(["regl_niveau", "vol_n_ann"], ascending=[False, False])
df.to_csv(FLAG, index=False, encoding="utf-8-sig")
print(f"{n} villes mises à jour par la recherche (sur {len(df)}).")
print("Confiance :", df["regl_confiance"].value_counts().to_dict())
print("Niveau    :", df["regl_niveau"].value_counts().sort_index().to_dict())
print("\n--- Niveau 3 (interdiction/moratoire/licence hôtelière) ---")
print(", ".join(df[df.regl_niveau == 3].city_fr.tolist()))
print("\n--- Villes restées en 'data' (non recherchées) ---")
print(", ".join(df[df.regl_confiance != "recherche"].city_fr.tolist()))
# &e &REGL_MERGE_RESEARCH_aaMAIN
