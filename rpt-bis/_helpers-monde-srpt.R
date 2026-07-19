CONT_COLS <- c("Europe" = col_cyan, "Americas" = col_yellow,
               "Asia-Pacific" = col_spacegray, "Africa" = col_green)

# Helpers format pour inline
.k <- function(x) format(round(x / 1000), big.mark = "\u202f")

# --- log_aa_vars : dump toutes les variables narratives aa$* dans le log JSON ---
# A appeler dans setup APRES claude_log_init() ET source(_data-load.R).
# Resultat : outputs/{nom}_rslt_claude_log.json contient les entrees aa_* en plus
# des plot_*/tbl_* habituelles. Devient source unique de verite pour les chiffres
# dynamiques cites en prose.
log_aa_vars <- function(aa_list, prefix = "aa_") {
  if (!is.list(aa_list)) {
    warning("log_aa_vars: aa_list n'est pas une liste")
    return(invisible(NULL))
  }
  for (nm in names(aa_list)) {
    val <- aa_list[[nm]]
    # Aplatir les sous-listes (ex: aa$ext) en aa_ext_X
    if (is.list(val) && !is.data.frame(val)) {
      for (sub_nm in names(val)) {
        sub_val <- val[[sub_nm]]
        type_str <- class(sub_val)[1]
        tryCatch(
          log_result(paste0(prefix, nm, "_", sub_nm), sub_val,
                     interpret = sprintf("aa$%s$%s [%s]", nm, sub_nm, type_str)),
          error = function(e) NULL)
      }
    } else {
      type_str <- class(val)[1]
      tryCatch(
        log_result(paste0(prefix, nm), val,
                   interpret = sprintf("aa$%s [%s]", nm, type_str)),
        error = function(e) NULL)
    }
  }
  message(sprintf(">>> log_aa_vars : %d variables aa$* dumpees dans le JSON", length(aa_list)))
  invisible(NULL)
}

# --- Continent_detail : 7 groupes, noms courts, couleurs, ordre ---
CD_ORDER <- c("Eur. Sud-Est", "Eur. Ouest-Nord", "Am. du Nord",
              "Am. latine", "Asie", "Oc\u00e9anie", "Afrique")
CD_RECODE <- c("Europe West & North" = "Eur. Ouest-Nord",
               "Europe South & East" = "Eur. Sud-Est",
               "North America" = "Am. du Nord",
               "Latin America" = "Am. latine",
               "Asia" = "Asie", "Oceania" = "Oc\u00e9anie", "Africa" = "Afrique")
CD_COLS <- c("Eur. Ouest-Nord" = "#1696d2", "Eur. Sud-Est" = "#fdbf11",
             "Am. du Nord" = "#ec008b", "Am. latine" = "#55b748",
             "Asie" = "#5c5859", "Oc\u00e9anie" = "#0a4c6a", "Afrique" = "#ca5800")

kpi$cd <- CD_RECODE[kpi$continent_detail]
kpi$cd <- factor(kpi$cd, levels = CD_ORDER)

# --- Helper : tableau m\u00e9dianes par continent_detail ---
# Retourne un data.frame pivot : indicateur | unit\u00e9 | Eur.ON | Eur.SE | ... | Monde
make_cd_table <- function(vars, data = kpi, digits = 1) {
  rows <- lapply(vars, function(v) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry)) entry$short else v
    unt <- if (!is.null(entry)) entry$unit else ""
    meds <- tapply(data[[v]], data$cd, median, na.rm = TRUE)
    monde <- median(data[[v]], na.rm = TRUE)
    row <- c(indicateur = lbl, unite = unt,
             setNames(round(meds[CD_ORDER], digits), CD_ORDER),
             Monde = round(monde, digits))
    as.data.frame(as.list(row), stringsAsFactors = FALSE, check.names = FALSE)
  })
  df <- do.call(rbind, rows)
  # Convertir colonnes num\u00e9riques
  num_cols <- c(CD_ORDER, "Monde")
  for (col in num_cols) df[[col]] <- as.numeric(df[[col]])
  df
}

# --- Helper v2 : make_cd_table_agg utilise kpi_agg (sums/medianes sp08-precomputees) ---
# Source de verite : kpi_agg level="continent_detail" + level="world"
# Avantage vs make_cd_table : evite median(median per ville), retourne SUM pour vols
make_cd_table_agg <- function(vars) {
  rows <- lapply(vars, function(v) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry)) entry$short else v
    unt <- if (!is.null(entry)) entry$unit else ""
    monde <- if (v %in% names(kpi_world)) as.numeric(kpi_world[[v]][1]) else NA_real_

    cd_vals <- setNames(rep(NA_real_, length(CD_ORDER)), CD_ORDER)
    if (v %in% names(kpi_cd_agg)) {
      for (i in seq_len(nrow(kpi_cd_agg))) {
        cd_en <- as.character(kpi_cd_agg$continent_detail[i])
        cd_fr <- CD_RECODE[cd_en]
        if (!is.na(cd_fr) && cd_fr %in% CD_ORDER) {
          cd_vals[cd_fr] <- as.numeric(kpi_cd_agg[[v]][i])
        }
      }
    }
    row <- data.frame(indicateur = lbl, unite = unt,
                       Monde = monde, stringsAsFactors = FALSE, check.names = FALSE)
    for (cn in CD_ORDER) row[[cn]] <- cd_vals[cn]
    row
  })
  do.call(rbind, rows)
}

