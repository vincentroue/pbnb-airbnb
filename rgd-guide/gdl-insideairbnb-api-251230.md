---
ukp: "Guide Inside Airbnb API = structure URLs datasets villes européennes fichiers disponibles listings calendar reviews snapshots trimestriels"
dcr: 25-12-30
dup: 25-12-30
tags:
  - pq/PBNB
  - DEI
tl: "gdl-insideairbnb-api"
---

# Guide API Inside Airbnb - Téléchargement Datasets

## 📋 Vue d'ensemble

**Inside Airbnb** : Projet open-source fournissant données publiques Airbnb pour analyse impact locations court-terme sur communautés locales.

**Site principal** : https://insideairbnb.com/
**Get the Data** : https://insideairbnb.com/fr/get-the-data/
**Data Dictionary** : http://insideairbnb.com/data-dictionary.html

## 🔗 Structure URLs

### Pattern général

```
http://data.insideairbnb.com/{country}/{region}/{city}/{date}/data/{file_name}
```

**Composants** :
- `{country}` : Pays en minuscules-tirets (ex: `france`, `united-kingdom`)
- `{region}` : Région administrative (ex: `ile-de-france`, `england`)
- `{city}` : Ville en minuscules-tirets (ex: `paris`, `london`)
- `{date}` : Date snapshot format `YYYY-MM-DD` (ex: `2024-12-12`)
- `{file_name}` : Nom fichier (voir section Fichiers disponibles)

### Exemples URLs

**Paris** (dernier snapshot décembre 2024) :
```
http://data.insideairbnb.com/france/ile-de-france/paris/2024-12-12/data/listings.csv.gz
http://data.insideairbnb.com/france/ile-de-france/paris/2024-12-12/data/calendar.csv.gz
http://data.insideairbnb.com/france/ile-de-france/paris/2024-12-12/data/neighbourhoods.geojson
```

**Londres** :
```
http://data.insideairbnb.com/united-kingdom/england/london/2024-12-10/data/listings.csv.gz
```

**Berlin** :
```
http://data.insideairbnb.com/germany/be/berlin/2024-12-21/data/listings.csv.gz
```

## 📂 Fichiers disponibles

### Listings (annonces)

| Fichier | Description | Taille typique | Compression |
|---------|-------------|----------------|-------------|
| `listings.csv.gz` | **Listings détaillés** (74 colonnes : prix, coordonnées GPS, hôte, reviews, disponibilité) | 10-50 MB | Gzip |
| `listings.csv` | Version non compressée (parfois indisponible) | 50-200 MB | Non |

**Colonnes clés** (74 total, voir Data Dictionary) :
- **Identifiants** : `id`, `listing_url`, `scrape_id`
- **Localisation** : `latitude`, `longitude`, `neighbourhood_cleansed`, `neighbourhood_group_cleansed`
- **Prix** : `price`, `weekly_price`, `monthly_price`
- **Hôte** : `host_id`, `host_name`, `host_since`, `host_listings_count`, `host_is_superhost`
- **Caractéristiques** : `room_type`, `accommodates`, `bedrooms`, `beds`, `bathrooms_text`
- **Disponibilité** : `availability_30`, `availability_60`, `availability_90`, `availability_365`
- **Reviews** : `number_of_reviews`, `review_scores_rating`, `reviews_per_month`
- **Réglementation** : `license`, `instant_bookable`, `minimum_nights`, `maximum_nights`

### Calendar (disponibilités)

| Fichier | Description | Taille typique |
|---------|-------------|----------------|
| `calendar.csv.gz` | Disponibilités 365 jours par listing (date, prix jour, dispo) | 50-200 MB |

**Colonnes** (4) :
- `listing_id` : ID listing
- `date` : Date format YYYY-MM-DD
- `available` : Disponible (t/f)
- `price` : Prix nuit (format texte avec $, ex: "$75.00")

**Dimensions** : ~65k listings Paris × 365 jours = ~24M lignes

### Reviews (avis)

| Fichier | Description | Taille typique |
|---------|-------------|----------------|
| `reviews.csv.gz` | Avis clients détaillés (date, reviewer_id, commentaire) | 20-100 MB |
| `reviews.csv` | Version summary (nombre avis par listing) | 1-5 MB |

**Colonnes reviews détaillés** (6) :
- `listing_id`, `id` (review_id), `date`, `reviewer_id`, `reviewer_name`, `comments`

### Neighbourhoods (quartiers)

| Fichier | Description | Format |
|---------|-------------|--------|
| `neighbourhoods.csv` | Liste quartiers (neighbourhood, neighbourhood_group) | CSV 1-10 KB |
| `neighbourhoods.geojson` | **Géométries quartiers** (polygones GeoJSON) | GeoJSON 100KB-5MB |

