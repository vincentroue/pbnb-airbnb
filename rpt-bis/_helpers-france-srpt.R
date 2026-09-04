# &s &HELPERS_FRANCE_SRPT_aaMAIN - Helpers rapport France (srpt)
# Fichier: _helpers-france-srpt.R | dcr: 26-06-05
# Usage: source() dans setup APRES _setup-common.R + _data-load-france.R
# Definitions de fonctions uniquement (pas de mutation de donnees au top-level)
# -> sourcable avant ou apres _data-load-france.R sans effet de bord.

# &s &LOG_AA_VARS - Dump des variables narratives aa_fr$* dans le JSON log
# Generique (copie de _helpers-monde-srpt.R) : source unique de verite Pass 2.
log_aa_vars <- function(aa_list, prefix = "aa_") {
  if (!is.list(aa_list)) {
    warning("log_aa_vars: aa_list n'est pas une liste")
    return(invisible(NULL))
  }
  for (nm in names(aa_list)) {
    val <- aa_list[[nm]]
    if (is.list(val) && !is.data.frame(val)) {
      for (sub_nm in names(val)) {
        sub_val <- val[[sub_nm]]
        tryCatch(
          log_result(paste0(prefix, nm, "_", sub_nm), sub_val,
                     interpret = sprintf("aa$%s$%s [%s]", nm, sub_nm, class(sub_val)[1])),
          error = function(e) NULL)
      }
    } else {
      tryCatch(
        log_result(paste0(prefix, nm), val,
                   interpret = sprintf("aa$%s [%s]", nm, class(val)[1])),
        error = function(e) NULL)
    }
  }
  message(sprintf(">>> log_aa_vars : %d variables aa$* dumpees", length(aa_list)))
  invisible(NULL)
}
# &e

# &s &PROFIL_6V - Tableau comparatif des 6 marches francais (gt)
# 14 indicateurs x 6 villes + refs France/Europe, coloration gradient vs France.

PROFIL_VARS <- c("vol_n_ann", "prs_listings_1000hab_dense", "prsf_listings_1000rp",
  "px_entire_med", "px_private_med",
  "str_entire_pct", "cr_offre_1plus", "str_minnuits30_pct",
  "cr_offre_10plus", "cr_hosts_offre50_pct",
  "act_cal_ouvert_med", "act_revenu_med", "act_reserv_j_med", "actrv_note_glb")

PROFIL_LABELS <- c(
  vol_n_ann = "Annonces actives", prs_listings_1000hab_dense = "Ann. / 1 000 hab.",
  prsf_listings_1000rp = "Ann. / 1 000 RP",
  px_entire_med = "Prix méd. entier (€)", px_private_med = "Prix méd. privé (€)",
  str_entire_pct = "% Logement entier", cr_offre_1plus = "% Offre multi-hôtes",
  str_minnuits30_pct = "% Longue durée",
  cr_offre_10plus = "Offre hôtes ≥10 ann.", cr_hosts_offre50_pct = "Hôtes pour 50% offre",
  act_cal_ouvert_med = "Disponibilité méd. (j)", act_revenu_med = "Revenu estimé (€/an)",
  act_reserv_j_med = "Occupation estimée (j)", actrv_note_glb = "Note globale (/5)")

PROFIL_THEMES <- c(
  vol_n_ann = "Volume", prs_listings_1000hab_dense = "Pression", prsf_listings_1000rp = "Pression",
  px_entire_med = "Prix", px_private_med = "Prix",
  str_entire_pct = "Structure", cr_offre_1plus = "Structure", str_minnuits30_pct = "Structure",
  cr_offre_10plus = "Concentration", cr_hosts_offre50_pct = "Concentration",
  act_cal_ouvert_med = "Activité", act_revenu_med = "Activité",
  act_reserv_j_med = "Activité", actrv_note_glb = "Activité")

.val_fr <- function(df, var) {
  v <- df[[var]]
  if (is.null(v) || all(is.na(v))) NA_real_ else v[1]
}

# Construit le data.frame long : theme | indicateur | <villes> | France | Europe
make_profil_6v <- function(vars = PROFIL_VARS) {
  data.frame(
    theme      = PROFIL_THEMES[vars],
    indicateur = PROFIL_LABELS[vars],
    Paris      = sapply(vars, function(v) .val_fr(paris_fr, v)),
    Lyon       = sapply(vars, function(v) .val_fr(lyon_fr, v)),
    Bordeaux   = sapply(vars, function(v) .val_fr(bordeaux_fr, v)),
    Biarritz   = sapply(vars, function(v) .val_fr(biarritz_fr, v)),
    Bayonne    = sapply(vars, function(v) .val_fr(bayonne_fr, v)),
    Anglet     = sapply(vars, function(v) .val_fr(anglet_fr, v)),
    France     = sapply(vars, function(v) .val_fr(kpi_fr_pays, v)),
    Europe     = sapply(vars, function(v) .val_fr(ref_europe, v)),
    row.names = NULL, stringsAsFactors = FALSE)
}

# gt stylee : format par theme + gradient relatif a France (gt_gradient_vs_focus canonique)
gt_profil_6v <- function(profil = make_profil_6v()) {
  cols_all <- c("Paris", "Lyon", "Bordeaux", "Biarritz", "Bayonne", "Anglet", "France", "Europe")
  vol_rows <- which(profil$theme == "Volume")

  profil |>
    gt_styled(
      title = "Paris domine en volume, Biarritz culmine en pression résidentielle",
      subtitle = "Profil comparé des 6 marchés français — Inside Airbnb juin 2025 · INSEE RP 2022",
      groupname_col = "theme") |>
    fmt(columns = all_of(cols_all), rows = theme == "Volume",
        fns = function(x) ifelse(is.na(x), "—", formatC(round(x), big.mark=" ", format="d"))) |>
    fmt(columns = all_of(cols_all), rows = theme == "Pression",
        fns = function(x) ifelse(is.na(x), "—", formatC(x, format="f", digits=1, decimal.mark=","))) |>
    fmt(columns = all_of(cols_all), rows = theme == "Prix",
        fns = function(x) ifelse(is.na(x), "—", formatC(round(x), big.mark=" ", format="d"))) |>
    fmt(columns = all_of(cols_all), rows = theme %in% c("Structure","Concentration"),
        fns = function(x) ifelse(is.na(x), "—", paste0(round(x)," %"))) |>
    fmt(columns = all_of(cols_all), rows = indicateur == "Note globale (/5)",
        fns = function(x) ifelse(is.na(x), "—", formatC(x, format="f", digits=2, decimal.mark=","))) |>
    fmt(columns = all_of(cols_all),
        rows = indicateur %in% c("Disponibilité méd. (j)", "Occupation estimée (j)"),
        fns = function(x) ifelse(is.na(x), "—", formatC(round(x), format="d"))) |>
    fmt(columns = all_of(cols_all), rows = indicateur == "Revenu estimé (€/an)",
        fns = function(x) ifelse(is.na(x), "—", paste0(formatC(round(x), big.mark=" ", format="d")," €"))) |>
    gt_gradient_vs_focus(columns = all_of(cols_all), ref_value = "France",
      focus_col = "France", type = "ratio", skip_rows = vol_rows,
      breaks_ratio = c(0.10, 0.30, 0.50)) |>
    tab_spanner(label = "Villes", columns = c("Paris","Lyon","Bordeaux","Biarritz","Bayonne","Anglet")) |>
    tab_spanner(label = "Réf.", columns = c("France","Europe")) |>
    cols_label(indicateur = "") |>
    cols_align(align = "center", columns = all_of(cols_all)) |>
    cols_width(indicateur ~ px(180)) |>
    tab_options(row_group.font.weight = "600", row_group.background.color = "#f0f0f0",
      row_group.border.top.color = "#aaa", table_body.hlines.style = "none") |>
    sub_missing(missing_text = "—")
}
# &e

