# TODO ajustements rapport monde — 2026-06-09

## 🎨 TODO PALETTE + BARRE MONDE (260715)
- [ ] **Réattribuer `CD_COLS`** (`_helpers-monde-srpt.R`) — nouvelle palette continents :
      - Eur. Sud-Est → **jaune**
      - Eur. Ouest-Nord → **orange**
      - Am. du Nord → **bleu cyan**
      - Am. latine → **cyan foncé** (dark cyan / teal — à confirmer « dar cyan »)
      - Asie → **magenta**
      - Océanie → **gris clair**
      (impacte carte clusters/continents, smult, légendes — vérifier contraste)
- [ ] **Barre Monde = ligne verticale pointillée visible PARTOUT** dans les small-multiples
      (`plot_cd_bars_ordered` / `plot_cd_bars_agg`) → `geom_vline(xintercept = <valeur Monde>, linetype = "dashed")` par facette (valeur Monde = médiane ou total selon le helper).
- [x] **Pastilles z-score** (`gt_cd_panel_zscore`) : `bblight` (orange) → **`brlight`** (bordeaux/rose clair + bleu) — FAIT 260715.


## ✅ FAIT (passe 1 — 260609)

### Helpers (mutils + projet)
- [x] `gt_panel_transp` (jcn-gtable.R) : + params `label_field="short"` et `show_categ=TRUE` (rétrocompat)
- [x] `gt_cd_panel_zscore` : passe `label_field="medium"` + `show_categ=FALSE` → labels medium, drop row-group categorie (TERRITOIRE…), garde colonne "Theme" (bloc)
- [x] `plot_cd_bars_agg` : nouveau helper smult = TOTAL continental (kpi_cd_agg) au lieu de médiane
- [x] `build_world_map` : contour TERRES marqué (ne_coastline, pas frontières pays) + labels top/bot N villes (stat="sf_coordinates") + params `n_label_top/n_label_bot`

### srpt-01 (P1 Portrait)
- [x] Carto remontée **juste après le bloc .cld-ctx** (avant : après le float KPI)
- [x] Carte : labels top 3 / bot 3 villes + contours terres
- [x] Bloc KPI panel (810 / 403 / ratio) **retiré de P1** → déplacé en tête P2 (kpi-list float)
- [x] Smult "Graphique par continent" = TOTAL (plot_cd_bars_agg), ordre annonces→hôtes→ann/host, source corrigée ("Total par groupe continental")
- [x] Topbot n_top_bot 5→8, ratio ann/hôte en rt_col_var rank

### srpt-02 (P2 → "Marché, structure et activité")
- [x] H2 retitré "2. Marché, structure et activité" (MAIN)
- [x] Ouverture = kpi-list cadrage panel en **float droit** (offres, 10% offre mondiale, %Europe, %Am Nord, top3 villes, hôtes) ; ancien bandeau prix kpi_band retiré
- [x] Ajout px chambre privée (px_private_med), capacité (str_cap_pers_med, str_cap_chbr_med), tx occupation (act_reserv_taux)
- [x] Tableau continent : make_cd_panel_agg (sans lignes contexte Nb villes/pays — doublon), medium labels, no categorie
- [x] H3 retitrés : 2.1 "Prix : une carte étrangère à celle des volumes" · 2.2 "Structure : le logement entier a effacé le partage" · 2.3 "Revenu : l'occupation, pas le prix, fait la recette"
- [x] §2.3 topbot ("merde") → rt_topbot_view top8/bot8, prix en rt_col_var rank

### Cross-parts P3-P6 + data
- [x] Tableaux continent : drop lignes contexte (make_cd_panel_agg), figure-source z-score
- [x] Topbot : n_top_bot 5→8 + sort col en rt_col_var intensity="rank" + footnote écart-à-moyenne
- [x] _data-load.R : + aa$v_nam_pct (% Am. Nord), aa$t_top3_villes
- [x] YAML : toc-depth 3 + toc-expand true (TOC 3 niveaux déplié à gauche)

**Render OK** : `quarto render rpt-pbnb-synth-monde.qmd --execute-daemon-restart` (83/83 chunks).
HTML : `_output/rpt-pbnb-synth-monde.html` (ouvrir dans navigateur pour relire).
⚠️ PDF Edge abandonné (zombies headless ingérables sur cette machine).

