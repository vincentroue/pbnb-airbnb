# Analyses agents — Session 2026-05-12

Synthèse intermédiaire des analyses produites par les agents parallèles pour alimenter la rédaction du rapport synth-monde.

---

## Agent 1 — Typologie ACP

### Axes ACP

[**Dim1 (35,1 %) oppose les "marchés grand format" aux "marchés régulés" : 5 variables tirent dans le même sens (entiers + capacité + avis + superhôtes + densité), tandis que la contrainte de min-30 nuits structure le pôle inverse**]{.insight}

L'axe principal est un **gradient d'intensité touristique-marchande**. Contributions positives massivement structurantes : **str_entire_pct (23,2)**, **str_cap_pers_med (21,8)**, **actrv_avis_mois (19,3)**, **act_superhost_pct (15,7)** et **prs_listings_1000hab_dense (12,5)**. Pôle négatif : **str_minnuits30_pct (-5,8)** — signature des marchés régulés (Berlin, NY, Singapour, Hong Kong, Barcelone, Istanbul).

[**Dim2 (20,2 %) sépare les marchés à offre concentrée et longue durée (Méditerranée, Asie) des marchés à offre diffuse et dense en habitants (capitales européennes du Nord)**]{.insight}

Dim2 portée par **cr_offre_5plus (+27,4)**, **str_minnuits30_pct (+21,5)** et **act_superhost_pct (+16,3)** contre **prs_listings_1000hab_dense (-21,3)**. Axe **professionnalisation × régulation**.

**Dim3 (15,8 %)** = axe **continental/climatique** (Bangkok -3,37, Buenos Aires -2,76, Thessalonique -2,42).

Variance cumulée Dim1-3 = **71,1 %**, 3 axes Kaiser, KMO=0,555, msa_min=0,258.

### 4 clusters

| C | n | Nom | Parangons | Signature |
|---|---|---|---|---|
| **C1** | 10 (13,5 %) | Métropoles régulées sous tension | Istanbul, San Francisco, Boston, Barcelone, NY | min30=49,8% (+33,7 v-test +6,3), cr_offre 50% (+11,7), capacité 2,4 pers (-3,15), entiers 65% (-4,3) |
| **C2** | 19 (25,7 %) | Capitales nord-européennes denses | Stockholm, Naples, Genève, Bordeaux, Zurich | min30 bas (7,8%), cr_offre le plus bas (22,1%, v-test -5,18), HDI=0,942 (+3,06), temp 10,6°C (-3,09) |
| **C3** | 29 (39,2 %) | Cœurs touristiques méditerranéens et globaux | Anvers, Melbourne, Porto, Vienne, Bergame | entiers 82,2%, prix le plus bas (86 €, v-test -5,21), capacité 3,5 pers, HDI 0,895 (-3,35) |
| **C4** | 16 (21,6 %) | Marchés professionnalisés haut-revenu US | Seattle, Austin, San Diego, Denver, Washington DC | revenu 11 627 €/an (+6,61), superhost 51,4% (+5,59), capacité 3,94 pers (+3,7), avis/mois 1,67 (+4,98) |

### Atypiques & mal-classés

- **1 seul mal-classé** : Montréal (silhouette -0,05, cluster 1, voisin 3)
- **Top 5 mahalanobis** : Hong Kong (19,1), Singapour (18,3), Naples (18,4), Buenos Aires (16,5), New York (15,9)
- **BAB présent dans ACP** ⚠️ — alors que doctrine sub_city exclu (À CORRIGER)
- **USA dispersées sur 4 clusters** : C1 (NY, LA, SF, Boston, 6), C2 (Oakland), C3 (Dallas), C4 (10)

### Continent_detail dans clusters

- **Europe West & North** : C2 à **80%** (16/20) — le plus pur
- **Latin America, Oceania, Africa** : intégralement C3
- **Europe South & East** : 4 clusters touchés (C3=14, C4=3 italiennes, C1=2, C2=1 Naples)
- **North America** : la plus dispersée (C4=12, C1=6, C3=2, C2=2)
- **Asia (5)** : C1 (HK, SG) vs C3 (Tokyo, Bangkok, Taipei)

### 3 hypothèses à valider

1. **Régulation = clusterisateur principal** : str_minnuits30_pct discrimine plus que la pression touristique brute
2. **Cluster 4 nord-américain = vacation rental pro** (pas Airbnb urbain) : revenus 2× supérieurs + capacité 4 pers + superhôtes 51% → maisons entières familiales loin du modèle pair-à-pair
3. **Cluster 3 fourre-tout cohérent sur "marché touristique mature à prix modéré"** : sous-typer (k=2 sur C3 isolerait Méditerranée vs Asie-Pacifique vs Amérique latine ?)

