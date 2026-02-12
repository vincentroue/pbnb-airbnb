---
ukp: |

aliases: []
dcr: 26-02-03_110846689
codx:
tags: []
pry: x
stf: x
sts: x
---

cnt::
url:: https://claude.ai/chat/ac0994fd-f468-48ed-9402-79eaba296e0a

# Datasets Inside Airbnb consolidés: aucun repo ne couvre Lyon-Bordeaux

# Datasets Inside Airbnb consolidés : aucun repo ne couvre Lyon-Bordeaux

**Verdict principal** : Après recherche exhaustive, **aucun dépôt GitHub ne contient de datasets consolidés incluant Lyon et Bordeaux**. La plupart des projets couvrent Paris uniquement ou se concentrent sur les capitales européennes. Pour les trois villes françaises prioritaires, vous devrez soit utiliser l'archive Tom Slee (2013-2017), soit soumettre une demande payante à Inside Airbnb (2018+), soit télécharger et consolider vous-même.

---

## Projets GitHub avec datasets consolidés (TOP 5)

### 1. jirfig/Airbnb-ETL-pipeline-Spark-Scala-Databricks-Airflow

| Critère | Détails |
|---------|---------|
| **Lien GitHub** | https://github.com/jirfig/Airbnb-ETL-pipeline-Spark-Scala-in-Databricks-Airflow |
| **Dataset disponible** | Scripts de téléchargement (`get_original_data.ipynb`) - données à télécharger |
| **Villes France** | Paris ☑️ Lyon ❌ Bordeaux ❌ |
| **Période couverte** | Janvier-Mars 2021 (snapshots mensuels) |
| **Format données** | CSV → Parquet → modèle dimensionnel |
| **Taille dataset** | **5.8 GB** source, ~14.7M enregistrements |
| **Documentation** | ⭐⭐⭐⭐⭐ Excellente (dictionnaire, diagrammes ETL) |
| **Licence** | Non spécifiée |
| **Dernière update** | Septembre 2021 |
| **Réplicabilité** | ⭐⭐⭐⭐☆ (pipeline complet mais configuration requise) |

**Bonus** : Analyse NLP des reviews, intégration données météo, 630K+ listings, 3.3M+ reviews. Villes : Paris, London, Amsterdam, Berlin.

---

### 2. tomslee/airbnb-data-collection (Archive historique)

| Critère | Détails |
|---------|---------|
| **Lien GitHub** | https://github.com/tomslee/airbnb-data-collection |
| **Dataset disponible** | ✅ OUI EXTERNE : https://tomslee.net/airbnb-data-collection-get-the-data |
| **Villes France** | Paris ☑️ Lyon ☑️ Bordeaux ☑️ Nice ☑️ Nantes ☑️ |
| **Période couverte** | **2013-2017** (16 snapshots Paris, 8 Lyon, 7 Bordeaux) |
| **Format données** | ZIP → CSV |
| **Taille dataset** | Variable par ville (~10-50 MB chaque) |
| **Documentation** | ⭐⭐⭐⭐☆ Bonne méthodologie scraping |
| **Licence** | MIT |
| **Dernière update** | Juillet 2019 (ABANDONNÉ) |
| **Réplicabilité** | ⭐⭐☆☆☆ (script cassé, données archivées uniquement) |

**CRITIQUE** : Seule source gratuite avec données historiques Paris/Lyon/Bordeaux. Téléchargements directs :
- **Paris** : https://s3.amazonaws.com/tomslee-airbnb-data-2/paris.zip (19,004→70,158 listings)
- **Lyon** : https://s3.amazonaws.com/tomslee-airbnb-data-2/lyon.zip (7,346→10,409 listings)
- **Bordeaux** : https://s3.amazonaws.com/tomslee-airbnb-data-2/bordeaux.zip (3,095→7,484 listings)

---

### 3. Zenodo European Cities Dataset (Académique)

