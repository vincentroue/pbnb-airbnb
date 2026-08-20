# &s &DATA_LOAD_aaMAIN - Chargement donnees + variables narratives aa_
# Fichier: _data-load.R | dcr: 26-04-15 | dup: 26-05-06
# Usage: source("_data-load.R") apres _setup-common.R
# Colonnes renommees mai 2026 : convention ddict thematique (px_, vol_, str_, act_, cr_, prs_, ctx_)

# &s &KPI_LOAD - CSV KPI (sp08) + jointure lat/lon depuis city-reference
kpi_raw <- read.csv(file.path(DATA_INTERIM, "kpi_global_by_city_2606.csv"),
                     stringsAsFactors = FALSE)
kpi <- kpi_raw |> dplyr::filter(scope == "city")
kpi_sub <- kpi_raw |> dplyr::filter(scope == "sub_city")

# Lat/lon villes (pour cartes geopoint monde / Europe)
city_ref <- tryCatch(
  read.csv(file.path(DATA_EXTERNAL, "city-reference-airbnb-260222.csv"),
           stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM"),
  error = function(e) NULL)
if (!is.null(city_ref) && all(c("city", "lat", "lon") %in% names(city_ref))) {
  kpi <- kpi |> dplyr::left_join(
    city_ref |> dplyr::select(city, lat, lon),
    by = "city")
}

kpi_eur <- kpi |> dplyr::filter(continent == "Europe")
kpi_fra <- kpi |> dplyr::filter(country_code == "FRA")
kpi_am  <- kpi |> dplyr::filter(continent == "Americas")
kpi_ap  <- kpi |> dplyr::filter(continent == "Asia-Pacific")
kpi_af  <- kpi |> dplyr::filter(continent == "Africa")

# Aggregats
kpi_agg <- read.csv(file.path(DATA_INTERIM, "kpi_global_by_aggregate_2606.csv"),
                     stringsAsFactors = FALSE)
kpi_world <- kpi_agg |> dplyr::filter(level == "world") |> dplyr::slice(1)
# Aggregats par continent_detail (sp08-pre-computed, plus fiable que median(median()))
kpi_cd_agg <- kpi_agg |> dplyr::filter(level == "continent_detail")

# Pays comparables
COMP_CC <- c("FRA", "ITA", "DEU", "GBR", "ESP", "NLD")
kpi_comp <- kpi |> dplyr::filter(country_code %in% COMP_CC)

# Raccourcis villes FR
paris <- kpi |> dplyr::filter(city == "paris") |> dplyr::slice(1)
bordeaux <- kpi |> dplyr::filter(city == "bordeaux") |> dplyr::slice(1)
lyon <- kpi |> dplyr::filter(city == "lyon") |> dplyr::slice(1)
bab <- kpi |> dplyr::filter(city == "pays-basque") |> dplyr::slice(1)
# &e

# &s &MOYENNES
avg_eur_prix <- median(kpi_eur$px_entire_med, na.rm = TRUE)
avg_eur_pression <- mean(kpi_eur$prs_listings_1000hab_dense, na.rm = TRUE)
avg_eur_multi <- mean(kpi_eur$cr_offre_1plus, na.rm = TRUE)
# &e

# &s &TOPBOT
top_prix <- kpi |> dplyr::slice_max(px_entire_med, n = 1)
bot_prix <- kpi |> dplyr::slice_min(px_entire_med, n = 1)
top_pression <- kpi |> dplyr::slice_max(prs_listings_1000hab_dense, n = 1)
bot_pression <- kpi |> dplyr::slice_min(prs_listings_1000hab_dense, n = 1)
top_multi <- kpi |> dplyr::slice_max(cr_offre_1plus, n = 1)
bot_multi <- kpi |> dplyr::slice_min(cr_offre_1plus, n = 1)
top_longterm <- kpi |> dplyr::slice_max(str_minnuits30_pct, n = 1)
bot_longterm <- kpi |> dplyr::slice_min(str_minnuits30_pct, n = 1)
top_offre10 <- kpi |> dplyr::slice_max(cr_offre_10plus, n = 1)
top_revenue <- kpi |> dplyr::filter(!is.na(act_revenu_med)) |> dplyr::slice_max(act_revenu_med, n = 1)
# &e

# &s &AA_VARS
.fn <- function(x) format(round(x), big.mark = "\u202f")
.fp <- function(x, d = 0) formatC(round(x, d), format = "f", decimal.mark = ",", digits = d)
.fk <- function(x) fv(x, "k")  # jcn-kmf : 809545 -> "810 K", 8e6 -> "8 M"

n_total <- sum(kpi$vol_n_ann)
n_hosts <- sum(kpi$vol_n_hotes)
n_countries <- length(unique(kpi$country_code))
n_continents <- length(unique(kpi$continent))
w <- kpi$vol_n_ann

# Couverture & representativite du panel vs marche mondial Inside Airbnb
# Source: data/external/bnb-inside-study-cont-world.csv (rapport "Threat of STR to Housing", Q4-2025, 224 territoires)
cov_cw <- tryCatch(
  read.csv(file.path(DATA_EXTERNAL, "bnb-inside-study-cont-world.csv"),
           stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM"),
  error = function(e) NULL)
if (!is.null(cov_cw)) {
  n_world_listings <- cov_cw$n_listings[cov_cw$level == "world"][1]
  n_world_terr     <- cov_cw$n_pays[cov_cw$level == "world"][1]
  cov_tbl <- cov_cw[cov_cw$level == "continent_detail",
                    c("continent_detail", "nos_villes", "part_panel_pct",
                      "share_global_pct", "ecart_repr_pts", "part_nos_annonces_pct")]
  cov_tbl <- cov_tbl[order(-cov_tbl$ecart_repr_pts), ]
} else {
  n_world_listings <- 8347967; n_world_terr <- 224L; cov_tbl <- NULL
}
v_couverture_pct <- round(n_total / n_world_listings * 100, 0)

aa <- list(
  # Perimetre
  n_villes = nrow(kpi),
  n_pays = n_countries,
  n_continents = n_continents,
  n_total = .fn(n_total),            # full : "809 545" (legacy, prose detaillee)
  n_total_km = .fk(n_total),         # jcn-kmf : "810 K" (KPI cards, prose courte)
  n_total_raw = n_total,              # numeric brut pour calculs
  n_hosts = .fn(n_hosts),
  n_hosts_km = .fk(n_hosts),
  n_world_listings_km = .fk(n_world_listings),  # "8 M"
  v_couverture_pct = v_couverture_pct,           # 10 (= 10%)
  n_villes_eur = nrow(kpi_eur),
  n_villes_fra = nrow(kpi_fra),

  # Marche global
  v_prix_med = round(median(kpi$px_entire_med, na.rm = TRUE), 0),
  v_pression_med = .fp(median(kpi$prs_listings_1000hab_dense, na.rm = TRUE), 1),
  v_dispo_med = round(median(kpi$act_cal_ouvert_med, na.rm = TRUE), 0),
  v_entire = round(weighted.mean(kpi$str_entire_pct, w), 0),
  v_multi = round(weighted.mean(kpi$cr_offre_1plus, w), 0),
  v_longterm = round(weighted.mean(kpi$str_minnuits30_pct, w, na.rm = TRUE), 0),
  v_offre5 = round(weighted.mean(kpi$cr_offre_5plus, w), 0),
  v_offre10_med = round(median(kpi$cr_offre_10plus, na.rm = TRUE), 0),
  v_hosts50 = round(weighted.mean(kpi$cr_hosts_offre50_pct, w), 0),

  # Top/bottom prix
  t_top_prix = top_prix$city_fr[1],
  v_top_prix = round(top_prix$px_entire_med[1], 0),
  t_bot_prix = bot_prix$city_fr[1],
  v_bot_prix = round(bot_prix$px_entire_med[1], 0),
  v_facteur_prix = .fp(top_prix$px_entire_med[1] / bot_prix$px_entire_med[1], 1),

  # Top/bottom pression
  t_top_pression = top_pression$city_fr[1],
  v_top_pression = .fp(top_pression$prs_listings_1000hab_dense[1], 1),
  t_bot_pression = bot_pression$city_fr[1],
  v_bot_pression = .fp(bot_pression$prs_listings_1000hab_dense[1], 1),
  v_facteur_pression = round(top_pression$prs_listings_1000hab_dense[1] /
    bot_pression$prs_listings_1000hab_dense[1], 0),

  # Évolution Monde 25->26 (agrégat pondéré kpi_world) — volume/structure fiables (pas prix, cf caveat)
  v_ann_evol    = round(as.numeric(kpi_world$vol_n_ann_vevol_2526), 1),      # +2,9 %
  v_host_evol   = round(as.numeric(kpi_world$vol_n_hotes_vevol_2526), 1),    # -0,3 %
  v_entire_evol = round(as.numeric(kpi_world$str_entire_pct_vdifp_2526), 1), # +0,4 pt

  # Top/bottom professionnalisation
  t_top_multi = top_multi$city_fr[1],
  v_top_multi = round(top_multi$cr_offre_1plus[1], 0),
  t_bot_multi = bot_multi$city_fr[1],
  v_bot_multi = round(bot_multi$cr_offre_1plus[1], 0),

  # Longterm / regulation
  t_top_lt = top_longterm$city_fr[1],
  v_top_lt = round(top_longterm$str_minnuits30_pct[1], 0),
  t_bot_lt = bot_longterm$city_fr[1],
  v_bot_lt = .fp(bot_longterm$str_minnuits30_pct[1], 1),
  n_longterm_30plus = sum(kpi$str_minnuits30_pct > 30, na.rm = TRUE),
  v_am_med_longterm = .fp(median(kpi_am$str_minnuits30_pct, na.rm = TRUE), 1),
  v_eur_med_longterm = .fp(median(kpi_eur$str_minnuits30_pct, na.rm = TRUE), 1),

  # Revenue
  t_top_rev = top_revenue$city_fr[1],
  v_top_rev = .fn(top_revenue$act_revenu_med[1]),
  v_top_rev_km = .fk(top_revenue$act_revenu_med[1]),

  # France
  n_fra = .fn(sum(kpi_fra$vol_n_ann)),
  n_fra_km = .fk(sum(kpi_fra$vol_n_ann)),
  v_paris_prix = round(paris$px_entire_med, 0),
  v_paris_pression = .fp(paris$prs_listings_1000hab_dense, 1),
  v_paris_multi = round(paris$cr_offre_1plus, 0),
  v_bab_pression = .fp(bab$prs_listings_1000hab_dense, 1),

  # Moyennes ref Europe
  v_avg_eur_prix = round(avg_eur_prix, 0),
  v_avg_eur_pression = .fp(avg_eur_pression, 1),
  v_avg_eur_multi = round(avg_eur_multi, 0),

  # Europe
  v_eur_pct = round(sum(kpi_eur$vol_n_ann) / n_total * 100, 0),
  v_eur_med_pression = .fp(median(kpi_eur$prs_listings_1000hab_dense, na.rm = TRUE), 1),

  # Part Amérique du Nord (kpi-list cadrage P2)
  v_nam_pct = round(sum(kpi$vol_n_ann[kpi$continent_detail == "North America"], na.rm = TRUE) / n_total * 100, 0),
  # Top 3 villes par volume (libellés FR)
  t_top3_villes = paste(kpi$city_fr[order(-kpi$vol_n_ann)][1:3], collapse = ", ")
)

message(sprintf(">>> _data-load.R v3 : %d villes (scope city), %d pays, %d variables aa",
  aa$n_villes, aa$n_pays, length(aa)))
# &e

# Representativite du panel -> aa$cov pour la prose methode + P1.
# BRUT A BRUT (260820) : le stock mondial Inside Airbnb n'est PAS nettoye -> on lui oppose nos
# volumes bruts (sp08c-volumes-bruts-panel-260820.py), pas vol_n_ann filtre. Sinon on compare deux
# definitions et la couverture est sous-estimee (11 % au lieu de 12,5 %). Fallback = ancien calcul.
.brut_cw <- tryCatch(
  read.csv(file.path(DATA_INTERIM, "panel-volumes-bruts-2606.csv"),
           encoding = "UTF-8", fileEncoding = "UTF-8-BOM"),
  error = function(e) NULL)

if (!is.null(cov_cw)) {
  .cd <- function(g, col) cov_cw[[col]][cov_cw$level == "continent_detail" & cov_cw$continent_detail == g][1]

  if (!is.null(.brut_cw)) {
    .b   <- setNames(.brut_cw$n_ann_brut, .brut_cw$continent_detail)
    .tb  <- sum(.b)
    .pp  <- function(g) .b[[g]] / .tb * 100                      # part du sous-continent dans le panel BRUT
    .ec  <- function(g) .pp(g) - .cd(g, "share_global_pct")      # ecart de representation (pts)
    .cv  <- function(g) .b[[g]] / .cd(g, "n_listings") * 100     # couverture reelle du sous-continent
    aa$cov <- list(
      monde_pct  = .fp(.tb / n_world_listings * 100, 1),   # .fp = virgule decimale FR
      n_terr     = n_world_terr, world_km = .fk(n_world_listings),
      panel_brut = .fn(.tb),
      eurse_sur  = .fp(abs(.ec("Europe South & East")), 1),
      latam_sous = .fp(abs(.ec("Latin America")), 1),
      asia_cov   = .fp(.cv("Asia"), 1),
      africa_cov = .fp(.cv("Africa"), 1))
  } else {
    aa$cov <- list(
      monde_pct   = v_couverture_pct,                                          # 11 (% offre mondiale observee)
      n_terr      = n_world_terr,                                              # 224 territoires
      world_km    = .fk(n_world_listings),                                     # "8 M"
      panel_brut  = aa$n_total,
      eurse_sur   = .fp(abs(.cd("Europe South & East", "ecart_repr_pts")), 1), # "8,2" pts au-dessus part monde
      latam_sous  = .fp(abs(.cd("Latin America", "ecart_repr_pts")), 1),       # "6,1" pts sous part monde
      asia_cov    = .fp(.cd("Asia", "part_nos_annonces_pct"), 1),              # "7,8" % couverture Asie
      africa_cov  = .fp(.cd("Africa", "part_nos_annonces_pct"), 1))            # "7,0" % couverture Afrique
  }
}

# &s &KPI_EXT - Chargement indicateurs externes (Airbnb 10-K, Eurostat, Adamiak, S&D, Colomb, Lighthouse)
# Source: data/external/kpi-ext-pbnb-adamiaknco-260510.csv
# 50 indicateurs avec usage_partie -> mappe vers intro/P1/P2/P3/P4/P5
ext_raw <- tryCatch(
  read.csv(file.path(DATA_EXTERNAL, "kpi-ext-pbnb-adamiaknco-260510.csv"),
           stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM"),
  error = function(e) NULL)

if (!is.null(ext_raw)) {
  # Helper : recuperer un champ pour une variable externe
  get_ext <- function(var, field = "short") {
    row <- ext_raw[ext_raw$variable == var, ]
    if (nrow(row) == 0) return(NA_character_)
    as.character(row[[field]][1])
  }
  # Filtre par usage_partie : retourne sous-df pour intro/partie_1/.../partie_5
  ext_partie <- function(usage) {
    ext_raw[grepl(usage, ext_raw$usage_partie, fixed = TRUE), ]
  }
  message(sprintf(">>> kpi-ext (adamiak&co) : %d indicateurs externes charges", nrow(ext_raw)))
} else {
  get_ext <- function(var, field = "short") NA_character_
  ext_partie <- function(usage) data.frame()
  message(">>> kpi-ext (adamiak&co) : non charge (CSV absent)")
}

# Variables ext_* pre-computees, accessibles via aa$ext$<nom>
aa$ext <- list(
  # --- Intro / cadrage Airbnb monde (Airbnb 10-K FY2024) ---
  listings_global      = get_ext("ext_listings_global", "short"),        # "5,6M -> 8M ann."
  listings_global_end  = get_ext("ext_listings_global", "value_end"),    # "8000000"
  nights_global        = get_ext("ext_nights_global", "short"),          # "327M -> 491M nuitees"
  revenue_global       = get_ext("ext_revenue_global", "short"),         # "4,8 -> 11,1 Mds USD"
  adr_global           = get_ext("ext_adr_global_airbnb", "short"),      # "116 -> 166 USD/nuit"

  # --- P2 Professionnalisation : Adamiak 2022 (167 pays, donnees 2018-2019) ---
  adam_pro_pct         = get_ext("bnch_adam_pro_pct", "short"),          # "59% pro mondial"
  adam_multihome_pct   = get_ext("bnch_adam_multihome_pct", "short"),    # "41,5% multi-home"
  adam_singlehome_pct  = get_ext("bnch_adam_singlehome_pct", "short"),   # "33,2% single-home"
  adam_multiroom_pct   = get_ext("bnch_adam_multiroom_pct", "short"),    # "17,5% multi-room"
  adam_singleroom_pct  = get_ext("bnch_adam_singleroom_pct", "short"),   # "7,9% single-room"
  adam_growth_18_19    = get_ext("bnch_adam_growth_2018_2019", "short"), # "+22,6% en 1 an"

  # --- P2 cross-villes : S&D 2025 et Colomb PE 2025 ---
  lisbon_sd_multi      = get_ext("bnch_lisbon_sd_multi", "short"),       # "70% multi-loueur Lisbonne"
  prague_eu_multi      = get_ext("bnch_eu_colomb_pragu", "short"),       # "74% multi-host Prague"

  # --- P3 Pression territoriale : Eurostat UE ---
  lcd_eu_nights        = get_ext("ext_lcd_eu_nights", "short"),          # "512 -> 854 M nuitees"
  lcd_share_eu         = get_ext("ext_lcd_share_eu", "short"),           # "28% LCD vs hotel"

  # --- P4 Concurrence vs hotellerie : Lighthouse 2025 ---
  growth_lcd_supply    = get_ext("ext_growth_lcd_supply", "short"),      # "+9% capacite LCD"
  buenos_aires_growth  = get_ext("ext_buenos_aires_growth", "short"),    # "+88% Buenos Aires"
  riyad_growth         = get_ext("ext_riyad_growth", "short")            # "+69% Riyad"
)
# &e

# &e &DATA_LOAD_aaMAIN