---

## Agent 2 — Corrélations EDA macro

### Redondances fortes (|r| > 0.70)

| Paire | r Pearson | Mécanisme |
|---|---|---|
| act_reserv_taux × act_revenu_med | **0,873** | revenu = prix × nuits réservées (quasi-tautologique) |
| act_reserv_taux × actrv_avis_mois | **0,829** | avis/mois = proxy occupation Inside Airbnb |
| px_entire_med × px_private_med | **0,746** | même marché urbain |
| act_reserv_taux × act_superhost_pct | **0,719** | superhost = statut algorithmique selon réservation+avis |

### Corrélations inattendues à creuser

1. **cr_offre_top10host_pct × actrv_note_glb : r = -0,558** — les marchés concentrés notent moins bien. Mécanisme : multi-hôtes pros délivrent expérience standardisée mais moins chaleureuse. **Central pour bloc 2**.
2. **ctx_ucdb_hdi_latest × ctx_ucdb_temp_mean_latest : r = -0,543** — villes chaudes = IDH plus faible (clivage Nord-Sud Athènes/Istanbul/Buenos Aires vs Copenhague/Oslo). À neutraliser si IDH = contrôle.
3. **str_entire_pct × str_cap_pers_med : r = 0,535** — forte part logements entiers ↔ capacités supérieures (4-6 pers). Signal *familial/groupe* vs *backpacker*.

### Variables candidates à retirer en ACP (redondance)
- act_revenu_med, actrv_avis_mois, act_superhost_pct → garder act_reserv_taux comme synthétique

### Variables à transformer (skew > 2)
- **ctx_ucdb_gdp_avg_20** : skew 4,25, kurtosis 19,97 — log obligatoire
- **prs_listings_1000hab_dense** : skew 2,49 — log recommandé

### Variables quasi-constantes problématiques
- **actrv_note_glb** : cv=0,01 (entre 4,72 et 4,94) — inutile en ACP active, basculer en supplémentaire

### 5 hypothèses émergentes par bloc synth-monde

**H1 (Bloc 1 — Marché)** : Forte part logements entiers ↔ capacités supérieures (r=0,535). Marché famille/groupe (4-6 pers) vs backpacker. À tester : segmenter et croiser str_cap_pers_med × px_entire_med (médiane 120 €).

**H2 (Bloc 2 — Professionnalisation)** : Concentration ↓ note client (r=-0,558). Mécanisme : pros standardisent. À tester : régression note ~ concentration + superhost + str_entire_pct.

**H3 (Bloc 3 — Pression)** : Densité Airbnb extrêmement asymétrique (médiane 5,8‰ max 48,1‰ Venise/Florence/Lisbonne). Villes-musées hyperspécialisées. À tester : croiser ctx_static_unesco_50km (médiane 1, max 6).

**H4 (Bloc 4 — Concurrence)** : GAWC (médiane 8,5) vs UNESCO (médiane 1) ne se recouvrent pas. Deux mondes touristiques (Francfort vs Florence). À tester : ratio densité Airbnb/hôtels par typologie GAWC×UNESCO.

**H5 (Bloc 5 — Régulation)** : str_minnuits30_pct (médiane 10,4%, max 81,8%) discrimine. 3 outliers à 71,6% (probable NYC/Berlin/Barcelone). Mécanisme : contrainte min_nights → basculement longue durée. À tester : str_minnuits30_pct × act_reserv_taux.

### Bugs identifiés

