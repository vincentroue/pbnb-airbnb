# &s &JCN_DDICT_aaMAIN - Helper dictionnaire indicateurs Airbnb

# Lecture et exploitation du ddict-airbnb.json pour labels, thèmes,
# couleurs et renommage de colonnes dans les rapports et graphiques.
# Compatible Quarto (reticulate) et scripts standalone.
#
# Usage:
#   import importlib.util
#   _spec = importlib.util.spec_from_file_location("jcn_ddict", "src/jcn-ddict.py")
#   _mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
#   dd = _mod.DDict("reports/helpers/ddict-airbnb.json")
#   dd.label("prix_med")            # → "Prix médian (tous types)"
#   dd.label("prix_med", "short")   # → "Prix méd. €"
#   dd.rename(["prix_med", "n_listings"])  # → {"prix_med": "Prix médian (tous types)", ...}
#
# Date: 2026-02-23

import json
from pathlib import Path

# &s &DDICT_CLASS - Classe principale DDict

class DDict:
    """Accès structuré au dictionnaire d'indicateurs ddict-airbnb.json."""

    def __init__(self, path):
        """Charge le ddict JSON.

        Args:
            path: chemin vers ddict-airbnb.json (str ou Path)
        """
        with open(Path(path), encoding="utf-8") as f:
            raw = json.load(f)
        self._indicators = raw.get("indicators", {})
        self._themes = raw.get("themes", {})
        self._palettes = raw.get("palettes", {})
        self._meta = raw.get("_meta", {})

        # Index inversé csv_col → ddict_key (pour les noms qui diffèrent)
        self._csv_map = {}
        for key, info in self._indicators.items():
            if key.startswith("_comment"):
                continue
            csv_col = info.get("csv_col")
            if csv_col:
                self._csv_map[csv_col] = key
            self._csv_map[key] = key

    def _resolve(self, col):
        """Résout un nom de colonne CSV vers la clé ddict."""
        return self._csv_map.get(col)

    def get(self, col):
        """Retourne le dict complet d'un indicateur, ou None."""
        key = self._resolve(col)
        if key:
            return self._indicators.get(key)
        return None

    # &s &LABELS - Accès labels (short / medium / long)

    def label(self, col, level="medium"):
        """Retourne le label d'une colonne.

        Args:
            col: nom de colonne CSV ou clé ddict
            level: "short" (≤15 car), "medium" (≤40 car), "long" (≤80 car)

        Returns: str label, ou col inchangé si non trouvé
        """
        info = self.get(col)
        if info:
            return info.get(level, info.get("medium", col))
        return col

    def labels(self, cols, level="medium"):
        """Retourne un dict {col: label} pour une liste de colonnes."""
        return {c: self.label(c, level) for c in cols}

    def rename(self, cols, level="medium"):
        """Alias de labels() — dict de renommage pour df.rename(columns=...)."""
        return self.labels(cols, level)

    # &e

    # &s &THEME - Accès thèmes et regroupement

    def theme(self, col):
        """Retourne le code thème d'une colonne (vol, px, cr, etc.)."""
        info = self.get(col)
        return info.get("theme") if info else None

    def theme_label(self, theme_code):
        """Retourne le label d'un thème (ex: 'px' → 'Prix nuitée')."""
        t = self._themes.get(theme_code, {})
        return t.get("label", theme_code)

    def themes_list(self):
        """Retourne la liste ordonnée des thèmes [(code, label), ...]."""
        return sorted(
            [(k, v.get("label", k)) for k, v in self._themes.items()],
            key=lambda x: self._themes[x[0]].get("order", 99)
        )

    def cols_by_theme(self, theme_code, status="ok"):
        """Retourne les colonnes d'un thème, triées par order.

        Args:
            theme_code: code thème (vol, px, cr, etc.)
            status: filtrer par status ("ok", None pour tous)
        """
        result = []
        for key, info in self._indicators.items():
            if key.startswith("_comment"):
                continue
            if info.get("theme") != theme_code:
                continue
            if status and info.get("status") != status:
                continue
            csv_col = info.get("csv_col", key)
            result.append((info.get("order", 99), csv_col, key))
        result.sort()
        return [csv_col for _, csv_col, _ in result]

    def grouped_cols(self, cols=None, status="ok"):
        """Regroupe des colonnes par thème — utile pour reactable colGroups.

        Args:
            cols: liste de colonnes à filtrer (None = toutes)
            status: filtrer par status

        Returns: list de dicts [{"theme": code, "label": label, "columns": [...]}, ...]
        """
        groups = []
        for code, label in self.themes_list():
            theme_cols = self.cols_by_theme(code, status=status)
            if cols is not None:
                theme_cols = [c for c in theme_cols if c in cols]
            if theme_cols:
                groups.append({
                    "theme": code,
                    "label": label,
                    "columns": theme_cols
                })
        return groups

    # &e

    # &s &TITLES - Génération titres graphiques depuis ddict

    def fig_title(self, col, fig_num=None, title=None, subtitle=None,
                  scope=None, source="Inside Airbnb, juin 2025"):
        """Génère titre et sous-titre pour un graphique à partir du ddict.

        Convention :
        - Ligne 1 (titre) : "Figure N — {title_override ou long label}"
        - Ligne 2 (sous-titre) : "{medium label} — {scope} — Source : {source}"

        Args:
            col: colonne indicateur (pour labels automatiques)
            fig_num: numéro figure (int ou None)
            title: titre personnalisé (si None → long label du ddict)
            subtitle: sous-titre personnalisé (si None → construit auto)
            scope: périmètre ("75 villes", "Europe", etc.)
            source: attribution source

        Returns: dict {"title": str, "subtitle": str}
        """
        info = self.get(col)
        long_label = info.get("long", col) if info else col
        med_label = info.get("medium", col) if info else col

        # Titre : personnalisé ou long label
        t = title if title else long_label
        if fig_num is not None:
            t = f"Figure {fig_num} — {t}"

        # Sous-titre : personnalisé ou auto
        if subtitle is None:
            parts = [med_label]
            if scope:
                parts.append(scope)
            if source:
                parts.append(f"Source : {source}")
            s = " — ".join(parts)
        else:
            s = subtitle

        return {"title": t, "subtitle": s}

    def note_lecture(self, col):
        """Retourne une note de lecture HTML pour un indicateur.

        Format : "Note de lecture : {description}. Unité : {unit}."
        Utilisable sous un graphique avec class="figure-note".
        """
        info = self.get(col)
        if not info:
            return ""
        desc = info.get("description", "")
        unit = info.get("unit", "")
        parts = []
        if desc:
            parts.append(desc)
        if unit:
            parts.append(f"Unité : {unit}")
        return "Note de lecture : " + ". ".join(parts) + "." if parts else ""

    def source_html(self, source="Inside Airbnb, juin 2025", extra=None):
        """Retourne le HTML de source pour sous un graphique.

        Args:
            source: texte source principal
            extra: texte additionnel (ex: "Calculs auteur")

        Returns: str HTML avec class figure-source
        """
        txt = f"Source : {source}"
        if extra:
            txt += f" · {extra}"
        return f'<div class="figure-source">{txt}</div>'

    def note_html(self, col):
        """Retourne le HTML de note de lecture pour sous un graphique."""
        note = self.note_lecture(col)
        if not note:
            return ""
        return f'<div class="figure-note">{note}</div>'

    # &e

    # &s &METADATA - Accès métadonnées indicateurs

    def unit(self, col):
        """Retourne l'unité d'un indicateur (€/nuit, %, n, etc.)."""
        info = self.get(col)
        return info.get("unit", "") if info else ""

    def polarity(self, col):
        """Retourne la polarité (-1 = défavorable, 0 = neutre, 1 = favorable)."""
        info = self.get(col)
        return info.get("polarity", 0) if info else 0

    def source(self, col):
        """Retourne la source (sum, gz, calc, ext)."""
        info = self.get(col)
        return info.get("source", "") if info else ""

    def description(self, col):
        """Retourne la description longue prose."""
        info = self.get(col)
        return info.get("description", "") if info else ""

    def formula(self, col):
        """Retourne la formule de calcul (si dérivé)."""
        info = self.get(col)
        return info.get("formula", "") if info else ""

    def indicator_type(self, col):
        """Retourne le type (stock, pct, ind, prix, ratio)."""
        info = self.get(col)
        return info.get("type", "") if info else ""

    # &e

    # &s &FORMAT - Formatage valeurs selon type/unité

    def format_value(self, col, value):
        """Formate une valeur selon le type et l'unité de l'indicateur.

        Args:
            col: nom de colonne
            value: valeur numérique

        Returns: str formatée (ex: "12.5 %", "135 €", "8 420")
        """
        if value is None or (isinstance(value, float) and value != value):
            return "—"

        info = self.get(col)
        if not info:
            return str(value)

        unit = info.get("unit", "")
        ind_type = info.get("type", "")

        # --- pct : 1 décimale ---
        if ind_type == "pct":
            return f"{value:.1f} %"

        # --- prix : 0 décimale, séparateur milliers pour €/an ---
        elif ind_type == "prix":
            if unit == "€/an":
                return f"{value:,.0f} €".replace(",", " ")
            return f"{value:.0f} €"

        # --- stock : entiers, séparateur milliers ---
        elif ind_type == "stock":
            if unit == "km²":
                return f"{value:.1f} km²"
            elif unit == "j/an":
                return f"{value:.0f} j"
            elif unit == "pers":
                return f"{value:.0f}"
            else:
                # n, hab : entier avec séparateur milliers
                if isinstance(value, float):
                    value = int(value)
                return f"{value:,}".replace(",", " ")

        # --- ind : notes /5 → 2 déc, /mois → 1 déc, reste → 0 déc ---
        elif ind_type == "ind":
            if unit == "/5":
                return f"{value:.2f}"
            elif unit == "/mois":
                return f"{value:.1f}"
            else:
                # ratio, ‰, n/km², j/an → 0 décimale
                return f"{value:.0f}"

        return str(round(value, 1))

    # &e

    # &s &FILTER - Filtrage colonnes par critères multiples

    def filter_cols(self, source=None, theme=None, ind_type=None, status="ok"):
        """Filtre les colonnes par critères.

        Args:
            source: "sum", "gz", "calc", "ext" ou None
            theme: code thème ou None
            ind_type: "stock", "pct", "ind", "prix", "ratio" ou None
            status: "ok", "planned", "deprecated" ou None

        Returns: liste de noms de colonnes CSV triés par theme.order, indicator.order
        """
        result = []
        for key, info in self._indicators.items():
            if key.startswith("_comment"):
                continue
            if status and info.get("status") != status:
                continue
            if source and info.get("source") != source:
                continue
            if theme and info.get("theme") != theme:
                continue
            if ind_type and info.get("type") != ind_type:
                continue

            theme_order = self._themes.get(info.get("theme", ""), {}).get("order", 99)
            csv_col = info.get("csv_col", key)
            result.append((theme_order, info.get("order", 99), csv_col))

        result.sort()
        return [c for _, _, c in result]

    # &e

    # &s &AUDIT - Croisement ddict vs colonnes CSV réelles

    def audit(self, csv_cols):
        """Croise le ddict avec les colonnes réelles d'un CSV.

        Args:
            csv_cols: list de noms de colonnes du CSV

        Returns: dict avec:
            - matched: colonnes présentes des deux côtés
            - csv_only: dans CSV mais pas dans ddict
            - ddict_only: dans ddict mais pas dans CSV
            - name_mismatches: colonnes avec csv_col != ddict_key
        """
        csv_set = set(csv_cols)
        ddict_cols = set()
        mismatches = []

        for key, info in self._indicators.items():
            if key.startswith("_comment"):
                continue
            if info.get("status") == "deprecated":
                continue
            csv_col = info.get("csv_col", key)
            ddict_cols.add(csv_col)
            if csv_col != key:
                mismatches.append({"ddict_key": key, "csv_col": csv_col})

        # Colonnes meta (continent, country_code, city, etc.) à exclure du diff
        meta_cols = {"continent", "country_code", "city", "city_fr", "pop_source", "n_gz"}

        return {
            "matched": sorted(csv_set & ddict_cols),
            "csv_only": sorted((csv_set - ddict_cols) - meta_cols),
            "ddict_only": sorted(ddict_cols - csv_set),
            "name_mismatches": mismatches,
        }

    # &e

    def __repr__(self):
        n = sum(1 for k in self._indicators if not k.startswith("_comment"))
        nt = len(self._themes)
        return f"DDict({n} indicators, {nt} themes)"

# &e

# &s &CONVENIENCE - Fonction raccourci pour chargement rapide

def load_ddict(path=None):
    """Charge le ddict depuis le chemin par défaut ou spécifié.

    Cherche dans l'ordre :
    1. path fourni
    2. reports/helpers/ddict-airbnb.json (depuis CWD)
    3. ../reports/helpers/ddict-airbnb.json (depuis scripts/)
    """
    if path:
        return DDict(path)

    candidates = [
        Path("reports/helpers/ddict-airbnb.json"),
        Path("../reports/helpers/ddict-airbnb.json"),
        Path(__file__).parent.parent / "reports" / "helpers" / "ddict-airbnb.json",
    ]
    for p in candidates:
        if p.exists():
            return DDict(p)

    raise FileNotFoundError("ddict-airbnb.json non trouvé. Spécifier le chemin.")

# &e

# &e
