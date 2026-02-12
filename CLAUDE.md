# CLAUDE.md - Projet pbnb-airbnb-log-jrr-jpy

Analyse Airbnb multi-villes avec données Inside Airbnb (2024-2025) et Kaggle Europe (2019/2020).

## Structure données

```
data/raw/zudb-inside-airbnbbnb/
├── europe/{country}/{city}/      # Pays européens
├── usa/united-states/{city}/     # États-Unis
└── world/{country}/{city}/       # Autres pays
```

### Flat view par ville

```
{ville}/
├── 25-03/
│   └── listings.csv.gz           ← GZ détaillé (74 cols)
├── 25-06/
│   └── listings.csv.gz
├── 25-03-XXX-{ville}_sumlistings.csv   ← Flat (18 cols)
├── 25-06-XXX-{ville}_sumlistings.csv
├── geo-XXX-{ville}_neighbourhoods.geojson  ← 1 par ville
└── nbh-XXX-{ville}_neighbourhoods.csv      ← 1 par ville
```

**Codes pays** : FRA, DEU, ITA, GBR, ESP, USA, CAN, AUS, JPN, BRA...

## Load Data

### Workflow (2 scripts)

```bash
# 1. Download (depuis https://insideairbnb.com/get-the-data/)
python scripts/sp04-download-insideairbnb-from-links-251231.py liens.txt -l -s -g -n

# 2. Flatten
python scripts/sp06-flatten-insideairbnb-251231.py
```

### sp04 - Download

| Option | Description |
|--------|-------------|
| `-l` | Listings.csv.gz uniquement |
| `-s` | + Sumlistings (tous snapshots) |
| `-g` | + GeoJSON (1/ville) |
| `-n` | + Neighbourhoods (1/ville) |
| `-e` | Filtre Europe |
| `-c france` | Filtre pays |
| `--dry-run` | Preview |

### sp06 - Flatten

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview |
| `--cleanup` | Supprime YYYY-MM-DD après |
| `-e`, `-c` | Filtres pays |

**Actions** : Copie extras flat → Renomme `YYYY-MM-DD/` → `YY-MM/` → Cleanup doublons

## Colonnes

**sumlistings (18)** : id, name, host_id, host_name, neighbourhood_group, neighbourhood, latitude, longitude, room_type, price, minimum_nights, number_of_reviews, last_review, reviews_per_month, calculated_host_listings_count, availability_365, number_of_reviews_ltm, license

**listings.csv.gz (74)** : Données complètes avec description, amenities, host details...

## Bases consolidées (data/interim/)

### 20 villes (courant)

| Fichier | Lignes | Taille | Contenu |
|---------|--------|--------|---------|
| `dbsumlistings_snaps_cons20city.parquet` | 1.41M | 73 MB | 20 villes × 3 snaps |
| `dbsumlistings_2506_cons20city.parquet` | 473K | 28 MB | Juin 2025 brut |
| `dbsumlistings_2506_clean20city.parquet` | 346K | 21 MB | Juin nettoyé |
| `recap_profiles_20cities_2506.csv` | 20 | - | Profils par ville |

### 10 villes (legacy)

| Fichier | Lignes | Taille | Contenu |
|---------|--------|--------|---------|
| `dbsumlistings_snaps_cons10city.parquet` | 875K | 48 MB | 10 villes × 3 snaps |
| `dblistingfull_snap_cons10city.parquet` | 875K | 567 MB | Full 79 cols |
| `dbsumlistings_2506.parquet` | 294K | 19 MB | Juin 2025 uniquement |
| `dblistingfull_2506_cons.parquet` | 294K | 193 MB | Juin full |

**20 villes consolidées** (15 pays) :

| Ville | Pays | Listings actifs (juin) |
|-------|------|----------------------|
| London | GBR | 62K |
| Paris | FRA | 53K |
| Rome | ITA | 32K |
| Istanbul | TUR | 25K |
| Lisbon | PRT | 21K |
| Madrid | ESP | 19K |
| Athens | GRC | 15K |
| Barcelona | ESP | 15K |
| Copenhagen | DNK | 14K |
| Budapest | HUN | 12K |
| Florence | ITA | 12K |
| Vienna | AUT | 10K |
| Prague | CZE | 9K |
| Berlin | DEU | 9K |
| Bordeaux | FRA | 8K |
| Venice | ITA | 7K |
| Amsterdam | NLD | 6K |
| Brussels | BEL | 6K |
| Dublin | IRL | 5K |
| Lyon | FRA | 5K |

**Taux de change EUR** : GBR ×1.17, HUN ×0.0026, TUR ×0.028, DNK ×0.134, CZE ×0.040

## Pipeline cleaning sumlistings

**Pipeline validé** (appliqué dans EDA et consolidation) :

| Étape | Action | Impact |
|-------|--------|--------|
| 1 | Prix non null | ~25% exclus (inactifs/retirés) |
| 2 | Disponibilité > 0 | ~5% supplémentaires |
| 3 | Exclure Hotel room | ~1% |
| 4 | Prix EUR 10-1000 | ~3% aberrants |
| 5 | **Flag** `is_longterm` | min_nights >= 30 (NON exclu) |

**Taux rétention global** : ~65-70% de la base brute

