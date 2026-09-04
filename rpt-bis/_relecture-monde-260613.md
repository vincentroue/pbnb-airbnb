# Relecture structurée — rpt-pbnb-synth-monde · 2026-06-13

> Source de vérité chiffres : `outputs/rapport-monde-v2_rslt_claude_log.json` (84 clés)
> Fichiers couverts : MAIN + 8 srpt (00 → 07). Aucun fichier source modifié.

---



RMQ transversal

veriieri les giraph c’est tjrs noramleent   1. Girafe : OUI, toujours render_girafe(p), jamais girafe(ggobj=p)
  brut. (Le brut = tooltip serif + polices Liolices Liberation non prunées.)
  C'est la règle, sans exception.

## P00 — Synthèse exécutive + Cadrage (_srpt-monde-00-intro.qmd)

### 1. Densité / équilibre
193 lignes. Trois blocs : accroche `.synth-accroche`, bandeau KPI 3 cartes, puis section Cadrage avec 2 H3 (Contexte + Méthodologie). Volume correct pour une intro, ni creux ni surchargé. Reference : P00 est le document le plus dense en prose concentrée — légèrement plus long que P1 (202 L) mais plus riche en substance.

### 2. Manques
- Le sous-titrage du MAIN (`subtitle:`) indique « 1 million d'annonces actives » mais `aa_n_total_raw = 809 545` (JSON confirmé). La couverture de 10 % de 8 M = ~810 K. Le "million" est une valeur arrondie à la hausse, probablement issue d'une version antérieure. **L'écart est de ~19 %.**
- La liste des 7 parties analytiques est sous forme de bullets avec descriptions, alors que la convention `ggdl-rgen-rl-quarto.md` exige des **questions évaluatives** (`- **Prix** — quels niveaux ? Quelle dispersion ?`), pas des phrases descriptives de 3 lignes.
- La variable `aa$v_eur_pct` est utilisée en prose (P00, P01 : « `r aa$v_eur_pct` % de l'offre ») et dans le KPI mais `aa_v_eur_pct = 55` dans le JSON ; la phrase du MAIN subtitle dit « Europe, Amériques, Asie-Pacifique » sans Afrique, alors que l'étude inclut Le Cap. Mineur mais à caler.

### 3. Bugs / incohérences
- **Bug majeur — subtitle hardcodé « 1 million »** : le MAIN (`rpt-pbnb-synth-monde.qmd`, ligne 4) porte `subtitle: "... 1 million d'annonces actives ..."`. La valeur exacte est `aa$n_total_km` = `810 K`. Correction : remplacer `1 million` par `` `r aa$n_total_km` `` ou par `810 000`.
- **Anti-pattern : `.cld-ctx` ligne 61-63 commenté avec `==&td==`** mais laissé dans le fichier avec balise open/close `<!-- ==&td== vv à reprendre ... ==&td== -->`. Pas de danger rendu mais pollution du source.
- **Variable technique nue dans `.encadre`** : `str_entire_pct`, `str_minnuits30_pct`, `prs_listings_1000hab_dense` apparaissent en texte courant dans l'encadré FOCUS (lignes 154-156). Selon les conventions, les codes techniques doivent être dans des `code backticks` ou remplacés par le label medium du ddict. Ici ils sont dans une liste en prose rédigée → léger anti-pattern.
- **Note Eurostat LCD 854M** apparaît à la fois dans P00 `.cld-ctx` (ligne 62, commenté) ET dans le KPI de P04 (`kpi_block value = "854 M"`). Double emploi potentiellement confus si le commenté est réactivé.

### 4. Actions de finalisation
1. **(CRITIQUE)** Corriger le subtitle du MAIN ligne 4 : remplacer `1 million` par `810 000` u la variable `r aa$n_total_km`. Fichier : `rpt-pbnb-synth-monde.qmd`.
2. **(MOYEN)** Reformuler les 7 bullets de la liste parties en questions évaluatives (`- **X** — question ?`). Fichier : `_srpt-monde-00-intro.qmd` lignes 140-147.
3. **(MINEUR)** Mettre `str_entire_pct`, `str_minnuits30_pct`, `prs_listings_1000hab_dense` dans des backticks dans l'encadré FOCUS. Lignes 154-156.
4. **(MINEUR)** Supprimer le bloc commenté `==&td==` lignes 61-63.

---

## P1 — Portrait mondial (_srpt-monde-01-portrait.qmd)

### 1. Densité / équilibre
202 lignes. Structure claire : intro 1 §, `.cld-ctx` Eurostat, carte monde/Europe pleine largeur, 2 § prose, tabset 3 onglets, float `rt_topbot` + 2 § prose. **Bien calibrée — partie de référence.** P1 sert de benchmark volumétrique pour évaluer les autres.

### 2. Manques

- Pas d'analyse de la **distribution intra-continentale** : la prose dit « L'Europe Sud-Est totalise X annonces » mais ne donne pas de ratios de concentration (% des top 3 villes dans le total EUR). `top3_share` est calculé en P2 (`srpt02-kpi-panel-list`) mais pas en P1. 
- La variable `str_ratio_ann_hote` est présente en P1 (tableau + topbot) comme **signal de professionnalisation** et réapparaît dans P5 (même var, même lecture). Cette duplication est intentionnelle mais sans renvoi explicite — la transition de fin de P1 (`Ce ratio préfigure la dimension de professionnalisation traitée en Partie 3`) est bien rédigée mais le tableau P5 la répète sans ajout de valeur analytique.

### 3. Bugs / incohérences

- **Log manquant sur la carte** : `girafe(ggobj = p_combined, ...)` en ligne 52 est utilisé à la place de `render_girafe()`. Selon les conventions (`ggdl-rgen-rl-quarto.md`) : « **TOUJOURS `render_girafe(p, …)`, JAMAIS `girafe(ggobj=p, …)` brut.** » Le `girafe()` brut ne pose pas de CSS tooltip correct (police serif/Times). **Bug visuel potentiel.**
- `log_map_auto` appelé **APRÈS** le widget (ligne 56, après `ggiraph::girafe(...)`). Selon la règle absolue : « **`log_*()` AVANT le widget, JAMAIS après.** ». Ici `log_map_auto` est en dernière ligne du chunk → le widget est bien retourné mais c'est contre la convention. En pratique knitr imprime le widget (pas le return de log_map_auto invisible) mais c'est un anti-pattern à corriger.
- `nrow(kpi_am)` et `nrow(kpi_ap)` utilisés inline dans la prose P00 (et P01) mais **non loggés dans le JSON**. Ces valeurs sont calculées dynamiquement au render — fragilité si le périmètre change.

### 4. Actions de finalisation
1. **(MOYEN)** Remplacer `girafe(ggobj = p_combined, ...)` par `render_girafe(p_combined, ...)` et mettre `log_map_auto` AVANT le widget. Fichier : `_srpt-monde-01-portrait.qmd` lignes 52-56.
2. **(MINEUR)** Ajouter `aa$n_villes_am` et `aa$n_villes_ap` dans `_data-load.R` pour remplacer les `nrow(kpi_am)` inline non loggés.
3. **(MINEUR)** Ajouter une phrase ou note sur la concentration intra-Europe (% de l'offre EUR dans les 5 premières villes).

---

## P2 — Marché, structure et activité (_srpt-monde-02-prix-structure.qmd)

### 1. Densité / équilibre
220 lignes. La partie la plus dense : 1 float KPI, 1 tabset 9 vars (riche), 3 sous-sections H3 avec chacune 1 float `rt_topbot` + 2 §. **C'est la partie la plus complète du rapport.** P5 représente ~70 % du volume de P2 (environ 154 vs 220 lignes utiles).

### 2. Manques
- `px_1br_med`, `px_2br_med`, `px_3brplus_med` (ddict status = `ok`) sont absents du rapport — des indicateurs de segmentation tarifaire par taille de logement utilisables en P2 pour affiner l'analyse prix/capacité.
- `act_superhost_pct` (ddict `ok`) et `str_instantbook_pct` (ddict `ok`) absents — pourraient enrichir §2.3 Activité sans alourdir (simples mentions ou ligne tableau).
- La conclusion de P2 (dernière phrase : « Le prix d'une nuit ne dit rien du revenu réel... ») est journalistique mais l'absence de **transition vers P3** explicite (elle annonce P4 !) — le lien P2 → P3 (professionnalisation) n'est pas assuré.

### 3. Bugs / incohérences
- **Variable inline non AA** : ligne 6 `r aa$t_top_rev` et `r aa$v_top_rev_km` sont utilisés dans l'accroche d'ouverture de P2, et ces vars sont dans le JSON (`aa_t_top_rev`, `aa_v_top_rev_km`). OK.
- **`str_minnuits30_pct` absent du tabset P2** (`srpt02_panel` et `rt p2_villes_detail`) alors qu'il est listé dans les vars du tableau (ligne 90, 109). En fait il EST dans le tableau détaillé ville (ligne 109). Mais absent du `plot_cd_bars_ordered` P2 (6 vars sans `str_minnuits30_pct`). Signal potentiel de régulation présent dans P6 uniquement → cohérent mais piste analytique perdue pour P2.
- **Sous-section H3 formatées en `### 2.1`** : les numéros `2.1` / `2.2` / `2.3` sont des titres scolaires. Les conventions exigent le format `### Concept : question ?`. À renommer.
- La variable `top3_share` (% top 3 villes sur total) est calculée inline dans `srpt02-kpi-panel-list` mais **non loggée dans le JSON** et **non affichée dans le texte narratif** — seule la valeur brute `sprintf("%d %%", top3_share)` apparaît dans un KPI card. C'est une stat exploitable en prose.

### 4. Actions de finalisation
1. **(MOYEN)** Renommer les H3 `### 2.1 Prix :` → `### Prix : la géographie tarifaire contredit celle des volumes ?` (convention `Concept : question ?`). Idem 2.2 et 2.3. Fichier : `_srpt-monde-02-prix-structure.qmd` lignes 124, 155, 186.
2. **(MOYEN)** Ajouter une transition explicite vers P3 en fin de P2 (actuellement la phrase annonce P4, pas P3). Ajouter une phrase avant la conclusion : « La disparité de revenus entre hôtes soulève une question distincte — qui gère ces logements et dans quelle proportion ? — objet de la Partie 3. »
3. **(MINEUR)** Loguer `top3_share` dans le JSON (ajouter `log_result("top3_share_pct", top3_share, ...)` dans le chunk ou `_data-load.R`).

---

## P3 — Professionnalisation (_srpt-monde-03-pro.qmd)

### 1. Densité / équilibre
153 lignes. Calibrée : `.cld-ctx` Adamiak riche, tabset 5 vars, float `rt_topbot` + prose analytique. **P3 est la plus analytiquement dense par ligne** (le scatter r=0,87 / quadrants / outliers = 5 § de haute intensité). Volume dans la moyenne basse (P3 ≈ 70 % de P2).

### 2. Manques
- Le scatter multi-hôtes × super-professionnels mentionné en prose (r=0,87, quadrants 27/29/18) **n'a pas de figure associée dans le rapport**. L'analyse de quadrants est décrite textuellement mais sans visualisation. C'est une lacune importante pour un rapport analytique : le lecteur ne peut pas vérifier les outliers (Hong Kong, Naples, Bergame) par lui-même.
- `cr_gini` (ddict status = `ok`) est absent du rapport. Le bloc `.cld-ctx` cite Törnberg Gini 0,68 (externe) et Quattrone 0,79 (externe), mais le **Gini calculé sur le panel** n'est jamais présenté. Si la donnée est disponible dans `kpi_global_by_city_2506.csv`, c'est un angle manquant.
- La grille Adamiak `crt_ada_single_home_pct` / `crt_ada_multi_home_pct` (ddict status = `planned`) est mentionnée en `.cld-ctx` externe mais n'est pas comparée au panel — la passerelle Adamiak → panel reste un commentaire non quantifié.

### 3. Bugs / incohérences
- **Chiffres quadrants hardcodés non loggés** : `27 villes`, `29 villes`, `18 villes` (prose ligne 146) sont des valeurs figées. Si le périmètre évolue (ajout/suppression de villes), ces nombres seront faux. Aucun `log_scatter_auto` ou `log_result` correspondant dans le JSON → non vérifiable. La somme est arithmétiquement juste (27+29+18=74) mais les valeurs elles-mêmes ne sont pas auditables.
- **Stats scatter hardcodées non loggées** : `r = 0,87`, `R² = 0,748`, `p < 10⁻²²` (prose ligne 144) sont absents du JSON. Règle convention : tout chiffre de figure doit venir du JSON via `log_scatter_auto`. Ces stats risquent d'être fausses si les données changent.
- **`cr_offre_1plus` utilisé en P3 ET en P6** (tabsets des deux parties). C'est une redondance documentée mais sans renvoi. Le lecteur qui scanne les tableaux trouvera la même colonne dans deux parties différentes sans explication.
- **Titre tabset H3 absent** : la convention impose un H3 entre le bandeau KPI et le tabset (avec la phrase périmètre). En P3 la phrase périmètre est là (ligne 33-34) mais sans H3 chapeau — les autres parties ont H3 implicite dans le float ou la prose.

### 4. Actions de finalisation
1. **(FORT)** Ajouter `log_scatter_auto("srpt03_scatter_multi_supro", ...)` dans un chunk dédié après le calcul de la corrélation multi × superpro, et ajouter une figure scatter (au moins un chunk `plot_scatter()` ggiraph). Fichier : `_srpt-monde-03-pro.qmd`.
2. **(FORT)** Remplacer les quadrant counts hardcodés par des variables aa calculées (`aa$n_q_corporate`, `aa$n_q_particulier`, `aa$n_q_hybride`) dans `_data-load.R`.
3. **(MOYEN)** Ajouter `cr_gini` (panel) dans le float topbot ou en mention dans la prose pour ancrer la comparaison Törnberg externe.
4. **(MINEUR)** Ajouter un renvoi « voir P6 pour l'analyse régulatoire » après la mention de `cr_offre_1plus` pour expliciter la redondance.

---

## P4 — Pression territoriale (_srpt-monde-04-pression.qmd)

### 1. Densité / équilibre
152 lignes. Structure parallèle aux autres parties : `.cld-ctx` dense (3 cas + note métho + effet loyers), tabset 3 vars, float `rt_topbot` + 3 § analytiques. **Volume légèrement en-dessous de P3 (152 vs 153 lignes)** — acceptable.

### 2. Manques
- `prs_density_l_km2_dense` et `prs_pct_listings_dense` sont dans le tabset mais **non commentés dans la prose analytique** — seule `prs_listings_1000hab_dense` est discutée. Ces deux indicateurs complémentaires (densité spatiale en annonces/km² et % de l'offre en zone dense) pourraient apporter 1-2 phrases.
- La mise en perspective **Lisbonne 38 ‰ vs panel** : le chiffre de Lisbonne cité dans le `.cld-ctx` (ligne 37 : « ~38 ‰ ») est une estimation externe. La valeur issue du panel JSON n'est pas croisée. Or la valeur exacte est dans le parquet (calculée par sp10).
- Angle absent : la **corrélation pression × multi-hôtes** (est-ce que les villes à forte pression sont celles à forte professionnalisation ?) serait pertinente après P3, et permettrait de ponter vers P6.

### 3. Bugs / incohérences
- **`aa$n_prs_above15` absent du JSON** (confirmé) : utilisé avec l'opérateur fallback `%||%` dans le KPI card ET dans la prose (ligne 149 : « `r aa$n_prs_above15 %||% ...` villes du panel »). La valeur s'affiche mais n'est pas loggée dans le JSON → non auditable. Ajouter dans `_data-load.R`.
- **Chiffre externe douteux** : le `.cld-ctx` cite « Bordeaux biais ×3,2 selon commune ou métropole fonctionnelle ; Lisbonne ×5,3 ; Porto ×7,5 ; Bergame ×9,2 ». Ces ratios ne sont pas sourcés explicitement dans le bloc (aucune référence pour ces biais multiplicateurs). La phrase est sans source.
- **`aa$v_facteur_pression` = 96** (JSON) utilisé dans la prose de P4 intro (ligne 8 : « un facteur `r aa$v_facteur_pression` »). Le ratio 48,1/0,5 = 96,2 — vérification : facteur 96 est mathématiquement correct mais doit être présenté comme ratio, pas comme « facteur » (phrasing à clarifier).
- La prose `facteur 5 à 8` en ligne 147 est calculée sur 30 ‰ / 5,8 ‰ ≈ 5,2 et 48,1 / 5,8 ≈ 8,3 — le « 5 à 8 » est cohérent avec le JSON mais **hardcodé** (non issu d'une variable `aa$`).

### 4. Actions de finalisation
1. **(FORT)** Ajouter `aa$n_prs_above15 <- sum(kpi$prs_listings_1000hab_dense > 15, na.rm = TRUE)` dans `_data-load.R` et loguer avec `log_result()`. Fichier : `_data-load.R` + `_srpt-monde-04-pression.qmd`.
2. **(MOYEN)** Ajouter une source explicite aux ratios biais multiplicateurs (Bordeaux ×3,2 etc.) dans le `.cld-ctx` ou les supprimer s'ils sont sans référence.
3. **(MINEUR)** Remplacer le `facteur 5 à 8` hardcodé par des variables `aa$v_facteur_prs_low` / `aa$v_facteur_prs_high`.

---

## P5 — Concurrence face à l'hôtellerie (_srpt-monde-05-concurrence.qmd)

### 1. Densité / équilibre
154 lignes. **P5 est la partie la plus mince analytiquement.** Elle mobilise seulement 3 variables panel (`str_cap_pers_med`, `str_ratio_ann_hote`, `px_entire_med`), dont deux déjà vues : `str_ratio_ann_hote` (P1) et `px_entire_med` (P2). La valeur ajoutée différentielle de P5 se limite au cadrage hôtellerie (`.cld-ctx`) et à la capacité d'accueil. **P5 ≈ 40 % du contenu analytique de P2** en termes de nouveauté.

### 2. Manques
- **Absence de données panel hôtelières** : P5 compare Airbnb et hôtellerie entièrement via des données externes (`.cld-ctx`). Il n'y a **aucun KPI panel propre à P5** qui ne soit pas déjà dans P1 ou P2. La partie ressemble à un dossier documentaire (`.cld-ctx` riche, 40 lignes) avec un tabset de remplissage.
- `ctx_tour_nights_total_24` et `ctx_tour_pct_foreign_24` (ddict `ok`, données contexte) sont absents alors qu'ils permettraient de calibrer la part Airbnb dans le tourisme local pour les villes du panel.
- La mention d'acteurs hybrides (Blueground, Sonder, Mint House) dans le `.cld-ctx` est pertinente mais sans chiffre panel : « Blueground = 781 annonces Paris » est une donnée APUR externe sur Paris uniquement, non représentative du panel mondial.
- Pas de **transition analytique** en fin de P5 : la phrase de clôture renvoie vers P6 mais de façon mécanique (« Comment les régulateurs ont-ils réagi ? »). La conclusion ne synthétise pas ce que P5 a apporté de nouveau par rapport à P1/P2.

### 3. Bugs / incohérences
- **Variables P5 calculées dans le chunk `srpt05-calc` (lignes 12-15)** mais **non loggées dans le JSON** : `aa$v_ratio_ann_hote_med`, `aa$t_top_ratio`, `aa$v_top_ratio`, `aa$v_cap_med`. Ces 4 variables sont utilisées dans la prose et dans les KPI cards mais **absentes du JSON** (confirmé). Si les données changent, les valeurs seraient silencieusement wronges sans invalidation de cache. **Risque médium.**
- **`str_ratio_ann_hote` en P5 = doublon P1** : le ratio annonces/hôte est dans le tableau détaillé ville de P5 et dans la prose (« médiane mondiale »), mais c'était déjà l'objet du P1 `srpt01_d`. Les topbot P1 et P5 sur cette variable présentent donc la même information.
- **Prix médian P5 ligne 6** : `r round(median(kpi$px_entire_med, na.rm = TRUE), 0)` est un calcul inline non loggé. La valeur est dans `aa_v_prix_med = 120` — utiliser `r aa$v_prix_med` à la place.
- **Titre KPI `"9 vs 1"`** : le `vs` dans un KPI card est toléré selon la convention. OK.

### 4. Actions de finalisation
1. **(FORT)** Déplacer les 4 variables `aa$v_ratio_ann_hote_med` etc. de `srpt05-calc` vers `_data-load.R` et les loguer. Fichier : `_data-load.R` + `_srpt-monde-05-concurrence.qmd`.
2. **(FORT)** Enrichir P5 avec 1-2 indicateurs vraiment différents de P1/P2 : `ctx_tour_nights_total_24` (nuitées touristiques totales par ville = dénominateur pour part Airbnb) ou `str_instantbook_pct` (signal d'offre professionnelle). Remplacement ou complétion du tabset actuel.
3. **(MOYEN)** Remplacer `r round(median(kpi$px_entire_med, ...))` inline par `r aa$v_prix_med`.
4. **(MOYEN)** Réécrire la conclusion de P5 pour synthétiser l'apport propre de la partie (argument sur la convergence LCD/hôtellerie) et différencier du renvoi vers P6.

---

## P6 — Régulation et trajectoires (_srpt-monde-06-regulation.qmd)

### 1. Densité / équilibre
149 lignes. Légèrement inférieure à P4/P5. Structure conforme : `.cld-ctx` 3 cas + UE + France, tabset 4 vars, float `rt_topbot` + prose analytique. **Volume approprié pour la partie la plus politique.**

### 2. Manques
- `str_minnuits90_pct` est dans le tabset P6 — c'est l'indicateur le plus direct du plafond New York (90 nuits) et de la loi Le Meur (90 nuits) — mais **non commenté dans la prose analytique**. Seul `str_minnuits30_pct` est discuté.
- La **liste des villes > 30 % long séjour** (13 villes selon `aa_n_longterm_30plus = 13`, JSON confirmé) n'est pas nommée explicitement dans la prose — pourtant ce serait un classement directement utilisable (« parmi les 13 villes dépassant 30 % ... »).
- L'angle **régulation de plateforme (Règlement UE + portail PANDA)** est bien documenté dans le `.cld-ctx` mais sans croisement panel : combien de villes du panel sont dans l'UE (concernées par le règlement 2024/1028) ? `aa_n_villes_eur = 40` villes européennes — portion villes UE non précisée.

### 3. Bugs / incohérences
- **`cr_offre_1plus` présent en P3 ET P6** : la colonne multi-hôtes (≥2 annonces) apparaît dans le tableau continent de P6 (ligne 56) — doublon documenté. La logique est que P6 le contextualise dans la régulation, mais le lecteur ne le voit pas directement. Ajouter une note ou un renvoi.
- **`prs_listings_1000hab_dense` dans P4 ET P6** (tabset ville P6 ligne 93) : même situation, doublon dans le tableau détaillé ville de P6.
- **`aa$v_eur_med_longterm` = 4,7 %** (JSON) cité correctement dans la prose P6 finale (ligne 146). OK.
- **Transition finale** : la dernière phrase de P6 (ligne 146) termine par « La synthèse continentale qui clôt le rapport... » — cette expression mélange un renvoi vers P7 (correct) avec l'expression « qui clôt le rapport » qui sous-entend que P7 = fin (ce qui est vrai mais donne une impression abrupte). Reformuler en « La typologie qui suit (Partie 7) synthétise ces six dimensions... »

### 4. Actions de finalisation
1. **(MOYEN)** Ajouter dans la prose P6 un commentaire sur `str_minnuits90_pct` — notamment sa corrélation avec la Local Law 18 NY et la loi Le Meur FR.
2. **(MOYEN)** Nommer les 13 villes à `str_minnuits30_pct > 30 %` (ou au moins les 5 premières) dans la prose analytique.
3. **(MINEUR)** Reformuler la transition finale P6 → P7 (« qui clôt le rapport » → « qui suit (Partie 7) »).
4. **(MINEUR)** Ajouter renvois explicites « (déjà détaillé en P3) » sur `cr_offre_1plus` et « (cf. P4) » sur `prs_listings_1000hab_dense` dans les notes des tableaux P6.

---

## P7 — Typologie ACP-HCPC (_srpt-monde-07-typologie.qmd)

### 1. Densité / équilibre
141 lignes. **La partie la plus courte du rapport.** Elle contient : 1 § d'intro résumant les 5 clusters (dense), 1 encadré `.encadre-insight` avec les 5 familles, 2 § analytiques sur les dimensions Dim1/Dim2, 1 tableau gt 5 lignes, 1 carte monde clusters (`.column-page`), 1 bloc `.cld-add` (lecture géographique à valider), 1 `.cld-ctx` qualité ACP. **P7 ≈ 64 % du volume de P2** (141 vs 220 lignes). C'est la partie la plus courte alors qu'elle est analytiquement la plus structurante.

### 2. Manques
- **Pas de `rt_topbot` en P7** : toutes les parties P1-P6 ont un `rt_topbot_ville` qui ancre le lecteur sur les cas extrêmes par cluster. P7 a un tableau gt 5 lignes (résumé clusters) et une carte, mais pas de tableau interactif ville-par-ville avec leur cluster et indicateurs clés. C'est la partie où ce tableau serait le plus utile (74 villes avec leur cluster assigné + marqueurs factoriels).
- **Pas de visualisation du plan factoriel Dim1×Dim2** : le rapport mentionne les deux dimensions et leurs parts de variance (64,4 % total), mais sans biplot ni cercle de corrélations. Le lecteur ne peut pas voir quels indicateurs structurent les axes. Le notebook ACP (`rpt-pbnb-acpnbk-monde.qmd`) contient ces visualisations mais P7 n'en reproduit aucune même partielle.
- **Biarritz-Anglet-Bayonne dans C3 (Nordique amateur)** : c'est une anomalie que le rapport n'explique pas. BAB (France, Atlantique) est dans un cluster avec Oslo, Copenhague, Amsterdam — ce qui surprend le lecteur sans explication. Une note ou une phrase serait nécessaire.
- Les **v.test** des marqueurs (ex. « Concentration hôtes -5,8 σ ») sont cités mais non mis en perspective : qu'est-ce qu'un v.test de -5,8 signifie concrètement ? Une note lecture courte serait utile.

### 3. Bugs / incohérences
- **Le bloc `.cld-add`** (lignes 115-131) est toujours présent, indiquant que la prose n'a pas encore été validée par l'utilisateur. C'est normal en cours de rédaction mais à noter.
- **Libellé cluster dans la table gt vs carte** : table gt dit « C3 — Nordique amateur » (ligne 30) mais la légende carte dit `"3" = "C3 · Single-home nordique"` (ligne 87). Incohérence de nommage entre les deux représentations de P7 — à unifier vers un label stable.
- **Src JSON ACP séparé** : la carte P7 lit depuis `data/interim/rsl/kpi_acp_city_2506-acp-B_rslt_claude_log.json` (JSON externe à `rapport-monde-v2`). Si ce fichier est absent ou mis à jour, la carte plantera silencieusement. Pas de vérification de l'existence du fichier dans le code.
- **Tailles clusters dans gt** : N=3+19+4+29+19=74 ✓ — arithmétiquement correct. Mais la table gt use `~N` comme integer tribble (` 3L, 19L, 4L, 29L, 19L`) — si le clustering évolue, ce tableau n'est pas dynamique (hardcodé). Vulnérabilité à une ré-exécution de l'ACP.

### 4. Actions de finalisation
1. **(FORT)** Ajouter un `rt_table` ville × cluster dans un onglet supplémentaire du gt ou en section finale de P7 (74 lignes avec cluster, v.test principaux, indicateurs clés). Cela ancrerait la lecture pour un non-statisticien.
2. **(FORT)** Expliquer le positionnement de BAB dans C3 (1-2 phrases : pression réglementaire de la zone balnéaire ? offre dominée par particuliers ? concurrence saisonnière ≠ profil métropole ?).
3. **(MOYEN)** Unifier le libellé C3 : choisir entre « Nordique amateur » (gt) et « Single-home nordique » (carte) et appliquer partout.
4. **(MOYEN)** Rendre dynamique le tableau gt (lire cluster sizes depuis le JSON ACP externe plutôt qu'en dur dans tribble).

---

## CROSS-PARTIES — Analyse transversale

### Équilibre global des 7 parties

| Partie | Lignes | Niveau analytique | Verdict |
|--------|--------|-------------------|---------|
| P00 Intro | 193 | Élevé (cadrage complet) | Référence |
| P1 Portrait | 202 | Moyen-élevé | Équilibré |
| P2 Prix/Structure | 220 | Très élevé | **Plus dense** |
| P3 Pro | 153 | Élevé (sans figure scatter) | OK mais manque 1 figure |
| P4 Pression | 152 | Élevé | OK |
| P5 Concurrence | 154 | **Faible** (doublon P1/P2) | **À étoffer** |
| P6 Régulation | 149 | Moyen | OK |
| P7 Typo | 141 | Élevé mais incomplet | **À étoffer** |

**P5 est la plus déséquilibrée** : volume similaire aux autres mais contenu analytique pauvre en données panel nouvelles (doublon P1/P2). P7 est trop courte pour la partie la plus synthétique.

### Redondances inter-parties

1. **`str_ratio_ann_hote`** : P1 (tableau + topbot + prose) + P5 (tableau + topbot + prose). Supprimer de P5 ou remplacer par un indicateur non vu.
2. **`cr_offre_1plus`** : P3 (tabset + topbot) + P6 (tabset continent). Ajouter renvoi `(cf. P3)` dans P6.
3. **`prs_listings_1000hab_dense`** : P4 (tabset + topbot + prose extensive) + P6 (tableau ville). Ajouter renvoi `(cf. P4)` dans P6.
4. **`px_entire_med`** : P2 (tabset + topbot + prose) + P5 (tabset + topbot). Doublon complet en P5.
5. **Exemples Lisbonne/Barcelone/Amsterdam** : cités dans P4 `.cld-ctx` ET P6 `.cld-ctx`. Couverture normale (angles différents) mais risque de lassitude lecteur.
6. **Chiffre 59 % Adamiak** : cité dans P00 synthèse ET dans P03 intro. Doublon acceptable (cohérence narrative) mais la phrasing est quasi identique. À varier.

### Cohérence des chiffres clés — contrôle croisé prose ↔ JSON

| Chiffre clé | Où dans la prose | Valeur JSON | Statut |
|-------------|-----------------|-------------|--------|
| 74 villes | P00, P01, P02, P04, P07 | `aa_n_villes = 74` | ✅ Cohérent |
| 31 pays | P00, P01 | `aa_n_pays = 31` | ✅ Cohérent |
| 4 continents | P00 | `aa_n_continents = 4` | ✅ Cohérent |
| **~810 K annonces** | P01, P02, P04 `aa$n_total_km = 810K` | 809 545 | ✅ Cohérent |
| **"1 million"** | MAIN subtitle (hardcodé) | 809 545 | ⛔ **FAUX** — écart 19 % |
| 40 villes EUR | P00, P01 | `aa_n_villes_eur = 40` | ✅ Cohérent |
| 55 % offre EUR | P00 KPI | `aa_v_eur_pct = 55` | ✅ Cohérent |
| 62 % multi-loueurs | P00, P03 | `aa_v_multi = 62` | ✅ Cohérent |
| 15 % hôtes → 50 % offre | P00 KPI hardcodé | `aa_v_hosts50 = 15` | ✅ Cohérent |
| 28 % super-pro ≥10 | P03 KPI `aa$v_offre10_med` | `aa_v_offre10_med = 28` | ✅ Cohérent |
| 5,8 ‰ pression med | P04 | `aa_v_pression_med = 5.8` | ✅ Cohérent |
| 48,1 ‰ top pression | P04 | `aa_t_top_pression = Biarr.-Anglet-Bayon., v = 48,1` | ✅ Cohérent |
| **82 % NY long séjour** | P06 `aa$v_top_lt` | `aa_v_top_lt = 82` | ✅ Cohérent |
| 13 villes > 30 % | P06 KPI `aa$n_longterm_30plus` | `aa_n_longterm_30plus = 13` | ✅ Cohérent |
| r=0,87 P3 scatter | P03 prose hardcodé | **NON LOGGÉ** | ⚠️ Non auditable |
| 27/29/18 quadrants | P03 prose hardcodé | **NON LOGGÉ** | ⚠️ Non auditable |
| Variables P5 calc | P05 KPI+prose | **NON LOGGÉ (chunk local)** | ⚠️ Risque si data change |
| n_prs_above15 | P04 fallback inline | **NON LOGGÉ** | ⚠️ Risque |

### Fil narratif et transitions

- **P00 → P1** : transition implicite (structure MAIN). OK.
- **P1 → P2** : transition de P1 « Ce ratio préfigure la professionnalisation (P3) » — cohérent mais ne prépare pas P2 (prix). Ajouter une phrase sur les prix avant la fin de P1.
- **P2 → P3** : fin de P2 annonce P4 (« croisera pression résidentielle »), pas P3. **Transition manquante vers P3.**
- **P3 → P4** : transition bien rédigée (« Cette concentration pèse-t-elle sur le tissu résidentiel ? »). ✅
- **P4 → P5** : transition présente (« face à l'hôtellerie traditionnelle »). ✅
- **P5 → P6** : transition présente (« Comment les régulateurs ont-ils réagi ? »). ✅
- **P6 → P7** : transition présente mais phrasing à revoir (« qui clôt le rapport »). ⚠️
- **P7 → fin** : pas de conclusion générale après P7. Le rapport se termine sur le `.cld-ctx` qualité ACP — aucune phrase de synthèse finale. À ajouter.

### Anti-patterns convention identifiés (prose rédigée)

| Anti-pattern | Localisation | Sévérité |
|---|---|---|
| `→` dans P00 cadrage (liste 7 parties) | `_srpt-monde-00-intro.qmd` ligne 140 | Mineur |
| Variable technique nue `str_entire_pct` dans `.encadre` | `_srpt-monde-00-intro.qmd` ligne 154 | Mineur |
| H3 numérotés `### 2.1` / `### 2.2` / `### 2.3` | `_srpt-monde-02-prix-structure.qmd` lignes 124, 155, 186 | Moyen |
| Calcul inline non-aa `round(median(kpi$px_entire_med, ...))` en prose | `_srpt-monde-05-concurrence.qmd` ligne 6 | Moyen |
| `vs` dans titre KPI card P5 (`"9 vs 1"`) | `_srpt-monde-05-concurrence.qmd` ligne 36 | Toléré (KPI compact) |
| Label cluster C3 différent table gt vs carte | `_srpt-monde-07-typologie.qmd` lignes 30 et 87 | Bug cohérence |
| Tribble gt P7 hardcodé (N par cluster) | `_srpt-monde-07-typologie.qmd` ligne 28-35 | Vulnérabilité data |

---

## Résumé des priorités

### Critique (à corriger avant publication)
1. **Subtitle MAIN « 1 million »** → corriger en `810 000` ou `r aa$n_total_km`. (`rpt-pbnb-synth-monde.qmd` ligne 4)
2. **P3 scatter non loggé** : r=0,87 + quadrants 27/29/18 hardcodés → ajouter `log_scatter_auto` + variables aa. (`_srpt-monde-03-pro.qmd`)
3. **P5 variables non loggées** : `v_ratio_ann_hote_med` / `t_top_ratio` / `v_top_ratio` / `v_cap_med` calculées en chunk local → déplacer dans `_data-load.R` et loguer. (`_srpt-monde-05-concurrence.qmd`)

### Fort (à corriger pour qualité finale)
4. **P4 `n_prs_above15` non loggé** → ajouter dans `_data-load.R`. (`_srpt-monde-04-pression.qmd`)
5. **P7 sans tableau ville × cluster** → ajouter `rt_table` interactif (74 villes + cluster + indicateurs clés).
6. **P1 `girafe()` brut** → remplacer par `render_girafe()`. (`_srpt-monde-01-portrait.qmd` ligne 52)
7. **P5 enrichissement** : remplacer `str_ratio_ann_hote` (doublon P1) par `ctx_tour_nights_total_24` ou `str_instantbook_pct`.

### Moyen (finitions)
8. H3 `### 2.1/2.2/2.3` → renommer en `### Concept : question ?` (`_srpt-monde-02-prix-structure.qmd`)
9. Transition P2 → P3 manquante (fin de P2 pointe vers P4).
10. Libellé cluster C3 unifié entre gt table et carte (P7).
11. Conclusion générale absente après P7 → ajouter 3-4 phrases de synthèse.
12. BAB dans C3 inexpliqué → 1-2 phrases de note.

---

*Relecture générée par analyse structurelle des 8 srpt + JSON `rapport-monde-v2_rslt_claude_log.json` (84 clés) · Aucun fichier source modifié · 2026-06-13*
