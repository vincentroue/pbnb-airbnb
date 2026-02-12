---
ukp: |

aliases: []
dcr: 26-02-03_110847011
codx:
tags: []
pry: x
stf: x
sts: x
---

cnt::
url:: https://claude.ai/chat/40cbcf1f-afaa-4204-ab4c-36c3202027c2

# Ressources méthodologiques pour l'analyse territoriale et la pression touristique Airbnb

# Ressources méthodologiques pour l'analyse territoriale et la pression touristique Airbnb

**Les études territoriales françaises récentes offrent un arsenal méthodologique robuste pour analyser la mobilité résidentielle**, tandis que la littérature internationale sur Inside Airbnb fournit des techniques d'analyse spatiale directement applicables à l'étude de la pression touristique. Ce rapport identifie les publications clés des deux champs et établit ce qui est réalisable avec trois snapshots trimestriels à l'échelle IRIS ou arrondissement.

---

## Les travaux INSEE et INRAE constituent la référence méthodologique française

L'article de **Breuillé, Le Gallo & Verlhiac (2022)** publié dans *Économie et Statistique* représente la référence la plus pertinente pour l'analyse des flux migratoires résidentiels récents. Cette étude utilise des **modèles logit simples et emboîtés** sur les données MeilleursAgents (2019-2021) pour analyser les intentions de mobilité post-Covid selon les aires d'attraction des villes. Les auteurs démontrent une augmentation significative du souhait de migrer vers les zones rurales après le premier confinement, avec des effets différenciés selon les profils socio-économiques.

Le programme **POPSU Territoires "Exode urbain : un mythe, des réalités"** (2021-2023), coordonné par la même équipe INRAE-CESAER, prolonge ces travaux avec une méthodologie mixte combinant modèles logit sur données SeLoger et analyse qualitative de six terrains d'enquête. L'outil cartographique **PopFlux** permet de visualiser les flux migratoires à l'échelle des aires d'attraction. Le programme conclut à l'absence d'exode urbain massif mais identifie une amplification des tendances préexistantes : périurbanisation, renaissance rurale sélective et littoralisation.

Pour les **modèles multiniveaux**, la référence méthodologique reste l'ouvrage de Daniel Courgeau (INED, 2004) *Du groupe à l'individu : synthèse multiniveau*, actualisé par le manuel pratique de Bringé & Golaz (2023) avec applications SAS, Stata et R. Ces ouvrages détaillent la séparation entre effets de composition et effets de contexte, central pour distinguer si les différences territoriales proviennent des caractéristiques des résidents ou des propriétés intrinsèques des lieux.

---

## France Stratégie et l'Observatoire des territoires documentent les dynamiques spatiales

La **note d'analyse n°92 de France Stratégie** (Botton et al., 2020) sur l'évolution de la ségrégation résidentielle en France constitue un modèle d'analyse quantitative à l'échelle IRIS. L'étude calcule des **indices de ségrégation** (indice de dissimilarité 0-100) sur les données Saphir harmonisées 1990-2015 pour **55 unités urbaines de plus de 100 000 habitants**. Les résultats montrent une ségrégation stable pour les catégories sociales mais en baisse pour le logement social (-11 points). Une datavisualisation interactive accompagne la publication.

Le **7e Rapport de l'Observatoire des territoires** (2018) reste le document de référence sur les mobilités résidentielles françaises. Il établit que 11% des Français changent de logement chaque année (7,3 millions de personnes) dont trois quarts restent dans le même département. L'analyse cartographique couvre les niveaux département, commune et aire urbaine. La Nouvelle-Aquitaine y apparaît comme gagnant quatre fois plus d'habitants qu'en 1968 tandis que l'Île-de-France a perdu 1,2 million d'habitants sur la période.

---

## Les économistes territoriaux proposent des cadres d'analyse alternatifs

