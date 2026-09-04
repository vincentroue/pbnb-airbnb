# &s &CONFIG_aaMAIN - Configuration ACP+HCPC depuis CSV validation

JCN <- "C:/Users/vince/hh/pq/PDS/mutils/jrr"
source(file.path(JCN, "jcn-all.R"))
source(file.path(JCN, "jcn-dml-acp-plots.R"))
source(file.path(JCN, "jcn-dml-hcpc-typo.R"))
source(file.path(JCN, "jcn-dml-grid-acp.R"))
source(file.path(JCN, "jcn-claude-log.R"))
source(file.path(JCN, "jcn-eda-summary.R"))   # calc_eda_summary pour log_eda_digest
source(file.path(JCN, "jcn-eda-corr.R"))      # calc_corr_diag, calc_eta2_table

LOG_OUT_DIR <- "C:/Users/vince/hh/pq/PDS/pbnb-airbnb-log-jrr-jpy/reports/outputs"
claude_log_init("acpnbk-monde", output_dir = LOG_OUT_DIR)

BASE <- "C:/Users/vince/hh/pq/PDS/pbnb-airbnb-log-jrr-jpy"
DATA_PATH <- file.path(BASE, "data/interim/kpi_global_by_city_2506.csv")
DDICT_CSV <- file.path(BASE, "reports/helpers/ddict-validation-airbnb.csv")

# Lire roles ACP depuis CSV validation (_acp1 = config A, _acp2 = config B)
dd_csv <- read.csv(DDICT_CSV, fileEncoding = "UTF-8-BOM", stringsAsFactors = FALSE)
dd_csv$X_acp1 <- trimws(dd_csv$X_acp1)  # read.csv prefixe _ avec X
dd_csv$X_acp2 <- trimws(dd_csv$X_acp2)

# Helper: extraire qa/qs/ql depuis une colonne
get_roles <- function(df, col) {
  list(
    qa = df$variable[df[[col]] == "qa"],
    qs = df$variable[df[[col]] == "qs"],
    ql = df$variable[df[[col]] == "ql"]
  )
}

roles_A <- get_roles(dd_csv, "X_acp1")
roles_B <- get_roles(dd_csv, "X_acp2")

cat(sprintf("Config A: %d qa, %d qs, %d ql\n", length(roles_A$qa), length(roles_A$qs), length(roles_A$ql)))
cat(sprintf("Config B: %d qa, %d qs, %d ql\n", length(roles_B$qa), length(roles_B$qs), length(roles_B$ql)))

# continent_detail toujours en quali sup
QUALI_SUP_BASE <- "continent_detail"

# Config C: concentration approfondie
roles_C_qa <- c("prs_listings_1000hab_dense","str_entire_pct","str_minnuits30_pct",
                "cr_host_5plus","cr_hosts_offre50_pct","cr_offre_top10host_pct",
                "px_entire_med","actrv_avis_mois")
roles_C_qs <- c("str_cap_pers_med","cr_offre_5plus","act_superhost_pct","actrv_note_glb",
                "vol_n_ann","ctx_ucdb_hdi_latest","ctx_ucdb_gdp_avg_20")

# Config D: Adamiak en active
roles_D_qa <- c("prs_listings_1000hab_dense",
                "crt_ada_multi_home_pct","crt_ada_multi_room_pct",
                "str_minnuits30_pct","px_entire_med","actrv_avis_mois",
                "act_superhost_pct")
roles_D_qs <- c("str_entire_pct","str_cap_pers_med","cr_offre_5plus",
                "crt_ada_single_home_pct","crt_ada_single_room_pct",
                "vol_n_ann","ctx_ucdb_hdi_latest","ctx_ucdb_gdp_avg_20")

# Config E: leger 6 vars
roles_E_qa <- c("prs_listings_1000hab_dense","str_entire_pct","str_minnuits30_pct",
                "cr_offre_5plus","px_entire_med","actrv_avis_mois")