**Décision min_nights** : Flag et non exclusion. Effet régulation : Istanbul 55%, Barcelona 41%, Berlin 40%, Paris 20%.

**Prix null = inactif** : 80.8% des null-prix ont availability_365=0. Listings bookés gardent leur prix (seulement 1.2% en anomalie).

## Cleaning - Colonnes lourdes (listings.gz)

**À supprimer (~620 MB gain)** :
```python
DROP_COLS = [
    'amenities',           # 149 MB - JSON
    'description',         # 134 MB - 3% null
    'neighborhood_overview', # 86 MB - 53% null
    'host_about',          # 67 MB - 52% null
    'host_picture_url',    # 45 MB - URLs
    'host_thumbnail_url',  # 44 MB
    'picture_url',         # 43 MB
    'listing_url',         # 26 MB - reconstructible
    'host_url',            # 26 MB - reconstructible
]
```

**Colonnes essentielles** : id, host_id, latitude, longitude, neighbourhood, room_type, price, minimum_nights, number_of_reviews, reviews_per_month, availability_365, calculated_host_listings_count

**Colonnes ajoutées** : city, country_code, date_snapshot, price_eur, is_entire_home, is_multihost, is_longterm

## Méthodologie

**Référentiel** : `gdmeth-indic-airbnb-260109.md`
- 5 hypothèses structurantes (H1-H5)
- 15 questions évaluatives par axe
- Formules indicateurs niveau 1-5
- Cleaning recommandé

## Helpers Python (mutils/jpy)

**Chemin** : `C:\Users\vince\hh\pq\PDS\mutils\jpy\`

Modules partagés entre projets PDS. Import via `sys.path.insert` ou `importlib.util`.

| Module | Rôle |
|--------|------|
| `jcn-style.py` | Palettes Urban Institute, plotly_layout(), init_style() |
| `jcn-claude-log.py` | ClaudeLog pour export JSON/TXT des métriques |
| `jcn-eda.py` | EDA unifiée (quick_eda, full_eda) |
| `jcn-paths.py` | Détection contexte, output_dir, préfixes |
| `jcn-parquet.py` | Load/convert Parquet, schema |
| `jcn-download.py` | Téléchargement URL → fichier local |
| `jcn-csv-bom.py` | Conversion CSV UTF-8 BOM |

### Palettes Urban (jcn-style.py)

```python
# Import et init
import importlib.util
_spec = importlib.util.spec_from_file_location("jcn_style", MUTILS_JPY / "jcn-style.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_mod.init_style()  # applique palettes Plotly + Matplotlib

# Couleurs disponibles
COL_CYAN = "#1696d2"      # Bleu Urban principal
COL_ORANGE = "#ca5800"    # Orange
COL_GREEN = "#55b748"     # Vert
PAL_URBN_CAT = [...]      # 8 couleurs catégorielles
PAL_URBN_DIV = [...]      # 8 couleurs divergentes orange→bleu
PAL_DEFAULT = [COL_ORANGE, COL_GREEN, ...]  # Pas de bleu en premier
```

```python
# Usage dans Quarto / scripts
import sys
sys.path.insert(0, r"C:\Users\vince\hh\pq\PDS\mutils\jpy")
```

## Reports (reports/)

| Fichier | Contenu |
|---------|---------|
| `eda-20cities-260203.qmd` | EDA Quarto Python 20 villes, 5 axes, plotly+itables |
| `paris-analyse-260203.qmd` | Analyse Paris, arrondissements + IRIS |
| `map-europe-20cities-260203.py` | Carte Folium 20 villes Europe |
| `theme-urban.scss` | Theme SCSS Urban Institute |

**Stack EDA** : pandas, plotly, seaborn, itables, folium, geopandas

**Templates source** : `pucfpds-jrr-jquarto-jpy/tpl-templates-nbk/tpl-nbk-eda-dae-jPY-jquarto-fd.qmd`

### Convention titres narratifs (QMD)

**Format idée-force** : Titre insight seul sur sa ligne, puis ligne vide, puis développement.

```markdown
## Section titre

[**Idée-force percutante en une phrase sans point**]{.insight}

Développement du paragraphe explicatif qui détaille l'observation...
```

**Règles** :
- Titre en gras dans span `.insight` (bleu, 1.05em)
- Pas de point final dans le titre insight
- Ligne vide obligatoire entre insight et développement
- Accents français dans tout le texte narratif

## Benchmarks (zuprj/)

| Repo | Auteur | Focus |
|------|--------|-------|
| `CleanAirbnb/` | kytola | FR cities, Inside Airbnb, 5 critères drop |
| `Airbnb-neural-network-price-prediction/` | L-Lewis | London, XGBoost 73% R² |
| `Airbnb/` | jose-jaen | LA, Streamlit+VADER+BayesianNN |

## Notes

- **Paris sept 2025** : `price` vide dans sumlistings → utiliser .gz
- **URLs invalides** : Ireland, Malta, New Zealand (format atypique)
- **Kaggle** : `data/raw/devastatoreurope/` (10 villes Europe 2019/2020)
- **sumlistings vs gz** : Rester sur sumlistings pour EDA/APUR. Merge gz sur `id` quand besoin accommodates, review_scores

---
*2026-02-05*
