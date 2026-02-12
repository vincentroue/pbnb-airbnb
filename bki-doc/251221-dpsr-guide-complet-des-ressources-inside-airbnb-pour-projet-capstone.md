---
ukp: |

aliases: []
dcr: 26-02-03_110847835
codx:
tags: []
pry: x
stf: x
sts: x
---

cnt::
url:: https://claude.ai/chat/ff264692-5de5-4250-bfbf-4d11049f5fab

# Inside Airbnb Data Sources for French Data Science Capstone: Complete Resource Guide

# Inside Airbnb pour projet capstone : guide complet des ressources

Pour un projet portfolio data science centré sur la France avec comparaisons européennes, **quatre sources de données historiques sont accessibles immédiatement** : l'archive Tom Slee couvrant Paris, Lyon et Bordeaux de 2013 à 2017 (gratuit), les datasets consolidés Kaggle avec **10 villes européennes** incluant Paris, et les données complémentaires INSEE/DVF permettant un enrichissement géographique avancé. Le principal défi reste l'accès aux archives Inside Airbnb 2018-2024, disponibles sur demande payante ($300-500/ville), car le site officiel ne conserve qu'un an de données.

---

## Données historiques : deux sources principales couvrent 2013-2024

L'obtention de **5+ années de données** nécessite de combiner plusieurs sources. L'**archive Tom Slee** (tomslee.net/airbnb-data-collection-get-the-data) représente la ressource gratuite la plus précieuse pour la période pré-2018. Paris y est documenté depuis novembre 2013 avec **19 004 listings** initiaux évoluant vers 70 158 en juillet 2017. Lyon et Bordeaux sont couverts à partir de 2016, avec respectivement 10 409 et 7 484 listings fin 2017. Nice et les Alpes-Maritimes complètent la couverture française. Le format CSV contient 12 champs (room_id, price, reviews, coordinates) sous licence Creative Commons.

Pour la période **2018-2024**, Inside Airbnb propose un système de demande d'archives (insideairbnb.com/data-requests). La tarification varie selon l'usage : gratuit pour activistes et journalistes alignés sur leur mission, **$300/ville** pour recherche académique sur l'impact logement, **$500/ville** pour recherche commerciale. Les données remontent jusqu'à 2015 pour les grandes villes. Le site officiel offre gratuitement les 12 derniers mois en snapshots trimestriels, plus des **fichiers régionaux par pays** (France complète incluant Paris, Lyon, Bordeaux consolidés).

| Période | Source | Coût | Villes FR |
|---------|--------|------|-----------|
| 2013-2017 | Tom Slee Archive | Gratuit | Paris, Lyon, Bordeaux, Nice |
| 2018-2024 | Inside Airbnb Request | $300-500 | Paris, Lyon, Bordeaux |
| 12 derniers mois | Inside Airbnb Official | Gratuit | Paris, Lyon, Bordeaux |

---

## Datasets Kaggle consolidés pour analyse multi-villes européenne

Le dataset **"Airbnb Prices in European Cities"** (kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities) constitue la ressource optimale pour un capstone ML. Issu d'une publication académique Zenodo (DOI: 10.5281/zenodo.4446043, Gyódi & Nawaro 2021), il couvre **10 villes européennes** : Amsterdam, Athènes, Barcelone, Berlin, Budapest, Lisbonne, Londres, Paris, Rome, Vienne. Les 51 707 listings sont répartis en 20 fichiers CSV distinguant weekday/weekend par ville. Les **20 features** incluent des variables géographiques avancées (distance centre-ville, distance métro, indices d'attractivité restaurants/attractions) particulièrement pertinentes pour la modélisation prix.

La version **"Airbnb Cleaned Europe Dataset"** (kaggle.com/datasets/dipeshkhemani/airbnb-cleaned-europe-dataset) propose 322 330 lignes pré-nettoyées, idéale pour démarrer immédiatement le ML sans preprocessing. Pour l'analyse NLP, le dataset **"Airbnb Listings & Reviews"** (kaggle.com/datasets/mysarahmadbhat/airbnb-listings-reviews) offre **5 millions de reviews** sur Paris et autres métropoles mondiales.

