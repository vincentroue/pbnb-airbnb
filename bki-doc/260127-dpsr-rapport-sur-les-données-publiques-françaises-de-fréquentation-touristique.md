---
ukp: |

aliases: []
dcr: 26-02-03_110847734
codx:
tags: []
pry: x
stf: x
sts: x
---

cnt::
url:: https://claude.ai/chat/8bd58ec8-0d6a-437d-9da6-6a4324a0633b

# Données publiques françaises de fréquentation touristique : inventaire et méthodologie

# Données publiques françaises de fréquentation touristique : inventaire et méthodologie

Les données de fréquentation touristique en France reposent sur un dispositif statistique structuré autour de **l'enquête mensuelle EFHCT de l'INSEE**, complétée par des sources complémentaires (DGE, Atout France, observatoires régionaux). Pour un observatoire territorial basé sur les 306 zones d'emploi, la principale difficulté réside dans la **granularité géographique** : les données de fréquentation s'arrêtent au niveau départemental, tandis que seules les capacités d'hébergement sont disponibles à l'échelle communale. L'estimation de la population présente nécessite de combiner ces sources avec les données sur les résidences secondaires du recensement et, potentiellement, les nouvelles approches par téléphonie mobile.

---

## L'enquête EFHCT constitue la source principale de fréquentation

Depuis 2019, l'INSEE a fusionné ses trois enquêtes distinctes (hôtels, campings, autres hébergements collectifs) en une seule opération : l'**Enquête de fréquentation des hébergements collectifs de tourisme (EFHCT)**. Cette enquête mensuelle constitue la pierre angulaire du dispositif statistique français.

Le champ couvert comprend trois segments d'hébergement : les **hôtels de tourisme** (classés et non classés, >5 chambres), les **campings classés** (hors résidentiels, avril-septembre uniquement), et les **autres hébergements collectifs** (résidences de tourisme, villages vacances, auberges de jeunesse, centres sportifs). L'échantillon atteint environ **12 000 hôtels** sur 18 000, soit un taux de sondage de 70%, avec une stratification par région, espace touristique national (ETN), catégorie et type d'établissement.

Les variables collectées incluent l'occupation quotidienne des chambres/emplacements, les arrivées et nuitées selon le pays de résidence des touristes, la durée moyenne de séjour, la part du tourisme d'affaires (hôtels uniquement), et le chiffre d'affaires hébergement. Les séries sont **comparables depuis 2010** suite à la rétropolation liée au nouveau classement Atout France.

Un élément critique pour votre projet : les données de fréquentation ne descendent pas en dessous du **niveau départemental**. Seules les capacités d'accueil sont disponibles à l'échelle communale.

---

## Indicateurs disponibles et granularité géographique

Le tableau suivant synthétise les indicateurs clés par niveau géographique :

| Indicateur | National | Régional | Départemental | Communal |
|-----------|----------|----------|---------------|----------|
| Nuitées totales | ✓ mensuel | ✓ mensuel | ✓ mensuel | ✗ |
| Arrivées touristes | ✓ mensuel | ✓ mensuel | ✓ hôtels/campings | ✗ |
| Taux d'occupation | ✓ mensuel | ✓ mensuel | ✓ hôtels | ✗ |
| Origine France/étranger | ✓ | ✓ | ✓ hôtels | ✗ |
| Détail par pays | ✓ | Partiel | ✗ | ✗ |
| Capacité (lits/chambres) | ✓ | ✓ | ✓ | ✓ annuel |
| Nombre établissements | ✓ | ✓ | ✓ | ✓ |

Les **espaces touristiques nationaux** (ETN) constituent une stratification géographique intermédiaire depuis 2013 : Île-de-France, Littoral, Montagne, Urbain de province, Rural/Autres. Cette classification peut enrichir l'analyse de votre observatoire pour les zones d'emploi correspondant à ces typologies.