# --- Helper : gt_cd_table_grad = gt + gradient vs Monde (focus_col) ---
# Monde a gauche sert de reference, gradient bordeaux (au-dessus) / bleu (en-dessous)
# Type auto : "pts" pour % (ecart absolu), "ratio" pour autres (ecart relatif)
gt_cd_table_grad <- function(cd_df) {
  library(gt)
  pct_rows <- which(grepl("%|‰", cd_df$unite))
  ratio_rows <- setdiff(seq_len(nrow(cd_df)), pct_rows)

  tbl <- gt(cd_df) |>
    cols_label(indicateur = "Indicateur", unite = "") |>
    fmt_number(columns = c("Monde", all_of(CD_ORDER)),
               decimals = 1, dec_mark = ",", sep_mark = " ") |>
    tab_style(style = list(cell_text(weight = "bold", color = "#1a2744"),
                            cell_borders(sides = "right", color = "#bbb", weight = px(2))),
              locations = cells_body(columns = "Monde")) |>
    tab_style(style = list(cell_text(weight = "600", size = px(12))),
              locations = cells_body(columns = "indicateur")) |>
    tab_style(style = list(cell_text(size = px(10), color = "#888")),
              locations = cells_body(columns = "unite")) |>
    opt_table_font(font = "Inter, system-ui, sans-serif") |>
    tab_options(table.font.size = px(12),
                column_labels.font.weight = "bold",
                column_labels.font.size = px(11),
                table.width = pct(100),
                table.background.color = "#fff",
                table_body.hlines.color = "#f0f0f0",
                column_labels.background.color = "#f7f9fc",
                column_labels.border.bottom.color = "#bbb",
                column_labels.border.bottom.width = px(1))

  if (length(pct_rows) > 0) {
    tbl <- tbl |> gt_gradient_vs_focus(
      columns = all_of(CD_ORDER), ref_value = "Monde",
      type = "pts", focus_col = "Monde", skip_rows = ratio_rows)
  }
  if (length(ratio_rows) > 0) {
    tbl <- tbl |> gt_gradient_vs_focus(
      columns = all_of(CD_ORDER), ref_value = "Monde",
      type = "ratio", focus_col = "Monde", skip_rows = pct_rows)
  }
  tbl
}

# --- Helper PANEL transpose : format pour gt_panel_transp() (pattern 4e showcase) ---
# Codes ASCII-safe en interne, labels FR via geo_labels au moment du render
CD_TO_CODE <- c("Eur. Sud-Est" = "EurSE", "Eur. Ouest-Nord" = "EurWN",
                "Am. du Nord" = "NAm",   "Am. latine" = "LatAm",
                "Asie" = "Asia",         "Océanie" = "Oceania",
                "Afrique" = "Africa")

# Mapping theme ddict -> (categorie, bloc) — auto-attribution
CATEG_BLOC_FROM_THEME <- list(
  vol   = c("Marche", "Volume"),
  px    = c("Marche", "Prix"),
  str   = c("Offre",  "Structure"),
  cr    = c("Offre",  "Concentration"),
  crt   = c("Offre",  "Concentration"),
  act   = c("Activite", "Performance"),
  actrv = c("Activite", "Qualite"),
  prs   = c("Territoire", "Pression"),
  prsf  = c("Territoire", "Pression"),
  ctx   = c("Contexte", "Contexte"))

auto_categ_bloc <- function(var_id) {
  entry <- dd$indics[[var_id]]
  th <- if (!is.null(entry)) entry$theme else NA
  if (is.na(th) || !th %in% names(CATEG_BLOC_FROM_THEME))
    return(c("Autre", "Autre"))
  CATEG_BLOC_FROM_THEME[[th]]
}

# Construit le panel transpose attendu par gt_panel_transp
make_cd_panel_agg <- function(vars) {
  rows <- lapply(vars, function(v) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry)) entry$short else v
    unt <- if (!is.null(entry)) entry$unit else ""
    cb <- auto_categ_bloc(v)

    monde <- if (v %in% names(kpi_world)) as.numeric(kpi_world[[v]][1]) else NA_real_

    r <- data.frame(categorie = cb[1], bloc = cb[2],
                    indicateur = lbl, unite = unt,
                    var_id = v, world = monde,
                    stringsAsFactors = FALSE, check.names = FALSE)

    for (cd_fr in CD_ORDER) {
      code <- CD_TO_CODE[cd_fr]
      val <- NA_real_
      if (v %in% names(kpi_cd_agg)) {
        idx <- which(CD_RECODE[as.character(kpi_cd_agg$continent_detail)] == cd_fr)
        if (length(idx) == 1) val <- as.numeric(kpi_cd_agg[[v]][idx])
      }
      r[[code]] <- val
    }
    r
  })
  do.call(rbind, rows)
}

# --- Wrapper : gt_panel_transp + gt_color_zscore_byrow (pattern 4e showcase) ---
GEO_LABELS_FR <- c(world = "Monde",
                   EurSE = "Eur. SE", EurWN = "Eur. ON",
                   NAm = "Am. N",     LatAm = "Am. L",
                   Asia = "Asie",     Oceania = "Océanie",
                   Africa = "Afrique")

# --- Helper make_cd_panel_with_ctx : injecte 2 lignes context (Nb villes / Nb pays) ---
# au-dessus du panel data, dans le meme schema (categorie/bloc/indicateur/unite/var_id/world/EurSE/...)
# A utiliser avec gt_cd_panel_zscore(skip_rows = 1:2) pour ne pas colorer les lignes context.
make_cd_panel_with_ctx <- function(vars, data = kpi) {
  panel <- make_cd_panel_agg(vars)

  cd_fr_keys <- c("Eur. Sud-Est", "Eur. Ouest-Nord", "Am. du Nord",
                   "Am. latine", "Asie", "Océanie", "Afrique")
  geo_codes <- c("EurSE", "EurWN", "NAm", "LatAm", "Asia", "Oceania", "Africa")

  build_ctx_row <- function(libelle, fn) {
    # var_id = "" — gt_panel_transp lookupera dd$label("") → NA/"" → garde indicateur
    r <- data.frame(categorie = "", bloc = "", indicateur = libelle,
                    unite = "n", var_id = "",
                    world = fn(data),
                    stringsAsFactors = FALSE, check.names = FALSE)
    for (i in seq_along(cd_fr_keys)) {
      cd_fr <- cd_fr_keys[i]
      code <- geo_codes[i]
      sub <- data[!is.na(data$cd) & data$cd == cd_fr, ]
      r[[code]] <- if (nrow(sub) > 0) fn(sub) else NA_real_
    }
    r
  }

  row_villes <- build_ctx_row("Nb villes", function(d) nrow(d))
  row_pays   <- build_ctx_row("Nb pays",   function(d) length(unique(d$country_code)))

  rbind(row_villes, row_pays, panel)
}