roles_E_qs <- c("str_cap_pers_med","act_cal_ouvert_med","act_reserv_taux",
                "act_superhost_pct","actrv_note_glb","act_revenu_med",
                "vol_n_ann","ctx_ucdb_hdi_latest","ctx_ucdb_gdp_avg_20","ctx_pop_dense")

# Sup communs
QS_ALL <- c("ctx_ucdb_hdi_latest", "ctx_ucdb_temp_mean_latest", "ctx_ucdb_gdp_avg_20",
            "ctx_ucdb_pop_ghsl_20", "ctx_static_gawc_score", "ctx_static_unesco_50km",
            "ctx_pop_dense", "vol_n_ann", "act_revenu_med")
QL_ALL <- c("continent_detail", "is_capital")

# Grille 5 configs
GRID_CONFIGS <- list(
  list(id = "A", actives = roles_A$qa, sup_quanti = QS_ALL,
       sup_quali = QL_ALL,
       k = 4, transform = "none",
       note = "Reference 10 vars brut k=4"),
  list(id = "B", actives = roles_B$qa, sup_quanti = QS_ALL,
       sup_quali = QL_ALL,
       k = 4, transform = c("prs_listings_1000hab_dense", "px_entire_med"),
       note = "Sans touchy, +avis_mois, log prs+px k=4"),
  list(id = "C", actives = roles_C_qa, sup_quanti = QS_ALL,
       sup_quali = QL_ALL,
       k = 4, transform = c("prs_listings_1000hab_dense"),
       note = "Concentration approfondie 8 vars k=4"),
  list(id = "D", actives = roles_D_qa, sup_quanti = QS_ALL,
       sup_quali = QL_ALL,
       k = 4, transform = c("prs_listings_1000hab_dense"),
       note = "Adamiak en active 7 vars k=4"),
  list(id = "E", actives = roles_E_qa, sup_quanti = QS_ALL,
       sup_quali = QL_ALL,
       k = 4, transform = c("prs_listings_1000hab_dense", "px_entire_med"),
       note = "Leger 6 vars, ratio n/p=12 k=4")
)

# Sup quanti et quali communs a toutes les configs
SUP_QS_COMMON <- QS_ALL
SUP_QL_COMMON <- QL_ALL

CONFIG <- list(
  data_path   = DATA_PATH,
  encoding    = "UTF-8-BOM",
  label_col   = "city_fr",
  filter_expr = "scope == 'city'",
  actives     = roles_B$qa,
  sup_quanti  = SUP_QS_COMMON,
  sup_quali   = SUP_QL_COMMON,
  transform   = c("prs_listings_1000hab_dense", "px_entire_med"),
  k           = 4,
  size_col    = "vol_n_ann",
  top_n       = 25,
  selected    = "B",
  run_grid    = TRUE,
  grid_configs = GRID_CONFIGS,

  # Pipeline cleaning |r| >= threshold_drop (Kaiser 1970, MSA min) — données pbnb
  # contiennent 164 paires |r|>0.90 (vrais doublons type cr_host_1plus vs
  # cr_host_single_pct), activation justifiée. force_keep peut protéger des
  # indicateurs métier critiques.
  threshold_drop = 0.90,
  force_keep     = NULL
)
# &e

library(dplyr)
library(FactoMineR)
library(factoextra)
library(cluster)
library(ggplot2)
library(patchwork)
library(reactable)

# &s &COMPUTE_ALL_aaMAIN - Donnees, grille ACP, HCPC

# &s &LOAD_DATA - Chargement + continent_detail
df_raw <- read.csv(CONFIG$data_path, stringsAsFactors = FALSE, fileEncoding = CONFIG$encoding)
if (!is.null(CONFIG$filter_expr) && nzchar(CONFIG$filter_expr)) {
  df <- df_raw %>% filter(eval(parse(text = CONFIG$filter_expr)))
} else {
  df <- df_raw
}