Les travaux de **Laurent Davezies** sur l'économie résidentielle fournissent un cadre conceptuel pour décomposer les bases de revenus des territoires : base productive (16,9%), base publique (8,2%), base sociale (22,1%) et base résidentielle (52,8%). Cette approche appliquée aux **306 zones d'emploi** permet d'identifier les systèmes productivo-résidentiels et d'expliquer le paradoxe "croissance sans développement" de certains territoires.

**Magali Talandier** (Université Grenoble Alpes, laboratoire PACTE) a récemment publié *Développement territorial : repenser les relations villes-campagnes* (2023) avec une analyse longitudinale des dynamiques communales 1806-2018 identifiant quatre régimes de développement successifs. Son article dans la *Revue d'Économie Régionale et Urbaine* (2024) analyse spécifiquement les mécanismes de redistribution via la mobilité des ménages et les inégalités métropolitaines sur trente ans.

**Olivier Bouba-Olga** (Université de Poitiers) propose une critique méthodologique des indicateurs de métropolisation dans *Dynamiques territoriales : éloge de la diversité* (2017). Avec Michel Grossetti, il démontre les biais des corrélations taille-performance urbaine et l'importance des effets de composition dans l'interprétation des indicateurs spatiaux.

---

## Thèses récentes avec méthodologies économétriques avancées

La thèse de Samuel Ettouati (Toulouse, 2020) intitulée *Les déterminants et impacts territoriaux des migrations résidentielles en France métropolitaine* utilise des **modèles économétriques avec autocorrélations spatiales** à l'échelle des zones d'emploi. Elle analyse l'attractivité résidentielle via le taux de solde migratoire (2013) et reconstruit une base harmonisée 1968-2014 pour étudier les préférences résidentielles des étrangers. L'un des apports majeurs est la mise en évidence d'un dualisme territorial où l'attractivité pour les seniors coexiste avec la fuite des jeunes diplômés.

La thèse sur la *Créativité, attractivité et développement économique des territoires européens* (Toulouse, 2019) applique des modèles avec **autocorrélation spatiale** aux 276 régions NUTS 2 européennes (2000-2015), offrant un cadre méthodologique transposable aux analyses infra-nationales françaises. Une thèse CIFRE soutenue en janvier 2024 sur la revitalisation des centres des villes moyennes combine analyse statistique et données qualitatives sur neuf villes du programme Action cœur de ville.

---

## La littérature Inside Airbnb fournit un arsenal complet de méthodes spatiales

L'article fondateur de **Gutiérrez et al. (2017)** dans *Tourism Management* établit le protocole d'analyse spatiale de référence pour les données Airbnb. L'étude de Barcelone utilise le **Moran's I global et local (LISA)** sur cellules hexagonales de 250 mètres pour identifier les clusters High-High (hot spots) et Low-Low (cold spots). Le **Bivariate Moran's I** mesure la corrélation spatiale entre densité Airbnb et localisation des attractions touristiques. Cette méthodologie est directement reproductible avec trois snapshots.

Les travaux de **Garha et collaborateurs** (2021) étendent cette approche à sept villes espagnoles et comparent Barcelone et Lisbonne. Leurs résultats montrent des valeurs Moran's I entre **0.49 et 0.83** selon les villes, confirmant un clustering spatial fort. Ils utilisent également des **Negative Binomial Regression Models** pour expliquer la distribution des listings par les caractéristiques socio-économiques des census tracts.

---

## La régression géographiquement pondérée capture l'hétérogénéité spatiale

**Zhang et al. (2017)** dans *Sustainability* démontrent la supériorité de la **Geographically Weighted Regression (GWR)** sur les modèles linéaires classiques pour analyser les déterminants des prix Airbnb. Sur Nashville, le GWR atteint un R² de 0.30 contre 0.12 pour le GLM, révélant une hétérogénéité spatiale significative dans les coefficients. Les variables distance au centre-ville, âge du listing et ratings présentent des effets qui varient selon la localisation.