# --- Helper rt_2h_wide : reactable PLEINE LARGEUR avec barres auto + sticky col 1 ---
# Pour le 3e onglet "Tableau detaille par ville" du tabset
# 5-8 cols numeriques avec barres auto via rt_col_var
# Intitulés via dd$medium (vs short dans rt_2h_fill float)
rt_2h_wide <- function(data, vars, label_col = "city_fr",
                       extra_id_cols = c("continent", "country_code"),
                       sort_by = NULL, sort_desc = TRUE,
                       height = 420,
                       label_dd_field = "medium",
                       footnote = NULL) {
  if (!is.null(sort_by) && sort_by %in% names(data)) {
    data <- if (sort_desc) data[order(-data[[sort_by]]), ]
            else            data[order( data[[sort_by]]), ]
  }
  keep_cols <- c(label_col, intersect(extra_id_cols, names(data)), vars)
  d <- data[, keep_cols, drop = FALSE]

  cols <- list()
  cols[[label_col]] <- rt_col_lib(d, label_col, "Ville", indent = FALSE)
  if ("continent" %in% names(d))    cols$continent    <- rt_col_tag("Cont.", w = 65)
  if ("country_code" %in% names(d)) cols$country_code <- rt_col_tag("Pays", w = 45)
  for (v in vars) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry) && !is.null(entry[[label_dd_field]])) entry[[label_dd_field]] else v
    unt <- if (!is.null(entry)) entry$unit else ""
    cols[[v]] <- rt_col_var(d, v, lbl, unit = unt)
  }

  rt_table(d, cols = cols, sticky_cols = 1, height = height,
           footnote = footnote)
}

gt_cd_panel_zscore <- function(panel_df, title = NULL,
                                drop_geos = "Africa",
                                sort_geo_by = "vol_n_ann",
                                skip_rows = NULL,
                                lecture_note = NULL,
                                source_note = NULL) {
  geo_cols_all <- c("EurSE", "EurWN", "NAm", "LatAm", "Asia", "Oceania", "Africa")
  geo_cols_color <- setdiff(geo_cols_all, drop_geos)

  panel_df |>
    gt_panel_transp(
      dd = dd, focus_col = "world",
      sort_geo_by = sort_geo_by,
      drop_geos = drop_geos,
      geo_labels = GEO_LABELS_FR,
      title = title,
      label_field = "medium",   # headers lisibles (vs short) — demande user 260609
      show_categ = FALSE,       # drop row-group categorie (TERRITOIRE/MARCHE...), garde bloc "Theme"
      lecture_note = lecture_note, source_note = source_note) |>
    gt_color_zscore_byrow(
      columns = dplyr::all_of(geo_cols_color),
      skip_rows = skip_rows,
      skip_types = c("stock", "vol"),
      mode = "pastille", pill_palette = "brlight",       # bordeaux/rose clair + bleu (PAS orange) — 260715
      scale = "rank") |>   # rang percentile DANS la ligne (n=6-7 continents → z instable) : 4 couleurs pâle/moyen — user 260716
    # Titre en gras + header colonnes plus haut (demande user 260610)
    gt::tab_style(style = gt::cell_text(weight = "bold", size = gt::px(14), color = "#1a2744"),
                  locations = gt::cells_title(groups = "title")) |>
    gt::tab_options(column_labels.padding = gt::px(9),
                    heading.padding = gt::px(4),
                    heading.align = "left")
}

# --- Helper alternatif legacy : gt avec zscore par ligne (gardé pour AB test) ---
# Pattern de yt-test-helper-zscore-byrow : gt_color_zscore_byrow palette light
# Skip volumes (vol_n_*) car ecarts non comparables en zscore
gt_cd_table_zscore <- function(cd_df) {
  library(gt)
  skip_idx <- which(grepl("^vol|^Volume|annonces|h[oô]tes", cd_df$indicateur, ignore.case = TRUE))

  tbl <- gt(cd_df) |>
    cols_label(indicateur = "Indicateur", unite = "") |>
    fmt_number(columns = c("Monde", all_of(CD_ORDER)),
               decimals = 1, dec_mark = ",", sep_mark = " ") |>
    tab_style(style = list(cell_text(weight = "bold", color = "#1a2744"),
                            cell_borders(sides = "right", color = "#bbb", weight = px(2))),
              locations = cells_body(columns = "Monde")) |>
    tab_style(style = list(cell_text(weight = "600", size = px(12))),
              locations = cells_body(columns = "indicateur")) |>
    tab_style(style = list(cell_text(size = px(10), color = "#888")),
              locations = cells_body(columns = "unite")) |>
    opt_table_font(font = "Inter, system-ui, sans-serif") |>
    tab_options(table.font.size = px(12),
                column_labels.font.weight = "bold",
                column_labels.font.size = px(11),
                table.width = pct(100),
                column_labels.background.color = "#f7f9fc",
                column_labels.border.bottom.color = "#bbb",
                column_labels.border.bottom.width = px(1),
                table_body.hlines.color = "#f0f0f0")

  gt_color_zscore_byrow(tbl,
    columns = all_of(CD_ORDER),
    skip_rows = skip_idx,
    focus_col = "Monde",
    palette = "light")
}

