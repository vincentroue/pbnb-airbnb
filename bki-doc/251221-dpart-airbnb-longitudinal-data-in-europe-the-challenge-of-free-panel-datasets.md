---
ukp: |

aliases: []
dcr: 26-02-03_110847837
codx:
tags: []
pry: x
stf: x
sts: x
---

cnt::
url:: https://claude.ai/chat/ff264692-5de5-4250-bfbf-4d11049f5fab

# Airbnb Longitudinal Data in Europe: The Challenge of Free Panel Datasets

# Données Airbnb longitudinales Europe : l'impasse des panels gratuits

**Verdict principal** : Aucun dataset panel multi-années consolidé et gratuit n'existe dans les dépôts académiques pour l'Europe. Inside Airbnb limite volontairement l'accès aux données historiques au-delà de 12 mois, et le célèbre dataset Kaggle "Airbnb Prices in European Cities" est un **snapshot unique**, non exploitable pour une analyse temporelle. La solution viable pour votre capstone : compiler vous-même un panel à partir des archives Inside Airbnb (disponibles depuis 2015 pour Paris, Berlin, Amsterdam).

---

## Pourquoi Inside Airbnb ne fournit pas de données gratuites 2018-2024

La politique officielle d'Inside Airbnb est explicite : seuls les **12 derniers mois** de données trimestrielles sont accessibles gratuitement. Cette restriction n'est pas technique mais stratégique.

**Raisons de l'archivage restrictif** : Le projet, fondé par Murray Cox, est un projet activiste financé principalement par donations. Les données historiques représentent une ressource monétisable pour assurer la pérennité du projet. La priorité d'accès va aux militants du logement, journalistes et associations communautaires — les usages académiques ou commerciaux sont secondaires. Toute demande de données archivées passe par un formulaire de requête évaluant l'identité du demandeur, le volume demandé et l'alignement avec la mission du projet. Des frais peuvent être exigés.

**Contraintes légales du scraping Airbnb** : Les Conditions d'Utilisation d'Airbnb interdisent explicitement le scraping. Cependant, l'arrêt *HiQ Labs v. LinkedIn* (9ème Circuit, USA) établit que le scraping de données publiques ne constitue pas un "piratage" au sens du Computer Fraud and Abuse Act. En Europe, le RGPD ne prohibe pas le scraping en soi, mais impose des obligations strictes (base légale, minimisation, limitation de conservation) dès lors que des données personnelles sont collectées. Une décision de la DPC irlandaise contre Airbnb (2023) a d'ailleurs sanctionné la plateforme pour rétention excessive de documents d'identité.

**Alternatives pour récupérer des données historiques** :

| Source | Période couverte | Coût | Faisabilité |
|--------|------------------|------|-------------|
| Archives Tom Slee | 2013-2017 | Gratuit | Téléchargement direct (tomslee.net) |
| Requête Inside Airbnb | 2015-présent | Variable (potentiellement payant) | Demande via data@insideairbnb.com |
| Wayback Machine | Incertain | Gratuit | Très faible (CSV rarement archivés) |
| Harvard Dataverse | 2014-2019 (Boston seulement) | Gratuit | Non applicable Europe |
| AirDNA | 2015-présent | Commercial (~$149-1600/mois) | Haute qualité mais onéreux |

**Wayback Machine : verdict** — La récupération des CSV Inside Airbnb via Internet Archive est techniquement improbable. Les fichiers volumineux et les structures profondes ne sont généralement pas crawlés. Aucun cas documenté de récupération réussie n'a été identifié.

---

## Le mythe des datasets Kaggle multi-années

La vérification critique du dataset "**Airbnb Prices in European Cities**" (thedevastator) révèle une réalité décevante pour l'analyse temporelle.

**Verdict : SNAPSHOT UNIQUE — PAS UN PANEL**

Ce dataset, très populaire sur Kaggle, provient des travaux de Gyódi & Nawaro (Zenodo DOI: 10.5281/zenodo.4446043). Il couvre **10 villes européennes** (Amsterdam, Athènes, Barcelona, Berlin, Budapest, Lisbonne, Londres, Paris, Rome, Vienne) avec **~51 707 annonces**. Cependant :