**Usage géométries** :
- Cartographie choroplèthes (prix médian par quartier)
- Spatial join listings → quartiers (si latitude/longitude imprécises)
- Agrégation statistiques quartier

## 📅 Dates snapshots

**Fréquence** : Trimestrielle (4 snapshots/an)
**Mois typiques** : Mars, Juin, Septembre, Décembre

**Exemple calendrier 2024** :
- 2024-03-08 (Mars Q1)
- 2024-06-10 (Juin Q2)
- 2024-09-12 (Septembre Q3)
- 2024-12-12 (Décembre Q4)

**Historique** : Snapshots conservés depuis 2015 pour certaines villes (Paris, Londres, NYC)

**⚠️ IMPORTANT** : Dates snapshots **varient par ville**. Consulter page Get the Data pour dates exactes.

## 🌍 Villes disponibles

### France (4 villes)

| Ville | Region | Country Path | Dernier snapshot (estimé) |
|-------|--------|--------------|---------------------------|
| Paris | Île-de-France | `france/ile-de-france/paris` | 2024-12-12 |
| Lyon | Auvergne-Rhône-Alpes | `france/auvergne-rhone-alpes/lyon` | 2024-09-11 |
| Bordeaux | Nouvelle-Aquitaine | `france/nouvelle-aquitaine/bordeaux` | 2024-09-08 |
| Pays Basque | Nouvelle-Aquitaine | `france/nouvelle-aquitaine/pays-basque` | 2024-09-09 |

### Europe (sélection 5 villes)

| Ville | Country | Region | Path | Dernier snapshot |
|-------|---------|--------|------|------------------|
| Londres | UK | England | `united-kingdom/england/london` | 2024-12-10 |
| Berlin | Allemagne | BE | `germany/be/berlin` | 2024-12-21 |
| Madrid | Espagne | Comunidad Madrid | `spain/comunidad-de-madrid/madrid` | 2024-12-18 |
| Rome | Italie | Lazio | `italy/lazio/rome` | 2024-12-19 |
| Budapest | Hongrie | Budapest | `hungary/budapest/budapest` | 2024-12-18 |

**Total villes mondiales** : ~120 villes (Europe, Amériques, Asie, Océanie)

## 🛠️ Utilisation pratique

### Téléchargement manuel (cURL)

```bash
# Paris listings
curl -o listings_paris.csv.gz \
  http://data.insideairbnb.com/france/ile-de-france/paris/2024-12-12/data/listings.csv.gz

# Décompression
gunzip listings_paris.csv.gz

# Lyon calendar
curl -o calendar_lyon.csv.gz \
  http://data.insideairbnb.com/france/auvergne-rhone-alpes/lyon/2024-09-11/data/calendar.csv.gz
```

### Script Python (voir sp01-download-insideairbnb-251230.py)

```python
import requests
from pathlib import Path

def download_dataset(country, region, city, date, file_name, output_dir):
    """Télécharger dataset Inside Airbnb."""
    url = f"http://data.insideairbnb.com/{country}/{region}/{city}/{date}/data/{file_name}"
    output_path = Path(output_dir) / city / file_name

    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        print(f"✓ Téléchargé : {output_path}")
    else:
        print(f"✗ Erreur {response.status_code} : {url}")

# Usage
download_dataset('france', 'ile-de-france', 'paris', '2024-12-12',
                 'listings.csv.gz', 'data/raw/france')
```

### Lecture Python (Pandas)

```python
import pandas as pd
import gzip

# Listings (décompression automatique Pandas)
df = pd.read_csv('data/raw/france/paris/listings.csv.gz', compression='gzip')
print(df.shape)  # (65000, 74)
print(df.columns.tolist())

# Nettoyage prix (format "$75.00" → 75.0)
df['price_clean'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)

# Calendar
cal = pd.read_csv('data/raw/france/paris/calendar.csv.gz')
cal['price_clean'] = cal['price'].str.replace('$', '').str.replace(',', '').astype(float)
cal['date'] = pd.to_datetime(cal['date'])
```

### Lecture R

```r
library(tidyverse)
library(sf)

# Listings
df <- read_csv('data/raw/france/paris/listings.csv.gz')
glimpse(df)

# Nettoyage prix
df <- df %>%
  mutate(price_clean = as.numeric(gsub('[$,]', '', price)))

# Géométries quartiers (GeoJSON)
neighbourhoods <- st_read('data/raw/france/paris/neighbourhoods.geojson')
plot(st_geometry(neighbourhoods))

# Spatial join listings → quartiers
df_sf <- st_as_sf(df, coords = c('longitude', 'latitude'), crs = 4326)
df_joined <- st_join(df_sf, neighbourhoods)
```

## 📊 Indicateurs clés calculables

### Marché global
- **Nb listings totaux** : `nrow(df)`
- **Prix médian nuit** : `median(df$price_clean, na.rm=TRUE)`
- **Taux occupation moyen** : `mean((365 - df$availability_365) / 365)`