# --- Helper : carte monde geopoint (ggiraph + sf + rnaturalearth) ---
# Lib : rnaturalearth::ne_countries() (sf, déjà installé via mutils ACP)
# CRS : Robinson pour le monde entier, WGS84 (4326) pour zoom Europe
build_world_map <- function(df, size_col = "vol_n_ann",
                             label_col = "city_fr",
                             title = NULL, subtitle = NULL,
                             bbox = NULL, palette = CD_COLS,
                             crs_proj = NULL,
                             label_cities = NULL, label_size = 2.7,
                             color_var = NULL, color_levels = NULL,
                             color_recode = NULL) {
  # color_var : colonne de coloration. NULL (defaut) = sous-continent (retrocompat).
  #   Sinon nom de colonne (ex "cluster") avec palette + color_levels fournis.
  # color_recode : vecteur nomme optionnel pour remapper les valeurs en labels lisibles.
  world_sf <- rnaturalearth::ne_countries(scale = "medium", returnclass = "sf")
  # Contour des TERRES marque (coastline) — pas les frontieres pays (demande user 260609)
  coast_sf <- tryCatch(rnaturalearth::ne_coastline(scale = "medium", returnclass = "sf"),
                       error = function(e) NULL)
  bg_fill <- "#f1efe7"; coast_color <- "#7d7d7d"

  if (is.null(color_var)) {
    df$.cd <- factor(CD_RECODE[df$continent_detail], levels = CD_ORDER)
  } else {
    raw <- as.character(df[[color_var]])
    if (!is.null(color_recode)) raw <- color_recode[raw]
    lev <- if (!is.null(color_levels)) color_levels else sort(unique(raw))
    df$.cd <- factor(raw, levels = lev)
  }
  df$.tooltip <- sprintf("<b>%s</b> (%s)<br>%s annonces",
    df[[label_col]], df$.cd,
    format(round(df[[size_col]]), big.mark = " "))

  p <- ggplot2::ggplot() +
    # Remplissage des terres SANS frontieres internes (color = NA)
    ggplot2::geom_sf(data = world_sf, fill = bg_fill, color = NA)
  # Coastline marquee par-dessus (contour terre/mer uniquement)
  if (!is.null(coast_sf))
    p <- p + ggplot2::geom_sf(data = coast_sf, color = coast_color, linewidth = 0.32)
  p <- p +
    ggiraph::geom_point_interactive(data = df,
      ggplot2::aes(x = lon, y = lat,
                   size = .data[[size_col]],
                   fill = .cd,
                   tooltip = .tooltip, data_id = city_fr),
      shape = 21, alpha = 0.85, stroke = 0.4, color = "#444") +
    ggplot2::scale_fill_manual(values = palette, drop = FALSE, na.value = "#aaa", name = NULL) +
    ggplot2::scale_size_continuous(range = c(1.5, 9), guide = "none") +
    ggplot2::labs(title = title, subtitle = subtitle, x = NULL, y = NULL) +
    ggplot2::theme_void(base_family = .font_family) +
    ggplot2::theme(
      plot.title = ggplot2::element_text(size = 12, face = "bold", color = "#222"),
      plot.subtitle = ggplot2::element_text(size = 10, color = "#666"),
      legend.position = "bottom",
      legend.text = ggplot2::element_text(size = 8),
      legend.key.size = ggplot2::unit(0.45, "cm"))

  # Labels villes : le caller fournit le vecteur exact (label_cities) de city_fr a annoter.
  # World = top 3 par sous-continent hors Europe · Europe = toutes les villes (demande user 260609).
  # stat="sf_coordinates" : labels projetes correctement sous coord_sf (Robinson).
  if (!is.null(label_cities) && length(label_cities) > 0) {
    lab_df <- df[df[[label_col]] %in% label_cities, ]
    if (nrow(lab_df) > 0) {
      lab_sf <- sf::st_as_sf(lab_df, coords = c("lon", "lat"), crs = 4326)
      p <- p + ggrepel::geom_text_repel(data = lab_sf,
        ggplot2::aes(geometry = geometry, label = .data[[label_col]]),
        stat = "sf_coordinates",
        size = label_size, fontface = "bold", color = "#222",
        family = .font_family, segment.color = "#888", segment.size = 0.3,
        min.segment.length = 0, box.padding = 0.4, point.padding = 0.1,
        max.overlaps = Inf, bg.color = "white", bg.r = 0.12)
    }
  }

  if (!is.null(bbox)) {
    p <- p + ggplot2::coord_sf(xlim = bbox[c(1, 3)], ylim = bbox[c(2, 4)],
                                expand = FALSE, crs = sf::st_crs(4326))
  } else if (!is.null(crs_proj)) {
    p <- p + ggplot2::coord_sf(crs = crs_proj)
  } else {
    # Robinson pour le monde — fallback WGS84 si Robinson échoue
    p <- p + ggplot2::coord_sf(crs = "+proj=robin", default_crs = sf::st_crs(4326))
  }
  p
}

# Carte Europe : bbox restrictive [lon_min, lat_min, lon_max, lat_max]
build_europe_map <- function(df, size_col = "vol_n_ann", label_col = "city_fr",
                              title = NULL, subtitle = NULL, palette = CD_COLS,
                              label_cities = NULL, label_size = 2.3) {
  build_world_map(df, size_col, label_col, title, subtitle,
                  bbox = c(-12, 35, 32, 62), palette = palette,
                  label_cities = label_cities, label_size = label_size)
}

# --- Helper : plot_cd_bars_ordered ---
# Small multiples horizontaux par continent_detail
# Ordre : Europe Ouest-Nord → Sud-Est → Am du Nord → Am latine → Asie → Oceanie → Afrique
# Drop continents avec < min_cities villes (Afrique souvent = 1)
plot_cd_bars_ordered <- function(vars, data = kpi, ncol_wrap = 3,
                                  min_cities = 2, drop_levels = TRUE) {
  cd_counts <- table(data$cd)
  keep_cd <- names(cd_counts)[cd_counts >= min_cities]
  ordered_cd <- intersect(CD_ORDER, keep_cd)

  plots_data <- lapply(vars, function(v) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry)) entry$short else v
    meds <- tapply(data[[v]], data$cd, median, na.rm = TRUE)
    d <- data.frame(
      cd = factor(names(meds), levels = rev(ordered_cd)),
      val = as.numeric(meds), var_label = lbl,
      stringsAsFactors = FALSE)
    d <- d[!is.na(d$val) & d$cd %in% ordered_cd, ]
    d
  })
  all_d <- do.call(rbind, plots_data)

  ggplot(all_d, aes(x = val, y = cd, fill = cd)) +
    geom_col(width = 0.6, show.legend = FALSE) +
    geom_text(aes(label = fmt_fr(val, 1)), hjust = -0.1, size = 2.3,
              color = "#555", family = .font_family) +
    scale_fill_manual(values = setNames(CD_COLS[rev(ordered_cd)], rev(ordered_cd))) +
    scale_x_continuous(expand = expansion(mult = c(0, 0.28))) +
    facet_wrap(~ var_label, scales = "free_x", ncol = ncol_wrap) +
    labs(x = NULL, y = NULL) +
    theme_minimal(base_size = 9, base_family = .font_family) +
    theme(
      strip.text = element_text(face = "bold", size = 8.3, color = "#333", hjust = 0),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank(),
      axis.text.y = element_text(size = 8, color = "#444"),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      plot.background = element_rect(fill = "white", color = NA),
      panel.spacing = unit(0.35, "lines"))
}

