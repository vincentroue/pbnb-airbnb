---
ukp: "Session setup projet PBNB Airbnb = création structure dossiers scripts téléchargement centralisation doc pzmRRtest planning phase 1"
dcr: 25-12-30
dup: 25-12-30
tags:
  - pq/PBNB
  - pd
tl: "nPBNB-setup-projet-airbnb"
---

# ,nPBNB-251230 - Setup Projet Airbnb Multi-villes

## &context

**Objectif session** : Centraliser travaux Airbnb dispersés (pzmRRtest, conversations Claude) dans nouveau projet structuré `pbnb-airbnb-log-jrr-jpy` avec architecture light, documentation API Inside Airbnb, et scripts téléchargement automatique datasets.

**Périmètre** : 9 villes (4 France + 5 Europe)
- **France** : Paris, Lyon, Bordeaux, Pays Basque
- **Europe** : Londres, Berlin, Madrid, Rome, Budapest

**Stack mixte R/Python** :
- **R** : Cartographie (sf, leaflet), dashboard Shiny, analyses statistiques
- **Python** : ETL pipelines, téléchargement datasets, ML prédictions prix

## &accomplissements

### ✅ Structure projet créée

**Dossiers** :
```
pbnb-airbnb-log-jrr-jpy/
├── _npbacklog/                  # Sessions RCP finalisées
├── _ibx/                        # Inbox contexte (vgz-ctx-capstone-airbnb)
├── data/
│   ├── raw/
│   │   ├── france/              # Paris, Lyon, Bordeaux, Pays Basque
│   │   └── europe/              # Londres, Berlin, Madrid, Rome, Budapest
│   └── processed/               # Datasets consolidés (à venir)
├── notebooks/                   # Quarto/Jupyter EDA
├── scripts/                     # Scripts Python/R production
├── shiny_dashboard/             # Dashboard Shiny (à créer)
├── outputs/
│   ├── reports/
│   └── figures/
├── rgd-guide/                   # Documentation technique
├── ytest/                       # Scripts temporaires
├── zu/                          # Archive
└── README.md
```

### ✅ Notes projet générées

**3 fichiers principaux** :
1. **Evergreen** : `,,epPBNB-evg🍃_pq.md`
   - Planning 5 phases (Setup → ETL → EDA → Dashboard → ML)
   - Stack technique détaillé R/Python/Quarto
   - TODOs avec #tnext phase 1
   - Architecture projet avec chemins complets

2. **Vrac** : `,,vpPBNB-vrk_pq.md`
   - Logs sessions quotidiennes
   - Notes techniques (structure datasets, villes disponibles)
   - Ideas (maquette dashboard, comparaison COVID)
   - Query Dataview TASK

3. **README** : `README.md`
   - Quick start installation environnements
   - Commandes utiles (téléchargement, inspection CSV)
   - Phases projet avec checklist
   - Ressources documentation officielle

### ✅ Script téléchargement datasets créé

**Fichier** : `scripts/sp01-download-insideairbnb-251230.py`

**Fonctionnalités** :
- Téléchargement automatique datasets Inside Airbnb 9 villes
- Configuration URLs par ville (country, region, city, date snapshot)
- Pattern modulaire : `{country}/{region}/{city}/{date}/data/{file_name}`
- Gestion erreurs (HTTP 404, timeout, retry 3×)
- CLI arguments : `--cities`, `--zone`, `--files`, `--list`
- Progress feedback (taille fichiers, succès/échecs)

**Usage exemples** :
```bash
# Lister villes disponibles
python sp01-download-insideairbnb-251230.py --list

# Télécharger Paris + Lyon (listings + calendar)
python sp01-download-insideairbnb-251230.py --cities paris lyon --files listings calendar

# Télécharger toute zone France (tous fichiers)
python sp01-download-insideairbnb-251230.py --zone france --files all

# Télécharger toutes villes (listings + neighbourhoods geo seulement)
python sp01-download-insideairbnb-251230.py --zone all --files listings neighbourhoods_geo
```