Un dataset historique rare mérite attention : **"Airbnb Amsterdam 2015-2016-2017"** (kaggle.com/datasets/merkuteharshad/airbnb-amsterdam-dataset-of-2015-20162017) permet l'analyse time-series sur 3 ans. Hugging Face héberge également le dataset européen en format Parquet optimisé (huggingface.co/datasets/kraina/airbnb), avec intégration Python directe.

---

## Projets GitHub exemplaires pour structurer votre portfolio

### Références techniques de premier plan

Le projet **amac-lfc/airbnb** (github.com/amac-lfc/airbnb) représente le gold standard pour l'intégration EDA/ML/cartographie. Développé sous supervision académique à Lake Forest College, il atteint **54% R²** avec XGBoost et introduit 5 features géospatiales originales (densité restaurants/bars/cafés, distance CTA). Les visualisations **Kepler.gl en hexbin 3D** et les routes Folium vers stations de métro démontrent une maîtrise cartographique avancée. L'environment.yml garantit la reproductibilité.

Pour la performance ML pure, **L-Lewis/Airbnb-neural-network-price-prediction** (github.com/L-Lewis/Airbnb-neural-network-price-prediction) atteint **73% R²** sur Londres avec XGBoost. L'auteur, ancien responsable pricing d'une société de gestion Airbnb, a documenté sa méthodologie dans une série de 3 articles Towards Data Science. Le projet **jose-jaen/Airbnb** (github.com/jose-jaen/Airbnb) pousse plus loin avec Bayesian Neural Networks, analyse de sentiment VADER customisée pour Airbnb, et une **application Streamlit déployée** (airbnb-prices.streamlit.app).

### Projets spécifiques Paris et réglementation

**gabrielleberanger/airbnb-visualization** analyse le marché parisien 2015-2019 avec contexte réglementaire (amende €12.5M à Airbnb mentionnée). Les mapping par arrondissement et l'analyse de l'émergence des "hotel rooms" correspondent à la période loi ELAN. Pour l'analyse NLP des reviews, **YongKhiang/Sentiment_Analysis_of_Airbnb_Reviews_and_Price_Prediction** atteint **81% R²** avec topic modeling LDA révélant 5 thèmes clés : expérience séjour, équipements, bruit, localisation, communication host.

| Projet | R² atteint | Points forts | URL |
|--------|------------|--------------|-----|
| amac-lfc/airbnb | 54% | Kepler.gl, features géospatiales | github.com/amac-lfc/airbnb |
| L-Lewis/Airbnb-neural-network | 73% | Expertise industrie, blog TDS | github.com/L-Lewis/Airbnb-neural-network-price-prediction |
| jose-jaen/Airbnb | N/A | Streamlit app, Bayesian NN | github.com/jose-jaen/Airbnb |
| YongKhiang/Sentiment_Analysis | 81% | NLP + prix, LDA topics | github.com/YongKhiang/... |

---

## Ressources pédagogiques structurées pour apprentissage méthodique

Le tutoriel **Dataquest Machine Learning** (dataquest.io/blog/machine-learning-tutorial) utilise Inside Airbnb Washington D.C. pour enseigner KNN de zéro jusqu'à scikit-learn, idéal pour consolider les fondamentaux. Le cours académique **Geographic Data Science with Python** (geographicdata.science/book) du trio Rey/Arribas-Bel/Wolf constitue la référence pour l'analyse spatiale avec GeoPandas sur données San Diego - chapitres sur régression spatiale directement applicables à l'analyse parisienne.

Sur Kaggle, le notebook **"NYC Airbnb: EDA, Visualization, Regression"** (kaggle.com/code/wguesdon/nyc-airbnb-eda-visualization-regression) démontre un workflow complet EDA→ML reproductible. Pour le NLP avancé, l'article **"Sentiment Analysis of Airbnb Reviews with BERT"** (tom-furu.medium.com) applique le transfer learning BERT aux reviews, technique transposable aux avis francophones.