# --- Helper : plot_cd_bars_agg ---
# Small multiples par continent_detail mais valeurs = AGREGATS sp08 (kpi_cd_agg)
# et non median(par ville). Pour les volumes : SOMME continentale (annonces, hotes).
# Pour les ratios (str_ratio_ann_hote) : ratio des sommes (deja pre-calcule sp08).
# Usage : P1 portrait (volumes) ou tout indicateur dont la SOMME a un sens.
plot_cd_bars_agg <- function(vars, agg = kpi_cd_agg, ncol_wrap = 3, min_cities = 2) {
  cd_counts <- table(kpi$cd)
  keep_cd <- names(cd_counts)[cd_counts >= min_cities]
  ordered_cd <- intersect(CD_ORDER, keep_cd)

  fmt_lbl <- function(vv) vapply(vv, function(v) {
    if (is.na(v)) return("")
    if (abs(v) >= 1000) fv(v, "k") else fmt_fr(v, 1)
  }, character(1))

  plots_data <- lapply(vars, function(v) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry) && !is.null(entry$medium)) entry$medium
           else if (!is.null(entry)) entry$short else v
    vals <- setNames(rep(NA_real_, length(ordered_cd)), ordered_cd)
    if (v %in% names(agg)) {
      for (i in seq_len(nrow(agg))) {
        cd_fr <- CD_RECODE[as.character(agg$continent_detail[i])]
        if (!is.na(cd_fr) && cd_fr %in% ordered_cd) vals[cd_fr] <- as.numeric(agg[[v]][i])
      }
    }
    data.frame(cd = factor(names(vals), levels = rev(ordered_cd)),
               val = as.numeric(vals), var_label = lbl,
               stringsAsFactors = FALSE)
  })
  all_d <- do.call(rbind, plots_data)
  all_d <- all_d[!is.na(all_d$val), ]
  all_d$var_label <- factor(all_d$var_label,
    levels = vapply(vars, function(v) {
      e <- dd$indics[[v]]; if (!is.null(e) && !is.null(e$medium)) e$medium
      else if (!is.null(e)) e$short else v }, character(1)))

  ggplot(all_d, aes(x = val, y = cd, fill = cd)) +
    geom_col(width = 0.6, show.legend = FALSE) +
    geom_text(aes(label = fmt_lbl(val)), hjust = -0.1, size = 2.3,
              color = "#555", family = .font_family) +
    scale_fill_manual(values = setNames(CD_COLS[rev(ordered_cd)], rev(ordered_cd))) +
    scale_x_continuous(expand = expansion(mult = c(0, 0.30))) +
    facet_wrap(~ var_label, scales = "free_x", ncol = ncol_wrap) +
    labs(x = NULL, y = NULL) +
    theme_minimal(base_size = 9, base_family = .font_family) +
    theme(
      strip.text = element_text(face = "bold", size = 8.3, color = "#333", hjust = 0),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank(),
      axis.text.y = element_text(size = 8, color = "#444"),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      plot.background = element_rect(fill = "white", color = NA),
      panel.spacing = unit(0.35, "lines"))
}

# --- Helper : small multiples barres horizontales par continent_detail (legacy) ---
plot_cd_bars <- function(vars, data = kpi, ncol_wrap = 3, bar_height = 3.5) {
  plots_data <- lapply(vars, function(v) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry)) entry$short else v
    meds <- tapply(data[[v]], data$cd, median, na.rm = TRUE)
    d <- data.frame(cd = factor(names(meds), levels = rev(CD_ORDER)),
                    val = as.numeric(meds), var_label = lbl,
                    stringsAsFactors = FALSE)
    d <- d[!is.na(d$val), ]
    d
  })
  all_d <- do.call(rbind, plots_data)

  ggplot(all_d, aes(x = val, y = cd, fill = cd)) +
    geom_col(width = 0.6, show.legend = FALSE) +
    geom_text(aes(label = fmt_fr(val, 1)), hjust = -0.1, size = 2.8,
              color = "#555", family = .font_family) +
    scale_fill_manual(values = setNames(CD_COLS[rev(CD_ORDER)], rev(CD_ORDER))) +
    scale_x_continuous(expand = expansion(mult = c(0, 0.25))) +
    facet_wrap(~ var_label, scales = "free_x", ncol = ncol_wrap) +
    labs(x = NULL, y = NULL) +
    theme_minimal(base_size = 9, base_family = .font_family) +
    theme(
      strip.text = element_text(face = "bold", size = 9, color = "#333"),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank(),
      axis.text.y = element_text(size = 8, color = "#444"),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      plot.background = element_rect(fill = "white", color = NA),
      panel.spacing = unit(0.8, "lines"))
}

# --- Helper : reactable continent_detail pivot (version simple, sans gradient) ---
rt_cd_table <- function(cd_df) {
  cols <- list(
    indicateur = colDef(name = "Indicateur", minWidth = 130,
      style = list(fontWeight = "600", fontSize = "12px")),
    unite = colDef(name = "", width = 50,
      style = list(fontSize = "10px", color = "#999")))
  for (cn in CD_ORDER) {
    cols[[cn]] <- colDef(name = cn, minWidth = 80, align = "right",
      style = function(value) {
        if (is.na(value)) return(list())
        list(fontSize = "12px", color = "#1a2744")
      })
  }
  cols[["Monde"]] <- colDef(name = "Monde", minWidth = 75, align = "right",
    style = list(fontSize = "12px", fontWeight = "700", color = col_cyan,
                 borderLeft = "2px solid #ddd"))
  reactable(cd_df, columns = cols, compact = TRUE, bordered = FALSE,
            pagination = FALSE, striped = TRUE,
            defaultColDef = colDef(align = "right"))
}