### Profils hôtes
- **% hôtes multi-listings** : `sum(df$host_listings_count > 3) / nrow(df)`
- **Concentration Gini** : Index inégalité distribution listings par hôte

### Spatial
- **Prix médian par quartier** : `df %>% group_by(neighbourhood_cleansed) %>% summarise(median_price = median(price_clean))`
- **Densité listings/km²** : Spatial join avec fonds carte communes

### Temporel (avec calendar)
- **Évolution prix 2019-2024** : Charger snapshots multiples, calculer TCAM
- **Saisonnalité** : Prix moyen par mois (été vs hiver)

## 🔍 Data Dictionary (résumé)

**Documentation complète** : http://insideairbnb.com/data-dictionary.html

### Colonnes essentielles listings

```
id                          : ID unique listing
listing_url                 : URL Airbnb listing
scrape_id                   : ID scrape (snapshot)
last_scraped                : Date dernier scrape

name                        : Titre annonce
description                 : Description

host_id                     : ID hôte
host_name                   : Nom hôte
host_since                  : Date inscription hôte
host_location               : Localisation hôte
host_response_time          : Temps réponse (within an hour, etc.)
host_response_rate          : Taux réponse (%)
host_listings_count         : Nb listings hôte (total)
host_is_superhost           : Superhost (t/f)

neighbourhood               : Quartier (texte libre)
neighbourhood_cleansed      : Quartier normalisé (utilisé cartographie)
neighbourhood_group_cleansed: Groupe quartiers (arrondissement Paris)

latitude                    : Latitude WGS84
longitude                   : Longitude WGS84

room_type                   : Type logement (Entire home/apt, Private room, Shared room, Hotel room)
accommodates                : Nb personnes max
bedrooms                    : Nb chambres
beds                        : Nb lits
bathrooms_text              : Nb salles bain (texte, ex: "1.5 baths")

price                       : Prix nuit (format "$75.00")
weekly_price                : Prix semaine (parfois null)
monthly_price               : Prix mois (parfois null)

minimum_nights              : Séjour minimum nuits
maximum_nights              : Séjour maximum nuits

availability_30/60/90/365   : Nb jours disponibles prochains 30/60/90/365 jours

number_of_reviews           : Nb avis total
number_of_reviews_ltm       : Nb avis derniers 12 mois (ltm = last twelve months)
review_scores_rating        : Note moyenne (0-100, ex: 94)
reviews_per_month           : Avis/mois moyen

instant_bookable            : Réservation instantanée (t/f)
license                     : Numéro licence (si réglementation locale)
```

## ⚠️ Limitations & Précautions

### Qualité données
- **Prix manquants** : Certains listings sans prix (listings inactifs)
- **Géocodage imprécis** : Latitude/longitude arrondies ~100m (privacy)
- **Données incomplètes** : Champs `weekly_price`, `monthly_price`, `license` souvent NULL
- **Texte non structuré** : `bathrooms_text` nécessite parsing ("1.5 baths", "2 shared baths")

### Biais échantillonnage
- **Snapshots trimestriels** : Pas données temps réel, saisonnalité non captée entre snapshots
- **Scraping partiel** : Listings privés/cachés non inclus
- **Évolution méthodologie** : Changements colonnes entre snapshots (vérifier compatibilité)

### Réglementation
- **Données publiques** : Listings visibles publiquement sur Airbnb, mais vérifier ToS Airbnb pour usage commercial
- **Anonymisation** : Hôtes identifiables (host_name, host_id) → attention RGPD si publication

### Performance
- **Fichiers volumineux** : Calendar Paris ~200 MB compressé, 24M lignes décompressé
- **Recommandations** :
  - Utiliser DuckDB ou Parquet pour stockage optimisé
  - Charger uniquement colonnes nécessaires (`usecols` Pandas)
  - Filtrer période temporelle avant analyses (calendar)

## 🔗 Ressources complémentaires

### Documentation officielle
- **About** : http://insideairbnb.com/about.html
- **Methodology** : http://insideairbnb.com/about.html#methodology
- **FAQ** : http://insideairbnb.com/about.html#faq
- **Data Assumptions** : http://insideairbnb.com/data-assumptions.html

### Projets similaires
- **AirDNA** (commercial) : https://www.airdna.co/
- **Tom Slee dataset** (2015-2017, obsolète) : http://tomslee.net/airbnb-data-collection-get-the-data

### Analyses académiques
- Rechercher Google Scholar : "Inside Airbnb" + "gentrification" / "housing" / "tourism"
- Exemple : Wachsmuth & Weisler (2018) "Airbnb and the rent gap"

---

**Dernière mise à jour** : 2025-12-30
**Snapshots référence** : Décembre 2024 (Paris, Londres, Berlin, Madrid, Rome, Budapest)
