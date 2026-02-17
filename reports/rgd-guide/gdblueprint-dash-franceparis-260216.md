# Blueprint — Dashboard Airbnb France (Paris · Lyon · Bordeaux)

Dashboard Quarto OJS + MapLibre · Inspiré Inside Airbnb · 3 villes françaises

## Architecture cible

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: Titre + KPI briques (3-4) + mini-texte storytelling │
│ [51K listings Paris] [8K Lyon] [10K Bordeaux] [3 villes FR] │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ BENCHMARK TABLE: 8-10 villes référence (KPI comparison)     │
│ London · Berlin · NYC · Lisbon · Paris · Lyon · Bordeaux    │
│ Colonnes: listings, prix_med, pct_multi, pression, etc.     │
│ Style 0table.js : barres + z-score violet/vert              │
└─────────────────────────────────────────────────────────────┘

┌───────────────────────┬─────────────────────────────────────┐
│ MAP Paris (40%)       │ TABLE territoire (60%)              │
│ MapLibre              │ Toggle: Arrondissement / IRIS       │
│ - Choroplèthe IRIS    │ Colonnes barres z-score             │
│ - Heatmap (slider)    │ Scroll horizontal top               │
│ - Points toggle       │ Search + CSV + pagination (300 max) │
│ Controls:             │ Écart à moyenne ville en couleur    │
│ - KPI selector        │                                     │
│ - Arr. dropdown       │                                     │
│ - Opacity slider      │                                     │
│ - Légende dynamique   │                                     │
├───────────────────────┼─────────────────────────────────────┤
│ MAP Lyon (40%)        │ TABLE Lyon arr/IRIS                 │
│ Même modèle Paris     │ Même modèle Paris                   │
│ 185 IRIS · 9 arr.     │                                     │
├───────────────────────┼─────────────────────────────────────┤
│ MAP Bordeaux (40%)    │ TABLE Bordeaux IRIS                 │
│ 88 IRIS ville         │ Même modèle Paris                   │
│ + métropole option    │                                     │
└───────────────────────┴─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TOP 200 HOSTS (full width)                                  │
│ Tri: nb_listings desc · Colonnes: host_name, n_listings,    │
│ prix_moyen, room_types, ville, part_offre_pct               │
│ Style catchy, distinct du tableau territoire                 │
│ Search + pagination                                         │
└─────────────────────────────────────────────────────────────┘
```

## Données requises

### Existant
- `dbsumlistings_2506_cons_global.parquet` — 789K listings (host_id, host_name, prix, etc.)
- `recap_iris_paris_2506.csv` — 965 IRIS Paris avec KPIs
- `kpi_global_by_city_2506.csv` — 64 villes benchmarks
- CONTOURS-IRIS GPKG national (48K IRIS France entière)
- `dbcln-communes-full.parquet` (ptod) — INSEE logements par commune

### À créer (scripts)
1. **`sp09-recap-iris-france-260216.py`** — Pipeline recap_iris pour Lyon + Bordeaux
   - Spatial join listings × IRIS (gpd.sjoin)
   - Agrégation: n, n_hosts, prix_med, pct_multi, pct_entire, pct_longterm, dispo_med, reviews_med
   - Output: `recap_iris_lyon_2506.csv` + `recap_iris_bordeaux_2506.csv`
   - Ou fichier unique: `recap_iris_france_2506.csv` (Paris + Lyon + Bordeaux)

2. **`ddict-airbnb.json`** — Dictionnaire indicateurs Airbnb
   - Types: stock (n, n_hosts), prix (prix_med), pct (pct_multi, pct_entire), ind (airbnb_1000log)
   - Polarité: n=neutre, pct_multi=-1 (défavorable si haut), prix_med=neutre
   - Unités: "listings", "€/nuit", "%", "L/1000 log"
   - Sert au z-score violet/vert dans le tableau

3. **`0table-airbnb.js`** — Helper tableau OJS adapté d'0table.js ptod
   - Import ddict-airbnb.json
   - renderBarCell avec z-score et couleurs violet/vert
   - renderSortHeader, pagination, search, CSV export
   - Scroll horizontal top synchronisé
   - Simplifié vs ptod (pas de France row sticky, pas de regdep)

## Composants MapLibre par ville

### Couches
1. **Choroplèthe IRIS** — fill-color par KPI sélectionné, légende dynamique
2. **Heatmap densité** — poids=prix, **slider opacité** (range 0-100)
3. **Points listings** — toggle, colorés par room_type
4. **Bordure IRIS highlight** — on hover

### Contrôles (overlay gauche)
- Dropdown arrondissement → fly-to + filtre IRIS
- Select KPI choroplèthe (6 variables)
- Slider opacité heatmap (0-100%)
- Checkboxes couches on/off

### Popup IRIS hover
- Nom IRIS + arrondissement
- Mini-tableau 7 KPIs
- **Écart à moyenne ville** en couleur (vert/orange) — v2

### Légende
- Gradient 5 paliers avec bornes
- Mise à jour dynamique selon KPI sélectionné

## Tableau territoire (par ville)

### Colonnes arrondissement
| Colonne | Type | Unité | Polarité |
|---------|------|-------|----------|
| Arr. | text | — | — |
| Listings | stock | n | neutre |
| Hosts | stock | n | neutre |
| Prix médian | prix | € | neutre |
| % Multi-host | pct | % | -1 |
| % Entire home | pct | % | neutre |
| % Long-term | pct | % | neutre |
| L/1000 logements | ind | ratio | -1 (pression) |
| Logements INSEE | stock | n | neutre |

### Colonnes IRIS (même + dispo_med, reviews_med)

### Style barres
- **Stock (n)** : barre bleue proportionnelle, z-score 3 bins (clair/moyen/foncé)
- **Prix** : barre orange gradient
- **Pct** : barre avec couleur z-score vs moyenne ville (vert=favorable, violet=défavorable)
- **Ind (pression)** : barre avec flèche ▲▼ vs référence France/moyenne

### Interactions
- Search bar texte libre
- Tri cliquable (↑↓) par colonne
- Pagination 300 max
- Scroll horizontal synchronisé top+bottom
- Export CSV (UTF-8 BOM, séparateur ;)

## KPI briques header

### 3-4 briques variables (style Inside Airbnb)
```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  51 283      │ │   153 €      │ │  39.8%       │ │  20.1%       │
│  listings    │ │  prix médian │ │  multi-host  │ │  long-term   │
│  Paris       │ │  nuit        │ │              │ │  ≥30 nuits   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```
- Fond bleu foncé (#0a4c6a) texte blanc, ou cards bordure gauche colored
- Valeurs calculées dynamiquement selon ville sélectionnée

### Mini-texte storytelling (2-3 phrases)
"Paris concentre 51K annonces Airbnb actives, soit 1 listing pour 27 logements.
Le marché est dominé par les logements entiers (85%) et la professionnalisation
touche 40% de l'offre via les multi-hosts."

## Benchmark table (8-10 villes)

| Ville | Listings | Prix med | % Multi | % Entire | L/1000 log | Pression |
|-------|----------|----------|---------|----------|------------|----------|
| London | 62K | 142 | 35 | 72 | — | — |
| Paris | 51K | 153 | 40 | 85 | 36.7 | — |
| Berlin | 9K | 78 | 28 | 52 | — | — |
| NYC | — | — | — | — | — | — |
| Lisbon | 21K | 115 | 62 | 76 | — | — |
| Lyon | 8K | 97 | 42 | 82 | — | — |
| Bordeaux | 10K | 108 | 45 | 83 | — | — |

Source: kpi_global_by_city_2506.csv (déjà calculé pour les 64 villes)

## Phases d'implémentation

### Phase 1 — Données (sp09)
- [ ] Script spatial join IRIS pour Lyon + Bordeaux
- [ ] Merge recap_iris : Paris + Lyon + Bordeaux en fichier unique
- [ ] Créer ddict-airbnb.json
- [ ] Agréger top hosts France (3 villes)

### Phase 2 — Helper table OJS
- [ ] Adapter 0table.js → 0table-airbnb.js (standalone, pas d'import ptod)
- [ ] Z-score violet/vert avec polarité
- [ ] Scroll horizontal top synchronisé
- [ ] Test isolé dans un QMD minimal

### Phase 3 — Dashboard v3 (Paris seul d'abord)
- [ ] Header KPI briques + storytelling
- [ ] Benchmark table 8 villes
- [ ] Map Paris améliorée (slider heatmap, légende écart)
- [ ] Table OJS avec 0table-airbnb.js
- [ ] Top 200 hosts Paris

### Phase 4 — Multi-villes
- [ ] Dupliquer modèle pour Lyon (185 IRIS, 9 arr.)
- [ ] Dupliquer pour Bordeaux (88 IRIS, pas d'arr.)
- [ ] Navigation/tabs entre villes ou scroll vertical
- [ ] Benchmark table commune en header

### Phase 5 — Polish
- [ ] Responsive / mobile
- [ ] Performance (simplifier géométries, limiter features)
- [ ] Deploy quarto publish (Netlify ou GitHub Pages)
- [ ] Interconnexion carte ↔ tableau (clic IRIS = highlight row)

## Fichiers cibles

| Fichier | Rôle |
|---------|------|
| `reports/rpt-pbnb-dash-franceparis-260215.qmd` | Dashboard principal |
| `reports/helpers/0table-airbnb.js` | Helper tableau OJS |
| `reports/helpers/ddict-airbnb.json` | Dictionnaire indicateurs |
| `data/interim/recap_iris_france_2506.csv` | IRIS KPIs 3 villes |
| `scripts/sp09-recap-iris-france-260216.py` | Pipeline spatial join |

## Stack technique

- **Carte** : MapLibre GL JS v3 (UMD via CDN)
- **Tableau** : OJS vanilla (inspiré 0table.js ptod)
- **Data prep** : R (sf, dplyr, arrow) dans setup chunk
- **Format** : Quarto dashboard (orientation: rows)
- **Interactivité** : OJS `viewof` + `ojs_define()` pour passer R→OJS
- **Déploiement** : quarto preview (dev) → quarto publish (prod)
- **Contrainte** : OJS requiert http:// (pas file://)

---

*Blueprint v1.0 — 2026-02-16*