# &s &FR_PANEL_ZSCORE - Tableau pastille z-score par ligne (pattern gt-tr-grp-lignezsc)
# Remplace le remplissage plein de gt_profil_6v par des pastilles legeres sur les
# seuls outliers (|z|>1). Compare les 6 villes entre elles par ligne. France = focus.
# Reutilise gt_panel_transp + gt_color_zscore_byrow (jcn-gtable), comme le monde.

# 260901 : deux corrections.
#  - `prsf_listings_1000rp` -> `prsf_listings_1000rps` : le ratio /RP est ENDOGENE (un logement
#    bascule en location courte duree sort du champ RP). On garde `prs_listings_1000hab_dense`
#    a cote : l'un rapporte au territoire habite, l'autre au parc.
#  - `cr_hosts_offre50_pct` RETIRE : sa polarite est inversee (part des hotes necessaires pour
#    detenir 50 % de l'offre -> 40 % = le MIEUX reparti, 22 % = le plus concentre). Il corrile a
#    -0,99 avec l'offre multi-hotes et -1,00 avec le Gini : redondant ET a contresens de lecture,
#    la pastille z-score le signalait comme une alerte a Bayonne/Anglet qui sont les marches les
#    moins concentres du panel. Remplace par `cr_offre_top10pct_pct`, qui se lit dans le bon sens.
FR_PANEL_VARS <- c("vol_n_ann", "prs_listings_1000hab_dense", "prsf_listings_1000rps",
  "px_entire_med", "px_private_med",
  "str_entire_pct", "str_minnuits30_pct",
  "cr_offre_1plus", "cr_offre_10plus", "cr_offre_top10pct_pct",
  "act_cal_ouvert_med", "act_revenu_med", "act_reserv_j_med", "actrv_note_glb")

# Mapping theme ddict -> (categorie MAJ, bloc) — meme logique que le monde
CATEG_BLOC_FR <- list(
  vol = c("Marché", "Volume"),   px = c("Marché", "Prix"),
  str = c("Offre", "Structure"), cr = c("Offre", "Concentration"), crt = c("Offre", "Concentration"),
  act = c("Activité", "Performance"), actrv = c("Activité", "Qualité"),
  prs = c("Territoire", "Pression"),  prsf = c("Territoire", "Pression"),
  ctx = c("Contexte", "Contexte"))

.cb_fr <- function(v) {
  th <- dd$indics[[v]]$theme
  if (is.null(th) || !th %in% names(CATEG_BLOC_FR)) c("Autre", "Autre") else CATEG_BLOC_FR[[th]]
}

# Panel transpose : 1 ligne / indicateur, 1 col / territoire (france focus + 6 villes)
make_fr_panel <- function(vars = FR_PANEL_VARS) {
  rows <- lapply(vars, function(v) {
    entry <- dd$indics[[v]]; cb <- .cb_fr(v)
    data.frame(
      categorie  = cb[1], bloc = cb[2],
      indicateur = if (!is.null(entry$short)) entry$short else v,
      unite      = if (!is.null(entry$unit)) entry$unit else "",
      var_id     = v,
      france     = .val_fr(kpi_fr_pays, v),
      Paris      = .val_fr(paris_fr, v),   Lyon    = .val_fr(lyon_fr, v),
      Bordeaux   = .val_fr(bordeaux_fr, v), Biarritz = .val_fr(biarritz_fr, v),
      Bayonne    = .val_fr(bayonne_fr, v),  Anglet  = .val_fr(anglet_fr, v),
      stringsAsFactors = FALSE, check.names = FALSE)
  })
  do.call(rbind, rows)
}

# gt pastille : gt_panel_transp + gt_color_zscore_byrow(mode="pastille")
gt_fr_panel_zscore <- function(panel = make_fr_panel()) {
  lecture <- paste0(
    "<span style='font-size:10px;color:#555'><b>Lecture :</b> chaque ligne compare les ",
    "6 villes entre elles. Pastille = écart à la moyenne des six ",
    "(<span style='background:#fde8ee;padding:0 4px'>|z|&gt;1</span> ",
    "<span style='background:#f0a8c0;padding:0 4px;font-weight:700'>|z|&gt;2</span> au-dessus, ",
    "bleu en-dessous). <b>France</b> = référence (gras, exclue du calcul). ",
    "Volumes = non colorés (non comparables en z-score).</span>")
  source_note <- paste0(
    "<span style='font-size:9px;color:#888'>Source : Inside Airbnb juin 2025 · INSEE RP 2022 · ",
    "Villes triées par nombre d'annonces décroissant (après France).</span>")

  panel |>
    gt_panel_transp(
      dd = dd, focus_col = "france", sort_geo_by = "vol_n_ann",
      geo_labels = c(france = "France"),
      title = "Paris domine, Biarritz sature : positionnement des 6 marchés français (z-score par ligne)",
      lecture_note = lecture, source_note = source_note) |>
    gt_color_zscore_byrow(
      columns = c("Paris", "Lyon", "Bordeaux", "Biarritz", "Bayonne", "Anglet"),
      skip_types = c("stock", "vol"), mode = "pastille") |>
    gt::sub_missing(missing_text = "—")  # pression dense = NaN pour BAB -> tiret, pas "NA"
}
# &e

