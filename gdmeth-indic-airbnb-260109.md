# Référentiel Méthodologique — Projet PBNB Airbnb

**dcr**: 26-01-09
**dup**: 26-01-09
**status**: En cours

---

## Question centrale

> **Comment se structurent les marchés Airbnb dans les grandes villes européennes, et quels indicateurs permettent de comparer leur intensité, leur professionnalisation et leur impact potentiel sur le logement ?**

---

## Hypothèses structurantes

| Code | Hypothèse | Statut | Section |
|------|-----------|--------|---------|
| **H1** | Paris et Londres dominent en volume mais pas nécessairement en densité | ⬜ À tester | Volumes |
| **H2** | Les villes touristiques (Rome, Florence, Venice) ont un ratio entire_home plus élevé | ⬜ À tester | Structure |
| **H3** | La professionnalisation (multi-listings) est plus forte dans les capitales | ⬜ À tester | Hosts |
| **H4** | Les prix médians corrèlent avec le PIB/habitant local | ⬜ À tester | Prix |
| **H5** | Les quartiers centraux/touristiques concentrent >50% des listings | ⬜ À tester | Spatial |

---

## Questions évaluatives par axe

### Axe 1 — Volumes & Structure du marché

| # | Question | Indicateurs | Méthode | Livrable |
|---|----------|-------------|---------|----------|
| Q1 | Quelle est la taille relative des marchés ? | nb_listings, nb_hosts | Barres comparatives | Graphique ranking |
| Q2 | Quelle évolution mars→sept 2025 ? | TCAM listings, delta % | Tableau évolution | Tendances |
| Q3 | Quelle structure par type de logement ? | % entire_home, % private_room | Barres empilées | Profil par ville |

### Axe 2 — Prix & Positionnement

| # | Question | Indicateurs | Méthode | Livrable |
|---|----------|-------------|---------|----------|
| Q4 | Quels niveaux de prix par ville ? | prix_median, Q25, Q75 | Boxplots | Comparatif |
| Q5 | Quelle dispersion des prix ? | IQR, ratio Q75/Q25 | Stats descriptives | Tableau |
| Q6 | Prix par type de logement ? | prix_median × room_type | Facettes | Graphique |

### Axe 3 — Professionnalisation & Hosts

| # | Question | Indicateurs | Méthode | Livrable |
|---|----------|-------------|---------|----------|
| Q7 | Quel ratio listings/host ? | calculated_host_listings_count | Distribution | Histogramme |
| Q8 | Quelle part de multi-hosts ? | % hosts avec >1 listing, >5 listings | Seuils | Tableau |
| Q9 | Concentration du marché ? | Top 10% hosts = X% listings | Courbe Lorenz | Gini |

### Axe 4 — Activité & Disponibilité

| # | Question | Indicateurs | Méthode | Livrable |
|---|----------|-------------|---------|----------|
| Q10 | Quelle activité moyenne ? | reviews_per_month, number_of_reviews | Stats | Comparatif |
| Q11 | Quelle disponibilité ? | availability_365, % dispo >180j | Distribution | Profils |
| Q12 | Listings "fantômes" ? | % reviews=0 ET dispo>300j | Filtres | Comptage |

### Axe 5 — Analyse spatiale (Paris/Lyon focus)

| # | Question | Indicateurs | Méthode | Livrable |
|---|----------|-------------|---------|----------|
| Q13 | Quels quartiers concentrent l'offre ? | nb_listings par neighbourhood | Choroplèthe | Carte |
| Q14 | Gradient centre-périphérie ? | densité × distance centre | Scatter | Corrélation |
| Q15 | Prix par quartier ? | prix_median par neighbourhood | Choroplèthe | Carte |

---

## Indicateurs clés — Formulaire de référence

### Niveau 1 : Volume

| Indicateur | Formule | Unité | Source |
|------------|---------|-------|--------|
| **Nb listings** | `COUNT(id)` | Effectif | sumlistings |
| **Nb hosts** | `COUNT(DISTINCT host_id)` | Effectif | sumlistings |
| **Ratio L/H** | `nb_listings / nb_hosts` | Ratio | Calcul |
| **TCAM listings** | `((L_t/L_0)^(1/n) - 1) × 100` | % | Calcul |

### Niveau 2 : Structure

| Indicateur | Formule | Seuil interprétation |
|------------|---------|---------------------|
| **% Entire home** | `COUNT(room_type='Entire') / n × 100` | >80% = marché pro |
| **% Private room** | `COUNT(room_type='Private') / n × 100` | >30% = économie partage |
| **% Shared room** | `COUNT(room_type='Shared') / n × 100` | Rare (<5%) |

### Niveau 3 : Prix

| Indicateur | Formule | Attention |
|------------|---------|-----------|
| **Prix médian** | `MEDIAN(price)` | Par nuit, devise locale |
| **Q25, Q75** | `PERCENTILE(price, 0.25/0.75)` | Dispersion |
| **IQR** | `Q75 - Q25` | Hétérogénéité marché |
| **Prix/capacité** | `price / accommodates` | Normalisation |

