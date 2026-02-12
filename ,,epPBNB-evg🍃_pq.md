---
ukp: "Projet capstone Airbnb multi-villes France/Europe = analyse comparative temporelle marchés locations court-terme Paris Lyon Bordeaux + cartographie dynamique dashboard Shiny"
dcr: 25-12-30
dup: 26-02-11
st: ttf
code: PBNB
tags:
  - pq/PBNB
  - pd
tl: "epPBNB-airbnb-log-jrr-jpy-evg🍃"
---

# ,,epPBNB - Airbnb Logements France/Europe - Evergreen 🍃

## &context

**Projet capstone data science** : Analyse comparative 35 marchés Airbnb européens (18 pays) avec données Inside Airbnb juin 2025, visualisations Plotly interactives, tableaux reactable, rapports Quarto HTML + RevealJS + PPTX.

**Stack technique mixte Python/R** :
- **Python** : ETL pipelines (pandas, parquet), EDA (plotly), consolidation 35 villes
- **R** : Tableaux reactable (jcn-table.R), ACP/clustering helpers
- **Quarto** : Rapport EDA HTML (2000+ lignes), présentations RevealJS + PPTX

**Périmètre géographique (fév 2026)** :
- **35 villes** × **18 pays** × **~600K listings** nettoyés (870K bruts)
- France (3), Italie (7), Espagne (6), UK (3), + 13 autres pays
- Population commune propre + estimations logements (city_reference_data.py)

**5 axes analytiques** :
1. **Volumes** : Structure bipolaire (Londres 97K + Paris 84K = 30 %)
2. **Pression** : Listings/1000 hab et entire homes/1000 logements
3. **Prix** : Fracture tarifaire facteur 4 (Amsterdam 223€ vs Budapest 57€)
4. **Professionnalisation** : % multi-host inversement corrélé aux prix (r = −0,47)
5. **Régulation** : 3 marqueurs convergents (ratio L/H, dispo, longterm)

## &ttd - TODO actifs

### Phase actuelle — Consolidation & qualité #tnext
- [ ] **Intégrer pop commune propre dans sp07/parquet** : Le parquet `dbsumlistings_2506_cons35city.parquet` utilise encore les populations METRO (city_pop) de CITY_META dans sp07. Remplacer par les valeurs commune propre de `city_reference_data.py`. Impact : les graphiques de pression du QMD (qui lisent city_pop) seront enfin cohérents avec les tableaux KPI sp08.
- [ ] **Mettre à jour FX_EUR dans sp07** : Ajouter NOR 0.085, SWE 0.087, CHE 1.06 (déjà fait dans QMD + sp08, pas encore dans sp07)
- [ ] **Manchester perimeter** : Greater Manchester dans IA couvre le metro (2.8M pop), pas la commune (550K). Documenter/flagger dans parquet.
- [ ] **Remonter theme-pres-v2.scss en central** : Ce SCSS est meilleur que `pucfpds/theme-revealjs.scss` (Google Fonts import, rem sizing, dark slides). Copier dans pucfpds comme nouveau standard.

### Prochaines étapes — Analyse
- [ ] **Analyse infra-ville Paris** : Arrondissements + IRIS avec listings.gz (74 cols)
- [ ] **Analyse temporelle** : Multi-snapshots 2024 → 2025 (3 snaps déjà consolidés)
- [ ] **Modélisation prix** : Features → prix prédit (listings.gz + amenities)

### Prochaines étapes — Livrables
- [ ] **Dashboard Shiny** interactif multi-villes (réactif, filtres ville/indicateur)
- [ ] **Carte Folium** interactive 35 villes (actuellement 20 dans map-europe-20cities)
- [ ] **Intégrer KPI recap tables dans QMD** : Déjà fait (reactable par ville + par pays en synthèse)

