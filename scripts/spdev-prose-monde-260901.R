# spdev-prose-monde.R — EXTRACTION PROSE DU RAPPORT MONDE (loop wording rapide, zéro Quarto).
#
# Imprime la prose des sous-rapports monde AVEC LES VALEURS CALCULÉES (inline `r ...` évalués),
# en ~20 s au lieu d'un render complet de plusieurs minutes. But : itérer le wording sans payer
# les 49 chunks du MAIN (dont les cartes ggiraph, obligatoirement en cache:false).
#
# ⚠️ POURQUOI CE SCRIPT DIFFÈRE DE `spdev-prose-extract.R` (ptod/pterr-fiche)
#   Là-bas la prose vit dans 18 FONCTIONS `prose_*()` : le script les appelle, point.
#   Ici elle vit en MARKDOWN avec ~176 inline `r ...` répartis dans les srpt. Il faut donc
#   reconstituer le contexte d'exécution (setup + données + snapshot ACP + chunks de calcul)
#   puis évaluer chaque inline. C'est ce que fait ce script.
#
# CE QU'IL NE FAIT PAS : aucun rendu visuel (cartes, tables, databars). Il valide le TEXTE et
# ses CHIFFRES, pas la mise en page. Le format se valide toujours sur le MAIN rendu.
#
# Usage (depuis la racine du projet OU rpt-bis/ — le script fait son propre setwd) :
#   Rscript scripts/spdev-prose-monde-260901.R                 # défaut : les 3 blocs de la synthèse exécutive
#   Rscript scripts/spdev-prose-monde-260901.R messages        # un seul bloc (nom partiel suffit)
#   Rscript scripts/spdev-prose-monde-260901.R all             # tous les srpt monde
#   Rscript scripts/spdev-prose-monde-260901.R 01 04 08        # plusieurs parties

suppressWarnings(suppressMessages({
  setwd_target <- "C:/Users/vince/hh/pq/PDS/pbnb-airbnb-log-jrr-jpy/rpt-bis"
  if (normalizePath(getwd(), "/") != normalizePath(setwd_target, "/")) setwd(setwd_target)

  source("_setup-common.R")
  source("_data-load.R")
  source("_helpers-monde-srpt.R")

  # Snapshot ACP : indiv_df, cluster_names, aa_n_actives, aa_n_bestk, aa_v_sil… (cités en prose).
  JCN <- "C:/Users/vince/hh/pq/PDS/mutils/jrr"
  source(file.path(JCN, "jcn-dml-acp-plots.R"))
  source(file.path(JCN, "jcn-dml-hcpc-typo.R"))
  invisible(try(list2env(readRDS("data/rsl/acp-bilan-snapshot.rds"), globalenv()), silent = TRUE))
}))

# Chunks LOURDS à ne pas exécuter. Liste VOLONTAIREMENT ÉTROITE : seuls les appels réellement
# coûteux (chargement rnaturalearth, découpe sf, sérialisation SVG ggiraph). Un ggplot ou un
# reactable construit sans être IMPRIMÉ ne coûte presque rien — on les laisse tourner, car leurs
# chunks calculent souvent des `aa$*` cités en prose.
# ⚠️ Piège corrigé le 260901 : la liste large (rt_, gt_, plot_) matchait dans les COMMENTAIRES.
# Un simple « # ... footer rt_topbot_view ... » faisait sauter srpt01-calc-cd-vars, d'où quatre
# `aa$v_volume_*` non définis et des NULL en prose — alors que le rapport rendu était juste.
# D'où le décommentage préalable avant test.
SKIP_RX <- paste("render_girafe", "girafe\\(", "build_world_map", "build_europe_map",
                 "ggsave", "log_map_auto",
                 "gt_cd_panel", "gt_styled", "rt_2h", "rt_topbot", "rt_table",
                 "plot_cd_bars", "make_cd_panel", sep = "|")

# ⚠️ GARDE-FOU : un chunk qui AFFECTE des variables de prose (`aa$x <- …` ou `x <- …`) est
# TOUJOURS exécuté, même s'il contient par ailleurs un appel lourd. Sans cette garde, sauter
# un chunk mixte « calcule PUIS affiche » laisse la prose avec des NULL (cf srpt01-calc-cd-vars).
# ⚠️ Restreint aux `aa$…` : une garde « toute affectation » ne saute plus RIEN (quasi tout chunk
# affecte une variable de travail) — testé, on retombe à 3 min 37. Seules les `aa$*` sont citées
# en prose ; les variables locales des chunks visuels ne le sont pas.
DEFINES_RX <- "aa\\$[A-Za-z0-9_.]+\\s*(<-|=[^=])"