| Critère | Détails |
|---------|---------|
| **Lien** | https://zenodo.org/records/4446043 |
| **DOI** | 10.5281/zenodo.4446043 |
| **Dataset disponible** | ✅ OUI DIRECT téléchargement |
| **Villes France** | Paris ☑️ Lyon ❌ Bordeaux ❌ |
| **Autres villes** | Amsterdam, Athens, Barcelona, Berlin, Budapest, Lisbon, London, Rome, Vienna |
| **Période couverte** | 2021 snapshot (weekday/weekend splits) |
| **Format données** | CSV + scripts Python |
| **Taille dataset** | **10.8 MB** (7.4 GB volume servi) |
| **Documentation** | ⭐⭐⭐⭐⭐ Publication Tourism Management associée |
| **Licence** | CC BY 4.0 |
| **Downloads** | 12,963+ téléchargements |
| **Réplicabilité** | ⭐⭐⭐⭐⭐ (téléchargement direct, code reproductible) |

**Variables** : realSum (prix 2 personnes/2 nuits EUR), room_type, cleanliness_rating, guest_satisfaction, dist (centre), metro_dist, attr_index, rest_index, lat/lng.

---

### 4. Hugging Face kraina/airbnb (Format ML)

| Critère | Détails |
|---------|---------|
| **Lien** | https://huggingface.co/datasets/kraina/airbnb |
| **Dataset disponible** | ✅ OUI DIRECT (API Hugging Face) |
| **Villes France** | Paris ☑️ Lyon ❌ Bordeaux ❌ |
| **Format données** | Parquet (optimisé ML) |
| **Taille dataset** | 21.5 MB (9.39 MB Parquet) |
| **Licence** | CC BY 4.0 |
| **Réplicabilité** | ⭐⭐⭐⭐⭐ (chargement 1 ligne Python) |

```python
from datasets import load_dataset
ds = load_dataset("kraina/airbnb")
```

---

### 5. rsanjabi/short-term-rentals-warehouse (Enterprise)

| Critère | Détails |
|---------|---------|
| **Lien GitHub** | https://github.com/rsanjabi/short-term-rentals-warehouse |
| **Dataset disponible** | Code-only (pipeline vers Snowflake) |
| **Villes France** | Configurable - ajout manuel requis |
| **Période couverte** | 2015-2020 (backfill possible) |
| **Format données** | Snowflake tables, DBT models |
| **Documentation** | ⭐⭐⭐⭐☆ Architecture bien documentée |
| **Licence** | Non spécifiée |
| **Dernière update** | Actif (68 commits) |
| **Réplicabilité** | ⭐⭐⭐☆☆ (setup complexe, Snowflake requis) |

**Capacité** : 35 millions+ enregistrements, tests qualité DBT, dashboard Metabase.

---

## Projets GitHub avec scripts téléchargement auto (TOP 3)

### 🥇 kytola/CleanAirbnb (Cornell University)

**URL** : https://github.com/kytola/CleanAirbnb  
**Langage** : Python (Jupyter Notebooks) | **Licence** : Apache-2.0 | **Maintenu** : 2024

**Setup rapide :**
```bash
git clone https://github.com/kytola/CleanAirbnb.git
cd CleanAirbnb
pip install pandas requests jupyter
jupyter notebook "1. Download and compile data/"
```

**Configuration villes françaises** (modifier URLs dans notebook) :
```python
CITIES = {
    'paris': 'france/ile-de-france/paris',
    'lyon': 'france/auvergne-rhone-alpes/lyon',
    'bordeaux': 'france/nouvelle-aquitaine/bordeaux'
}
```

**Temps exécution estimé** : 30-60 min (3 villes, snapshots récents)

---

### 🥈 southern-cross-ai/Inside-Airbnb-Australia

**URL** : https://github.com/southern-cross-ai/Inside-Airbnb-Australia  
**Langage** : Python CLI | **Licence** : MIT | **Dernière update** : Août 2024

**Usage CLI** (après modification pour France) :
```bash
python utils/download.py \
  -s 2020-01-01 \
  -e 2024-12-31 \
  -l france/ile-de-france/paris france/auvergne-rhone-alpes/lyon \
  -r ./data
```