## &tdz - TODO différés
- [ ] Scoring régulation par ville (indice composite 3 marqueurs)
- [ ] Merge listings.gz pour review_scores, amenities, host_since
- [ ] Export dashboard public (Shiny ou Observable)
- [ ] Modèle ML prédiction prix (XGBoost, SHAP)

## &tdn - DONE log

### ✅ 2026-02-10 — Présentations v2 RevealJS + PPTX
- RevealJS v2 avec 5 graphiques Plotly interactifs (carte scatter_geo, bars, scatters)
- SCSS v2 : Google Fonts import, rem sizing (pas de cascade em), dark slide support
- PPTX 13 slides via python-pptx avec thème XML Urban (accent1-6 mappés, Segoe UI)
- Tableaux KPI recap (ville + pays) ajoutés en synthèse du QMD via reactable

### ✅ 2026-02-09 — KPI recap + données population/logement
- Script sp08-recap-kpi-35cities : 2 CSV (35 villes × 24 KPIs, 18 pays × 22 KPIs)
- city_reference_data.py : 35 villes pop commune propre + logements (18 confirmés, 17 estimés)
- Comparaison Eurostat Urban Audit (population OK mais greater city, logement inutilisable)
- Documentation sources et limites dans data/external/
- Fix FX_EUR : ajout NOR 0.085, SWE 0.087, CHE 1.06 (sp08 + QMD)

### ✅ 2026-02-07 — EDA 35 villes complet
- Rapport Quarto 2000+ lignes, 81 chunks, 20 figures séquentielles
- 5 axes : volumes, pression, prix, professionnalisation, activité
- Corrélations, ACP 2 composantes (~75% variance), clustering Ward k=4
- Lignes moyennes (COL_MAGENTA dashed) sur barplots clés
- Section méthodologie (~2 pages) avec pipeline et hypothèses H1-H5
- Consolidation 35 villes (sp07) : parquet 600K clean, 870K brut

### ✅ 2026-02-03 — EDA 20 villes + carte Folium
- Premier rapport EDA 20 villes Europe
- Carte Folium interactive (map-europe-20cities)
- Analyse Paris arrondissements (paris-analyse)

### ✅ 2025-12-31 — Pipeline ETL
- Scripts download (sp04), flatten (sp06), consolidation (sp07)
- Flat view sumlistings 18 cols × snapshots multiples

## &fichiers-clés

| Fichier | Rôle |
|---------|------|
| `reports/eda-bnb-35cities-260207.qmd` | Rapport EDA principal (2000+ lignes, 20 figures) |
| `reports/pres-airbnb-35cities-v2-260210.qmd` | Pres RevealJS v2 (14 slides, 5 Plotly interactifs) |
| `reports/pres-airbnb-35cities-v2-260210.pptx` | Pres PPTX (13 slides, thème Urban) |
| `reports/theme-urban.scss` | Thème HTML Urban Institute |
| `reports/theme-pres-v2.scss` | Thème RevealJS v2 (rem, fonts, dark) |
| `scripts/sp07-consolidate-35cities-260207.py` | Pipeline consolidation parquet |
| `scripts/sp08-recap-kpi-35cities-260209.py` | Export KPI 35 villes + 18 pays |
| `scripts/city_reference_data.py` | Pop/logements commune propre (référentiel) |
| `data/interim/kpi_35cities_by_city_2506.csv` | 35 villes × 24 KPIs |
| `data/interim/kpi_35cities_by_country_2506.csv` | 18 pays × 22 KPIs |
| `data/external/city-pop-housing-reference-260209.md` | Documentation sources pop/logements |

## &next

**Immédiat (qualité données)** :
- Intégrer pop commune propre dans sp07 → regenerer parquet
- Fix FX_EUR dans sp07 (NOR/SWE/CHE)
- Remonter theme-pres-v2.scss dans pucfpds

**Court terme (analyse)** :
- Paris infra-ville (arrondissements + IRIS)
- Analyse temporelle multi-snapshots
- Dashboard Shiny interactif