# continent_detail deja dans le CSV (sp08)
df$continent_detail <- factor(df$continent_detail)

# Fallback city_fr = city si manquant (Winnipeg, etc.)
if ("city_fr" %in% names(df)) {
  miss <- is.na(df$city_fr) | df$city_fr == ""
  df$city_fr[miss] <- df$city[miss]
}

# Capital en factor pour sup quali (string "True"/"False"/"" -> booleen -> factor)
if ("is_capital" %in% names(df)) {
  v <- df$is_capital
  is_cap <- ifelse(is.na(v) | v == "" | v == "False", FALSE, TRUE)
  df$is_capital <- factor(is_cap, levels = c(FALSE, TRUE), labels = c("Non-capitale", "Capitale"))
}

df <- df[complete.cases(df[, CONFIG$actives, drop = FALSE]), ]
aa_n_pool <- nrow(df)

# Imputer NA dans les sup quanti par la mediane (PCA refuse les NA en sup)
all_qs <- unique(unlist(lapply(GRID_CONFIGS, function(x) x$sup_quanti)))
for (v in all_qs) {
  if (v %in% names(df) && any(is.na(df[[v]]))) {
    med_val <- median(df[[v]], na.rm = TRUE)
    n_imp <- sum(is.na(df[[v]]))
    df[[v]][is.na(df[[v]])] <- med_val
    cat(sprintf("  Impute %s: %d NA -> mediane %.1f\n", v, n_imp, med_val))
  }
}
# &e

# &s &RUN_ACP - Grid ou single (centralise dans jcn-dml-grid-acp)
acp <- prepare_pca_hcpc(df, CONFIG)
list2env(acp, environment())  # expose pca, hcpc, df_pca, grid
# &e

# &s &METRICS - aa_* inline + scores + sil_obj + size_vec + inert
m <- compute_acp_metrics(pca, hcpc, df = df,
  size_col  = CONFIG$size_col,
  label_col = CONFIG$label_col,
  vars_mah  = CONFIG$actives)
list2env(m, environment())
# &e

# &s &LOG_RESULTS - Export JSON pour analyse posterieure
log_step("SETUP",
         n_villes = aa_n_ind,
         n_actives = aa_n_actives,
         config_selected = CONFIG$selected,
         k = aa_n_bestk,
         transform = paste(CONFIG$transform, collapse = "+"))

# Socle stat global pour Claude — describe + corr + eta² + dump dataset 77 villes
log_eda_digest(df,
  vars       = CONFIG$actives,
  quali_vars = CONFIG$sup_quali,
  label_col  = CONFIG$label_col,
  name_prefix = "eda",
  max_rows_dump = 500L)

# Grid summary (5 configs comparees + variable polluante MSA min)
if (!is.null(grid)) {
  log_result("grid_summary", as.data.frame(grid$summary),
             interpret = sprintf("5 configs testees, config %s retenue (silhouette=%.3f, KMO=%.2f)",
                                 CONFIG$selected, aa_v_sil,
                                 grid$summary$kmo[grid$summary$id == CONFIG$selected]))

  # MSA individuels de la config retenue (identifie la variable polluante)
  msai_vec <- grid$results[[CONFIG$selected]]$msai
  if (!is.null(msai_vec)) {
    log_result("msai_individual", as.list(msai_vec),
      interpret = sprintf("Variable la plus polluante : %s (MSA=%.2f)",
        names(msai_vec)[which.min(msai_vec)], min(msai_vec)))
  }

  # Bench k_alt par config (silent si aucune config n'a de k_alt)
  log_k_alt_grid(grid$results)
}

# ACP : contributions et eigenvalues
log_acp_results(pca)
log_hcpc_results(hcpc, pca)

# Profil clusters par variable active (z-score)
profil_df <- typo_profil(hcpc, CONFIG$actives)
log_result("clusters_profil", profil_df,
           interpret = sprintf("Profil %d clusters sur %d variables actives", aa_n_bestk, length(CONFIG$actives)))

