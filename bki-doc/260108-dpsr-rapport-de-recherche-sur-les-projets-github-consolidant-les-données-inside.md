---
ukp: |

aliases: []
dcr: 26-02-03_110846687
codx:
tags: []
pry: x
stf: x
sts: x
---

cnt::
url:: https://claude.ai/chat/ac0994fd-f468-48ed-9402-79eaba296e0a

# Inside Airbnb Multi-City Data Consolidation: European Dataset Analysis and Download Strategies

# Projets GitHub consolidation Inside Airbnb multi-villes : état des lieux complet

**Aucun projet "gold standard" n'existe actuellement** pour des données Inside Airbnb consolidées couvrant plusieurs villes européennes avec historique temporel 2015-2022. Cependant, cette recherche a identifié **8 projets complémentaires** qui, combinés stratégiquement, permettent de construire le dataset souhaité. Le projet Tom Slee offre l'historique le plus profond (2013-2017) tandis que des scripts comme tmasjc/airbnb-market-data permettent d'automatiser le téléchargement des snapshots récents depuis Inside Airbnb.

---

## Projet recommandé #1 : tomslee/airbnb-data-collection

- **URL** : https://github.com/tomslee/airbnb-data-collection
- **Données** : https://tomslee.net/airbnb-data-collection-get-the-data
- **Villes** : ✅ Paris (16 surveys) ✅ Amsterdam ✅ Barcelona ✅ Berlin ✅ Rome ✅ London + 80 autres villes mondiales
- **Période** : **2013-11 à 2017-07** (historique longitudinal réel)
- **Snapshots Paris** : 16 surveys de novembre 2013 à juillet 2017 (19k→70k listings)
- **Format** : ZIP → CSV (room_id, host_id, room_type, neighborhood, reviews, price, lat/lng)
- **Taille** : ~500 Mo compressé pour toutes les villes
- **Téléchargement** : https://tomslee.net/airbnb-data-collection-get-the-data (liens directs par ville)
- **Réplicabilité** : ⭐⭐⭐⭐⭐
- **Licence** : Creative Commons Attribution-NonCommercial 2.5

**Pourquoi pertinent** : C'est le seul projet offrant un **véritable panel longitudinal** sur plusieurs années pour Paris et de nombreuses villes européennes. Les données couvrent la période pré-régulation (avant les lois strictes de 2018), ce qui est idéal pour analyser l'évolution du marché avant les contraintes légales. La méthodologie est documentée et les données sont cohérentes entre les snapshots. Limitation majeure : collection arrêtée mi-2017.

---

## Projet recommandé #2 : gabrielleberanger/airbnb-visualization

