# &s &DATA_LOAD_FRANCE_aaMAIN - Chargement données France + IRIS géo
# Fichier: _data-load-france.R | dcr: 26-04-30 | dup: 26-06-05
# Usage: source("_data-load-france.R") après _setup-common.R
# Produit: kpi_fr, kpi_fr_city, kpi_fr_arr, kpi_fr_iris, load_iris_geo(),
#          kpi_comp (benchmark Europe 23 villes), naf/nint, aa_fr

# &s &KPI_FRANCE_LOAD - CSV KPI France (sp10)
kpi_fr_all <- read.csv(file.path(DATA_INTERIM, "kpi_france_byterr_2606.csv"),
                        stringsAsFactors = FALSE,
                        colClasses = c(code_iris = "character"))

kpi_fr_ref   <- kpi_fr_all |> dplyr::filter(level %in% c("ref_monde", "ref_europe"))
kpi_fr_pays  <- kpi_fr_all |> dplyr::filter(level == "country") |> dplyr::slice(1)
kpi_fr_city  <- kpi_fr_all |> dplyr::filter(level == "city")
kpi_fr_arr   <- kpi_fr_all |> dplyr::filter(level == "arr")
kpi_fr_iris  <- kpi_fr_all |> dplyr::filter(level == "iris")

# Refs rapides
ref_monde  <- kpi_fr_all |> dplyr::filter(level == "ref_monde") |> dplyr::slice(1)
ref_europe <- kpi_fr_all |> dplyr::filter(level == "ref_europe") |> dplyr::slice(1)

# Labels ville (AVANT les raccourcis : le CSV a un city_fr vide pour les communes
# basques ; on le corrige sur kpi_fr_city d'abord, puis on slice les raccourcis).
CITY_FR_LABELS <- c(paris = "Paris", lyon = "Lyon", bordeaux = "Bordeaux",
                     biarritz = "Biarritz", anglet = "Anglet", bayonne = "Bayonne")
kpi_fr_city$city_fr <- CITY_FR_LABELS[kpi_fr_city$territory]

# Raccourcis villes (héritent du city_fr corrigé)
paris_fr    <- kpi_fr_city |> dplyr::filter(territory == "paris") |> dplyr::slice(1)
lyon_fr     <- kpi_fr_city |> dplyr::filter(territory == "lyon") |> dplyr::slice(1)
bordeaux_fr <- kpi_fr_city |> dplyr::filter(territory == "bordeaux") |> dplyr::slice(1)
biarritz_fr <- kpi_fr_city |> dplyr::filter(territory == "biarritz") |> dplyr::slice(1)
anglet_fr   <- kpi_fr_city |> dplyr::filter(territory == "anglet") |> dplyr::slice(1)
bayonne_fr  <- kpi_fr_city |> dplyr::filter(territory == "bayonne") |> dplyr::slice(1)
# &e


# &s &FMT_NASAFE - Formatters NA-safe (jamais "NA" en prose)
# naf : decimal FR + tiret cadratin si NA/NaN/vide. nint : comptage gros nombre.
naf <- function(x, d = 1, suf = "") {
  if (length(x) == 0 || is.na(x) || is.nan(x)) return("—")
  paste0(fmt_fr(x, d), suf)
}
nint <- function(x) {
  if (length(x) == 0 || is.na(x) || is.nan(x)) return("—")
  format(round(x), big.mark = " ", scientific = FALSE)
}
# &e

# &s &BENCHMARK_EUROPE - 23 villes de 6 pays comparables (CSV global sp08)
# Sert la Partie 1 (France dans l'Europe). scope == city ; pays-basque = agglo BAB.
kpi_global <- read.csv(file.path(DATA_INTERIM, "kpi_global_by_city_2606.csv"),
                        stringsAsFactors = FALSE)
# Périmètre du benchmark : France + 5 voisins d'Europe de l'Ouest retenus pour la taille
# de leur marché et leur proximité économique. Écarte 17 des 40 villes européennes du panel
# monde — dont les plus concentrées (Porto 60,9 %, Prague 60,6 %, Lisbonne 56,8 %) ET les
# moins professionnalisées (Copenhague 5,3 %, Oslo 6,5 %). Le biais est CONSERVATEUR pour
# la thèse "France peu professionnalisée" : médiane concentration 33,2 % ici contre 39,9 %
# sur l'Europe entière, soit un écart France de -9,2 pt qui passerait à -15,9 pt élargi.
# ⚠️ Les sous-titres des figures (23 villes / 6 pays) sont écrits en dur : les revoir si COMP_CC change.
COMP_CC <- c("FRA", "ITA", "DEU", "GBR", "ESP", "NLD")
kpi_comp <- kpi_global |> dplyr::filter(scope == "city", country_code %in% COMP_CC)
kpi_comp$is_fr <- ifelse(kpi_comp$country_code == "FRA", "France", "Autres pays")
kpi_comp_fr <- kpi_comp |> dplyr::filter(country_code == "FRA")
# BAB agglo : pression dense calculee au niveau agglomeration (vs NaN par commune dans byterr)
bab_glob <- kpi_comp |> dplyr::filter(city == "pays-basque") |> dplyr::slice(1)
# &e

# &s &IRIS_GEO - Chargement IRIS géométries (GPKG IGN)

# Patterns IRIS par ville (préfixe code_iris)
IRIS_FILTERS <- list(
  paris       = "code_iris LIKE '75%'",
  lyon        = "code_iris LIKE '6938%'",
  bordeaux    = "SUBSTR(code_iris,1,5) = '33063'",
  bab         = "SUBSTR(code_iris,1,5) IN ('64102','64122','64024')"
)