La profondeur historique des séries varie selon les indicateurs. Les données de capacité communale sont disponibles depuis **2013**. Les séries de fréquentation mensuelles comparables remontent à **2010**, avec une rupture méthodologique en 2019 (nouvelle méthode d'imputation des non-réponses).

---

## Méthodes d'estimation de la population présente

L'estimation de la population réellement présente sur un territoire constitue un enjeu majeur pour les territoires touristiques. Les travaux de référence sont ceux de **Christophe Terrier** (Direction du Tourisme/INSEE, 2006), qui a développé la notion d'**économie présentielle** et produit des estimations jour par jour de la population présente dans chaque département métropolitain.

La formule fondamentale est :
> **Population présente = Population résidente − Résidents absents + Non-résidents présents**

Pour l'appliquer, trois sources doivent être combinées :
- **Enquête SDT** (Suivi de la Demande Touristique) : panel de 20 000 personnes mesurant la mobilité touristique des résidents français, incluant l'hébergement non marchand (famille, amis, résidences secondaires représentant **62% des nuitées** en 2020)
- **Enquête EFHCT** : nuitées en hébergement collectif marchand
- **Enquête EVE** (Banque de France) : flux de touristes étrangers aux frontières

Les **résidences secondaires** représentent un enjeu particulier : la France compte **3,7 millions** de logements classés résidences secondaires au recensement 2024, concentrés sur le littoral (50% en Nouvelle-Aquitaine sur la façade atlantique) et en montagne. La convention INSEE attribue **5 lits** par résidence secondaire. Ces résidences représentent **les trois quarts des lits touristiques** français mais leur taux d'occupation reste difficile à mesurer.

Les **données de téléphonie mobile** offrent une approche innovante explorée par le projet MobiTic (ANR, depuis 2020) associant INSEE, Orange Labs et plusieurs universités. Les applications pendant le COVID-19 ont démontré la faisabilité : Paris a vu sa population diminuer de **450 000 à 610 000 personnes** (-20 à -25%) pendant le premier confinement. Ces données permettent une granularité à l'échelle intercommunale avec mise à jour quotidienne, mais restent expérimentales et dépendantes de partenariats avec les opérateurs.

---

## Sources publiques complémentaires à l'INSEE

**La Direction Générale des Entreprises (DGE)** publie annuellement le **Mémento du tourisme**, synthèse de référence incluant la consommation touristique intérieure (7,25% du PIB), l'emploi touristique (1,3 million de salariés) et le compte satellite du tourisme. L'**enquête EVE** (60 000 non-résidents interrogés/an aux frontières) fournit les données sur les touristes étrangers : origine, durée de séjour, dépenses, satisfaction.

**Atout France** pilote le dispositif **France Tourisme Observation (FTO)**, plateforme de données partagées comprenant le baromètre HPA (suivi hebdomadaire des campings), City Trends (indicateurs pour 15 grandes agglomérations) et l'Observatoire Mutualisé du Locatif. Les notes de conjoncture mensuelles sont accessibles gratuitement.

Les **Comités Régionaux du Tourisme** constituent des relais territoriaux essentiels. Les CRT Provence-Alpes-Côte d'Azur, Centre-Val de Loire et Bourgogne-Franche-Comté offrent des observatoires particulièrement documentés avec données de fréquentation régionale et départementale, enquêtes clientèles et études thématiques. Le dispositif **Flux Vision Tourisme** (partenariat Orange Business / ADN Tourisme depuis 2013) analyse les données mobiles anonymisées pour estimer les nuitées tous hébergements confondus ; ces données sont utilisées par 11 CRT et 73 CDT.

Concernant les **plateformes de location courte durée**, Eurostat collecte depuis 2020 des données agrégées auprès d'Airbnb, Booking, Expedia et Tripadvisor : **192 millions de nuitées** en France en 2024 via ces plateformes. Inside Airbnb (projet indépendant) fournit des données scrappées téléchargeables pour Paris, Lyon et Bordeaux sous licence Creative Commons.

---

## Impact COVID et tendances structurelles

L'année 2020 a provoqué un effondrement historique : **-50% de nuitées hôtelières** par rapport à 2019, avec un impact encore plus sévère en Île-de-France (-65 à -68%) et pour l'hôtellerie haut de gamme (-73,7%). La reprise s'est amorcée en 2022 (+3% au-dessus du niveau 2019 pour hôtels et campings) et 2024 a établi un nouveau record avec **451 millions de nuitées** en hébergements collectifs.

Plusieurs changements structurels post-COVID méritent attention pour un observatoire territorial :
- **Explosion du tourisme de proximité** : +10 millions de nuitées résidents en juillet 2020 vs 2019
- **Report vers l'hébergement non-marchand** : 62% des nuitées chez famille/amis/résidence secondaire en 2020
- **Montée en gamme des campings** : +25,3% dans les 4-5 étoiles entre 2019 et 2024
- **Effondrement durable du tourisme d'affaires** : part passée de 48% à 31,5% des nuitées hôtelières en Île-de-France
- **Croissance des locations courte durée** : volume doublé 2018-2024, **1,31 million d'annonces Airbnb** actives mensuellement

Sur la longue période, la concentration géographique reste marquée : le littoral concentre **40% de l'hébergement touristique** métropolitain. Trois régions (Nouvelle-Aquitaine, Occitanie, PACA) totalisent plus de 54% des nuitées camping.

---

## Application aux 306 zones d'emploi : guide méthodologique

Le zonage en 306 zones d'emploi (ZE2020) définit des espaces où la plupart des actifs résident et travaillent (taux de stabilité cible : 70%). Les tailles varient considérablement : de moins de 10 000 emplois à **4,2 millions pour Paris**. L'INSEE a identifié 7 profils économiques dont un profil **zones touristiques** (exemple : Sainte-Maxime).

Pour intégrer la dimension touristique à votre observatoire, la **table de passage commune → zone d'emploi** est essentielle (téléchargeable sur insee.fr, mise à jour janvier 2025). Les données communales de capacité d'hébergement peuvent être directement agrégées par zone d'emploi. Pour les données de fréquentation (disponibles uniquement au niveau départemental), une **ventilation proportionnelle** est nécessaire, au prorata de la capacité d'hébergement des communes de chaque zone d'emploi dans le département.

Les indicateurs calculables pour chaque zone d'emploi comprennent :
- **Taux de fonction touristique** = Lits touristiques / Population résidente × 100
- **Pression touristique annuelle** = Nuitées totales estimées / Population résidente
- **Indice de saisonnalité** = Emploi touristique mois pic / Emploi touristique mois creux
- **Population présente estimée** = Pop. résidente × (1 - taux départ résidents) + (Nuitées touristes / 30)

Les zones d'emploi à forte saisonnalité identifiables incluent Briançon, Gap, Sainte-Maxime (profil touristique INSEE), Challans (22,7% emplois saisonniers hébergement-restauration), et les zones littorales corses (emploi touristique ×4 entre janvier et août).

---

## Liens d'accès aux données principales

| Source | Contenu | URL |
|--------|---------|-----|
| INSEE - Capacités communales | Lits par type d'hébergement, par commune | insee.fr/fr/statistiques/2021703 |
| INSEE - Fréquentation mensuelle | Nuitées, arrivées, taux d'occupation | insee.fr/fr/statistiques/2012672 |
| INSEE - Table passage ZE | Correspondance commune→zone d'emploi | insee.fr/fr/information/4652957 |
| INSEE - Métadonnées EFHCT | Documentation méthodologique | insee.fr/fr/metadonnees/source/serie/s1039 |
| data.gouv.fr - Tourisme | Jeux de données fréquentation | data.gouv.fr/datasets/frequentations-touristiques |
| DGE - Mémento tourisme | Synthèse annuelle | entreprises.gouv.fr/fr/etudes-et-statistiques |
| Atout France - FTO | Notes conjoncture, indicateurs | atout-france.fr/fr/fto-22 |
| ADN Tourisme - Flux Vision | Nuitées téléphonie mobile | adn-tourisme.fr/nuitees-touristiques-francais-2023 |
| Inside Airbnb | Données Airbnb Paris/Lyon/Bordeaux | insideairbnb.com/get-the-data |

---

## Limites et précautions d'usage

Plusieurs limitations structurelles doivent guider l'interprétation des données. **L'hébergement non marchand** (famille, amis) représente près de 40% des nuitées des résidents français mais n'est mesuré que par enquête déclarative (SDT). Les **locations entre particuliers** (Airbnb) ne sont pas incluses dans les enquêtes EFHCT, seules les données Eurostat agrégées au niveau régional sont disponibles. Les **résidences secondaires** sont recensées mais leur taux d'occupation reste inconnu.

La **discontinuité géographique** entre capacités (communales) et fréquentation (départementale) impose des hypothèses de ventilation pour calculer des indicateurs à l'échelle zone d'emploi. Les **ruptures de série** (2010, 2019, COVID 2020-2021) limitent les analyses de tendances longues. Enfin, les données de **téléphonie mobile** restent expérimentales et non accessibles en routine.

Pour un observatoire territorial robuste, la recommandation est de privilégier les indicateurs de **capacité et de structure** (taux de fonction touristique, part hébergement marchand) directement calculables à l'échelle zone d'emploi, et d'utiliser les indicateurs de **fréquentation** comme ordres de grandeur pour les analyses comparatives inter-zones, en documentant explicitement les hypothèses de ventilation appliquées.
