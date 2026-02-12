---
ukp: "Dataset Kaggle Airbnb Europe = MÊMES listings 2 prix weekday/weekend (PAS snapshots mensuels) 10 villes 2019-2020 spatial econometrics Gyódi & Nawaro"
dcr: 25-12-30
dup: 25-12-30
tags:
  - pq/PBNB
  - dbd
tl: "rcp-analyse-kaggle-weekdays-vs-monthly"
---

# Analyse Dataset Kaggle - Pourquoi weekdays/weekends ?

**Question centrale** : Pourquoi des fichiers `paris_weekdays.csv` et `paris_weekends.csv` au lieu de listings mensuels comme Inside Airbnb ?

## Réponse courte

**Ce ne sont PAS deux snapshots temporels différents**, mais **les mêmes listings avec des prix différents** selon le type de réservation (jours semaine vs week-end).

## Détails méthodologie

### Source académique

- **Auteurs** : Gyódi, Kristóf & Nawaro, Łukasz (2021)
- **Publication** : *Tourism Management*, vol. 86, Article 104319
- **Dataset Zenodo** : https://zenodo.org/records/4446043
- **Kaggle** : https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities

### Date de collecte (estimation)

- **Publication Zenodo** : 13 janvier 2021
- **Collecte probable** : **Fin 2019 / début 2020** (AVANT COVID)
- **Mise à jour Kaggle** : 10 mars 2024 (version 3 - réupload sans nouvelle collecte)

⚠️ **IMPORTANT** : Pas de date de collecte explicite dans les métadonnées. L'année "2019" est une estimation basée sur :
- Publication janvier 2021 (délai publication académique ~6-12 mois)
- Pas de mention COVID dans le papier (suggère collecte pré-pandémie)

### Structure weekdays vs weekends

**Principe** : Airbnb affiche des **prix variables** selon le jour de réservation :
- **Weekdays** (lun-jeu) : Prix jours semaine, généralement plus bas
- **Weekends** (ven-dim) : Prix week-end, souvent majorés 10-30%

**Conséquence** : Chaque fichier capture les **prix affichés** pour une requête simulée :
- `paris_weekdays.csv` : Prix pour réservation 2 nuits jours semaine
- `paris_weekends.csv` : Prix pour réservation 2 nuits week-end

### Comparaison Inside Airbnb vs Kaggle

| Critère | Inside Airbnb | Kaggle (Gyódi & Nawaro) |
|---------|--------------|-------------------------|
| **Snapshot** | Mensuel (1 fois/mois) | Unique (fin 2019/début 2020) |
| **Prix** | Prix global/moyen listing | 2 prix séparés (weekday/weekend) |
| **Colonnes** | 74 variables détaillées | 20 variables économétriques |
| **Objectif** | Monitoring longitudinal | Étude spatial econometrics |
| **Format** | `listings.csv.gz` unique | `{city}_weekdays.csv` + `{city}_weekends.csv` |

## Analyse fichiers Paris

### Statistiques

```
Paris weekdays : 3130 listings
Paris weekends : 3558 listings
Colonnes       : 20
```

⚠️ **Nombres différents** (3130 vs 3558) → Pas exactement les mêmes listings dans les 2 fichiers

**Hypothèses** :
1. Certains hôtes n'acceptent que week-ends (logements saisonniers)
2. Disponibilité variable selon jour semaine
3. Filtres appliqués différemment lors de la collecte

### Exemple données

**Même listing dans 2 fichiers** (détecté via coordonnées GPS identiques) :

```csv
# Weekdays (ligne 2)
realSum,room_type,lng,lat
296.16,Private room,2.35385,48.86282

# Weekends (ligne 3)
realSum,room_type,lng,lat
290.10,Private room,2.35385,48.86282
```

→ **Mêmes coordonnées GPS** (2.35385, 48.86282) = même logement
→ Prix différents : 296€ (weekday) vs 290€ (weekend)

## Variables disponibles (20 colonnes)

### Compatibles Inside Airbnb

| Variable Kaggle | Variable Inside Airbnb | Compatible |
|-----------------|------------------------|------------|
| `room_type` | `room_type` | ✅ 100% |
| `person_capacity` | `accommodates` | ✅ 100% |
| `bedrooms` | `bedrooms` | ✅ 100% |
| `host_is_superhost` | `host_is_superhost` | ✅ 100% |
| `lng`, `lat` | `longitude`, `latitude` | ✅ 100% |
| `realSum` | `price` | ⚠️ Weekday vs global |

### Variables UNIQUES Kaggle (absentes Inside Airbnb)

| Variable | Description | Utilité |
|----------|-------------|---------|
| `dist` | Distance centre-ville (km) | Analyse gradient spatial |
| `metro_dist` | Distance métro le plus proche | Accessibilité transports |
| `attr_index` | Index attractivité quartier | Valeur touristique |
| `rest_index` | Index densité restaurants | Attractivité gastronomique |
| `guest_satisfaction_overall` | Note satisfaction globale | Qualité service |
| `cleanliness_rating` | Note propreté | Qualité hébergement |
| `multi` | Hôte avec 2-4 listings | Détection multi-propriétaires |
| `biz` | Hôte avec >4 listings | Détection professionnels |

## Cas d'usage recommandés

### ✅ Utiliser Kaggle SI

1. **Étude prix weekday vs weekend** - Variation saisonnalité courte
2. **Analyse spatiale enrichie** - Variables `dist`, `metro_dist`, `attr_index`
3. **Comparaison avant/après COVID** - Snapshot 2019/2020 + Inside Airbnb 2024
4. **Multi-villes consolidé** - 10 villes format homogène (pas besoin ETL complexe)

### ❌ NE PAS utiliser Kaggle SI

1. **Analyse longitudinale** - 1 snapshot unique (pas de TCAM, pas de tendances)
2. **Saisonnalité annuelle** - Pas de variation mensuelle
3. **Reviews détaillées** - Pas de `number_of_reviews`, `reviews_per_month`
4. **Disponibilité** - Pas de `availability_365`, `minimum_nights`

## Recommandation projet Paris

**Stratégie hybride** : Utiliser les **2 sources** pour analyse complémentaire

### Phase 1 - Snapshot 2019/2020 (Kaggle)

- Charger `paris_weekdays.csv` (baseline weekday)
- EDA : Distribution prix, types logements, gradient spatial (`dist`, `metro_dist`)
- Modèle spatial : Impact `attr_index` + `rest_index` sur prix

### Phase 2 - Snapshot 2024 (Inside Airbnb - pzmRRtest)

- Charger `data/raw/2412-paris/listings.csv` (décembre 2024)
- EDA : Mêmes analyses que 2019
- Comparaison évolution : Prix médian, % superhôtes, densité listings

### Phase 3 - Comparaison avant/après COVID

- Harmoniser colonnes communes (8 variables)
- Calculer évolution 2019→2024 :
  - Prix médian (inflation ajustée)
  - Distribution types logements (Entire home/apt vs Private room)
  - Profils hôtes (% superhôtes, % multi-listings)

## Références

- [Kaggle dataset](https://www.kaggle.com/datasets/thedevastator/airbnb-prices-in-european-cities)
- [Zenodo publication](https://zenodo.org/records/4446043)
- [Paper Tourism Management](https://doi.org/10.1016/j.tourman.2021.104319)
- [Inside Airbnb](https://insideairbnb.com/get-the-data/)

---

**Dernière mise à jour** : 2025-12-30
**Auteur** : Session Claude Code pbnb-airbnb-log-jrr-jpy