**Temps exécution estimé** : 2-4 heures (full historique 3 villes)

---

### 🥉 Script custom minimal (recommandé pour démarrage rapide)

```python
import requests
import os

CITIES = {
    'paris': 'france/ile-de-france/paris',
    'lyon': 'france/auvergne-rhone-alpes/lyon',
    'bordeaux': 'france/nouvelle-aquitaine/bordeaux'
}
FILES = ['listings.csv.gz', 'reviews.csv.gz', 'calendar.csv.gz']
DATE = '2024-09-15'  # Vérifier dates sur insideairbnb.com

def download_city(city_key, date):
    base = f"http://data.insideairbnb.com/{CITIES[city_key]}/{date}/data/"
    os.makedirs(f"data/{city_key}", exist_ok=True)
    for file in FILES:
        response = requests.get(base + file)
        if response.status_code == 200:
            with open(f"data/{city_key}/{file}", 'wb') as f:
                f.write(response.content)
            print(f"✓ {city_key}/{file}")

for city in CITIES:
    download_city(city, DATE)
```

**Temps exécution** : 15-30 min

---

## Datasets académiques Zenodo/Figshare

| Dataset | URL | Villes | Taille | Licence |
|---------|-----|--------|--------|---------|
| **European Cities (Gyódi 2021)** | https://zenodo.org/records/4446043 | Paris + 9 capitales EU | 10.8 MB | CC BY 4.0 |
| **Hugging Face mirror** | https://huggingface.co/datasets/kraina/airbnb | Idem | 9.39 MB | CC BY 4.0 |
| **OSF French Rentals** | DOI: 10.17605/OSF.IO/CW37U | Marché locatif FR (pas Airbnb) | Variable | CC BY |

**Publications associées** :
- Gyódi & Nawaro (2021) "Determinants of Airbnb prices" - Tourism Management
- Alsudais (2020) "Data quality issues in Inside Airbnb" - Decision Support Systems (DOI: 10.1016/j.dss.2020.113453)

**GAP CRITIQUE** : Aucun dataset académique longitudinal >50MB n'existe pour Lyon/Bordeaux sur Zenodo/Figshare.

---

## Inside Airbnb Data Request - Procédure complète

### Formulaires officiels
- **Données archivées (>12 mois)** : https://forms.gle/16E5RttAGM12Dx2dA
- **Nouvelles régions** : https://forms.gle/HjssGT3GEeBnst8Q9
- **Contact** : data@insideairbnb.com

### Grille tarifaire (USD)

| Villes | Recherche mission-aligned | Commercial |
|--------|---------------------------|------------|
| 1 | $300 | $500 |
| 2 | $500 | $800 |
| 3 | **$700** | $1,100 |
| 5 | $1,000 | $1,600 |
| 10 | $1,750 | $2,350 |

**Réductions équité globale** : -10% (pays revenus moyens-supérieurs), -25% (revenus moyens-inférieurs/faibles)

### Critères priorité
- **Très haute** : Activistes, journalistes, résidents (mission-aligned)
- **Haute** : Gouvernements/administrations
- **Moyenne** : Recherche académique housing/gentrification
- **Basse** : Recherche commerciale tourisme/pricing

### Format livraison
- Fichiers CSV compressés (.csv.gz)
- Liens de téléchargement direct
- Licence CC BY 4.0

### Délais
Non documentés officiellement. Prévoir 1-4 semaines selon priorité.

---

## Archive.org / Tom Slee - Snapshots disponibles

### Tom Slee Archive (2013-2017) - GRATUIT ✅

| Ville | Période | Snapshots | Téléchargement |
|-------|---------|-----------|----------------|
| **Paris** | Nov 2013 - Juil 2017 | 16 | https://s3.amazonaws.com/tomslee-airbnb-data-2/paris.zip |
| **Lyon** | Mai 2016 - Juil 2017 | 8 | https://s3.amazonaws.com/tomslee-airbnb-data-2/lyon.zip |
| **Bordeaux** | Mars 2016 - Juin 2017 | 7 | https://s3.amazonaws.com/tomslee-airbnb-data-2/bordeaux.zip |
| **Nice** | Juin 2016 - Juil 2017 | 11 | https://s3.amazonaws.com/tomslee-airbnb-data-2/nice.zip |