Les études plus récentes privilégient le **Multiscale GWR (MGWR)** qui permet à chaque variable explicative d'opérer à sa propre échelle spatiale. **Hong & Yoo (2020)** comparent Los Angeles et New York et montrent que le MGWR capture mieux les stratégies de pricing différenciées selon les quartiers. **Shabrina et al. (2021)** appliquent cette méthode à Londres au niveau LSOA en intégrant les données sparse (87% des zones sans hôtels).

---

## Machine learning et clustering pour caractériser les zones de pression

**Rahman et al. (2022)** proposent une approche innovante combinant **XGBoost avec Moran Eigenvector Spatial Filtering (MESF)**. Le XGBoost seul ne gère pas l'autocorrélation spatiale, ce qui biaise les prédictions. Le code reproductible est disponible sur Code Ocean. Cette méthode est applicable avec trois snapshots pour identifier les variables les plus importantes dans l'explication de la densité de listings.

Pour le clustering, le **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise) s'avère particulièrement adapté car il identifie les clusters de densité variable sans spécifier le nombre de groupes a priori. Une analyse récente de Londres utilise les paramètres **eps = 0.003 (~330m) et min_samples = 5**. Le **K-means** reste pertinent pour classifier les unités spatiales selon un profil multivariable (densité, prix, type de logement) et comparer la composition des clusters entre snapshots.

L'analyse **Getis-Ord Gi*** permet d'identifier statistiquement les hot spots et cold spots de pression touristique. **Lupu & Brochado (2024)** l'appliquent à Cape Town et Broward County dans *Cities*, montrant la concentration des listings dans les zones côtières et les CBD.

---

## Ce qui est réalisable avec trois snapshots trimestriels

Avec trois points temporels à l'échelle IRIS ou arrondissement, l'approche optimale combine **analyse exploratoire spatiale comparée (ESDA)** et **modélisation pooled cross-section**.

**Analyses pleinement réalisables** : le Moran's I global et local peut être calculé indépendamment à chaque date puis comparé, permettant d'évaluer la stabilité des clusters. Les indices de concentration (Gini spatial, Herfindahl-Hirschman) mesurent l'évolution de l'inégalité de distribution des listings. Le DBSCAN et K-means appliqués à chaque snapshot permettent d'analyser la persistance des clusters haute densité. Les régressions spatiales (SAR, SEM, SDM) fonctionnent sur chaque cross-section, et l'approche **pooled avec dummies temporelles** permet d'empiler les trois snapshots pour tester si les relations changent dans le temps via des interactions.

**Analyses non réalisables** : les modèles de panel à effets fixes souffrent d'un biais de Nickell important quand T=3 (biais proportionnel à 1/T). L'analyse de tendance temporelle est impossible avec seulement trois points. Les modèles dynamiques autorégressifs nécessitent T > 10 pour des estimateurs Arellano-Bond fiables. Toute prétention à l'inférence causale temporelle (Granger, difference-in-differences) est à proscrire.

---

## Workflow recommandé pour l'analyse de pression touristique

La stratégie optimale se décompose en quatre étapes successives.

L'**étape 1 (caractérisation spatiale)** produit des cartes choroplèthes de densité pour chaque snapshot, calcule le Moran's I global avec test de significativité par 9999 permutations Monte Carlo, et génère les cartes LISA identifiant les clusters HH, LL, HL et LH. Les indices Gini et HHI mesurent la concentration globale.

L'**étape 2 (analyse de stabilité)** compare les clusters LISA entre dates via des matrices de transition entre quartiles de densité. La corrélation de rang de Spearman évalue si le classement des unités spatiales est stable. Le coefficient de variation temporel identifie les zones volatiles.