# --- Helper : reactable cd avec gradient relatif a la mediane Monde de chaque ligne ---
rt_cd_table_grad <- function(cd_df) {
  cols <- list(
    indicateur = colDef(name = "Indicateur", minWidth = 180,
      style = list(fontWeight = "600", fontSize = "12px")),
    unite = colDef(name = "", width = 45,
      style = list(fontSize = "10px", color = "#999"))
  )
  for (cn in CD_ORDER) {
    cols[[cn]] <- colDef(name = cn, minWidth = 78, align = "right",
      cell = function(value, index) {
        if (is.na(value)) return(htmltools::span(style = "color:#ccc", "—"))
        ref <- as.numeric(cd_df$Monde[index])
        if (is.na(ref) || ref == 0) {
          ratio <- 0
        } else {
          ratio <- (as.numeric(value) - ref) / abs(ref)
        }
        ratio <- max(min(ratio, 1.5), -1.5)
        intensity <- min(abs(ratio) / 0.6, 1)
        if (ratio >= 0) {
          bg <- sprintf("rgba(26, 111, 160, %.2f)", intensity * 0.55)
        } else {
          bg <- sprintf("rgba(202, 88, 0, %.2f)", intensity * 0.55)
        }
        col_txt <- if (intensity > 0.75) "#ffffff" else "#333"
        fw <- if (intensity > 0.5) "600" else "normal"
        txt <- formatC(round(as.numeric(value), 1), format = "f", digits = 1,
                       big.mark = " ", decimal.mark = ",")
        htmltools::div(style = sprintf("background:%s;color:%s;font-weight:%s;padding:4px 6px;border-radius:3px;font-size:12px;text-align:right;",
            bg, col_txt, fw), txt)
      })
  }
  cols[["Monde"]] <- colDef(name = "Monde", minWidth = 78, align = "right",
    style = list(fontSize = "12px", fontWeight = "700", color = col_cyan,
                 borderLeft = "2px solid #ddd"),
    cell = function(value) {
      if (is.na(value)) return(htmltools::span(style = "color:#ccc", "—"))
      formatC(round(as.numeric(value), 1), format = "f", digits = 1,
              big.mark = " ", decimal.mark = ",")
    })
  reactable(cd_df, columns = cols, compact = TRUE, bordered = FALSE,
            pagination = FALSE, striped = FALSE,
            defaultColDef = colDef(align = "right"))
}

# --- Helper : reactable 74 villes float scrollable, 2-3 indic max, sticky col Ville ---
rt_villes_float <- function(data, vars, label_col = "city_fr",
                             sort_by = NULL, height = 400) {
  d <- data[, c(label_col, vars)]
  if (!is.null(sort_by) && sort_by %in% names(d)) {
    d <- d[order(-d[[sort_by]]), ]
  }
  cols <- list()
  cols[[label_col]] <- colDef(name = "Ville", minWidth = 110, sticky = "left",
    style = list(fontWeight = "600", fontSize = "12px",
                 backgroundColor = "#fff", borderRight = "1px solid #eee"))
  for (v in vars) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry)) entry$short else v
    unt <- if (!is.null(entry)) entry$unit else ""
    cols[[v]] <- rt_col_var(d, v, lbl, unit = unt)
  }
  reactable(d, columns = cols, compact = TRUE, bordered = FALSE,
            pagination = FALSE, striped = TRUE,
            height = height, defaultColDef = colDef(align = "right"),
            theme = reactableTheme(
              headerStyle = list(fontSize = "11px", fontWeight = "600")))
}

# --- Helper rt_2h_fill : reactable float droite hauteur fixe + barres auto partout ---
# Usage: dans :::{.float-section} ::: {.graph-droite-50} ... :::
# Toutes les vars numeriques recoivent rt_col_var (barre auto)
# n_cols_max : limite a 2-3 cols pour bonne lisibilite en float
# label_dd_field : "medium" par defaut (vs "short" plus court) — convention v2
rt_2h_fill <- function(data, vars, label_col = "city_fr",
                       sort_by = NULL, sort_desc = TRUE,
                       height = 380, n_max_cities = NULL,
                       label_dd_field = "medium",
                       footnote = NULL) {
  if (!is.null(sort_by) && sort_by %in% names(data)) {
    data <- if (sort_desc) data[order(-data[[sort_by]]), ]
            else            data[order( data[[sort_by]]), ]
  }
  if (!is.null(n_max_cities)) data <- head(data, n_max_cities)

  vars <- head(vars, 3)  # limite 3 cols numeriques (float exige)
  d <- data[, c(label_col, vars), drop = FALSE]

  cols <- list()
  cols[[label_col]] <- colDef(name = "Ville", minWidth = 95, sticky = "left",
    style = list(fontWeight = "600", fontSize = "11.5px",
                 backgroundColor = "#fff", borderRight = "1px solid #eee"))
  for (v in vars) {
    entry <- dd$indics[[v]]
    lbl <- if (!is.null(entry) && !is.null(entry[[label_dd_field]])) entry[[label_dd_field]] else v
    unt <- if (!is.null(entry)) entry$unit else ""
    cols[[v]] <- rt_col_var(d, v, lbl, unit = unt, mw = 78, bw = 22, bh = 8)
  }

  ftnode <- if (!is.null(footnote)) {
    htmltools::div(style = "font-size:9.5px;color:#888;padding:4px 6px 0;border-top:1px solid #eee;margin-top:4px",
                   footnote)
  } else NULL

  tbl <- reactable(d, columns = cols, compact = TRUE, bordered = FALSE,
            pagination = FALSE, striped = TRUE,
            height = height, defaultColDef = colDef(align = "right"),
            theme = reactableTheme(
              headerStyle = list(fontSize = "10.5px", fontWeight = "600",
                                 color = "#555")))
  if (!is.null(ftnode)) htmltools::tagList(tbl, ftnode) else tbl
}

# --- Helper PROJET : pastille couleur sous-continent + ville + code pays ISO3 gris (même ligne) ---
# HTML porté par la VALEUR de la cellule -> survit au reorder interne de rt_topbot_view.
# Aligné à gauche, 1 seule ligne. country = vecteur code pays ISO3 (optionnel, affiché gris).
.lib_pastille_html <- function(city, cd, country = NULL) {
  cd <- as.character(cd)
  col <- ifelse(!is.na(cd) & cd %in% names(CD_COLS), CD_COLS[cd], "#bbb")
  cc <- if (!is.null(country))
    sprintf(' <span style="color:#9a9a9a;font-weight:400">%s</span>', as.character(country))
  else rep("", length(city))
  sprintf(paste0('<span style="display:inline-block;width:9px;height:9px;border-radius:50%%;',
                 'background:%s;margin-right:7px;vertical-align:middle"></span>',
                 '<span style="vertical-align:middle">%s</span>%s'),
          col, city, cc)
}