**Évolution Paris** : 19,004 listings (2013) → 70,158 listings (2017)

### Archive.org Wayback Machine
⚠️ **Limitation** : Capture les pages HTML mais **PAS les fichiers CSV**. Les données brutes ne sont pas archivées.

### Inside Airbnb - Données gratuites actuelles

| Ville | Dernière date | URL |
|-------|---------------|-----|
| Paris | Sept 2025 | https://data.insideairbnb.com/france/ile-de-france/paris/ |
| Lyon | 18 Sept 2025 | https://data.insideairbnb.com/france/auvergne-rhone-alpes/lyon/2025-09-18/data/ |
| Bordeaux | 18 Sept 2025 | https://data.insideairbnb.com/france/nouvelle-aquitaine/bordeaux/2025-09-18/data/ |

**Accès gratuit** : 12 derniers mois uniquement (snapshots trimestriels)

---

## Verdict : meilleure option pour projet Paris 2019 vs 2024

### Scénario A : Comparaison Paris pré-COVID (2019) vs actuel (2024)

| Option | Données 2019 | Données 2024 | Coût | Temps setup | Recommandation |
|--------|--------------|--------------|------|-------------|----------------|
| **Inside Airbnb Request** | ✅ Via request | ✅ Gratuit | ~$300-500 | 2-4 semaines | ⭐⭐⭐⭐⭐ **RECOMMANDÉ** |
| **Tom Slee + IA actuel** | ❌ Max 2017 | ✅ Gratuit | $0 | 1 jour | ⭐⭐☆☆☆ Gap 2018-2023 |
| **Zenodo EU dataset** | ❌ 2021 only | ❌ 2021 only | $0 | 30 min | ⭐⭐☆☆☆ Pas longitudinal |

### Scénario B : Analyse multi-villes France (Paris + Lyon + Bordeaux)

| Option | Couverture | Période | Coût | Trade-off |
|--------|------------|---------|------|-----------|
| **IA Request 3 villes** | Complète | 2015-2024 | **$700** | Meilleur rapport qualité/prix |
| **Tom Slee + script custom** | Partielle | 2016-2017 + 2024 | $0 | Gap 7 ans, analyse limitée |
| **DIY mensuel 12 mois** | 2024 seulement | 12 snapshots | $0 | Pas de comparaison pré-COVID |

### Recommandation finale

**Pour une analyse Paris 2019 vs 2024** : Soumettez une demande Inside Airbnb à $300 pour Paris uniquement (données archivées 2019), combinée avec le téléchargement gratuit des snapshots 2024. **Délai total : ~3 semaines. Budget : $300.**

**Pour les trois villes françaises** : La demande groupée à **$700** pour Paris/Lyon/Bordeaux représente le meilleur investissement. Aucune alternative gratuite ne couvre cette combinaison avec profondeur historique.

**Option gratuite maximale** : Combiner Tom Slee (2013-2017) + snapshots actuels gratuits. Permet une analyse de croissance long-terme mais avec gap 2018-2023 impossible à combler gratuitement.

---

## Ressources complémentaires

### OSM + Airbnb (méthodologie)
- **AReburg/Airbnb-Price-Prediction** : Pipeline ML Vienna avec features OSM (restaurants, métro, attractions)
- **amac-lfc/airbnb** : London avec OSMnx + calculs temps trajet

### Data dictionary officiel
https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/

### Pattern URL Inside Airbnb
```
https://data.insideairbnb.com/{country}/{region}/{city}/{YYYY-MM-DD}/data/{file}.csv.gz
```

**Fichiers disponibles par snapshot** : `listings.csv.gz`, `calendar.csv.gz`, `reviews.csv.gz`, `neighbourhoods.geojson`