L'**étape 3 (modélisation explicative)** estime des régressions spatiales pooled avec dummies temporelles et erreurs standard robustes clusterisées par unité spatiale. Les variables explicatives incluent la distance au centre et aux attractions, la densité de population résidente, le revenu médian (données FILOSOFI), la présence hôtelière et l'accessibilité transports. Les modèles Random Forest ou XGBoost avec MESF fournissent une analyse de feature importance.

L'**étape 4 (indice composite)** construit un indicateur de pression touristique normalisant et agrégeant plusieurs dimensions : densité d'offre par km² et par habitant, ratio Airbnb/population, taux de professionnalisation (hôtes multi-propriétés), et ratio Airbnb/hôtels. La méthodologie OECD/UNWTO ou le cadre DPSIR de l'Agence Européenne de l'Environnement servent de référence.

---

## Outils logiciels pour l'implémentation

**En Python**, l'écosystème PySAL domine l'analyse spatiale : `geopandas` pour la manipulation des données, `libpysal` pour les matrices de poids spatiaux, `esda` pour Moran's I et LISA (`esda.Moran`, `esda.Moran_Local`), `spreg` pour les régressions spatiales, et `splot` pour la visualisation. Le clustering utilise `sklearn.cluster` pour DBSCAN et K-means, complété par `mapclassify` pour les classifications choroplèthes. Le package `mgwr` implémente le Multiscale GWR.

**En R**, `sf` gère les données spatiales, `spdep` calcule les statistiques d'autocorrélation (`moran.test`, `localmoran_perm`), `spatialreg` estime les modèles SAR et SEM, et `tmap` produit les cartographies. Le package `ineq` calcule les indices de concentration.

**GeoDa** (logiciel gratuit de Luc Anselin) offre une interface graphique intuitive pour l'ESDA, les cartes LISA et les régressions spatiales, utile pour l'exploration initiale avant le codage.

---

## Sources de données à mobiliser

Pour l'analyse Airbnb, les snapshots Inside Airbnb fournissent les variables listing : localisation, type de logement, prix, nombre d'avis, disponibilité, caractéristiques hôte. La normalisation requiert les données INSEE (population IRIS, revenus FILOSOFI, logements), les données d'attractivité (localisation monuments via OpenStreetMap, fréquentation touristique DGE), et les données hôtelières (base Sirene, fichiers préfectoraux).

Pour le volet territorial français, les données clés sont l'**Échantillon Démographique Permanent (EDP)** pour les analyses longitudinales, les **Enquêtes Logement** de l'INSEE pour les déterminants de la mobilité, la **base Saphir** de recensements harmonisés, et le fichier **FILOSOFI** pour les revenus localisés. L'accès aux microdonnées nécessite généralement le Centre d'Accès Sécurisé aux Données (CASD).

---

## Conclusion : deux littératures complémentaires à croiser

L'analyse de la pression touristique via Inside Airbnb peut s'appuyer sur une littérature académique mature offrant des protocoles méthodologiques reproductibles. Les techniques de Moran's I, LISA, GWR et clustering spatial sont directement applicables avec trois snapshots trimestriels sans compromis majeur sur la validité statistique.

La valeur ajoutée d'un croisement avec la littérature française sur les dynamiques territoriales réside dans trois apports : premièrement, le cadre conceptuel de l'économie résidentielle (Davezies, Talandier) permet de situer la pression Airbnb dans les flux de revenus captés par les territoires ; deuxièmement, les modèles multiniveaux (Courgeau, Bringé & Golaz) offrent une méthode pour séparer les effets de composition des résidents des effets propres aux quartiers dans l'explication de la densité Airbnb ; troisièmement, les analyses INSEE sur les aires d'attraction des villes fournissent un zonage fonctionnel pertinent pour contextualiser les concentrations de locations courte durée au-delà des limites administratives.

L'approche pooled cross-section avec dummies temporelles représente le meilleur compromis méthodologique pour exploiter trois snapshots tout en contrôlant les variations conjoncturelles, sans prétendre à une analyse de tendance que la série temporelle courte ne permet pas de fonder.
