# PBNB - Analyse Airbnb Multi-villes France/Europe

**Projet capstone data science** : Analyse comparative marchés locations court-terme Airbnb avec données historiques Inside Airbnb, cartographie dynamique et dashboard interactif.

## 📊 Vue d'ensemble

### Objectif métier
Comprendre structures et dynamiques marchés locations Airbnb dans 9 villes européennes (4 France + 5 Europe) avec analyse temporelle avant/après COVID (2019-2024), cartographie hotspots touristiques, et modélisation prédictive prix.

### Périmètre géographique
- **France** : Paris, Lyon, Bordeaux, Pays Basque
- **Europe** : Londres, Berlin, Madrid, Rome, Budapest

### Stack technique
- **R** : Cartographie (sf, leaflet), dashboard Shiny, analyses statistiques
- **Python** : ETL pipelines, scraping, ML prédictions prix
- **Quarto** : Rapports reproductibles HTML/PDF, notebooks EDA

## 🗂️ Structure projet

```
pbnb-airbnb-log-jrr-jpy/
├── data/
│   ├── raw/
│   │   ├── france/          # Datasets Inside Airbnb France
│   │   │   ├── paris/
│   │   │   ├── lyon/
│   │   │   ├── bordeaux/
│   │   │   └── pays-basque/
│   │   └── europe/          # Datasets Inside Airbnb Europe
│   │       ├── london/
│   │       ├── berlin/
│   │       ├── madrid/
│   │       ├── rome/
│   │       └── budapest/
│   └── processed/
│       ├── consolidated_listings.parquet
│       ├── spatial_joined.gpkg
│       └── indicators_aggregated.csv
├── notebooks/
│   ├── 01_eda_france.qmd
│   ├── 02_eda_europe.qmd
│   ├── 03_spatial_analysis.qmd
│   └── 04_ml_price_prediction.ipynb
├── scripts/
│   ├── sp01_download_insideairbnb.py
│   ├── sp02_etl_consolidation.py
│   ├── sp03_spatial_join.R
│   └── sp04_indicators_calc.R
├── shiny_dashboard/
│   ├── app.R
│   ├── ui.R
│   ├── server.R
│   └── global.R
├── outputs/
│   ├── reports/
│   └── figures/
├── rgd-guide/
└── README.md
```

## 🚀 Quick Start

### 1. Setup environnements

**Python** :
```bash
cd pbnb-airbnb-log-jrr-jpy
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install pandas geopandas requests duckdb scikit-learn matplotlib seaborn
```

**R** :
```r
# Dans RStudio ou R terminal
install.packages(c("renv", "sf", "leaflet", "shiny", "tidyverse", "DT", "skimr"))
renv::init()  # Initialiser environnement virtuel R
```

### 2. Télécharger datasets Inside Airbnb

```bash
# Script Python automatique (à créer)
python scripts/sp01_download_insideairbnb.py --cities paris lyon bordeaux pays-basque london berlin madrid rome budapest --output data/raw
```

**Ou manuellement** :
- Aller sur https://insideairbnb.com/fr/get-the-data/
- Télécharger pour chaque ville :
  - `listings.csv.gz` (listings détaillés)
  - `calendar.csv.gz` (disponibilités)
  - `neighbourhoods.geojson` (géométries quartiers)
- Placer dans `data/raw/{zone}/{ville}/`

### 3. ETL consolidation

```bash
# Pipeline ETL Python + DuckDB
python scripts/sp02_etl_consolidation.py
```

Génère :
- `data/processed/consolidated_listings.parquet` : Tous listings consolidés
- Schema unifié : `city, snapshot_date, listing_id, price, latitude, longitude, host_id, room_type, ...`

### 4. Lancer notebooks EDA

**Quarto** :
```bash
quarto preview notebooks/01_eda_france.qmd
```

**Jupyter** :
```bash
jupyter notebook notebooks/04_ml_price_prediction.ipynb
```

### 5. Dashboard Shiny

```r
# Dans R
library(shiny)
runApp("shiny_dashboard/")
```

Ouvre navigateur avec dashboard interactif :
- Carte leaflet multi-villes
- Filtres dynamiques (ville, période, prix)
- Graphiques évolution temporelle
- Tableau DT avec gradient prix

## 📋 Phases projet