# --- Helper PROJET .rt_col_evol : colonne ÉVOLUTION SANS barre (260717) ---
# La barre est structurellement inadaptée aux évols serrées autour de 0 : piste grise 28px quasi vide
# (remplissage 0%) → espace mort avant la valeur (rage user). Ici : juste flèche + valeur signée colorée
# (bordeaux hausse / bleu baisse), GRAS si forte variation. Calée à DROITE = alignée avec les colonnes niveau.
.rt_col_evol <- function(data, col, label, unit = "%", mw = 92) {
  vc  <- data[[col]][!is.na(data[[col]])]
  thr <- if (length(vc) > 1) as.numeric(stats::quantile(abs(vc), 0.75, na.rm = TRUE)) else 1
  if (thr < 1e-6) thr <- 1
  cell_fn <- function(value) {
    if (is.na(value)) return(htmltools::span(style = "color:#bbb", "—"))
    up <- value >= 0
    strong <- abs(value) >= thr
    ctxt <- if (up) (if (strong) "#74303f" else "#b07680") else (if (strong) "#26506f" else "#6f93b5")
    tri  <- if (up) "▲" else "▼"
    htmltools::div(
      style = "display:flex;align-items:center;justify-content:flex-end;gap:3px;white-space:nowrap;width:100%",
      htmltools::span(style = sprintf("color:%s;font-size:8px;flex-shrink:0", ctxt), tri),
      htmltools::span(style = sprintf("color:%s;font-size:11.5px;font-weight:%s", ctxt, if (strong) "700" else "400"),
        sub("\\.", ",", sprintf("%+.1f", value))))
  }
  reactable::colDef(name = label, header = hdr_unit2(label, unit),
                    minWidth = mw, maxWidth = 108, cell = cell_fn, align = "right")
}

# --- Helper PROJET .rt_col_vol : colonne VOLUME/comptage en GRIS (260717) ---
# Barre grise + valeur grise (neutre) → distingue les volumes des indicateurs colorés (taux/ratio/évol
# en bordeaux/bleu). Barre = magnitude (percentile P98). Trait médiane vertical comme les autres.
.rt_col_vol <- function(data, col, label, unit = "", mw = 110, bh = 16) {
  vals <- data[[col]][!is.na(data[[col]])]
  max_abs <- if (length(vals) > 1) as.numeric(stats::quantile(abs(vals), 0.98, na.rm = TRUE)) else max(abs(vals), 1)
  if (max_abs < 1e-6) max_abs <- 1
  med_pct <- min(abs(stats::median(vals, na.rm = TRUE)) / max_abs * 100, 100)
  cell_fn <- function(value) {
    if (is.na(value)) return(htmltools::span(style = "color:#bbb", "—"))
    w <- min(abs(value) / max_abs * 100, 100)
    # PAS de trait vertical sur les volumes (user 260718) : le trait médiane n'a de sens que pour les indicateurs comparés.
    htmltools::div(style = "display:flex;align-items:center;gap:4px;white-space:nowrap;width:100%",
      htmltools::div(style = sprintf("position:relative;flex:1;min-width:42px;height:%dpx;background:#f0f0f0;border-radius:2px", bh),
        htmltools::div(style = sprintf("width:%.0f%%;height:100%%;background:#b3b3b3;opacity:0.9;border-radius:2px", w))),
      htmltools::span(style = "color:#6f6f6f;font-size:11px;flex-shrink:0;display:inline-block;min-width:32px;text-align:right",
        fmt_compact(value)))
  }
  reactable::colDef(name = label, header = hdr_unit2(label, unit), minWidth = mw, cell = cell_fn, align = "right")
}

# --- Headers DOUBLE NIVEAU (260717 user) : L1 nom gris centré · L2 unité italique gris clair · évol = ▲ 26/25 % ---
# Sous un GROUPE : L1 = nom (porté par le colGroup), L2 = ces sous-headers. STANDALONE : L1+L2 dans la colonne.
.hdr_lvl_unit <- function(unit) htmltools::div(          # sous-header d'un NIVEAU groupé = juste l'unité
  style = "width:100%;display:block;text-align:center;color:#9a9a9a;font-size:9.5px;font-style:italic;line-height:1.1",
  if (!is.null(unit) && nzchar(unit)) unit else " ")
.hdr_evol <- function(pts = FALSE) htmltools::div(        # sous-header d'une ÉVOL groupée = ▲ 26/25 % (ou pts%)
  style = "width:100%;display:block;text-align:center;color:#8a8a8a;font-size:9.5px;font-style:italic;font-weight:400;line-height:1.1;white-space:nowrap",
  htmltools::HTML(if (pts) "▲ 26/25 pts%" else "▲ 26/25 %"))
.hdr_standalone <- function(label, unit) htmltools::div( # colonne SEULE (sans évol) : nom L1 + unité L2 italique
  style = "text-align:center;line-height:1.15",
  htmltools::div(style = "color:#777;font-weight:400;font-size:10.5px", label),
  if (!is.null(unit) && nzchar(unit)) htmltools::div(style = "color:#9a9a9a;font-size:9.5px;font-style:italic", unit) else NULL)