# &s &SMULT_CITIES - Small multiples barres horizontales par ville (standard projet)
# Mirroir de plot_cd_bars_ordered (monde) mais sur villes au lieu de continents.
# Theme canonique des barres : .th_bar (jcn-graph-bar.R) — PAS theme_urbn (cf. ligne 12 du helper).
plot_cities_smult <- function(cities_df, vars, var_labels,
                              label_col = "city_fr", ncol = 2,
                              fill = col_cyan, digits = 0) {
  ord <- cities_df[[label_col]]
  long <- do.call(rbind, lapply(vars, function(v) data.frame(
    city = cities_df[[label_col]], var = var_labels[[v]], val = cities_df[[v]],
    stringsAsFactors = FALSE)))
  long$city <- factor(long$city, levels = rev(ord))
  long$var  <- factor(long$var, levels = unname(var_labels))

  ggplot(long, aes(x = val, y = city)) +
    geom_col(width = 0.66, fill = fill, show.legend = FALSE) +
    geom_text(aes(label = fmt_fr(val, digits)), hjust = -0.12, size = 2.8,
              color = "#555", family = .font_family) +
    scale_x_continuous(expand = expansion(mult = c(0, 0.22))) +
    facet_wrap(~ var, scales = "free_x", ncol = ncol) +
    labs(x = NULL, y = NULL) +
    .th_bar +
    theme(
      strip.text = element_text(face = "bold", size = 9.5, color = "#333", hjust = 0),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.spacing = unit(0.9, "lines"))
}
# &e

# &s &EU_VAL - Valeur benchmark d'une ville UE (dynamique, NA-safe) pour la prose
# Usage inline : `r eu_val("amsterdam", "px_entire_med", 0)` -> "331"
eu_val <- function(city_code, var, digits = 0) {
  v <- kpi_comp[[var]][kpi_comp$city == city_code]
  naf(if (length(v)) v[1] else NA_real_, digits)
}
# Max d'un indicateur parmi les villes FR du benchmark (ex : ville FR la plus pro)
fr_max <- function(var, digits = 0) naf(max(kpi_comp_fr[[var]], na.rm = TRUE), digits)
# &e

# &s &BENCH_EUROPE - Tableau reactable benchmark 23 villes UE (FR surlignees)
# Villes francaises (is_fr == "France") en gras via rt_col_lib + tag pays.
# Format repris du rapport monde (srpt01) : rt_col_level + barres elastiques bw="fill",
# bh=16. Les VOLUMES passent en gris (light = TRUE), les ratios/prix restent colores.
BENCH_VOL_VARS <- c("vol_n_ann", "vol_n_hotes")   # -> barre grise (light)

BENCH_VARS_DEF <- c("vol_n_ann", "prs_listings_1000hab_dense", "px_entire_med",
                    "str_entire_pct", "cr_offre_1plus", "cr_offre_10plus",
                    "str_minnuits30_pct", "act_revenu_med")

# label_field : "short" (compact, tient en PDF portrait) ou "medium" (verbeux, large).
# mw : largeur MINIMALE par colonne (rt_col_level prend max(mw, auto_w)).
# bw : "fill" = barre elastique (jolie mais exige >= ~130 px/col sinon le nombre est
# tronque en PDF) ; valeur numerique (ex 26) = barre fixe courte -> colonnes etroites OK.
# Defauts = variante E3 (validee au PDF 260822, cf dev/dev-bench-europe.qmd) :
# 8 indicateurs conserves, labels courts, barres FIXES LONGUES (bw=56) et angles DROITS
# (radius=0, plus lisible que l'arrondi sur des barres denses) -> ~1025 px, tient en portrait.
# Pieges ecartes par le test : bw="fill" sur 8 colonnes tronque les NOMBRES sous ~130 px/col
# (on lisait "69" au lieu de "69 933") ; labels medium + mw=150 = 1400 px, coupe en PDF.
rt_bench_europe <- function(data = kpi_comp, height = 560, mw = 108,
                            label_field = "short", vars = BENCH_VARS_DEF,
                            lib_mw = 115, bw = 56, bh = 15, radius = 0) {
  d <- data |>
    dplyr::arrange(dplyr::desc(vol_n_ann)) |>
    dplyr::select(dplyr::any_of(c("city_fr", "country_code", "is_fr", vars)))

  cols <- list(
    city_fr      = rt_col_lib(d, "city_fr", "Ville", indent = FALSE, mw = lib_mw),
    country_code = rt_col_tag("Pays", w = 46),
    is_fr        = colDef(show = FALSE))
  for (v in vars) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry) && !is.null(entry[[label_field]])) entry[[label_field]] else v
    unt <- if (!is.null(entry)) entry$unit else ""
    cols[[v]] <- rt_col_level(d, v, label = lbl, unit = unt,
                              bw = bw, bh = bh, mw = mw, radius = radius,
                              light = v %in% BENCH_VOL_VARS)
  }
  rt_table(d, cols = cols, sticky_cols = 1, height = height,
           searchable = FALSE, full_width = TRUE,
           footnote = "Inside Airbnb, juin 2026 · 23 villes de 6 pays · tri par volume · volumes en gris (light), ratios colorés · BAB = agglo Biarritz-Anglet-Bayonne")
}
# &e

# &s &IRIS_FOCUS - Modele reutilisable de focus territorial a la maille IRIS