- **URL** : https://github.com/gabrielleberanger/airbnb-visualization
- **Villes** : ✅ Paris uniquement
- **Période** : **Mai 2015 - Novembre 2019** (4,5 ans d'historique)
- **Snapshots Paris** : 48 fichiers mensuels avec données consolidées
- **Format** : CSV (depuis Inside Airbnb)
- **Taille** : ~200 Mo estimé
- **Téléchargement** : Données intégrées au repo + scripts Python pour mise à jour
- **Réplicabilité** : ⭐⭐⭐⭐
- **Dernière activité** : 2020 (projet terminé)

**Pourquoi pertinent** : **Meilleur historique temporel pour Paris** avec des données mensuelles de 2015 à 2019. Le projet inclut des visualisations de la croissance du marché parisien, des analyses par arrondissement, et des scripts Python réutilisables pour le scraping automatique d'Inside Airbnb. Permet une analyse comparative Paris 2019 vs 2024 si combiné avec des données récentes.

---

## Projet recommandé #3 : MargotMarchais/Airbnb_France_Rshiny

- **URL** : https://github.com/MargotMarchais/Airbnb_France_Rshiny
- **Villes** : ✅ Paris ✅ Lyon ✅ Bordeaux (les 3 villes françaises cibles)
- **Période** : Octobre 2022 (snapshot unique)
- **Snapshots Paris** : 1 (données fin octobre 2022)
- **Format** : CSV (Inside Airbnb) - ~700 Mo total
- **Taille** : ~700 Mo pour les 3 villes
- **Téléchargement** : Données incluses dans le repo + scripts R/Shiny
- **Réplicabilité** : ⭐⭐⭐⭐
- **Scripts automatisation** : OUI (R/Shiny, clustering k-means, cartes Leaflet)

**Pourquoi pertinent** : **Seul projet couvrant simultanément Paris, Lyon et Bordeaux** avec des données nettoyées et une application Shiny complète. L'analyse inclut clustering géographique, visualisations ggplot2, et cartes interactives. Excellente documentation en français. Limitation : pas d'historique temporel, mais fournit une base méthodologique réutilisable pour analyser plusieurs villes françaises.

---

## Projet recommandé #4 : Zenodo (Gyódi & Nawaro - University of Warsaw)

- **URL** : https://zenodo.org/records/4446043
- **DOI** : 10.5281/zenodo.4446043
- **Villes** : ✅ Paris ✅ Amsterdam ✅ Athens ✅ Barcelona ✅ Berlin ✅ Budapest ✅ Lisbon ✅ London ✅ Rome ✅ Vienna (10 villes EU)
- **Période** : 2020-2021 (cross-sectional)
- **Snapshots Paris** : 2 fichiers (paris_weekdays.csv, paris_weekends.csv)
- **Format** : CSV (20 fichiers - 2 par ville)
- **Taille** : **10.8 MB** total, ~51,707 listings
- **Téléchargement** : Direct via Zenodo (DOI persistant)
- **Réplicabilité** : ⭐⭐⭐⭐⭐
- **Licence** : CC BY 4.0
- **Publication associée** : Tourism Management (DOI: 10.1016/j.tourman.2021.104319)

**Pourquoi pertinent** : **Dataset académique de référence** avec DOI citable, 10 villes européennes majeures, et variables enrichies (distance centre-ville, proximité métro, indices attractivité/restaurants). Utilisé dans de nombreuses publications académiques. Idéal pour comparaisons cross-sectionnelles entre villes européennes, mais **pas de dimension temporelle**.

---

## Projet recommandé #5 : LucPeeters21/Airbnb-pricing (Tilburg University)

- **URL** : https://github.com/LucPeeters21/Airbnb-pricing
- **Villes** : ✅ Toutes villes EU disponibles sur Inside Airbnb (dynamique)
- **Période** : Données courantes (scraping automatisé)
- **Snapshots Paris** : Via scraper automatique
- **Format** : CSV (généré par scraper)
- **Taille** : Variable selon villes sélectionnées
- **Téléchargement** : Via script `Inside_Airbnb_link_scraper.py`
- **Réplicabilité** : ⭐⭐⭐⭐⭐
- **Dernière activité** : 312 commits, projet actif

**Pourquoi pertinent** : **Pipeline automatisé complet** avec scraper Python (BeautifulSoup, Selenium), workflow Make, et application Shiny pour visualisation. Le script scrape automatiquement tous les liens disponibles sur Inside Airbnb et télécharge les données. Facilement adaptable pour collecter des snapshots historiques en modifiant les URLs cibles. Projet universitaire bien documenté avec 5 contributeurs.

---

## Scripts automatisation téléchargement

### tmasjc/airbnb-market-data ⭐ RECOMMANDÉ

- **URL** : https://github.com/tmasjc/airbnb-market-data
- **Technologie** : R + Docker
- **Usage CLI** :
```bash
./download_csv.R list                 # Liste toutes les villes disponibles
./download_csv.R paris                # Télécharge dernier snapshot Paris
./download_csv.R list -s paris        # Liste tous les snapshots historiques Paris
./download_csv.R paris -i 7           # Télécharge snapshot spécifique par index
```
- **Docker** : `docker run -it rocker/tidyverse R` puis exécuter le script
- **Avantages** : Simple, CLI intuitif, accès aux snapshots historiques, Docker-ready
- **Stars** : 6 | **Forks** : 8

### kytola/CleanAirbnb (Cornell University)

- **URL** : https://github.com/kytola/CleanAirbnb
- **Technologie** : Python (Jupyter Notebooks)
- **Structure** : 3 dossiers (Download, Clean, Graphics)
- **Auteur** : Prof. Lauri Kytömaa, Cornell University
- **Licence** : Apache-2.0
- **Avantages** : Notebooks bien documentés, pipeline complet download→clean→visualize

### aditya-prasad-projects/Data-Pipeline-for-analyzing-Inside-Airbnb-dataset

- **URL** : https://github.com/aditya-prasad-projects/Data-Pipeline-for-analyzing-Inside-Airbnb-dataset
- **Technologie** : Apache Airflow, AWS S3, Spark, Redshift, Athena
- **Fonctionnalités** : Scraping automatique URLs, transfert S3, backfill depuis 2015, scheduling mensuel
- **Avantages** : Solution enterprise-grade, Data Lake queryable, scalable
- **Prérequis** : Compte AWS

---

## Datasets académiques Zenodo/Figshare

### Dataset principal trouvé

| Attribut | Valeur |
|----------|--------|
| **Titre** | Determinants of Airbnb prices in European cities |
| **URL** | https://zenodo.org/records/4446043 |
| **DOI** | 10.5281/zenodo.4446043 |
| **Auteurs** | Gyódi, Kristóf & Nawaro, Łukasz (University of Warsaw) |
| **Villes** | 10 capitales européennes dont Paris |
| **Statistiques** | 10K+ views, 13K+ downloads |
| **Article associé** | Tourism Management, DOI: 10.1016/j.tourman.2021.104319 |

Aucun dataset longitudinal multi-villes n'a été trouvé sur Zenodo, Figshare ou OSF. Le dataset ci-dessus est le plus complet mais reste cross-sectional.

---

## Réponses aux questions spécifiques

**1. Existe-t-il UN projet "gold standard" consolidation Inside Airbnb multi-cities Europe ?**

**Non.** Aucun projet unique ne consolide des snapshots multi-villes européennes avec historique 2015-2022. Le plus proche est le dataset Tom Slee (2013-2017) mais il s'arrête en 2017.

**2. Quels sont les 3-5 meilleurs projets complémentaires à combiner ?**

La stratégie optimale combine :
- **Tom Slee** (historique 2013-2017 multi-villes)
- **gabrielleberanger** (Paris 2015-2019 détaillé)
- **tmasjc/airbnb-market-data** (script téléchargement snapshots récents)
- **Inside Airbnb archives** (données 2020-2024 téléchargeables)

**3. Pour Paris spécifiquement : quel projet a l'historique le plus long ?**

**gabrielleberanger/airbnb-visualization** avec des données Paris de mai 2015 à novembre 2019 (48 snapshots mensuels). Pour la période antérieure, Tom Slee remonte jusqu'à novembre 2013.

**4. Existe-t-il scripts Python/R réutilisables pour télécharger automatiquement snapshots historiques ?**

**Oui** :
- `tmasjc/airbnb-market-data` (R, CLI avec accès historique par index)
- `kytola/CleanAirbnb` (Python Jupyter)
- `LucPeeters21/Airbnb-pricing` (Python scraper)

**5. Des chercheurs ont-ils déposé datasets consolidés sur Zenodo/Figshare/OSF ?**

Le seul dataset académique multi-villes trouvé est celui de Gyódi & Nawaro sur Zenodo (10 villes, cross-sectional). Aucun panel longitudinal n'a été identifié sur ces plateformes.

---

## Plan B : stratégie création pipeline download automatisé

En l'absence de dataset prêt à l'emploi, voici la stratégie recommandée pour construire le dataset Paris 2015-2024 :

**Étape 1 : Consolider les sources existantes**

| Période | Source | Villes |
|---------|--------|--------|
| 2013-2017 | Tom Slee archives | Paris + 30 villes EU |
| 2015-2019 | gabrielleberanger | Paris uniquement |
| 2017-2024 | Inside Airbnb archives | Paris, Lyon, Bordeaux |

**Étape 2 : Script Python pour téléchargement batch Inside Airbnb**

```python
import requests
from bs4 import BeautifulSoup
import os

def get_all_paris_snapshots():
    """Scrape tous les liens historiques Paris depuis Inside Airbnb"""
    url = "http://insideairbnb.com/get-the-data/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Pattern URL: data.insideairbnb.com/france/ile-de-france/paris/{date}/
    paris_links = [a['href'] for a in soup.find_all('a', href=True) 
                   if 'paris' in a['href'].lower() and 'listings.csv' in a['href']]
    return paris_links

def download_snapshot(url, output_dir="data/paris"):
    """Télécharge un snapshot et extrait la date"""
    os.makedirs(output_dir, exist_ok=True)
    # Extraire date depuis URL
    date = url.split('/')[-3]  # Format: 2024-09-13
    filename = f"{output_dir}/listings_{date}.csv.gz"
    
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")

# Usage
for link in get_all_paris_snapshots():
    download_snapshot(link)
```

**Étape 3 : Structure URL Inside Airbnb**

Les archives suivent ce pattern :
```
http://data.insideairbnb.com/{country}/{region}/{city}/{date}/data/listings.csv.gz
```

Pour Paris :
```
http://data.insideairbnb.com/france/ile-de-france/paris/2024-09-13/data/listings.csv.gz
```

**Étape 4 : Contact Inside Airbnb**

Murray Cox (fondateur) peut fournir des archives plus anciennes sur demande. Email via le site insideairbnb.com.

---

## Tableau récapitulatif final

| Projet | Paris | Lyon | Bordeaux | Période | Format | Historique | Scripts Auto |
|--------|-------|------|----------|---------|--------|------------|--------------|
| Tom Slee | ✅ | ❌ | ❌ | 2013-2017 | CSV | ✅ 16 surveys | Python |
| gabrielleberanger | ✅ | ❌ | ❌ | 2015-2019 | CSV | ✅ 48 monthly | Python |
| MargotMarchais | ✅ | ✅ | ✅ | 2022 | CSV | ❌ snapshot | R/Shiny |
| Zenodo Gyódi | ✅ | ❌ | ❌ | 2020-21 | CSV | ❌ cross-sect | ❌ |
| LucPeeters21 | ✅ | ✅ | ✅ | actuel | CSV | ❌ live | Python |
| tmasjc | ✅ | ✅ | ✅ | multi | CSV | ✅ index | R/Docker |
| Inside Airbnb | ✅ | ✅ | ✅ | 2015-2024 | CSV.GZ | ✅ manuel | ❌ |

---

## Conclusion

La recherche confirme qu'**aucun projet unique ne répond aux critères complets** (Paris+Lyon+Bordeaux, historique 2015-2022, données consolidées). La stratégie recommandée est de **combiner Tom Slee (2013-2017) + gabrielleberanger (Paris 2015-2019) + téléchargement manuel des archives Inside Airbnb (2017-2024)** en utilisant les scripts tmasjc ou kytola. Pour Lyon et Bordeaux, seules les archives Inside Airbnb récentes sont disponibles. Le dataset Zenodo reste la meilleure option pour des comparaisons cross-sectionnelles entre villes européennes avec un DOI académique citable.