### ✅ Phase 1 - Setup Infrastructure (EN COURS)
- [x] Création structure projet
- [x] Notes projet (evergreen + vrac)
- [ ] Script téléchargement datasets automatique
- [ ] Téléchargement fonds carte IGN France
- [ ] Setup environnements R/Python (renv + venv)

### Phase 2 - ETL & Consolidation
- [ ] Pipeline ETL DuckDB consolidation 9 villes
- [ ] Jointure géographique listings → communes/zones emploi
- [ ] Calcul indicateurs agrégés (prix médian, TCAM, concentration)

### Phase 3 - EDA & Visualisations
- [ ] Rapport Quarto EDA comparatif 9 villes
- [ ] Graphiques évolution temporelle (ggplot2/plotly)
- [ ] Cartes choroplèthes prix par quartier (leaflet)

### Phase 4 - Dashboard Shiny
- [ ] Maquette UI (3 colonnes : filtres | carte | graphiques+tableau)
- [ ] Backend réactif (reactive expressions)
- [ ] Déploiement local + documentation

### Phase 5 - ML (optionnel)
- [ ] Features engineering (spatial + temporel)
- [ ] Benchmarks modèles prédiction prix (RF, XGBoost, GLM)
- [ ] Interprétabilité (SHAP values)

## 📚 Ressources

### Données
- **Inside Airbnb** : https://insideairbnb.com/fr/get-the-data/
- **IGN Admin Express** : https://geoservices.ign.fr/adminexpress
- **INSEE Comparateur** : https://www.insee.fr/fr/statistiques/1405599

### Documentation
- **Data dictionary Inside Airbnb** : http://insideairbnb.com/data-dictionary.html
- **sf package R** : https://r-spatial.github.io/sf/
- **Shiny dashboards** : https://shiny.posit.co/r/gallery/
- **Quarto dashboards** : https://quarto.org/docs/gallery/#dashboards

### Projets similaires
- **Observatoire Territoires** (Shiny migrations) : https://github.com/observatoire-territoires
- Capstone Airbnb Londres XGBoost : Rechercher GitHub "airbnb price prediction london"

## 📝 Fichiers documentation existants (pzmRRtest)

**À centraliser depuis** `C:\Users\vince\hh\pq\PDS\pzmRRtest\` :
- `tpl-EDA-notebook_template_r_airbnb-251123.md` : Template EDA R
- `data/airbnb_paris_listings_summary.csv` : Dataset Paris existant
- `eda-airbnb-paris-251124.qmd` : Notebook EDA Paris Quarto
- `eda-airbnb-paris-LIGHT-251124.qmd` : Version light EDA
- Contexte conversation : `C:\Users\vince\hh\_ibx\vgz-ctx-capstone-airbnb-251230.md` (440KB)

## 🔧 Commandes utiles

### Téléchargement manuel datasets (cURL)
```bash
# Exemple Paris dernier snapshot
curl -o data/raw/france/paris/listings.csv.gz http://data.insideairbnb.com/france/ile-de-france/paris/2024-12-12/data/listings.csv.gz
```

### Inspection rapide CSV
```bash
# Python
python -c "import pandas as pd; df=pd.read_csv('data/raw/france/paris/listings.csv'); print(df.info()); print(df.head())"

# R
Rscript -e "df <- read.csv('data/raw/france/paris/listings.csv'); str(df); head(df)"
```

### Décompression .gz
```bash
gunzip data/raw/france/paris/listings.csv.gz
```

### Quarto render batch
```bash
quarto render notebooks/ --output-dir outputs/reports/
```

## 🎯 Métriques clés projet

### Dimensions données (estimations)
- **Listings totaux** : ~500k lignes (9 villes)
- **Période temporelle** : 2019-2024 (5 ans, snapshots trimestriels)
- **Variables** : 16 colonnes (summary) ou 74 (detailed)

### Indicateurs business
- Prix médian/m² par ville
- % hôtes multi-listings (>3 logements)
- TCAM nb listings 2019-2024
- Taux occupation moyen
- Concentration Gini hôtes (inégalités marché)

### Performance ML cibles
- **R² prédiction prix** : >70% (benchmark Londres XGBoost 73%)
- **RMSE** : <30€ (prix nuit)
- **Features importance** : Top 10 variables explicatives

## 📧 Contact & Notes projet

**Notes projet Obsidian** :
- Evergreen : `,,epPBNB-evg🍃_pq.md`
- Vrac sessions : `,,vpPBNB-vrk_pq.md`

**Tags** : `pq/PBNB`, `pd`