# --- DENOMINATEUR : LOGEMENTS OCCUPES (RP + secondaires), arbitrage 260820 ---
# Trois candidats testes sur les 1057 IRIS du panel :
#
#   denominateur              endogeneite*   biais de vacance          dispo pipeline
#   /RP                       -0,61          --                        sp10 OK
#   /RP + secondaires         -0,455         immunise                  sp10 OK      <- RETENU
#   /logements (parc total)   -0,417         expose (3,6 % a 9,8 %)    sp10 STANDBY
#   * corr(indicateur, part de RP dans le parc) : plus c'est negatif, plus le ratio s'auto-gonfle.
#
# 1) Pourquoi PAS les seules residences principales : c'est ENDOGENE. Un logement bascule en
#    location courte duree sort du champ RP (l'INSEE le reclasse en residence secondaire ou
#    occasionnelle), donc le denominateur retrecit exactement la ou la pression monte.
#    Champs-Elysees 3 : 120 annonces, 522 logements occupes mais 237 RP -> 506 pour 1 000 RP
#    contre 230 pour 1 000 occupes. Facteur 2,2 d'artefact.
# 2) Pourquoi PAS le parc total : il embarque les logements VACANTS, dont la part varie d'un
#    facteur 2,7 entre territoires (Pays Basque 3,6 %, Paris 9,8 %). C'est un effet de
#    composition local, sans rapport avec Airbnb, qui dilue mecaniquement Paris. Et un
#    logement vacant n'est pas un usage concurrent. Le gain d'endogeneite est marginal.
# 3) Les logements OCCUPES incluent le stock bascule en Airbnb (compte en secondaire /
#    occasionnel) : le denominateur ne bouge pas quand l'usage change, et il exclut la vacance.
#    Lecture : "sur 1 000 logements effectivement occupes, combien sont en location courte duree".
#
# NB : la correlation residuelle de -0,455 n'est PAS que de l'artefact — la ou Airbnb est dense
# il y a reellement moins de residences principales. C'est le phenomene, pas un biais : chercher
# a l'annuler reviendrait a effacer le signal.
MIN_OCC_IRIS <- 200                              # garde-fou sur le denominateur reel (14 IRIS ecartes)
VAR_PRESSION_IRIS <- "prsf_listings_1000rps"     # calcule par sp10 : annonces / (logements - vacants)

# Les 4 perimetres IRIS reellement cartographiables (le CSV porte 6 villes, mais les 3
# communes basques partagent un seul perimetre IRIS contigu de 41 quartiers).
FOCUS_IRIS <- list(
  list(key = "paris",    label = "Paris"),
  list(key = "lyon",     label = "Lyon"),
  list(key = "bordeaux", label = "Bordeaux"),
  list(key = "biarritz", label = "Biarritz · Anglet · Bayonne")
)

#' Neutralise les IRIS dont le parc occupe est trop petit pour un ratio fiable.
#' Vectorise : sert sur le data.frame KPI comme sur les geometries jointes.
add_pression_iris <- function(d, min_occ = MIN_OCC_IRIS) {
  d$logements_occ <- d$logements - d$log_vacants
  ok <- !is.na(d$logements_occ) & d$logements_occ >= min_occ
  for (v in intersect(c("prsf_listings_1000rps", "prsf_listings_1000rp"), names(d))) {
    d[[v]][!ok] <- NA_real_
  }
  d$.iris_ok <- ok
  d
}

#' Geometries IRIS d'une ville + KPI + garde-fou + infobulle prete.
# Deux filtres COMPLEMENTAIRES pour ecarter le non-residentiel qui deforme le cadrage :
#  - type_iris == "D" (divers) : bois, jardins, grands equipements. Attrape les bois de
#    Boulogne 1-2 et de Vincennes 1, qui n'ont meme pas de KPI (sous les 20 annonces).
#  - densite de logements < min_dens_log : attrape ce que le type ne voit pas, comme
#    "Le Lac 1" a Bordeaux — type "A" (activite), 1 944 logements sur 9,6 km2 (202/km2),
#    soit 9,6 des 50 km2 du cadre bordelais pour un IRIS de parc des expositions.
# A 300 log/km2 : 3 IRIS ecartes a Paris, 1 a Bordeaux, 0 a Lyon et au Pays Basque.
load_iris_focus <- function(city_key, min_occ = MIN_OCC_IRIS, drop_divers = TRUE,
                             min_dens_log = 300) {
  g <- add_pression_iris(load_iris_geo(city_key), min_occ)
  if (drop_divers && "type_iris" %in% names(g)) g <- g[g$type_iris != "D", ]
  if (!is.null(min_dens_log)) {
    .dens <- g$logements / (as.numeric(sf::st_area(g)) / 1e6)
    g <- g[is.na(.dens) | .dens >= min_dens_log, ]
  }
  nb <- function(x, dg = 0) ifelse(is.na(x), "—", format(round(x, dg), big.mark = " "))
  g$tooltip <- sprintf(
    paste0("<b>%s</b><br>%s annonces · %s logements occupés (dont %s rés. principales)",
           "<br>%s<br>%s €/nuit · %s %% de l'offre à des multi-hôtes"),
    g$nom_iris, nb(g$vol_n_ann), nb(g$logements_occ), nb(g$rp),
    # 3 statuts a NE PAS confondre : pas de KPI (IRIS sous le filtre 20 annonces de sp10) /
    # KPI present mais parc trop petit / valeur reelle, donnee dans les DEUX lectures.
    ifelse(is.na(g$vol_n_ann), "moins de 20 annonces",
      ifelse(!g$.iris_ok, "ratio non significatif (parc trop petit)",
        sprintf("<b>%s</b> ann./1 000 log. occupés · %s ann./1 000 rés. princ.",
                fmt_fr(g$prsf_listings_1000rps, 0), fmt_fr(g$prsf_listings_1000rp, 0)))),
    nb(g$px_entire_med), nb(g$cr_offre_1plus_ville))
  g
}

#' Bins PARTAGES entre les 4 territoires : sans ca chaque carte a sa propre echelle et
#' Bordeaux parait aussi tendu que Paris. Comparabilite = bins communs.
iris_bins <- function(var = VAR_PRESSION_IRIS, min_occ = MIN_OCC_IRIS, n_mid = 5) {
  v <- add_pression_iris(kpi_fr_iris, min_occ)[[var]]
  make_bins_level(v[!is.na(v)], n_mid = n_mid, palette = PAL_BV8)
}