# Coordonnees individus + cluster
indiv_df <- data.frame(
  city_fr = rownames(pca$ind$coord),
  cluster = as.character(hcpc$data.clust$clust),
  dim1 = round(pca$ind$coord[, 1], 3),
  dim2 = round(pca$ind$coord[, 2], 3),
  dim3 = round(pca$ind$coord[, 3], 3),
  silhouette = round(scores$silhouette, 3),
  voisin = scores$voisin,
  mahalanobis = round(scores$mahalanobis, 2),
  stringsAsFactors = FALSE
)
# Joindre meta (continent_detail, country, pop, vol_n_ann)
meta_cols <- c("country_code","continent","continent_detail","is_capital","ctx_pop_dense","vol_n_ann")
meta_cols <- meta_cols[meta_cols %in% names(df)]
df_meta <- df[match(indiv_df$city_fr, df[[CONFIG$label_col]]), c(CONFIG$label_col, meta_cols), drop = FALSE]
names(df_meta)[1] <- "city_fr"
indiv_df <- merge(indiv_df, df_meta, by = "city_fr", all.x = TRUE, sort = FALSE)
log_result("indiv_clusters", indiv_df,
           interpret = sprintf("%d villes avec coordonnees ACP + cluster + meta", nrow(indiv_df)))

# Atypiques mahalanobis (top 10)
top_aty <- indiv_df[order(-indiv_df$mahalanobis), ][1:min(10, nrow(indiv_df)), ]
log_result("top_atypiques", top_aty,
           interpret = paste("Top 10 villes atypiques (mahalanobis):",
                             paste(head(top_aty$city_fr, 5), collapse = ", ")))

# Mal classes (silhouette < 0)
mal_classes <- indiv_df[indiv_df$silhouette < 0, ]
if (nrow(mal_classes) > 0) {
  log_result("mal_classes", mal_classes,
             interpret = sprintf("%d villes mal classees (silhouette<0)", nrow(mal_classes)))
}

# Croisement cluster x continent_detail
if ("continent_detail" %in% names(indiv_df)) {
  ct_cont <- as.data.frame.matrix(table(indiv_df$continent_detail, indiv_df$cluster))
  ct_cont$total <- rowSums(ct_cont)
  ct_cont$region <- rownames(ct_cont)
  log_result("crosstab_cluster_continent_detail", ct_cont,
             interpret = "Distribution clusters par sous-region continentale")
}

# Croisement cluster x pays (top pays par cluster)
ct_pays <- as.data.frame(table(indiv_df$country_code, indiv_df$cluster))
names(ct_pays) <- c("country_code", "cluster", "n")
ct_pays <- ct_pays[ct_pays$n > 0, ]
log_result("crosstab_cluster_country", ct_pays,
           interpret = "Distribution clusters par pays")

# Parangons et atypiques HCPC
para_df <- typo_parangons(hcpc, n = 5)
log_result("parangons", para_df,
           interpret = "Parangons (centres) et atypiques par cluster")

# Inertie + qualite globale
log_result("inertie", inert,
           interpret = sprintf("Inertie inter/totale apres consolidation: %.3f",
                               ifelse(!is.na(inert$inertie_inter_apres),
                                      inert$inertie_inter_apres, 0)))

claude_log_save()
# &e

# &e (FIN COMPUTE_ALL_aaMAIN)

ACP_CTX <- "territorial"
options(acp.context = ACP_CTX)

cat(acp_grid_topo_auto_comment(grid$summary, selected = CONFIG$selected, context = ACP_CTX))

render_referentials_table(context = ACP_CTX)









