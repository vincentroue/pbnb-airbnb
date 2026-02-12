---
ukp: "Vrac logs sessions projet PBNB Airbnb = notes quotidiennes avancement phases setup ETL dashboard centralisation documentation"
dcr: 25-12-30
dup: 25-12-30
code: PBNB
tags:
  - pq/PBNB
  - pd
tl: "vpPBNB-airbnb-log-jrr-jpy-vrk"
---

# ,,vpPBNB - Airbnb Logements France/Europe - Vrac

## &logs-Sessions

### 2025-12-30 - Initialisation projet PBNB

**Phase** : Setup infrastructure

**Actions** :
- Création structure projet pbnb-airbnb-log-jrr-jpy dans PDS/
- Dossiers data/raw/ organisés par zone (france/, europe/) et ville
- Structure minimale : _npbacklog/, scripts/, notebooks/, rgd-guide/, ytest/, zu/
- Génération notes evergreen + vrac avec planning 5 phases
- .gitignore configuré (Python, R, Jupyter, datasets volumineux)

**Décisions** :
- Stack mixte R/Python validé (R=carto+Shiny, Python=ETL+ML)
- Périmètre 9 villes : 4 France (Paris, Lyon, Bordeaux, Pays Basque) + 5 Europe (Londres, Berlin, Madrid, Rome, Budapest)
- Priorité phase 1 : Script téléchargement automatique datasets Inside Airbnb
- Historique ciblé : Dernier snapshot 2024 + snapshot 2019-2020 (comparaison COVID)

**Blocages** :
- WebFetch site Inside Airbnb échoue (contenu JavaScript dynamique)
- URLs datasets à documenter manuellement via inspection page

**Next** :
- Créer script Python sp01_download_insideairbnb.py avec pattern URLs
- Documenter structure fichiers disponibles (listings, calendar, reviews, neighbourhoods)
- Copier fichiers existants pzmRRtest vers nouveau projet (template EDA, dataset Paris)

---

## &notes-Techniques

### Structure datasets Inside Airbnb

**Pattern URLs** (à valider par inspection manuelle) :
```
http://data.insideairbnb.com/{country}/{city}/{date}/data/{file}
```

**Fichiers par ville** :
- `listings.csv.gz` : Listings détaillés (~65k lignes Paris, 16 colonnes summary)
- `listings_detailed.csv.gz` : Version étendue (74 colonnes)
- `calendar.csv.gz` : Disponibilités 365 jours
- `reviews.csv.gz` : Avis clients
- `reviews_summary.csv` : Résumé avis
- `neighbourhoods.csv` : Liste quartiers
- `neighbourhoods.geojson` : Géométries quartiers

**Dates snapshots** : Trimestriels (mars, juin, septembre, décembre)

### Villes françaises Inside Airbnb

Basé sur https://insideairbnb.com/fr/explore/ :
- **Bordeaux** : Nouvelle-Aquitaine
- **Lyon** : Auvergne-Rhône-Alpes
- **Paris** : Île-de-France
- **Pays Basque** : Pyrénées-Atlantiques

### Stack technique détails

**R packages prioritaires** :
- `sf` : Géométries spatiales, spatial join
- `leaflet` : Cartes interactives HTML
- `shiny` : Dashboard réactif
- `DT` : Tableaux interactifs
- `tidyverse` : Manipulation données (dplyr, ggplot2)
- `skimr` : Statistiques descriptives

**Python packages prioritaires** :
- `pandas` : Manipulation DataFrames
- `geopandas` : Géométries spatiales Python
- `requests` : Téléchargement HTTP
- `duckdb` : Base analytique SQL (alternative Parquet)

---

## &ideas

### Dashboard Shiny architecture

**Idée maquette 3 colonnes** :
```
┌─────────────┬──────────────────┬─────────────────┐
│  Filtres    │   Carte          │  Graphiques     │
│  Sidebar    │   Leaflet        │  + Tableau      │
│             │   Interactive    │  DT sortable    │
│  - Ville    │   Zoom quartiers │  Gradient prix  │
│  - Période  │   Popup détails  │                 │
│  - Prix     │   Cluster points │  Top 10         │
│  - Type     │                  │  quartiers      │
└─────────────┴──────────────────┴─────────────────┘
```

**Réactivité** :
- Filtre ville → Recharge données + recalcule indicateurs
- Filtre période → Filtre snapshot temporal
- Clic carte → Highlight quartier dans tableau
- Sélection tableau → Zoom carte sur quartier

### Comparaison avant/après COVID

**Snapshots cibles** :
- **2019 Q4** : Avant COVID (décembre 2019)
- **2020 Q2** : Confinement (juin 2020)
- **2024 Q4** : Situation actuelle (décembre 2024)

**Métriques évolution** :
- TCAM nb listings 2019-2024
- Variation prix médian
- Changement profil hôtes (% multi-listings)
- Taux occupation moyen

---

## &links-Sessions

**RCP sessions** (à venir dans _npbacklog/) :
- Aucune session RCP pour le moment

**Notes modules** (à venir) :
- `,epPBNB-ppETL-evg🍃_pq.md` : Module pipeline ETL (si complexe)
- `,epPBNB-ppSHINY-evg🍃_pq.md` : Module dashboard Shiny (si complexe)

---

## TASK Dataview

```dataview
TASK
FROM "pq/PDS/pbnb-airbnb-log-jrr-jpy"
WHERE contains(tags, "pq/PBNB")
```