### Niveau 4 : Professionnalisation

| Indicateur | Formule | Seuil |
|------------|---------|-------|
| **Multi-hosts** | `hosts avec listings_count > 1` | >20% = pro |
| **Super-hosts** | `hosts avec listings_count > 5` | Investisseurs |
| **Gini hosts** | Concentration listings | >0.5 = concentré |

### Niveau 5 : Activité

| Indicateur | Formule | Interprétation |
|------------|---------|----------------|
| **Reviews/mois** | `reviews_per_month` | Proxy activité |
| **Disponibilité** | `availability_365` | <90j = très occupé |
| **Nb reviews** | `number_of_reviews` | Historique activité |

---

## Colonnes dataset — Classification

### Colonnes ESSENTIELLES (garder)

| Colonne | Type | Usage |
|---------|------|-------|
| id | int | Identifiant unique |
| host_id | int | Groupement hosts |
| latitude, longitude | float | Spatial |
| neighbourhood | str | Agrégation |
| room_type | str | Segmentation |
| price | float | Variable clé |
| minimum_nights | int | Filtre court/long terme |
| number_of_reviews | int | Activité |
| reviews_per_month | float | Intensité |
| availability_365 | int | Disponibilité |
| calculated_host_listings_count | int | Professionnalisation |

### Colonnes UTILES (optionnel)

| Colonne | Type | Usage |
|---------|------|-------|
| review_scores_rating | float | Qualité (⚠️ 30% null) |
| review_scores_* | float | Détail qualité |
| accommodates | int | Capacité |
| bedrooms, beds | int | Taille |
| host_is_superhost | bool | Statut |

### Colonnes LOURDES (à supprimer pour optimisation)

| Colonne | Taille | % Null | Raison suppression |
|---------|--------|--------|-------------------|
| amenities | 149 MB | 0% | JSON, analyse NLP séparée |
| description | 134 MB | 3% | Texte, NLP séparée |
| neighborhood_overview | 86 MB | 53% | Texte, peu utile |
| host_about | 67 MB | 52% | Texte, peu utile |
| host_picture_url | 45 MB | 0% | URL, inutile |
| host_thumbnail_url | 44 MB | 0% | URL, inutile |
| picture_url | 43 MB | 0% | URL, inutile |
| listing_url | 26 MB | 0% | URL, reconstructible |
| host_url | 26 MB | 0% | URL, reconstructible |

**Gain potentiel** : ~620 MB → réduction 50% de la taille dataset

---

## Cleaning recommandé

### Étape 1 : Suppression colonnes lourdes

```python
DROP_COLS = [
    'amenities', 'description', 'neighborhood_overview', 'host_about',
    'host_picture_url', 'host_thumbnail_url', 'picture_url',
    'listing_url', 'host_url', 'source', 'last_scraped',
    'calendar_last_scraped', 'scrape_id'
]
df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
```

### Étape 2 : Conversion types

```python
# Prix : supprimer $ et convertir
df['price'] = df['price'].replace(r'[\$,]', '', regex=True).astype(float)

# Dates
df['last_review'] = pd.to_datetime(df['last_review'])

# Booléens
df['host_is_superhost'] = df['host_is_superhost'].map({'t': True, 'f': False})
```

### Étape 3 : Filtres qualité

```python
# Supprimer prix aberrants
df = df[(df['price'] > 10) & (df['price'] < 10000)]

# Supprimer listings sans localisation
df = df.dropna(subset=['latitude', 'longitude'])
```

---

## Sources et limites

### Limites Inside Airbnb

| Limite | Impact | Mitigation |
|--------|--------|------------|
| Localisation anonymisée (0-150m) | Erreurs jointure IRIS | Analyser à l'arrondissement |
| Pas de données transactions | Revenus = estimations | Utiliser reviews comme proxy |
| Snapshot = photo instantanée | Listings disparus non captés | Comparer snapshots |
| ~30% null sur scores | Analyses qualité partielles | Exclure ou imputer |

### Données complémentaires (optionnel)

| Source | Contenu | Usage |
|--------|---------|-------|
| INSEE Filosofi | Revenus médians IRIS | Ratio prix/revenu |
| INSEE RP | Logements par IRIS | Ratio pénétration |
| IGN Admin Express | Contours géo | Cartographie |

---

## Checklist validation

### Avant analyse
- [ ] Vérifier colonnes présentes dans dataset
- [ ] Vérifier taux de null par colonne clé
- [ ] Tester cohérence prix (pas de valeurs aberrantes)
- [ ] Documenter snapshot utilisé

### Après analyse
- [ ] Chaque question a une réponse
- [ ] Graphiques annotés et lisibles
- [ ] Limites explicitement mentionnées
- [ ] Comparaison inter-villes cohérente

---

*Document généré le 2026-01-09*