- ❌ **JSON eda-ville incomplet** : pas de blocs eta2 ni Cramer V (notebook semble s'arrêter après BIVARIE corrélations). À ajouter `log_anova_eta2()` et `log_cramer()` dans rpt-pbnb-edanbk-macro.qmd
- ❌ act_revenu_med = 0 et act_reserv_taux = 0 : 1 ville à revenu nul (Buenos Aires anomalie jan 2026 ?)
- ❌ ctx_static_gawc_score : 8 NA (10,8%) — décider imputation vs retrait
- ❌ actrv_note_glb : cv=0,01 — variabilité trop faible

---

## Agent 3 — Pays/continent_detail explicatif

[**Le continent_detail explique 15-50% de la variance entre villes, mais le pays reste plus puissant sur les indicateurs d'activité et de pression**]{.insight}

### Profil par sous-région — clivages majeurs

| Sous-région (n) | px_entire | minnuits30 | cr_offre5+ | dens/1000hab | reserv_taux |
|---|---:|---:|---:|---:|---:|
| Europe West & North (20) | **132,9 €** | 4,2 % | 25,4 % | 5,9 ‰ | 9,2 % |
| Europe South & East (20) | 103,0 € | 4,9 % | 48,6 % | **11,4 ‰** | 14,0 % |
| North America (22) | **137,1 €** | **28,1 %** | 37,8 % | 4,9 ‰ | **19,5 %** |
| Asia (5) | 89,9 € | 18,3 % | **69,6 %** | 1,8 ‰ | 3,8 % |
| Latin America (3) | 58,3 € | 2,5 % | 39,0 % | 4,8 ‰ | 9,9 % |
| Oceania (3) | 119,4 € | 1,7 % | 40,7 % | 5,0 ‰ | 11,5 % |
| Africa (1) | 69,8 € | 1,2 % | 34,0 % | 3,2 ‰ | 5,5 % |

**NA = champion des longs séjours** (28,1% vs 4,2% Europe Ouest, **facteur 6,7×**) → contournement de régulation par extension durée. **Asia = champion concentration** (cr_offre 69,6% vs 25,4%) profile hubs pros. **LatAm = volumes massifs** (médiane 31K annonces : Rio 38K, BA 31K, Mexico 23K).

### eta² continent_detail (top 5 vs flop 3)

| Variable | eta² | Lecture |
|---|---:|---|
| **cr_offre_5plus** | **0,498** | Concentration = indicateur le plus régional |
| **act_superhost_pct** | **0,470** | Culture de qualification (NA 47% vs Eur W&N 28%) |
| **str_minnuits30_pct** | **0,425** | Empreinte régulations locales |
| actrv_note_glb | 0,370 | Biais culturel notation |
| act_cal_ouvert_med | 0,331 | Intensité usage commercial |
| --- | --- | --- |
| str_entire_pct | 0,145 (ns) | **Universelle** : ~80% partout |
| cr_offre_top10host_pct | 0,152 | Concentration extrême globale |
| vol_n_ann | 0,175 | Dépend ville (pop, attractivité) |

### Dispersion intra-pays (top et bottom)

| Pays | n | CV moyen | Lecture |
|---|---:|---:|---|
| **USA** | 16 | **0,367** | Forte hétérogénéité (NY/LA premium vs Columbus/Dallas résidentiel) |
| GBR | 4 | 0,342 | — |
| FRA | 4 | 0,332 | densité très dispersée (CV=0,73 — Paris vs régions) |
| CAN | 6 | 0,330 | — |
| ITA | 7 | 0,316 | — |
| ESP | 5 | 0,226 | Cohérence forte modèle méditerranéen |
| **AUS** | 3 | **0,154** | Brisbane/Melbourne/Sydney quasi identiques |

### Capitales vs non-capitales (Mann-Whitney)

**Seul indicateur significatif** : str_minnuits30_pct (capitales **4,3%** vs non-cap **12,2%**, p=0,041). Asymétrie : 80% Asie capitale, 100% Afrique, mais **9% NA** (Washington-DC, Ottawa).

### continent (4) vs continent_detail (7) vs country

| Variable | eta² cont | eta² cont_detail | **Gain** | eta² country |
|---|---:|---:|---:|---:|
| cr_offre_5plus | 0,213 | 0,498 | **+0,285** | 0,240 |
| px_entire_med | 0,026 | 0,254 | **+0,228** | 0,250 |
| vol_n_ann | 0,006 | 0,175 | +0,170 | 0,125 |
| str_minnuits30_pct | 0,289 | 0,425 | +0,136 | 0,376 |
| act_superhost_pct | 0,368 | 0,470 | +0,103 | 0,387 |
| **actrv_note_glb** | 0,289 | 0,370 | +0,081 | **0,582** |
| **dens/1000hab** | 0,168 | 0,203 | +0,035 | **0,466** |

### Villes hors région (top atypiques)

- **pays-basque** (Eur W&N) : densité **48‰** vs 6‰ régional — ultra-saisonnier littoral
- **edinburgh** : prix **233€** + reserv 30% — premium touristique extrême
- **venice** (Eur S&E) : densité **39‰** vs 11‰ — ville-musée saturée
- **istanbul** : minnuits30 **50%** — régulation forte façon NA
- **new-york** + **los-angeles** : prix 176-193€ + minnuits30 74-82% — hyper-régulés
- **singapore** : prix 177€ + cr 70% — hub financier
- **bangkok** : prix 40€ — low cost extrême

### Recommandation grille croisements

| Cas | Variable géographique optimale |
|---|---|
| **Prix, concentration, régulation, qualité** | **continent_detail** (eta² 0,25-0,50) |
| **Densité résidentielle** | country (0,47 vs 0,20) — politiques urbaines nationales |
| **Note moyenne** | country (0,58 vs 0,37) — biais culturel |
| **Focus multi-villes** | country (USA, ITA, CAN, ESP, FRA) — dispersion intra forte |
| **À éviter** | continent (4 niveaux) — masque fracture nord/sud Europe |
| **is_capital** | secondaire descriptive (différencie peu hors longs séjours) |

---

## Agent 4 — EDA micro

Échantillon stratifié 10K (sur 847K), 4 continents, 31 pays, 20,8% NA omis (review_scores_rating + reviews_per_month).

### Distributions niveau annonce

| Variable | Médiane | Moyenne | Skew | Outliers | Insight |
|---|---|---|---|---|---|
| price_eur | **102 €** | 149,94 | 4,15 | 7,4% (P99 cap 599€) | Médiane = seul indicateur robuste |
| minimum_nights | 2 | — | — | — | **14,2% is_longterm** (proxy régulation) |
| accommodates | 3 | — | — | — | 78,5% entire_home |
| review_scores_rating | 4,74 | 4,74 | -4,43 | 5,9% sous 4,0 | **cv=0,08** (vs 0,01 macro) — peu discriminante |
| availability_365 | 239 | 218,8 | -0,33 | — | Distribution quasi-uniforme |

### Aucune corrélation critique micro (|r|>0,70)

Top 5 :
1. minimum_nights × is_longterm : r=0,619 (mécanique)
2. reviews_per_month × estimated_occupancy : r=0,609, Spearman 0,715
3. number_of_reviews × estimated_occupancy : r=0,524, Spearman 0,672
4. **price_eur × accommodates : r=0,489** — **effet Simpson confirmé** : forte au macro, modérée au micro
5. estimated_occupancy × host_is_superhost : r=0,373 — **superhôtes louent ~37% plus**

### Insight Cramer V — Continent ≠ pays

- **room_type × continent V=0,022 (p=0,157 NON significatif)** ❗ — composition entiers/chambres étonnamment homogène à grande maille
- **room_type × country_code V=0,144 (p<10⁻⁵³)** — les écarts se jouent au niveau pays
- **country_code × host_response_time V=0,172** — variation culturelle/pro par pays

**Conséquence** : pour les croisements rapport synth-monde, le **niveau pays > continent** pour room_type/réactivité. Mais le **continent_detail** (sous-régions) capture davantage que continent à 4 niveaux.

### Bug majeur

❌ **estimated_revenue_l365d** : max **130 534 488 €/an** (130 M€), skew 41,81, kurtosis 2 763. Médiane 7 801 € mais moyenne 234 273 €. Impact KPI ville à vérifier (`kpi_global_by_city_2506.csv`).

### Questions creuser

1. **Top 1% calculated_host_listings_count** (max 1054) — quels pays ? lien régulation ?
2. **price_eur × is_multihost absent top 10** — prime pro annulée par composition produit ?
3. **is_longterm 14,2%** global — quels pays dépassent 30-40% ?
4. **Annonces "fantômes"** : haute dispo + zéro occupation + zéro avis — quelle fraction ?
5. **Bug revenue** — impact KPI agrégés ?

---

## Synthèse transversale (Agent 5)

Note transversale Quarto **prête à insérer** dans le rapport synth-monde : `rpt-bis/_note_transversale_synth_monde_260512.qmd`

**Structure** :
- **A. 5 insights majeurs** (régulation = clusterisateur, concentration ↓ notes, C4=vacation rental, continent_detail puissant, 14,2% longue durée)
- **B. 6 notes d'étonnement** (cluster Europe Ouest = absence de signal, room_type homogène continent, capitales sur minnuits30 only, Asie champion concentration, effet Simpson prix×capacité, HDI×temp -0,543)
- **C. 7 bugs à creuser** (revenue 130M€, Buenos Aires nuls, note_glb cv=0,01, gawc 8 NA, gdp/density skew, eta²/cramer non logués, redondances ACP)
- **D. Recommandation lecture** par bloc 1-5
- **E. 3 grandes questions ouvertes**

**Suggestion insertion** : après `## Méthodologie et données` et `## Glossaire des indicateurs clés`, avant `## 1. Le marché mondial`. Comme `{{< include _note_transversale_synth_monde_260512.qmd >}}` ou directement intégré.

**Correction par rapport à v1 agent** : le "bug BAB présent dans ACP" était un faux positif — `pays-basque` est bien scope=city (= agglomération comme une ville), les 3 sub_cities (Biarritz/Anglet/Bayonne) sont bien exclues du filtre `scope == 'city'`.