# strip_comments() : retire les commentaires R pour que SKIP_RX ne matche que du CODE réel.
strip_comments <- function(code) {
  paste(sub("#.*$", "", strsplit(code, "\n", fixed = TRUE)[[1]]), collapse = "\n")
}

files_all <- sort(Sys.glob("srpt/_srpt-monde-*.qmd"))
files_all <- files_all[!grepl("OLD", files_all)]

.a <- commandArgs(trailingOnly = TRUE)
sel <- if (!length(.a)) c("synthese", "kpi-synth", "messages") else
       if (identical(.a[1], "all")) "" else .a
files <- if (identical(sel, "")) files_all else
         unique(unlist(lapply(sel, function(s) files_all[grepl(s, files_all, fixed = TRUE)])))
if (!length(files)) { cat("Aucun srpt ne correspond à :", paste(.a, collapse = " "), "\n"); quit(status = 1) }

# eval_inline() : remplace chaque `r expr` par sa valeur. Une expression qui échoue devient
# <<ERR: message>> — visible dans la sortie plutôt que silencieusement vide (comme dans le HTML,
# où une typo `aa$xxx` inexistante rend une chaîne VIDE sans lever d'erreur).
eval_inline <- function(txt) {
  m <- gregexpr("`r [^`]+`", txt)[[1]]
  if (m[1] == -1) return(txt)
  hits <- regmatches(txt, gregexpr("`r [^`]+`", txt))[[1]]
  for (h in unique(hits)) {
    expr <- sub("^`r\\s+", "", sub("`$", "", h))
    val <- tryCatch(paste(format(eval(parse(text = expr), envir = globalenv())), collapse = " "),
                    error = function(e) sprintf("<<ERR: %s>>", conditionMessage(e)))
    txt <- gsub(h, val, txt, fixed = TRUE)
  }
  txt
}

for (f in files) {
  cat("\n", strrep("=", 78), "\n", basename(f), "\n", strrep("=", 78), "\n", sep = "")
  L <- readLines(f, warn = FALSE, encoding = "UTF-8")

  in_chunk <- FALSE; in_cmt <- FALSE; buf <- character(0); n_run <- 0; n_skip <- 0
  for (ln in L) {
    # Commentaires HTML MULTILIGNES : filtrer la seule ligne d'ouverture laissait passer le corps
    # du commentaire, qui s'affichait comme de la prose.
    if (in_cmt) { if (grepl("-->", ln)) in_cmt <- FALSE; next }
    if (grepl("^\\s*<!--", ln) && !grepl("-->", ln)) { in_cmt <- TRUE; next }
    if (!in_chunk && grepl("^```\\{r", ln)) { in_chunk <- TRUE; buf <- character(0); next }
    if (in_chunk && grepl("^```\\s*$", ln)) {
      in_chunk <- FALSE
      code <- paste(buf, collapse = "\n")
      .c <- strip_comments(code)
      if (grepl(SKIP_RX, .c) && !grepl(DEFINES_RX, .c)) { n_skip <- n_skip + 1 } else {
        n_run <- n_run + 1
        try(suppressWarnings(suppressMessages(eval(parse(text = code), envir = globalenv()))), silent = TRUE)
      }
      next
    }
    if (in_chunk) { buf <- c(buf, ln); next }

    if (grepl("^<!--", ln) || grepl("^:::", ln) || grepl("^<div", ln)) next   # markup, pas de la prose
    if (!nzchar(trimws(ln))) next

    out <- eval_inline(ln)
    if (grepl("^#", out)) cat("\n", out, "\n", sep = "")                       # heading
    else if (grepl("\\{\\.insight\\}", out)) {
      cat("\n  ▸ ", trimws(gsub("\\{\\.insight\\}|\\[|\\]|\\*\\*", "", out)), "\n", sep = "")
    } else {
      cat(strwrap(gsub("\\*\\*", "", out), width = 96, prefix = "    "), sep = "\n")
    }
  }
  cat(sprintf("\n    [chunks: %d exécutés, %d ignorés (lourds)]\n", n_run, n_skip))
}

cat("\n", strrep("-", 78), "\n",
    "Rappel : ce script valide le TEXTE et ses CHIFFRES, pas la mise en page.\n",
    "Les <<ERR: ...>> signalent un inline cassé (dans le HTML il rendrait une chaîne VIDE).\n", sep = "")