- **Aucune colonne temporelle** : pas de scrape_date, collection_date, ou variable de date quelconque
- **Collection unique** : fin 2019/début 2020
- **Les fichiers weekday/weekend sont trompeurs** : il s'agit de scénarios tarifaires, pas de périodes différentes
- Impossible de suivre l'évolution des prix, les entrées/sorties d'annonces, ou toute dynamique temporelle

**Autres datasets Kaggle vérifiés** — Tous dérivés de la même source Gyódi/Nawaro :
- "Airbnb Cleaned Europe Dataset" (dipeshkhemani) → même snapshot
- "Airbnb Price Determinants in Europe" → même snapshot
- "airbnb_europe_sample_dataset_2021" → même snapshot

**Conclusion Kaggle** : Pour une analyse longitudinale européenne, Kaggle n'offre aucune solution viable. Il faut aller directement à la source (Inside Airbnb).

---

## Datasets panel RÉELS : état des lieux académique

Après recherche exhaustive sur Zenodo, Harvard Dataverse, Figshare, OSF et ICPSR, le constat est sans appel : **aucun dataset panel européen multi-années consolidé avec DOI n'existe en accès libre**.

**Ce qui existe dans la littérature académique** (données NON publiées) :

| Étude | Source données | Période | Couverture | Accessibilité |
|-------|----------------|---------|------------|---------------|
| Milone et al. (2023) Tourism Management | AirDNA | Jan 2019 - Déc 2020 | 130 999 listings, 27 pays UE | ❌ Commercial |
| Gunter et al. (2024) Tourism Economics | AirDNA | Jan 2017 - Déc 2020 | 43 pays européens | ❌ Commercial |
| Demir & Zoğal (2023) | Inside Airbnb compilé | 2020 | 40 villes, 17 pays | ❌ Non déposé |
| Todd et al. (2022) London | CDRC/AirDNA | Jan 2015 - Mai 2018 | Inner London | ❌ Accès restreint |

**La seule source exploitable** reste Inside Airbnb avec compilation manuelle des snapshots trimestriels. Les archives remontent à **2015** pour Paris, Berlin, Amsterdam, Barcelona, Londres, Rome avec couverture complète.

---

## Projets GitHub avec vraie analyse temporelle

Plusieurs projets démontrent la faisabilité d'analyses temporelles à partir d'Inside Airbnb, bien que majoritairement centrés sur des villes non-européennes.

**Analyse impact COVID-19** :

| Projet | URL | Données | Villes | Méthodologie |
|--------|-----|---------|--------|--------------|
| huskyjp/airbnb-covid-analysis | github.com/huskyjp | Inside Airbnb + AirDNA | Londres, Tokyo, Melbourne, Seattle | Comparaison pré/post pandémie, multi-continents |
| bf108/London_Airbnb_Review | github.com/bf108 | Inside Airbnb 2019-2020 | Londres | Saisonnalité + impact COVID sur occupation |
| farrellwahyudi/Singapore-Analysis | github.com/farrellwahyudi | Inside Airbnb 2018-2022 | Singapour | Panel 4 ans, évolution occupation |
| Franky007Bond/Munich-Analysis | github.com/Franky007Bond | Inside Airbnb →mars 2020 | Munich | Évolution demande temporelle |

**Time series et prévision prix** :

| Projet | URL | Méthodologie | Période |
|--------|-----|--------------|---------|
| Zhitaow/Airbnb-Data-Analysis | github.com/Zhitaow | Patterns temporels, prédiction taux réservation | 2015-2016 Boston/Seattle |
| samuelklam/airbnb-pricing-prediction | github.com/samuelklam | Saisonnalité via calendar.csv | NYC année complète |
| psanghal/Inside-AirBNB-Dataset | github.com/psanghal | Forecasting prix/disponibilité multi-villes | Seattle, NYC, SF |

**Pipelines de données pour panel** (les plus utiles pour votre capstone) :

- **aditya-prasad-projects/Data-Pipeline-for-analyzing-Inside-Airbnb-dataset** : Pipeline Apache Airflow + Spark pour ingestion mensuelle depuis 2015+, structure scalable multi-villes
- **dingluo1205/AirbnbDataPipeline** : ETL Airflow → Redshift pour mises à jour mensuelles (Boston, NYC, Seattle)

---

## Publications académiques avec méthodologies réplicables

Pour une analyse d'impact réglementaire, plusieurs études offrent des cadres méthodologiques directement applicables.