Le projet **mohamedirfansh.github.io/Airbnb-Data-Science-Project** offre une documentation exceptionnelle avec site web dédié comparant 6 modèles ML (Linear Regression, Random Forest, XGBoost, CatBoost, Ridge, Lasso) et intégrant K-Fold Cross Validation - structure idéale à reproduire pour un portfolio.

---

## Données complémentaires INSEE et DVF pour enrichissement géographique

### IRIS : la granularité géographique française optimale

Les contours **IRIS** (Ilots Regroupés pour l'Information Statistique) disponibles sur geoservices.ign.fr/contoursiris découpent la France en ~16 000 unités de 1 800-5 000 habitants. Le téléchargement 2025 en GeoPackage ou Shapefile (projection Lambert 93, EPSG:2154) s'intègre directement avec GeoPandas. Les statistiques INSEE par IRIS (insee.fr/fr/statistiques) couvrent population, revenus, logement, activité - variables explicatives puissantes pour modéliser les prix Airbnb.

```python
import geopandas as gpd
iris = gpd.read_file('CONTOURS-IRIS.gpkg').to_crs('EPSG:4326')
airbnb_gdf = gpd.GeoDataFrame(airbnb, geometry=gpd.points_from_xy(airbnb.longitude, airbnb.latitude))
airbnb_enriched = gpd.sjoin(airbnb_gdf, iris[['CODE_IRIS', 'NOM_IRIS', 'geometry']])
```

### DVF : transactions immobilières en open data

Le dataset **DVF** (data.gouv.fr/datasets/demandes-de-valeurs-foncieres) recense toutes les transactions immobilières françaises des 5 dernières années. La version géolocalisée pré-traitée (data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees) ajoute latitude/longitude. Croiser prix de vente DVF et tarifs Airbnb par IRIS permet d'analyser la relation entre valeur immobilière et rendement locatif court-terme.

### Encadrement des loyers Paris

L'API Paris Open Data (opendata.paris.fr/explore/dataset/logement-encadrement-des-loyers) expose les loyers de référence par quartier, nombre de pièces et période de construction. Comparer tarifs Airbnb aux plafonds réglementaires quantifie l'écart économique motivant la location touristique versus bail classique - angle d'analyse original pour votre capstone.

---

## Réglementation française : contexte pour analyse d'impact

La **loi ELAN** (novembre 2018) impose un plafond de **120 jours/an** pour les résidences principales louées sur plateformes. Paris, Lyon, Bordeaux, Nice et 14 autres villes exigent un numéro d'enregistrement obligatoire. Les plateformes doivent bloquer automatiquement les annonces dépassant le quota. Les sanctions atteignent €50 000 pour location de résidence secondaire sans autorisation de changement d'usage.

Analyser l'évolution des listings Paris autour de novembre 2018 (données Tom Slee puis archives Inside Airbnb) permettrait de mesurer l'impact réglementaire - **lacune identifiée** dans les projets GitHub existants, donc opportunité de différenciation.

---

## Stratégie recommandée pour votre capstone

**Phase 1 - Acquisition données** : Télécharger immédiatement l'archive Tom Slee (Paris 2013-2017), les snapshots Inside Airbnb récents, et le dataset Kaggle 10 villes européennes. Soumettre une demande Inside Airbnb pour archives 2018-2024 si budget disponible.

**Phase 2 - Enrichissement** : Récupérer contours IRIS et données INSEE (population, revenus), DVF géolocalisé pour Paris, données encadrement loyers. Effectuer spatial join pour attribuer code IRIS à chaque listing.

**Phase 3 - Analyse** : Structurer en 5 notebooks (EDA, preprocessing/feature engineering, analyse géospatiale Folium/Kepler.gl, modélisation ML XGBoost, NLP sentiment reviews). Viser 70%+ R² sur prédiction prix.

**Phase 4 - Différenciation** : Intégrer analyse impact loi ELAN (évolution pré/post novembre 2018) et comparaison tarifs Airbnb versus loyers référence - angles sous-exploités dans les projets existants.

Les ressources identifiées permettent de construire un projet portfolio de niveau professionnel mobilisant EDA avancée, ML performant, cartographie interactive et analyse contextuelle française unique.