**Fichiers téléchargeables** :
- `listings.csv.gz` : Listings détaillés (74 colonnes)
- `calendar.csv.gz` : Disponibilités 365 jours
- `reviews.csv.gz` : Avis clients
- `neighbourhoods.geojson` : Géométries quartiers

### ✅ Documentation API Inside Airbnb

**Fichier** : `rgd-guide/gdl-insideairbnb-api-251230.md`

**Contenu** (200 lignes) :
- **Structure URLs** : Pattern général + exemples Paris/Londres/Berlin
- **Fichiers disponibles** : Tableau comparatif listings/calendar/reviews/neighbourhoods
- **Colonnes clés** : Data dictionary résumé (74 colonnes listings)
- **Dates snapshots** : Calendrier trimestriel 2024, historique depuis 2015
- **Villes** : Tableaux France (4) + Europe (5) avec paths exacts
- **Utilisation pratique** : Code Python/R lecture CSV/GeoJSON
- **Indicateurs** : Formules prix médian, taux occupation, concentration hôtes
- **Limitations** : Biais échantillonnage, qualité données, performance

### ✅ Centralisation documentation pzmRRtest

**Fichiers copiés** :
1. **Template EDA** : `rgd-guide/tpl-EDA-notebook_template_r_airbnb-251123.md`
   - Template R Markdown EDA complet (checklist méthodologique, graphiques, cartes)

2. **Dataset Paris** : `data/raw/france/paris/airbnb_paris_listings_summary.csv`
   - Listings Paris existant (~65k lignes, 16 colonnes summary)

3. **Notebooks Quarto** :
   - `notebooks/eda-airbnb-paris-251124.qmd` : EDA Paris version complète
   - `notebooks/eda-airbnb-paris-LIGHT-251124.qmd` : Version light

4. **Contexte conversation** : `_ibx/vgz-ctx-capstone-airbnb-251230.md`
   - Conversation Claude 304 messages (440KB)
   - Discussions Shiny vs Streamlit, données INSEE, cartographie

### ✅ .gitignore configuré

**Exclusions** :
- Python : `__pycache__/`, `*.pyc`, `venv/`
- R : `.Rproj.user`, `.Rhistory`, `.quarto/`
- Jupyter : `.ipynb_checkpoints/`
- Temporaires : `ytest/`, `devtest/`, `tz/`, `zu/`
- (Optionnel) Datasets volumineux : `data/raw/**/*.csv` (commenté)

## &decisions

### Architecture light validée

**Principes** :
- **Pas de sur-ingénierie** : Structure minimale obligatoire seulement
- **Scripts simples** : Préfixe `sp{alias}-{nom}-{date}.py` (pas modules complexes)
- **Documentation ciblée** : Guides techniques essentiels (API Inside Airbnb)
- **Notebooks prioritaires** : Quarto EDA avant dashboard Shiny

### Stack R/Python confirmé

**Répartition tâches** :
- **Python** : ETL (téléchargement, consolidation DuckDB), ML (scikit-learn, XGBoost)
- **R** : Cartographie (sf, leaflet), dashboard Shiny, statistiques (tidyverse)
- **Quarto** : Rapports reproductibles HTML/PDF (R chunks)

**Raison** : Capitaliser expérience R cartographie (Observatoire Territoires) + Python ML

### Priorité phase 1 : Données

**Focus immédiat** :
1. Tester script téléchargement `sp01-download-insideairbnb-251230.py` sur Paris
2. Vérifier structure CSV téléchargés (colonnes, prix format)
3. Télécharger snapshots 2024 + historique 2019-2020 (comparaison COVID)
4. Documenter dates snapshots réelles (page Get the Data change fréquemment)

## &blockers

### ⚠️ Dates snapshots variables

