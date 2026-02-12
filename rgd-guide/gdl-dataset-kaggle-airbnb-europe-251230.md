---
ukp: "Dataset Kaggle Airbnb Europe = snapshot 2019/2020 10 villes consolidé Paris Berlin Amsterdam 8 variables communes weekday/weekend CC0 4MB comparaison COVID"
dcr: 25-12-30
dup: 25-12-30
tags:
  - pq/PBNB
  - dbd
tl: "dataset-kaggle-airbnb-europe"
---

# Dataset Kaggle - Airbnb Prices in European Cities

**URL** : https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities
**Source originale** : Zenodo (https://zenodo.org/record/4446043)
**Auteurs** : Gyódi & Nawaro (2021)
**Licence** : CC0 1.0 Universal (Public Domain) - **Libre usage commercial**

---

## 📊 Vue d'ensemble

### Couverture géographique

**10 villes européennes** :
1. Amsterdam
2. Athènes
3. Barcelone
4. Berlin ✅
5. Budapest
6. Lisbonne
7. Londres
8. **Paris** ✅
9. Rome
10. Vienne

**⚠️ IMPORTANT** : **Paris ET Berlin** sont dans le dataset → Comparaison France/Allemagne possible

### Date de collecte

- **Publication Zenodo** : Janvier 2021
- **Article soumis** : 2020
- **Estimation données** : **Fin 2019 / début 2020** (avant COVID)
- **Dernière mise à jour Kaggle** : 10 mars 2024 (version 3)

### Taille & Format

- **Taille totale** : 4.1 MB (ZIP)
- **Format** : CSV (2 fichiers par ville = 20 fichiers)
- **Structure** :
  - `paris_weekdays.csv` (jours de semaine)
  - `paris_weekends.csv` (week-ends)

**⚠️ Clarification weekday/weekend** :
- Ce ne sont **PAS deux snapshots temporels différents**
- Ce sont les **mêmes listings** avec prix différents selon jour semaine vs week-end
- Un listing apparaît dans les 2 fichiers avec 2 prix différents

---

## 📋 Variables disponibles (Kaggle)

### Noyau commun avec Inside Airbnb (8 variables)

Ces variables sont **directement comparables** avec datasets Inside Airbnb 2024 :

| Variable Kaggle | Variable Inside Airbnb | Type | Compatible |
|-----------------|------------------------|------|------------|
| `room_type` | `room_type` | Catégorique | ✅ 100% |
| `bedrooms` | `bedrooms` | Numérique | ✅ 100% |
| `person_capacity` | `accommodates` | Numérique | ✅ 100% |
| `host_is_superhost` | `host_is_superhost` | Booléen | ✅ 100% |
| `multi` | `calculated_host_listings_count > 1` | Booléen | ✅ Calculable |
| `biz` | `host_is_superhost + multi` | Booléen | ⚠️ Approximation |
| `lng`, `lat` | `longitude`, `latitude` | Numérique | ✅ 100% |
| `realSum` | `price` | Numérique | ⚠️ Weekday vs global |

### Variables uniques Kaggle (NON dans Inside Airbnb)

| Variable | Description | Type |
|----------|-------------|------|
| `dist` | Distance centre-ville (km) | Numérique |
| `metro_dist` | Distance métro le plus proche | Numérique |
| `attr_index` | Index attractivité quartier | Numérique |
| `attr_index_norm` | Index attractivité normalisé | Numérique |
| `rest_index` | Index densité restaurants | Numérique |
| `rest_index_norm` | Index restaurants normalisé | Numérique |
| `guest_satisfaction_overall` | Note satisfaction globale | Numérique |
| `cleanliness_rating` | Note propreté | Numérique |

### Variables uniques Inside Airbnb (NON dans Kaggle)

- `number_of_reviews` (nb avis total)
- `reviews_per_month` (avis/mois)
- `minimum_nights` (séjour minimum)
- `availability_365` (jours disponibles/an)
- `neighbourhood_cleansed` (quartier normalisé)

---

## 🎯 Cas d'usage pour votre projet

### ✅ Forces du dataset Kaggle

1. **Comparaison avant/après COVID**
   - Kaggle 2019/2020 + Inside Airbnb 2024 = 5 ans d'écart
   - Impact pandémie + réglementations (loi ELAN nov 2018)

2. **Variables enrichies spatiales**
   - `dist`, `metro_dist` → Analyses accessibilité
   - `attr_index`, `rest_index` → Analyses attractivité quartiers

3. **Données consolidées multi-villes**
   - 10 villes format homogène (pas besoin pipelines ETL complexes)
   - Comparaisons cross-cities (Paris vs Berlin vs Amsterdam)

4. **Petite taille (4 MB)**
   - Pas de contraintes stockage/mémoire
   - Chargement rapide pour prototypage

### ❌ Limitations

1. **Snapshot unique (pas de série temporelle)**
   - Impossible analyse saisonnalité 2019
   - Pas de TCAM ou tendances intra-année

2. **Variables manquantes vs Inside Airbnb 2024**
   - Pas de `number_of_reviews` (indicateur popularité)
   - Pas de `availability_365` (indicateur occupation)
   - Pas de `minimum_nights` (indicateur stratégie pricing)

3. **Biais de survie**
   - Listings 2019 disparus en 2024 non visibles
   - Comparaison biaisée si profils différents (professionnels vs particuliers)

4. **Saisonnalité confondante**
   - Si Kaggle snapshot été 2019 + Inside Airbnb snapshot hiver 2024
   - Effet saison confondu avec effet temporel

---

## 📐 Stratégie d'analyse recommandée

### Option 1 - Comparaison avant/après COVID (Simple)

**Ville unique** : Paris (ou Berlin)

**Analyse** :
1. **Cross-section 2019** (Kaggle)
   - Distribution prix, types logements, superhôtes
   - Gradient spatial (prix vs distance centre)
   - Profils hôtes (multi-listings)

2. **Cross-section 2024** (Inside Airbnb)
   - Mêmes analyses que 2019

3. **Comparaison 2019 vs 2024**
   - Évolution prix médian (inflation ajustée)
   - Changement profil hôtes (% multi-listings)
   - Évolution densité listings par quartier

**Livrables** :
- 2 notebooks EDA (2019 + 2024)
- 1 notebook comparatif avec tests statistiques
- 1 dashboard Shiny filtres temporels (2019/2024)

### Option 2 - Comparaison multi-villes (Ambitieux)

**3-4 villes** : Paris, Berlin, Amsterdam, (Londres)

**Analyse** :
- Clustering villes selon structure marché (prix, densité, % superhôtes)
- Hétérogénéité impact COVID par ville
- Analyse réglementaire (Paris loi ELAN vs autres villes)

**Livrables** :
- 1 pipeline ETL consolidation 4 villes × 2 snapshots
- 1 rapport Quarto comparatif multi-villes
- 1 dashboard Shiny multi-sélection villes/périodes

---

## 💾 Téléchargement & Setup

### Étape 1 - Télécharger depuis Kaggle

**Manuel** :
1. Aller sur : https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities
2. Cliquer "Download" (nécessite compte Kaggle gratuit)
3. Décompresser ZIP → 20 fichiers CSV

**Automatique (Kaggle API)** :
```bash
# Installer Kaggle CLI
pip install kaggle

# Configurer authentification (créer API token depuis Kaggle profile)
# Placer kaggle.json dans ~/.kaggle/ (Linux) ou C:\Users\{user}\.kaggle\ (Windows)

# Télécharger dataset
kaggle datasets download -d thedevastator/airbnb-prices-in-european-cities -p data/raw/kaggle

# Décompresser
unzip data/raw/kaggle/airbnb-prices-in-european-cities.zip -d data/raw/kaggle/european-cities
```

### Étape 2 - Charger les données

**Python (Pandas)** :
```python
import pandas as pd

# Charger Paris weekdays + weekends
paris_weekdays = pd.read_csv('data/raw/kaggle/european-cities/paris_weekdays.csv')
paris_weekends = pd.read_csv('data/raw/kaggle/european-cities/paris_weekends.csv')

# Ajouter colonne période
paris_weekdays['period'] = 'weekday'
paris_weekends['period'] = 'weekend'

# Consolider (si besoin analyse weekday/weekend)
paris_all = pd.concat([paris_weekdays, paris_weekends], ignore_index=True)

print(f"Paris weekdays : {len(paris_weekdays)} listings")
print(f"Paris weekends : {len(paris_weekends)} listings")
print(f"Total (dédupliqué par listing_id) : {paris_all['listing_id'].nunique()}")
```

**R (tidyverse)** :
```r
library(tidyverse)

# Charger Paris
paris_weekdays <- read_csv('data/raw/kaggle/european-cities/paris_weekdays.csv')
paris_weekends <- read_csv('data/raw/kaggle/european-cities/paris_weekends.csv')

# Ajouter période
paris_weekdays <- paris_weekdays %>% mutate(period = 'weekday')
paris_weekends <- paris_weekends %>% mutate(period = 'weekend')

# Moyenne prix par listing (si weekday/weekend)
paris_avg_price <- bind_rows(paris_weekdays, paris_weekends) %>%
  group_by(across(-c(realSum, period))) %>%
  summarise(avg_price = mean(realSum, na.rm = TRUE), .groups = 'drop')
```

### Étape 3 - Harmoniser avec Inside Airbnb

```python
# Kaggle 2019
kaggle_df = pd.read_csv('data/raw/kaggle/european-cities/paris_weekdays.csv')

# Inside Airbnb 2024
airbnb_df = pd.read_csv('data/raw/france/paris/listings.csv.gz')

# Harmoniser colonnes (noyau commun)
kaggle_harmonized = kaggle_df.rename(columns={
    'person_capacity': 'accommodates',
    'realSum': 'price'
}).assign(
    snapshot_date = '2019-12-01',  # Estimation
    source = 'kaggle'
)[['room_type', 'bedrooms', 'accommodates', 'host_is_superhost',
   'lng', 'lat', 'price', 'snapshot_date', 'source']]

airbnb_harmonized = airbnb_df.rename(columns={
    'longitude': 'lng',
    'latitude': 'lat'
}).assign(
    price = airbnb_df['price'].str.replace('$', '').str.replace(',', '').astype(float),
    snapshot_date = '2024-12-12',
    source = 'inside_airbnb'
)[['room_type', 'bedrooms', 'accommodates', 'host_is_superhost',
   'lng', 'lat', 'price', 'snapshot_date', 'source']]

# Consolider
consolidated_df = pd.concat([kaggle_harmonized, airbnb_harmonized], ignore_index=True)
consolidated_df.to_csv('data/processed/paris_2019_2024.csv', index=False)
```

---

## 📊 Métriques clés comparables

### Prix

```python
# Prix médian par snapshot
consolidated_df.groupby('snapshot_date')['price'].median()

# Évolution prix médian (inflation ajustée)
import numpy as np
inflation_rate = 1.12  # Inflation EUR 2019-2024 (~12%)

price_2019 = kaggle_harmonized['price'].median()
price_2024 = airbnb_harmonized['price'].median()
price_2019_adjusted = price_2019 * inflation_rate

evolution_real = ((price_2024 - price_2019_adjusted) / price_2019_adjusted) * 100
print(f"Évolution prix réel (inflation ajustée) : {evolution_real:.1f}%")
```

### Profils hôtes

```python
# % superhôtes
consolidated_df.groupby('snapshot_date')['host_is_superhost'].mean() * 100

# Distribution types logements
consolidated_df.groupby(['snapshot_date', 'room_type']).size().unstack(fill_value=0)
```

### Spatial

```python
import geopandas as gpd
from shapely.geometry import Point

# Créer GeoDataFrame
gdf = gpd.GeoDataFrame(
    consolidated_df,
    geometry=gpd.points_from_xy(consolidated_df.lng, consolidated_df.lat),
    crs='EPSG:4326'
)

# Densité listings par km² (avec hexagones H3 ou grid)
# Évolution densité centre vs périphérie
```

---

## 🔗 Ressources complémentaires

### Dataset Kaggle

- **Page Kaggle** : https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities
- **Zenodo original** : https://zenodo.org/record/4446043
- **Article académique** : Gyódi & Nawaro (2021) - Airbnb pricing strategies

### Inside Airbnb

- **Get the Data** : https://insideairbnb.com/fr/get-the-data/
- **Data Dictionary** : http://insideairbnb.com/data-dictionary.html

### Projets similaires utilisant Kaggle dataset

- GitHub "airbnb european cities" : Rechercher projets EDA avec ce dataset
- Notebooks Kaggle : https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities/code

---

## ⚖️ Verdict faisabilité

| Critère | Score | Commentaire |
|---------|-------|-------------|
| **Faisabilité technique** | 8/10 | Harmonisation simple (8 variables communes) |
| **Richesse analytique** | 6/10 | Limité par snapshot unique, mais variables spatiales enrichies |
| **Pertinence capstone** | 9/10 | Suffisant pour démontrer compétences EDA + ML + carto |
| **Risque usine à gaz** | 3/10 | Simple si ville unique, gérable si multi-villes |
| **Différenciation** | 7/10 | Comparaison avant/après COVID + réglementation = angle solide |

**Conclusion** :
- **Option solide et réaliste** pour capstone
- Perte granularité temporelle **compensée par** :
  - Variables enrichies (dist, metro_dist, indices attractivité)
  - Comparaison avant/après COVID défendable académiquement
  - Consolidation multi-villes facilitée

**Recommandation** :
1. Commencer par **Paris uniquement** (prototype rapide)
2. Si fluide → Ajouter Berlin ou Amsterdam (comparaison cross-cities)
3. Compléter avec données INSEE (revenus, population) pour enrichissement contextuel

---

**Dernière mise à jour** : 2025-12-30
**Auteur** : Session Claude Code pbnb-airbnb-log-jrr-jpy