# Mapping ville pipeline → filtre IRIS
CITY_IRIS_MAP <- c(paris = "paris", lyon = "lyon", bordeaux = "bordeaux",
                    biarritz = "bab", anglet = "bab", bayonne = "bab")

load_iris_geo <- function(city_key) {
  filt <- IRIS_FILTERS[[CITY_IRIS_MAP[city_key] %||% city_key]]
  if (is.null(filt)) stop("Pas de filtre IRIS pour: ", city_key)

  lyr <- sf::st_layers(GPKG_IRIS)$name[1]
  iris_sf <- sf::st_read(GPKG_IRIS, query = sprintf('SELECT * FROM "%s" WHERE %s', lyr, filt),
                          quiet = TRUE)
  # Renommer geom → geometry si nécessaire
  if (!"geometry" %in% names(iris_sf)) sf::st_geometry(iris_sf) <- "geometry"

  # Projeter en Lambert 93 (cartes France)
  if (!is.na(sf::st_crs(iris_sf)) && sf::st_crs(iris_sf)$epsg != 2154) {
    iris_sf <- sf::st_transform(iris_sf, 2154)
  }
  iris_sf <- sf::st_simplify(iris_sf, dTolerance = 5, preserveTopology = TRUE)

  # Jointure KPI IRIS
  # Pour BAB : filtrer par city dans kpi_fr_iris (city = "pays-basque" pour les 3 communes)
  if (city_key %in% c("biarritz", "anglet", "bayonne")) {
    kpi_sub <- kpi_fr_iris |> dplyr::filter(city == "pays-basque")
  } else {
    kpi_sub <- kpi_fr_iris |> dplyr::filter(city == city_key)
  }

  # Supprimer nom_iris du KPI pour éviter doublon avec le GPKG
  iris_sf |>
    dplyr::left_join(
      kpi_sub |> dplyr::select(-dplyr::any_of(c("level", "city", "territory", "nom_iris"))),
      by = "code_iris"
    )
}
# &e

# &s &AA_FR_VARS - Variables narratives inline France

# Toutes les valeurs chiffrees sont pre-formatees en chaines NA-safe (naf/nint)
# pour ne JAMAIS afficher "NA" en prose. Pression basque : dense = NaN par commune
# (denominateur GHS-POP non calcule) -> on narre via /1000 res. principales (prsf).
aa_fr <- list(
  # Périmètre
  n_villes = nrow(kpi_fr_city),
  n_iris   = nrow(kpi_fr_iris),
  n_arr    = nrow(kpi_fr_arr),
  n_total  = nint(sum(kpi_fr_city$vol_n_ann, na.rm = TRUE)),
  n_hosts  = nint(sum(kpi_fr_city$vol_n_hotes, na.rm = TRUE)),

  # Paris
  paris_n        = nint(paris_fr$vol_n_ann),
  paris_prix     = naf(paris_fr$px_entire_med, 0),
  paris_pression = naf(paris_fr$prs_listings_1000hab_dense, 1),  # /1000 hab (existe : 23,1)
  paris_rp       = naf(paris_fr$prsf_listings_1000rp, 1),         # /1000 RP   (46,1)

  # Lyon / Bordeaux (pression dense disponible)
  lyon_n            = nint(lyon_fr$vol_n_ann),
  lyon_pression     = naf(lyon_fr$prs_listings_1000hab_dense, 1),
  bordeaux_n        = nint(bordeaux_fr$vol_n_ann),
  bordeaux_pression = naf(bordeaux_fr$prs_listings_1000hab_dense, 1),

  # Biarritz / BAB — dense = NaN par commune -> narration via /1000 RP + agglo dense
  biarritz_n         = nint(biarritz_fr$vol_n_ann),
  biarritz_prix      = naf(biarritz_fr$px_entire_med, 0),
  biarritz_rp        = naf(biarritz_fr$prsf_listings_1000rp, 1),  # 135,8 (record panel)
  anglet_rp          = naf(anglet_fr$prsf_listings_1000rp, 1),    # 68,2
  bayonne_rp         = naf(bayonne_fr$prsf_listings_1000rp, 1),   # 35,3
  bab_pression_dense = naf(bab_glob$prs_listings_1000hab_dense, 1), # agglo dense : 48,1

  # Refs (dense, existent)
  ref_monde_pression  = naf(ref_monde$prs_listings_1000hab_dense, 1),
  ref_europe_pression = naf(ref_europe$prs_listings_1000hab_dense, 1),
  ref_france_pression = naf(kpi_fr_pays$prs_listings_1000hab_dense, 1),

  # --- Synthèse : agrégats France + position dans le benchmark européen ---
  fr_prix       = naf(kpi_fr_pays$px_entire_med, 0),
  fr_multi      = naf(kpi_fr_pays$cr_offre_1plus, 0),
  fr_entire     = naf(kpi_fr_pays$str_entire_pct, 0),
  fr_revenu     = nint(kpi_fr_pays$act_revenu_med),
  n_eu_bench    = nrow(kpi_comp),
  paris_rank_eu = as.integer(rank(-kpi_comp$vol_n_ann)[kpi_comp$city == "paris"][1]),
  eu_prix_med   = naf(median(kpi_comp$px_entire_med, na.rm = TRUE), 0),
  eu_multi_med  = naf(median(kpi_comp$cr_offre_1plus, na.rm = TRUE), 0)
)

message(sprintf(">>> _data-load-france.R : %d villes, %d arr, %d IRIS, %d variables aa_fr",
  aa_fr$n_villes, aa_fr$n_arr, aa_fr$n_iris, length(aa_fr)))
# &e

# &e &DATA_LOAD_FRANCE_aaMAIN