**Études diff-in-diff sur réglementations européennes** :

**Berlin — Zweckentfremdungsverbot** : L'étude de Duso, Michelsen, Schäfer & Tran (DIW Berlin, 2024) constitue la référence. Elle exploite les chocs politiques de 2016 et 2018 avec une méthodologie difference-in-differences combinant données Inside Airbnb (2015-2020) et données du marché locatif. Les données de réplication peuvent être demandées aux auteurs.

**Amsterdam, Berlin, Londres** : Hübscher et al. (2023) analysent les snapshots d'août 2015-2020 pour comparer les trajectoires réglementaires des trois capitales plus 9 autres villes européennes. Données Inside Airbnb publiques utilisables.

**Barcelona — PEUAT zoning** : Garcia-López et al. (2024) utilisent des méthodes spatio-temporelles pour évaluer les restrictions zonales. Données Inside Airbnb multi-années.

**Dates clés des réglementations pour design d'étude** :

| Ville | Réglementation | Date d'effet | Type d'étude possible |
|-------|----------------|--------------|----------------------|
| Berlin | Zweckentfremdungsverbot | Mai 2014 (appliqué 2016) | Diff-in-diff |
| Berlin | Renforcement | 2018 | Second choc |
| Barcelona | Zonage PEUAT | 2017 | Diff-in-diff spatial |
| Amsterdam | Plafond 30 nuits | 2019 | Avant/après |
| Paris | Limite 120 jours | 2017 | Restriction temporelle |
| France | Loi ELAN | Nov 2018 | Diff-in-diff national |

---

## Solution pratique pour votre capstone

**Stratégie recommandée en 4 étapes** :

**1. Compilation du panel Inside Airbnb** — Téléchargez les snapshots trimestriels pour vos villes cibles (Paris, Berlin, Amsterdam recommandés pour densité de données et variété réglementaire). Matchez les annonces par `listing_id` à travers le temps. Période réaliste : 2018-2024 (environ 24 snapshots par ville).

**2. Enrichissement avec calendar.csv** — Chaque snapshot inclut un fichier calendrier avec prix quotidiens sur 365 jours. Permet d'analyser la saisonnalité et les patterns de pricing prospectif.

**3. Variables externes** — Intégrez les dates de chocs réglementaires (loi ELAN novembre 2018, restrictions COVID mars 2020-2021), indices de loyers locaux (Idealista pour Paris, Immobilienscout24 pour Berlin), données touristiques (nuitées hôtelières Eurostat).

**4. Méthodologies suggérées** :
- **Panel fixed effects** : contrôle des caractéristiques invariantes des annonces
- **Difference-in-differences** : comparaison villes régulées vs. non-régulées
- **SARIMA/Prophet** : prévision et décomposition saisonnière
- **Event study** : analyse pré-trend et effets dynamiques autour des chocs

---

## Sources alternatives pour données pré-2018

**Archive Tom Slee** (tomslee.net/airbnb-data-collection-get-the-data) : Données 2013-2017 pour 100+ villes incluant Paris (novembre 2013 - juillet 2017), Londres, Barcelona, Berlin. Téléchargement direct CSV. Variables : room_id, host_id, room_type, neighborhood, reviews, rating, price, coordinates.

**Contact chercheurs McGill UPGo** : Le laboratoire de David Wachsmuth dispose de ~10 milliards de points de données Airbnb/HomeAway. Pas de dépôt public mais partage possible pour collaboration académique.

---

## Conclusion

L'absence de datasets panel gratuits consolidés pour l'Europe reflète la nature activiste d'Inside Airbnb et la valeur commerciale des données longitudinales. Les datasets Kaggle fréquemment cités sont des mirages pour l'analyse temporelle — tous sont des snapshots uniques.

**Votre chemin le plus viable** : compiler manuellement 24+ snapshots Inside Airbnb (2018-2024) pour Paris, Berlin et Amsterdam, en suivant le modèle des pipelines GitHub existants. Cette approche reproduit exactement la méthodologie des publications académiques les plus rigoureuses (Duso et al., Hübscher et al.), tout en restant dans le cadre gratuit de la licence CC BY 4.0 d'Inside Airbnb. Comptez 2-3 jours pour l'acquisition et le nettoyage initial des données — investissement raisonnable pour un capstone avec analyse d'impact réglementaire crédible.