---

## ✅ PASSE 2 — tableaux + cartes (260610)
- [x] Helper PROJET `rt_topbot_ville` : pastille couleur sous-continent avant ville, SANS col continent (fini les débordements 3-col), titre obligatoire, footer médiane Monde auto, 1re col = rt_col_var rank
- [x] Topbot refactorés P1/P3/P4/P5/P6 → rt_topbot_ville (titres + pastilles)
- [x] Carte : labels = 3 villes/sous-continent hors Europe (monde) + toutes les villes (Europe)
- [x] Tableau continent : titre en GRAS + header plus haut + retrait « écarts z-score à la moyenne mondiale » (P1, P2)
- [x] P2 : scatters §2.1/§2.3 + bar empilé §2.2 SUPPRIMÉS → remplacés par 1 top/bottom ville par sous-section (prix entier+chambre privée · part entiers+capacité+chambres · revenu+occupation+calendrier)
- [x] P2 : topbot global de fin supprimé (distribué dans les sous-sections)

## ✅ PASSE 2b — affinage tableaux (260612)
- [x] `rt_topbot_ville` ALLÉGÉ : code pays ISO3 en gris **même ligne** que la ville (plus de 2ᵉ ligne, plus de mapping nom-pays CC_FR) · col ville réduite (mw 130) · gauche
- [x] Tables continent (`gt_cd_panel_zscore`) → `mode = "pastille", light = TRUE` (pastilles rose/bleu clair sur outliers, fond blanc ailleurs)
- [x] Banc de test `dev/dev-topbot-test.qmd` étendu (Test C = tableau continent pastille light) — validé
- [x] P2 topbots en float (graph-droite-65), `country_code` partout, `echo: true` (code replié visible)

## 🔜 RESTE — passe 3
- [ ] **Bilan jcn-all** validé (preview = vrai levier, split = ROI nul) → actualiser ggd quarto + hygiène stub ext (en attente arbitrage user)
- [ ] **srpt-00 intro** : KPI « Concentration de l'offre » → déplacer dans P3 ; KPI « Marché mondial » → float au-dessus du graph, source unique, retirer ▲ parasites
- [ ] **srpt-00 Contexte** : harmoniser le paragraphe (conventions rédac) + ligne Sources unique
- [ ] Tableaux « détaillé par ville » (tabsets) : appliquer aussi pastille + retrait col continent ? (à confirmer)

## 🔜 PASSE 2 — nouvelles consignes user (260609 soir)

### srpt-00 intro — réorg KPI cadrage
- [ ] KPI "**Concentration de l'offre**" (15% hôtes → 50% annonces) : **déplacer dans Partie 3 Professionnalisation** (pas dans l'intro)
- [ ] KPI "**Marché mondial Airbnb**" (8M ann / 491M nuitées / 59% multi) : mettre **au-dessus du graph nuitées, en float** (pas pleine largeur)
- [ ] **Une seule source** sous le bloc (pas une source par carte / pas répétée)
- [ ] Nettoyer les cartes KPI : retirer les "▲ Airbnb 10-K" / "▲ Airbnb SEC filings" en `top=` (le ▲ est réservé aux variations, pas aux sources)

### srpt-00 — harmoniser le paragraphe "Contexte" (convention rédac)
- [ ] Appliquer règles : "passant de 140 millions en 2016 à 491 millions en 2024" (déjà OK), nombres en toutes lettres en prose ("491 millions"), "hausse de 10 %" pas "+10 %", pas de flèches dans la prose, source lisible unique en fin de bloc
- [ ] Texte de référence fourni par user (3 paras : croissance / creux 2020 / bascule LCD vs hôtellerie) + ligne *Sources : Airbnb 10-K FY2024 ; Eurostat ; Lighthouse 2025 ; CoStar/STR.*

### À vérifier au render navigateur (passe 1)
- [ ] Carte : contours terres assez marqués ? labels top3/bot3 bien placés (projection Robinson) ?
- [ ] Tableaux continent : medium labels OK, plus de ligne TERRITOIRE, plus de Nb villes/pays (sauf P1) ?
- [ ] Topbot rose▲/bleu▼ lisibles, footer médiane Monde cohérent ?
- [ ] kpi-list float P2 : rendu correct à droite ?
- [ ] TOC 3 niveaux bien déplié à gauche ?