**Problème** : Dates snapshots Inside Airbnb changent fréquemment (trimestriel)
**Impact** : URLs dans `sp01-download-insideairbnb-251230.py` peuvent devenir obsolètes
**Solution** :
- Tester téléchargement manuel avant automatisation complète
- Script doit gérer erreurs HTTP 404 gracefully
- Documenter procédure mise à jour dates (consulter https://insideairbnb.com/fr/get-the-data/)

### ⚠️ WebFetch site Inside Airbnb échoue

**Problème** : Site charge données via JavaScript dynamique (WebFetch retourne CSS seulement)
**Impact** : Impossible scraper dates snapshots automatiquement
**Solution** : Inspection manuelle page Get the Data + mise à jour config script

## &next-actions

### 🎯 Phase 1 - Setup Infrastructure (suite)

**Priorité 1 - Tester téléchargement** :
```bash
# Tester script sur Paris seulement
cd C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy
python scripts/sp01-download-insideairbnb-251230.py --cities paris --files listings neighbourhoods_geo

# Vérifier fichiers téléchargés
ls -lh data/raw/france/paris/

# Inspecter CSV
python -c "import pandas as pd; df=pd.read_csv('data/raw/france/paris/listings.csv.gz'); print(df.info()); print(df.head())"
```

**Priorité 2 - Documenter snapshots réels** :
- Aller sur https://insideairbnb.com/fr/get-the-data/
- Noter dates exactes Paris, Lyon, Bordeaux, Pays Basque (Q4 2024)
- Mettre à jour `CITIES_CONFIG` dans script si nécessaire
- Chercher snapshots historiques 2019-2020 (comparaison COVID)

**Priorité 3 - Setup environnements** :
```bash
# Python venv
python -m venv venv
venv\Scripts\activate
pip install pandas geopandas requests duckdb

# R packages (dans RStudio)
install.packages(c("renv", "sf", "leaflet", "tidyverse", "DT", "skimr"))
renv::init()
```

**Priorité 4 - Premier EDA** :
- Ouvrir `notebooks/eda-airbnb-paris-LIGHT-251124.qmd` (déjà existant)
- Tester rendu Quarto : `quarto preview notebooks/eda-airbnb-paris-LIGHT-251124.qmd`
- Adapter code pour nouveau chemin dataset : `../data/raw/france/paris/airbnb_paris_listings_summary.csv`

### 📝 Documentation à créer (optionnel phase 1)

- `rgd-guide/gdl-quarto-setup-251230.md` : Setup Quarto + RStudio + Jupyter kernel
- `rgd-guide/gdl-shiny-reactivity-251230.md` : Guide réactivité Shiny (si avance dashboard)

## &resources

### Documentation projet
- **Evergreen** : `C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy\,,epPBNB-evg🍃_pq.md`
- **Vrac** : `C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy\,,vpPBNB-vrk_pq.md`
- **README** : `C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy\README.md`

### Documentation technique
- **API Inside Airbnb** : `rgd-guide/gdl-insideairbnb-api-251230.md`
- **Template EDA R** : `rgd-guide/tpl-EDA-notebook_template_r_airbnb-251123.md`

### Scripts
- **Téléchargement** : `scripts/sp01-download-insideairbnb-251230.py`

### Datasets
- **Paris existant** : `data/raw/france/paris/airbnb_paris_listings_summary.csv`

### Contexte
- **Conversation Claude** : `_ibx/vgz-ctx-capstone-airbnb-251230.md` (304 messages, 440KB)

### Liens externes
- **Inside Airbnb Get the Data** : https://insideairbnb.com/fr/get-the-data/
- **Data Dictionary** : http://insideairbnb.com/data-dictionary.html
- **IGN Admin Express** : https://geoservices.ign.fr/adminexpress
- **Quarto Dashboards** : https://quarto.org/docs/gallery/#dashboards

## &changelog

**2025-12-30** :
- Création projet `pbnb-airbnb-log-jrr-jpy` dans `PDS/`
- Structure minimale obligatoire (README, evergreen, vrac, .gitignore, dossiers)
- Dossiers data organisés par zone (france/, europe/) et ville
- Script Python téléchargement automatique 9 villes (sp01)
- Guide documentation API Inside Airbnb (gdl-insideairbnb-api)
- Centralisation fichiers pzmRRtest (template EDA, notebooks Quarto, dataset Paris)
- Copie contexte conversation Claude (vgz-ctx-capstone-airbnb) vers _ibx/

## &metrics

**Fichiers créés** : 10
- 3 notes projet (evergreen, vrac, README)
- 1 script Python (sp01-download)
- 1 guide technique (gdl-insideairbnb-api)
- 1 .gitignore
- 4 fichiers copiés (template, notebooks, dataset, contexte)

**Dossiers créés** : 15
- Structure minimale (8) : _npbacklog, tz, scripts, ytest, zu, rgd-guide, czcbench, _ibx
- Data (7) : raw/france (4 villes), raw/europe (5 villes), processed, notebooks, outputs (2)

**Lignes documentation** :
- Evergreen : ~250 lignes
- Vrac : ~150 lignes
- README : ~180 lignes
- Guide API : ~400 lignes
- Script Python : ~280 lignes
- **Total** : ~1260 lignes documentation + code

## &qna

**?? Quelle différence entre scripts `sp*` vs `psp*` dans convention nommage ?**
---
- **`sp{alias}-{nom}`** : Scripts **simples** autonomes, une tâche spécifique, <300 lignes
  - Exemple : `sp01-download-insideairbnb.py` (téléchargement datasets)
- **`psp{alias}-{nom}`** : Scripts **production** modulaires, complexes, >300 lignes, réutilisables
  - Exemple : `pspETL-consolidation-duckdb.py` (pipeline ETL complet avec classes)
- **Critère** : Complexité + taille (sp=simple, psp=production)
---

**?? Pourquoi stocker datasets dans `data/raw/` avec sous-dossiers zone (france/europe) ?**
---
- **Organisation logique** : Séparer sources géographiques facilite navigation
- **Scalabilité** : Ajout futures zones (Asie, Amériques) sans réorganisation
- **Scripts téléchargement** : Argument CLI `--zone france` télécharge groupe villes
- **Jointures** : Comparaison France vs Europe nécessite agrégation séparée avant consolidation
---

**?? Pourquoi dupliquer fichier contexte `vgz-ctx-capstone-airbnb` dans `_ibx/` projet ?**
---
- **Centralisation** : Tous éléments projet dans un dossier (éviter dépendances externes `hh/_ibx/`)
- **Référence future** : Conversation 304 messages contient décisions techniques (Shiny vs Streamlit, données INSEE)
- **Portabilité** : Projet PBNB autonome si déplacement/archivage
- **Taille** : 440KB acceptable pour référence historique (_ibx/ non versionné Git)
---

**?? Script Python utilise `urllib` au lieu de `requests` library, pourquoi ?**
---
- **Dépendances minimales** : `urllib` est standard library Python (pas installation pip)
- **Setup léger** : Utilisateur peut tester script immédiatement sans `pip install requests`
- **Trade-off** : `requests` plus user-friendly, mais urllib suffit pour téléchargements simples
- **Évolution** : Si pipeline ETL complexe (authentification, sessions), migrer vers `requests`
---

**?? Dates snapshots Inside Airbnb dans script (2024-12-12 Paris) sont-elles à jour ?**
---
- **Non garanties** : Dates snapshots changent trimestriellement (mars, juin, septembre, décembre)
- **Dernière vérification** : 2025-12-30 (estimations basées calendrier typique Q4)
- **Maintenance nécessaire** : Vérifier https://insideairbnb.com/fr/get-the-data/ avant téléchargement
- **Gestion erreurs** : Script affiche HTTP 404 si URL obsolète → mettre à jour `CITIES_CONFIG`
- **Recommandation** : Tester téléchargement manuel Paris avant batch 9 villes
---