# --- Helper PROJET rt_topbot_ville : top/bot par ville, SANS col continent ---
# Pastille couleur sous-continent avant la ville (évite débordement à 3 cols).
# 1re col (= sort_col) en rt_col_var rank (écart à moyenne rose▲/bleu▼), autres en rt_col_level.
# Footer auto = médiane Monde. Titre obligatoire (les topbot manquaient de titre).
# d : data.frame avec city_fr + cd + les vars (cd = facteur CD_ORDER, posé sur kpi).
rt_topbot_ville <- function(d, vars, sort_col, title,
                            footnote = NULL, labels = NULL, units = NULL,
                            digits = NULL, n_top_bot = 8, n_middle = NULL, height = 460,   # n_middle=NULL : middle scrollable (top+bot visibles d'emblée)
                            mw_lib = 130, mw_num = 110,
                            country_col = "country_code",
                            footer = TRUE, footer_lib = "Médiane Monde",
                            footer2 = FALSE, footer_lib2 = "Total Monde", agg_row = NULL,
                            group_pairs = FALSE) {   # agg_row = ligne agrégat Monde (total volumes + VRAIE évol pondérée)
  d <- as.data.frame(d)
  country <- if (!is.null(country_col) && country_col %in% names(d)) d[[country_col]] else NULL
  d$.libp <- .lib_pastille_html(d$city_fr, d$cd, country)
  d <- d[, c(".libp", vars), drop = FALSE]
  names(d)[1] <- "lib"

  # group_pairs : détecte les couples (base V, son évol V_vevol_/V_vdifp_/V_vabs_) → 1 groupe = 1 double header.
  # Neutralise l'absence de label ddict pour les _vevol_ (le groupe porte le nom, l'évol = sous-header court).
  # group_pairs : CHAQUE colonne = un groupe (double header UNIFORME). Une évol rejoint le groupe de sa base
  # (V_vevol_/V_vdifp_) ; une colonne seule (ex prix) = son propre groupe → L1 = nom, L2 = UNIQUEMENT l'unité.
  grp_base <- setNames(if (group_pairs) vars else rep(NA_character_, length(vars)), vars)
  if (group_pairs) for (vv in vars) if (.is_variation_col(vv)) {
    base <- sub("_(vevol|vdifp|vabs)_[0-9]+$", "", vv)
    if (base %in% vars) grp_base[vv] <- base
  }

  cols <- list(lib = colDef(
    name = "Villes", minWidth = mw_lib, sticky = "left", html = TRUE, align = "left",
    style = list(fontWeight = "600", fontSize = "12px", textAlign = "left",
                 backgroundColor = "#fff", borderRight = "1px solid #eee"),
    headerStyle = list(fontSize = "11px", fontWeight = "600", textAlign = "left",
                       background = if (group_pairs) "#e8e8e8" else NULL)))   # colore le début (au-dessus de Ville) comme L1
  for (i in seq_along(vars)) {
    v <- vars[i]
    e <- dd$indics[[v]]
    is_var <- .is_variation_col(v)
    med  <- if (!is.null(labels)) labels[i] else if (!is.null(e$medium)) e$medium else v
    unt  <- if (!is.null(units)) units[i] else if (!is.null(e$unit)) e$unit else ""
    dtype <- tryCatch(dd$type(v), error = function(e) NA_character_)
    mw_v  <- if (group_pairs && is_var) 92 else mw_num
    hdr_unt <- if (group_pairs) "" else unt   # groupé : header custom ci-dessous ; sinon hdr_unit2 normal
    cols[[v]] <- if (is_var)
      rt_col_var(d, v, med, unit = hdr_unt, bw = "fill", bh = 13, mw = mw_v, intensity = "rank")
    else if (isTRUE(dtype %in% c("stock", "vol")))
      .rt_col_vol(d, v, med, unit = hdr_unt, mw = mw_v)                # VOLUME → gris
    else
      rt_col_level(d, v, med, unit = hdr_unt, bw = "fill", bh = 13, mw = mw_v)  # taux/ratio/prix → coloré
    if (group_pairs) {
      # HEADER UNIFORME : L2 = UNIQUEMENT l'unité (niveau) ou ▲ 26/25 (évol). Fond gris clair, CENTRÉ.
      unt_h <- if (isTRUE(dtype %in% c("stock", "vol")) && identical(unt, "n")) "vol" else unt  # ddict "n" → "vol" (volumes)
      cols[[v]]$header <- if (is_var) .hdr_evol(grepl("_vdifp_", v)) else .hdr_lvl_unit(unt_h)
      cols[[v]]$align  <- "center"   # header centré (le align="right" de .rt_col_vol empêchait le centrage L2)
      cols[[v]]$headerStyle <- list(background = "#f5f5f5", justifyContent = "center", textAlign = "center")
    }
  }

  # Groupes (double header) : 1 groupe = base + son évol UNIQUEMENT (standalone reste hors groupe).
  # Nom = medium ddict de la base, style gris centré (L1). L2 = les sous-headers ci-dessus.
  col_groups <- NULL
  if (group_pairs) {
    bases <- unique(stats::na.omit(grp_base))
    data_grps <- lapply(bases, function(b) {
      members <- intersect(vars, names(grp_base)[!is.na(grp_base) & grp_base == b])
      gname   <- if (!is.null(dd$indics[[b]]$medium)) dd$indics[[b]]$medium else b
      reactable::colGroup(name = gname, columns = members,   # L1 : gras + fond gris, texte plus clair (user 260718)
        headerStyle = list(color = "#6e6e6e", fontWeight = "600", fontSize = "11px", textAlign = "center", background = "#e8e8e8"))
    })
    # Groupe IDENTITÉ (rang + Ville) : nom vide + fond gris → L1 grise AU-DESSUS de Ville aussi (fini le trou blanc).
    id_grp <- reactable::colGroup(name = "", columns = c(".rank", "lib"),
                headerStyle = list(background = "#e8e8e8"))
    col_groups <- c(list(id_grp), data_grps)
  }

  monde_row <- NULL; monde_row2 <- NULL
  if (footer) {
    monde_row <- list(.rank = "Réf.", lib = footer_lib)
    for (i in seq_along(vars)) {
      v <- vars[i]
      dg <- if (!is.null(digits)) digits[i] else 1
      monde_row[[v]] <- round(median(kpi[[v]], na.rm = TRUE), dg)
    }
    if (footer2) {   # 2e ligne = MONDE agrégat : total volumes + VRAIE évol Monde pondérée (depuis agg_row), pas la médiane villes.
      monde_row2 <- list(.rank = "", lib = footer_lib2)
      for (i in seq_along(vars)) {
        v <- vars[i]
        dg <- if (.is_variation_col(v)) (if (!is.null(digits)) digits[i] else 1) else 0
        monde_row2[[v]] <- if (!is.null(agg_row) && v %in% names(agg_row) && !is.na(agg_row[[v]])) {
          round(as.numeric(agg_row[[v]]), dg)                      # valeur Monde agrégée (total vol OU évol pondérée)
        } else {
          dtp <- tryCatch(dd$type(v), error = function(e) NA_character_)
          if (!.is_variation_col(v) && isTRUE(dtp %in% c("stock", "vol"))) round(sum(kpi[[v]], na.rm = TRUE), 0) else NA
        }
      }
    }
  }

  rt_topbot_view(d, cols = cols, sort_col = sort_col, sort_dir = "desc",
                 n_top_bot = n_top_bot, n_middle = n_middle, height = height, searchable = FALSE,  # n_middle=NULL : middle scrollable
                 full_width = TRUE, footer_row = monde_row, footer_row2 = monde_row2,
                 groups = col_groups,
                 title = title, footnote = footnote)
}