# Ajouter continent_detail au ddict si absent (sup quali commune)
if (!"continent_detail" %in% dd_csv$variable) {
  extra <- dd_csv[1, , drop = FALSE]; extra[1, ] <- NA
  extra$variable <- "continent_detail"; extra$short <- "Continent det."
  extra$theme <- "ctx"
  dd_csv <- rbind(dd_csv, extra)
}
if (!"is_capital" %in% dd_csv$variable) {
  extra <- dd_csv[1, , drop = FALSE]; extra[1, ] <- NA
  extra$variable <- "is_capital"; extra$short <- "Capitale"
  extra$theme <- "ctx"
  dd_csv <- rbind(dd_csv, extra)
}

pivot_df <- build_config_pivot(GRID_CONFIGS, dd_csv,
  theme_col = "theme", var_col = "variable", label_col = "short",
  unit_col  = "unit")
rt_config_pivot(pivot_df, selected = CONFIG$selected,
  show_var = FALSE, unit_col = "unit", legend = TRUE)

plot_screeplot(pca)

plot_biplot_dual(pca, axes = c(1, 2), top_n = CONFIG$top_n,
  show_sup = TRUE, show_cor = TRUE, size_col_data = size_vec,
  interactive = FALSE, title = FALSE)

plot_biplot_dual(pca, axes = c(1, 3), top_n = CONFIG$top_n,
  show_sup = TRUE, show_cor = TRUE, size_col_data = size_vec,
  interactive = FALSE, title = FALSE)

plot_dendro_elbow(hcpc, k = aa_n_bestk)

factoextra::fviz_silhouette(sil_obj, print.summary = FALSE) +
  labs(title = sprintf("Silhouette = %.3f — %d mal classe(s) (%.1f%%)",
    aa_v_sil, aa_n_neg, aa_v_neg_pct)) +
  theme_minimal(base_size = 11) +
  theme(plot.title = element_text(size = 12, face = "bold"))

ind_coords <- pca$ind$coord
shared_ylim <- range(c(ind_coords[,2], ind_coords[,3])) * 1.15
shared_xlim <- range(ind_coords[,1]) * 1.15

p12 <- plot_ind_cluster(pca, hcpc, axes = c(1, 2)) +
  coord_cartesian(xlim = shared_xlim, ylim = shared_ylim)
p13 <- plot_ind_cluster(pca, hcpc, axes = c(1, 3)) +
  coord_cartesian(xlim = shared_xlim, ylim = shared_ylim)
p12 + p13 +
  plot_layout(ncol = 2, guides = "collect") &
  theme(legend.position = "bottom")

typo_vtest_rt(hcpc, cap_z = 2.0, seuil_zscore = 0.3)

cat(typo_summary_text(hcpc))

typo_individus_rt(hcpc, pca, vars = CONFIG$actives,
  label_col = CONFIG$label_col,
  cap_z = 2.0, band = 0.3, page_size = 25, max_rows = 2000)



parangons <- typo_parangons(hcpc, n = 5)
if (nrow(parangons) > 0) {
  parangons %>% filter(type == "paragon") %>%
    select(cluster, individu, distance) %>%
    rt_table(cols = list(
      cluster = colDef(name = "Cl.", width = 50),
      individu = colDef(name = "Ville", minWidth = 180),
      distance = colDef(name = "Distance", width = 100, align = "right",
        cell = function(v) sprintf("%.3f", v))
    ))
}

cat(sprintf("- **%d clusters**, %d villes (%s)\n", aa_n_bestk, aa_n_ind, aa_t_sizes))
cat(sprintf("- Silhouette : **%.3f** (%s)\n", aa_v_sil, aa_t_sil_qual))
cat(sprintf("- Mal classes : %d (%.1f%%)\n", aa_n_neg, aa_v_neg_pct))
if (!is.na(inert$inertie_inter_apres))
  cat(sprintf("- Inertie inter : **%.3f** (gain consolid. %+.1f%%)\n",
    inert$inertie_inter_apres, if (!is.na(inert$gain_consol_pct)) inert$gain_consol_pct else 0))