#' Carte IRIS d'une ville, format stabilise du panneau comparatif.
#'  - `n_val` : seules les N valeurs les plus fortes sont ecrites sur la carte. Toutes les
#'    afficher noyait le lecteur sous 800 nombres a Paris et rendait Bordeaux illisible.
#'  - `n_top` : les N premieres portent EN PLUS leur nom de quartier (mecanisme natif de
#'    build_map : repel + surlignage).
#'  - contours et noms des communes des que la ville en agrege plusieurs (Pays Basque).
#' bins = NULL -> echelle propre a la ville (focus autonome) ; bins = iris_bins() -> echelle
#' commune (panneau comparatif). interactive = FALSE pour le panneau : le survol n'apporte
#' rien sur une vignette et 4 x 1 000 polygones en SVG interactif alourdissent la page.
map_iris_ville <- function(city_key, var = VAR_PRESSION_IRIS, bins = NULL,
                            titre = NULL, legend_title = "Ann./1 000 log. occ.",
                            n_top = 2, n_val = 12, label_size = 2.1, geo = NULL,
                            interactive = TRUE, val_size = 1.9, communes = NULL) {
  # communes : tracer les limites communales. NULL = auto, uniquement pour les peri-
  # metres qui agregent de VRAIES communes (le Pays Basque). A Paris et Lyon la colonne
  # nom_commune vaut l'ARRONDISSEMENT : le declenchement automatique y ecrivait
  # "Paris 18e Arrondissement" sur toute la carte.
  if (is.null(communes)) {
    communes <- identical(unname(CITY_IRIS_MAP[city_key]), "bab")
  }
  g <- if (is.null(geo)) load_iris_focus(city_key) else geo
  p <- build_map(g, var, bins = bins, bin_type = "level", interactive = interactive,
                 titre = titre, label_col = "nom_iris", n_top = n_top, n_bottom = 0,
                 show_values = FALSE, label_position = "repel",
                 label_fill_sign = FALSE, label_style = "text", label_size = label_size,
                 tooltip_col = "tooltip", legend_title = legend_title,
                 legend_drop = FALSE, terr_lbl = "IRIS",
                 na_hatch = FALSE, na_color = "#d9d9d9",
                 bin_args = list(palette = PAL_BV8, n_mid = 5)) + th_map_sm

  # Contour des communes : dissolution des IRIS (le geojson "neighbourhoods" d'Inside Airbnb
  # ne contient qu'un seul polygone pour pays-basque, inexploitable pour les 3 communes).
  if (communes && "nom_commune" %in% names(g) && dplyr::n_distinct(g$nom_commune) > 1) {
    com <- g |> dplyr::group_by(nom_commune) |> dplyr::summarise(.groups = "drop")
    p <- p +
      ggplot2::geom_sf(data = com, fill = NA, colour = "#333333", linewidth = 0.45) +
      ggplot2::geom_sf_text(data = com, ggplot2::aes(label = nom_commune),
                            size = 2.5, fontface = "bold", colour = "#2a2a2a",
                            family = .font_family, check_overlap = TRUE)
  }

  # Valeurs des n_val premiers IRIS, SANS nom (les n_top premiers sont deja nommes ci-dessus)
  v <- g[[var]]
  if (n_val > n_top && sum(!is.na(v)) > n_top) {
    idx <- utils::tail(utils::head(order(-v, na.last = NA), n_val), -n_top)
    if (length(idx)) {
      p <- p + ggplot2::geom_sf_text(
        data = g[idx, ], ggplot2::aes(label = round(.data[[var]])),
        size = val_size, colour = "#1a1a1a", fontface = "bold",
        family = .font_family, check_overlap = TRUE)
    }
  }
  p
}

#' Colonne EVOLUTION compacte : fleche + valeur signee, bordeaux (hausse) / bleu (baisse),
#' GRAS au-dela du 3e quartile. Pas de barre : sur des evolutions serrees autour de 0 la piste
#' grise reste quasi vide et mange la largeur pour rien.
.rt_col_evol_fr <- function(data, col, label, unit = "%", mw = 96) {
  vc  <- data[[col]][!is.na(data[[col]])]
  thr <- if (length(vc) > 1) as.numeric(stats::quantile(abs(vc), 0.75, na.rm = TRUE)) else 1
  if (!is.finite(thr) || thr < 1e-6) thr <- 1
  reactable::colDef(
    name = label, header = hdr_unit2(label, unit), minWidth = mw, maxWidth = 118, align = "right",
    cell = function(v) {
      if (is.na(v)) return(htmltools::span(style = "color:#bbb", "—"))
      up <- v >= 0; strong <- abs(v) >= thr
      col_txt <- if (up) (if (strong) "#74303f" else "#b07680") else (if (strong) "#26506f" else "#6f93b5")
      htmltools::div(
        style = "display:flex;align-items:center;justify-content:flex-end;gap:3px;white-space:nowrap",
        htmltools::span(style = sprintf("color:%s;font-size:8px", col_txt), if (up) "▲" else "▼"),
        htmltools::span(style = sprintf("color:%s;font-size:11.5px;font-weight:%s", col_txt,
                                        if (strong) "700" else "400"),
                        sub(".", ",", sprintf("%+.1f", v), fixed = TRUE)))
    })
}

#' Classement IRIS pleine page : volume et sa dynamique, pression, professionnalisation, prix.
#' La maille administrative est NOMMABLE (contrairement aux hexagones) : c'est ici, et ici
#' seulement, qu'on peut citer des quartiers. `sort_by` bascule le classement entre les
#' quartiers les plus tendus et les plus professionnalises.
top_iris_table <- function(n = 15, min_occ = MIN_OCC_IRIS,
                            sort_by = c("pression", "pro"), title = NULL) {
  sort_by <- match.arg(sort_by)
  scol <- if (sort_by == "pression") "prsf_listings_1000rps" else "cr_offre_1plus_ville"
  lab  <- c(paris = "Paris", lyon = "Lyon", bordeaux = "Bordeaux", `pays-basque` = "Pays Basque")
  d <- add_pression_iris(kpi_fr_iris, min_occ) |>
    dplyr::filter(!is.na(.data[[scol]]), !is.na(prsf_listings_1000rps)) |>
    dplyr::slice_max(.data[[scol]], n = n) |>
    dplyr::transmute(
      nom_iris,
      ville     = unname(lab[city]),
      vol_n_ann,
      vol_n_ann_vevol_2526 = if ("vol_n_ann_vevol_2526" %in% names(kpi_fr_iris)) vol_n_ann_vevol_2526 else NA_real_,
      prsf_listings_1000rps = round(prsf_listings_1000rps, 0),
      cr_offre_1plus_ville  = round(cr_offre_1plus_ville, 0),
      prsf_listings_1000rp  = round(prsf_listings_1000rp, 0),
      px_entire_med         = round(px_entire_med, 0))
  if (is.null(title)) {
    title <- if (sort_by == "pression") sprintf("Les %d quartiers les plus tendus de France", n)
             else sprintf("Les %d quartiers les plus professionnalisés de France", n)
  }
  rt_table(d, cols = list(
    nom_iris  = rt_col_lib(d, "nom_iris", "Quartier (IRIS)", indent = FALSE, mw = 180),
    ville     = rt_col_tag("Ville", w = 88),
    vol_n_ann = rt_col_var(d, "vol_n_ann", "Annonces actives", unit = "n", mw = 118),
    vol_n_ann_vevol_2526  = .rt_col_evol_fr(d, "vol_n_ann_vevol_2526", "Évol. 26/25"),
    prsf_listings_1000rps = rt_col_level(d, "prsf_listings_1000rps", "Pression",
                                         unit = "/1 000 log. occ.", bw = "fill", bh = 16, mw = 130),
    cr_offre_1plus_ville  = rt_col_level(d, "cr_offre_1plus_ville", "Professionnalisation",
                                         unit = "% de l'offre", bw = "fill", bh = 16, mw = 138),
    prsf_listings_1000rp  = rt_col_level(d, "prsf_listings_1000rp", "Rappel : lecture /RP",
                                         unit = "/1 000 RP", bw = "fill", bh = 16, mw = 120),
    px_entire_med = rt_col_level(d, "px_entire_med", "Prix logement entier",
                                 unit = "€/nuit", bw = "fill", bh = 16, mw = 124)),
    sticky_cols = 1, searchable = FALSE, full_width = TRUE, height = "auto",
    title = title,
    subtitle = sprintf(paste0("Annonces pour 1 000 logements occupés (rés. principales et secondaires) · ",
                              "IRIS d'au moins %s logements occupés · 4 périmètres"),
                       format(min_occ, big.mark = " ")),
    footnote = paste0("Inside Airbnb juin 2026 · INSEE RP 2022 · Évolution 2025→2026 des annonces actives, ",
                      "appariée par IRIS entre les deux snapshots · La professionnalisation est mesurée à ",
                      "l'échelle de la VILLE (un hôte multi-annonces réparties sur plusieurs quartiers est ",
                      "compté multi-hôte partout) · Le ratio est rapporté au parc OCCUPÉ ; la colonne /RP ",
                      "est donnée pour mémoire."))
}
# &e


