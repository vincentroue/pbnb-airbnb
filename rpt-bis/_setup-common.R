# &s &SETUP_COMMON_aaMAIN - Setup partagé rapports Airbnb v2 (full R)
# Fichier: _setup-common.R | dcr: 26-04-15
# Usage: source("_setup-common.R") dans le chunk setup de chaque QMD
# Charge: jcn-all (helpers R), ddict, claude-log, palettes projet, sf

# &s &JCN_LOAD - Helpers jcn (toute la stack)
source("C:/Users/vince/hh/pq/PDS/mutils/jrr/jcn-all.R")
source("C:/Users/vince/hh/pq/PDS/mutils/jrr/jcn-ggmapstatic.R")
source("C:/Users/vince/hh/pq/PDS/mutils/jrr/jcn-claude-log.R")
source("C:/Users/vince/hh/pq/PDS/mutils/jrr/jcn-ddict.R")
source("C:/Users/vince/hh/pq/PDS/mutils/jrr/jcn-rpt-kpi.R")

library(sf)
library(ggrepel)
# &e

# &s &PATHS - Chemins projet
BASE <- "C:/Users/vince/hh/pq/PDS/pbnb-airbnb-log-jrr-jpy"
DATA_INTERIM <- file.path(BASE, "data", "interim")
DATA_EXTERNAL <- file.path(BASE, "data", "external")
GPKG_IRIS <- "C:/Users/vince/DBD-datab/TDC-ref/geo-shape-raw/CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2025-01-01/iris.gpkg"
# &e

# &s &DDICT - Dictionnaire indicateurs
dd <- load_ddict(file.path(BASE, "reports", "helpers", "ddict-airbnb.json"))
# &e

# &s &PALETTE_PROJET - Couleurs par ville / palette cartes
CITY_COLORS <- c(
  "Paris" = col_cyan, "Bordeaux" = col_magenta,
  "Lyon" = col_green, "Biarritz\u00b7Anglet\u00b7Bayonne" = col_yellow,
  "London" = col_spacegray, "Rome" = col_orange
)
CITY_ORDER_FRA <- c("Paris", "Biarritz\u00b7Anglet\u00b7Bayonne", "Bordeaux", "Lyon")

# Palette commune beige -> violet fonce (8 bins, identique pour tous les territoires)
PAL_BV8 <- c("#faf6ed", "#fff3b0", "#ffe68a", "#fecc5c",
             "#fd8d3c", "#fc4e2a", "#e31a1c", "#5b1a8c")

# Bins fixes : pression (ann. / 1 000 logements)
BRK_PRESSION <- c(0, 3, 5, 10, 20, 40, 80, 150, Inf)
LBL_PRESSION <- c("< 3", "3-5", "5-10", "10-20", "20-40", "40-80", "80-150", "> 150")

# Bins fixes : prix median logement entier (EUR/nuit)
BRK_PRIX <- c(0, 60, 80, 100, 120, 150, 200, 300, Inf)
LBL_PRIX <- c("< 60", "60-80", "80-100", "100-120", "120-150", "150-200", "200-300", "> 300")
# &e

# &s &FX_EUR - Taux de change vers EUR
FX_EUR <- c(GBP = 1.17, HUF = 0.0026, TRY = 0.028, DKK = 0.134,
            CZK = 0.040, PLN = 0.23, SEK = 0.089, NOK = 0.087,
            RON = 0.20, BGN = 0.51, HRK = 0.13, ISK = 0.0068,
            USD = 0.92, CAD = 0.68, AUD = 0.60, NZD = 0.56,
            JPY = 0.0062, BRL = 0.18, MXN = 0.054, THB = 0.027, CNY = 0.13)
# &e

message(">>> _setup-common.R : jcn-all + ddict + palettes projet OK")
# &e &SETUP_COMMON_aaMAIN