# &s &DUO_IRIS_GRID - Grille N villes x 2 indicateurs, cartes generees dynamiquement

# Pas de facettes : N x 2 VRAIES cartes independantes, posees dans la grille Quarto via
# un tagList de <div class="grid"> / <div class="g-col-6">. .grid et .g-col-6 sont des
# classes CSS pures -> un seul chunk suffit, knitr collecte les dependances ggiraph au vol.
#
# Les 3 decisions qui font la lecture :
#  1. BINS PARTAGES PAR COLONNE, calcules sur le pool de TOUTES les villes. L'axe de
#     comparaison bascule ici : gauche/droite = 2 indicateurs non comparables entre eux,
#     haut/bas = les villes, elles comparables. Un bins par ville rendrait la lecture
#     verticale fausse sans que ca se voie.
#  2. legend_drop = FALSE : une ville qui n'atteint pas la classe haute la garde quand meme
#     dans sa legende -> legendes de meme longueur d'une ligne a l'autre.
#  3. Legende sur la 1re ligne seulement (bins partages = elle est identique partout).
#
# map_fig_h() est calcule UNE fois par ville et passe aux deux cartes : meme geometrie, meme
# ratio, alignement parfait. Ne PAS mettre de fig-height sur le chunk : avec girafe c'est
# height_svg qui pilote, l'option de chunk serait ignoree.
# Colonne de droite = PROFESSIONNALISATION a portee VILLE (`_ville`, produite par sp10 depuis
# le 260820). La version sans suffixe est recomptee DANS l'IRIS : un hote gerant 5 annonces sur
# 5 IRIS y ressort "mono-annonce" dans chacun -> mediane Paris 14,3 % contre 41,4 % au niveau
# ville, et le seuil >=10 annonces tombait a 0,0 partout. Cartographier ca donnerait la
# geographie de l'etalement des portefeuilles, pas celle de la professionnalisation.
DUO_INDICS <- list(
  list(var = VAR_PRESSION_IRIS,       lab = "Pression — annonces / 1 000 logements occupés",
       leg = "Ann./1 000 log. occ."),
  list(var = "cr_offre_1plus_ville",  lab = "Professionnalisation — offre aux multi-hôtes",
       leg = "% de l'offre")
)

duo_iris_grid <- function(villes, indics = DUO_INDICS, labels = NULL,
                           interactive = TRUE, zoom = TRUE, w = 4.5, n_top = 3) {
  if (is.null(labels)) {
    lb <- c(paris = "Paris", lyon = "Lyon", bordeaux = "Bordeaux",
            biarritz = "Biarritz · Anglet · Bayonne")
    labels <- unname(lb[villes])
  }
  geos <- stats::setNames(lapply(villes, load_iris_focus), villes)

  # Bins par COLONNE sur le pool de toutes les villes (cf. decision 1)
  pool <- do.call(rbind, lapply(geos, function(g) sf::st_drop_geometry(g)[, sapply(indics, `[[`, "var"), drop = FALSE]))
  bins <- lapply(indics, function(ic) make_bins_level(pool[[ic$var]][!is.na(pool[[ic$var]])],
                                                      n_mid = 5, palette = PAL_BV8))

  rows <- lapply(seq_along(villes), function(i) {
    g <- geos[[i]]
    h <- map_fig_h(g, w = w)          # UNE hauteur par ligne -> les 2 cartes s'alignent
    cells <- lapply(seq_along(indics), function(j) {
      ic <- indics[[j]]
      p <- build_map(g, ic$var, bins = bins[[j]], bin_type = "level",
                     interactive = interactive, hover_key = interactive,
                     titre = sprintf("%s · %s", labels[i], ic$lab),
                     label_col = "nom_iris", n_top = n_top, n_bottom = 0,
                     show_values = TRUE, label_position = "repel",
                     label_fill_sign = FALSE, label_style = "text", label_size = 1.9,
                     tooltip_col = "tooltip", legend_title = ic$leg,
                     legend_drop = FALSE, terr_lbl = "IRIS",
                     na_hatch = FALSE, na_color = "#d9d9d9") + th_map_sm
      if (i > 1) p <- p + ggplot2::theme(legend.position = "none")   # cf. decision 3
      # Un ggplot BRUT dans un div n'est pas rendable par htmltools -> en non-interactif
      # on ne peut pas utiliser la grille .g-col-6. On garde le widget dans les deux cas
      # (girafe sans hover ni zoom reste plus leger qu'un widget complet), et pour du vrai
      # statique il faut assembler en patchwork hors grille (cf ir_grid de la partie 2).
      htmltools::div(class = "g-col-6",
                     render_girafe(p, width_svg = w, height_svg = h,
                                   hover_key = interactive, zoom = interactive && zoom))
    })
    htmltools::div(class = "grid", cells)
  })
  do.call(htmltools::tagList, rows)   # do.call : tagList(list) ne compte qu-UN enfant
}
# &e


# &s &FR_DATABAR - Panneau comparatif des 6 villes (statique ggplot + databar HTML)

# Palette PAR FAMILLE, pas par ville : gris = la capitale, chauds = les metropoles regionales,
# bleus = le littoral basque. L'oeil regroupe donc avant de comparer, ce qu'une palette
# categorielle ne permet pas. Ordre = volume decroissant dans chaque famille.
FR_COLS <- c(
  "Paris"    = "#8c8c8c",
  "Lyon"     = "#f5821f", "Bordeaux" = "#fbc02d",
  "Biarritz" = "#1a6d8f", "Anglet"   = "#3aa6d6", "Bayonne" = "#8ec9e3")
FR_ORDER <- names(FR_COLS)

# data.frame 1 ligne / ville, dans l'ordre FR_ORDER (les raccourcis *_fr viennent du data-load)
fr_cities_df <- function() {
  d <- dplyr::bind_rows(paris_fr, lyon_fr, bordeaux_fr, biarritz_fr, anglet_fr, bayonne_fr)
  d$city_fr <- factor(CITY_FR_LABELS[d$territory], levels = FR_ORDER)
  d[order(d$city_fr), ]
}

#' Small multiples barres horizontales, 1 facette / indicateur, evolution sous la valeur.
#' Aligne sur plot_cd_bars_agg (rapport monde) : pas de grille verticale, reference France
#' en pointille, palette par famille.
plot_fr_bars <- function(vars, labels = NULL, evol = NULL, dec = NULL,
                          ncol_wrap = 3, ref_fr = TRUE, bar_width = 0.72,
                          alpha = 0.9, strip_size = 10.5, lab_size = 2.9) {
  d <- fr_cities_df()
  labels <- labels %||% vapply(vars, function(v) {
    e <- dd$indics[[v]]; if (!is.null(e$medium)) e$medium else v }, character(1))
  dec <- dec %||% rep(1, length(vars))

  rows <- lapply(seq_along(vars), function(i) {
    v <- vars[i]
    ev <- if (!is.null(evol) && !is.na(evol[i]) && evol[i] %in% names(d)) d[[evol[i]]] else NA_real_
    data.frame(ville = d$city_fr, val = as.numeric(d[[v]]), evol = as.numeric(ev),
               ind = factor(labels[i], levels = labels),
               ref = if (ref_fr && v %in% names(kpi_fr_pays)) as.numeric(kpi_fr_pays[[v]][1]) else NA_real_,
               dec = dec[i], stringsAsFactors = FALSE)
  })
  df <- do.call(rbind, rows)
  df$lbl <- mapply(function(x, dd_) if (is.na(x)) "" else
                     if (abs(x) >= 1000) fv(x, "k") else fmt_fr(x, dd_), df$val, df$dec)
  df$lbl_ev <- ifelse(is.na(df$evol), "",
                      sub(".", ",", sprintf("%+.1f", df$evol), fixed = TRUE))

  ggplot2::ggplot(df, ggplot2::aes(x = val, y = forcats::fct_rev(ville), fill = ville)) +
    ggplot2::geom_col(width = bar_width, alpha = alpha) +
    ggplot2::geom_vline(ggplot2::aes(xintercept = ref), linetype = "dotted",
                        colour = "#555555", linewidth = 0.4, na.rm = TRUE) +
    ggplot2::geom_text(ggplot2::aes(label = lbl), hjust = -0.15, size = lab_size,
                       family = .font_family, colour = "#333333",
                       vjust = ifelse(df$lbl_ev == "", 0.5, -0.05)) +
    ggplot2::geom_text(ggplot2::aes(label = lbl_ev), hjust = -0.2, vjust = 1.25,
                       size = lab_size - 0.75, family = .font_family,
                       colour = ifelse(!is.na(df$evol) & df$evol < 0, "#26506f", "#74303f")) +
    ggplot2::facet_wrap(~ ind, ncol = ncol_wrap, scales = "free_x") +
    ggplot2::scale_fill_manual(values = FR_COLS, guide = "none") +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0, 0.28))) +
    ggplot2::labs(x = NULL, y = NULL) +
    theme_urbn(base_size = 11) +
    ggplot2::theme(
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor   = ggplot2::element_blank(),
      axis.text.x        = ggplot2::element_blank(),
      axis.ticks         = ggplot2::element_blank(),
      strip.text         = ggplot2::element_text(size = strip_size, face = "bold", hjust = 0))
}

#' Meme panneau en DATABAR HTML (mutils/jcn-databar-panel.R) : rendu identique en PDF,
#' aucune dependance JS, et la pilule d'evolution ne peut pas etre confondue avec la barre.
databar_fr <- function(vars, labels = NULL, evol = NULL, dec = NULL, units = NULL,
                        subs = NULL, n_col = 3, title = NULL, subtitle = NULL,
                        target = FALSE, ref_all = TRUE, lbl_width = "96px") {
  d <- fr_cities_df()
  series <- as.character(d$city_fr)
  labels <- labels %||% vapply(vars, function(v) {
    e <- dd$indics[[v]]; if (!is.null(e$medium)) e$medium else v }, character(1))
  dec <- dec %||% rep(1, length(vars)); units <- units %||% rep("", length(vars))

  indics <- lapply(seq_along(vars), function(i) {
    v <- vars[i]
    ev <- if (!is.null(evol) && !is.na(evol[i]) && evol[i] %in% names(d)) {
      stats::setNames(as.numeric(d[[evol[i]]]), series) } else NULL
    list(lbl  = labels[i], sub = if (!is.null(subs)) subs[i] else NULL,
         unit = units[i], dec = dec[i],
         vals = stats::setNames(as.numeric(d[[v]]), series),
         evol = ev,
         ref  = if (v %in% names(kpi_fr_pays)) as.numeric(kpi_fr_pays[[v]][1]) else NULL)
  })
  # target = FALSE : les 6 villes sont des PAIRS, aucune n'est « la cible » — sans ca Paris
  # (1re serie) prenait l'aspect cible, ce qui n'a pas de sens dans un panel comparatif.
  # ref_all = TRUE : le trait France est trace sur CHAQUE barre, pas seulement la premiere.
  databar_psect(indics, series = series, pal = unname(FR_COLS[series]),
                n_col = n_col, ref_lab = "FR", title = title, subtitle = subtitle,
                target = target, ref_all = ref_all, lbl_width = lbl_width)
}
# &e


# &s &FOCUS_COMMUNE - Focus territorial sur UNE commune (Biarritz / Bayonne / Anglet)
# Modele de focus reutilisable (pterr) : 3 briques — KPI header, duo de cartes IRIS a echelle
# PROPRE (on zoome, on ne compare plus), tableau des quartiers. Chaque brique ne depend que de
# kpi_fr_city / kpi_fr_iris / load_iris_geo : aucun objet du MAIN rapport France.

FOCUS_COMMUNES <- list(
  biarritz = list(lib = "Biarritz", nom = "Biarritz"),
  bayonne  = list(lib = "Bayonne",  nom = "Bayonne"),
  anglet   = list(lib = "Anglet",   nom = "Anglet"))

focus_city_row <- function(commune) kpi_fr_city[kpi_fr_city$territory == commune, ][1, ]

#' Geometries IRIS d'UNE commune basque : le perimetre IRIS charge est l'agglo BAB entiere
#' (cle historique "biarritz" -> filtre bab), on filtre ensuite sur nom_commune du GPKG.
load_iris_commune <- function(commune) {
  g <- load_iris_focus("biarritz")
  g[!is.na(g$nom_commune) & g$nom_commune == FOCUS_COMMUNES[[commune]]$nom, ]
}

#' Bandeau 4 KPI du focus : volume + evolution, prix, pression, professionnalisation.
focus_kpi_row <- function(commune) {
  r <- focus_city_row(commune)
  ev <- as.numeric(r$vol_n_ann_vevol_2526)
  ev_txt <- if (is.na(ev)) NULL else
    sprintf("%s %s %% vs 2025", if (ev < 0) "▼" else "▲", fmt_fr(abs(ev), 1))
  kpi_row(
    kpi_band("Annonces actives", value = nint(r$vol_n_ann),
             subtitle = "juin 2026", ref = ev_txt),
    kpi_band("Prix médian logement entier", value = naf(r$px_entire_med, 0), unit = "€/nuit",
             subtitle = sprintf("France entière : %s €", naf(kpi_fr_pays$px_entire_med, 0))),
    kpi_band("Pression", value = naf(r$prsf_listings_1000rps, 0), unit = "/1 000 log. occ.",
             subtitle = sprintf("%s annonces / 1 000 hab en zone dense",
                                naf(r$prs_listings_1000hab_dense, 0))),
    kpi_band("Offre multi-hôtes", value = naf(r$cr_offre_1plus, 0), unit = "%",
             subtitle = sprintf("dont hôtes à 10 annonces ou plus : %s %%",
                                naf(r$cr_offre_10plus, 0))))
}

#' Duo de cartes IRIS interactives (pression | professionnalisation), echelle propre.
focus_duo_maps <- function(commune, geo = NULL, w = 4.5) {
  g <- if (is.null(geo)) load_iris_commune(commune) else geo
  h <- map_fig_h(g, w = w)
  lib <- FOCUS_COMMUNES[[commune]]$lib
  cell <- function(var, titre, leg) {
    p <- map_iris_ville(commune, var = var, bins = NULL, geo = g, titre = titre,
                        legend_title = leg, n_top = 2, n_val = 15, interactive = TRUE)
    htmltools::div(class = "g-col-6",
                   render_girafe(p, width_svg = w, height_svg = h, hover_key = TRUE, zoom = TRUE))
  }
  htmltools::div(class = "grid",
    cell(VAR_PRESSION_IRIS,
         sprintf("%s · Pression — annonces / 1 000 logements occupés", lib), "Ann./1 000 log. occ."),
    cell("cr_offre_1plus_ville",
         sprintf("%s · Professionnalisation — offre aux multi-hôtes", lib), "% de l'offre"))
}

#' Tableau des quartiers de la commune, tries par pression. La maille IRIS est nommable :
#' c'est ici qu'on cite les quartiers en prose.
focus_top_iris <- function(commune, geo = NULL, n = 12, title = NULL, subtitle = NULL) {
  g <- if (is.null(geo)) load_iris_commune(commune) else geo
  d <- sf::st_drop_geometry(g) |>
    dplyr::filter(!is.na(vol_n_ann)) |>
    dplyr::arrange(dplyr::desc(prsf_listings_1000rps)) |>
    dplyr::slice_head(n = n) |>
    dplyr::transmute(
      nom_iris, vol_n_ann,
      vol_n_ann_vevol_2526  = round(vol_n_ann_vevol_2526, 1),
      prsf_listings_1000rps = round(prsf_listings_1000rps),
      cr_offre_1plus_ville  = round(cr_offre_1plus_ville),
      px_entire_med         = round(px_entire_med))
  rt_table(d, cols = list(
    nom_iris  = rt_col_lib(d, "nom_iris", "Quartier (IRIS)", indent = FALSE, mw = 190),
    vol_n_ann = rt_col_level(d, "vol_n_ann", "Annonces actives", unit = "n",
                             bw = "fill", bh = 16, mw = 140, light = TRUE),
    vol_n_ann_vevol_2526  = .rt_col_evol_fr(d, "vol_n_ann_vevol_2526", "Évol. 26/25"),
    prsf_listings_1000rps = rt_col_level(d, "prsf_listings_1000rps", "Pression",
                                         unit = "/1 000 log. occ.", bw = "fill", bh = 16, mw = 140),
    cr_offre_1plus_ville  = rt_col_level(d, "cr_offre_1plus_ville", "Offre multi-hôtes",
                                         unit = "%", bw = "fill", bh = 16, mw = 130),
    px_entire_med = rt_col_level(d, "px_entire_med", "Prix logement entier",
                                 unit = "€/nuit", bw = "fill", bh = 16, mw = 130)),
    sticky_cols = 1, searchable = FALSE, full_width = TRUE, height = "auto",
    title = title, subtitle = subtitle,
    footnote = paste0("Inside Airbnb juin 2026 · INSEE RP 2022 · Pression rapportée aux logements ",
                      "occupés (— = moins de ", format(MIN_OCC_IRIS, big.mark = " "),
                      " logements occupés, non significatif) · Professionnalisation mesurée à ",
                      "l'échelle de la ville."))
}
# &e

# &e &HELPERS_FRANCE_SRPT_aaMAIN
