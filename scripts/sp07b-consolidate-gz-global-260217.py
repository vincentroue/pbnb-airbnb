# &s &CONSOLIDATE_GZ_aaMAIN - Consolidation listings.csv.gz pour villes intégrées

# Charge les listings.csv.gz (79 cols) pour toutes les villes intégrées,
# ne garde que ~30 cols utiles, applique le cleaning pipeline, exporte parquet.
# Utilise city-reference-airbnb-260217.csv comme source de vérité.
#
# Usage:
#   python scripts/sp07b-consolidate-gz-global-260217.py [--snapshot 26-06] [--europe-only]
#
# Outputs:
#   data/interim/dblistingfull_<SNAP>_cons_global.parquet  (SNAP: 2506 défaut, 2606 via --snapshot 26-06)
#   data/interim/dblistingfull_<SNAP>_cons_europe.parquet  (si --europe-only)
#
# Fichier: sp07b-consolidate-gz-global-260217.py | dcr: 26-02-17 | dup: 26-07-15

from pathlib import Path
import pandas as pd
import numpy as np
import gzip
import sys

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
RAW_BASE = BASE / "data" / "raw" / "zudb-inside-airbnbbnb"
INTERIM_DIR = BASE / "data" / "interim"
REF_CSV = BASE / "data" / "external" / "city-reference-airbnb-260222.csv"

europe_only = "--europe-only" in sys.argv
scope = "europe" if europe_only else "global"

# Snapshot cible paramétrable : --snapshot 26-06 (défaut 25-06 pour rétrocompat)
SNAPSHOT = "25-06"
for _i, _a in enumerate(sys.argv):
    if _a == "--snapshot" and _i + 1 < len(sys.argv):
        SNAPSHOT = sys.argv[_i + 1]
SNAP_TAG = SNAPSHOT.replace("-", "")  # "26-06" -> "2606"

# Proxy TOTAL {snapshot_cible: {ville: snapshot_substitut}} : ville dont TOUT le snapshot cible est vide/absent
# à la source. On FORCE le snapshot de substitution (même saison), PRIORITAIRE sur le fallback auto.
# Flaggé is_proxy=1 -> exclu de TOUTE l'évolution.
#   - berlin 26-06 : fichier vide (604 o) chez Inside Airbnb -> proxy juin 2025 complet
PROXY_SNAPSHOT = {
    "26-06": {"berlin": "25-06"},
    "25-06": {"buenos-aires": "25-07"},  # BA n'a pas de juin 2025 -> réf juillet 2025 (même saison, hiver austral)
}

# Prix-invalide {snapshot_cible: {villes}} : SEUL le prix est corrompu à la source, le reste (volumes, avis,
# occupation, structure, concentration) est valide en 2026. On GARDE le vrai snapshot cible mais on met
# price / price_eur / estimated_revenue_l365d à NA (flag price_invalid=1) -> exclu de la seule évolution PRIX.
#   - zurich / geneva 26-06 : prix ~0,15/nuit (100% < 10 EUR) ; non-prix 2026 complet (3308 / 2593 annonces)
PRICE_INVALID = {
    "25-06": {"buenos-aires"},                        # ARS : taux contrôlé + hyperinflation -> prix € non fiable
    "26-06": {"zurich", "geneva", "buenos-aires"},
}

# Colonnes à garder (sur ~79 disponibles)
KEEP_COLS = [
    # Identifiants
    "id", "name", "host_id", "host_name",
    # Géo
    "latitude", "longitude", "neighbourhood_cleansed", "neighbourhood_group_cleansed",
    # Logement
    "property_type", "room_type", "accommodates", "bedrooms", "bathrooms_text",
    # Prix et dispo
    "price", "minimum_nights", "maximum_nights",
    "availability_365",
    # Activité
    "number_of_reviews", "number_of_reviews_ltm",
    "reviews_per_month", "first_review", "last_review",
    # Review scores
    "review_scores_rating", "review_scores_accuracy",
    "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location",
    "review_scores_value",
    # Host profil
    "host_is_superhost", "host_response_time", "host_response_rate",
    "host_identity_verified", "host_since",
    "calculated_host_listings_count",
    # Booking
    "instant_bookable", "license",
    # Estimations Inside Airbnb
    "estimated_occupancy_l365d", "estimated_revenue_l365d",
]

# Table de référence
_ref = pd.read_csv(REF_CSV)
_ref_int = _ref[_ref["status"] == "integrated"]
if europe_only:
    _ref_int = _ref_int[_ref_int["continent"] == "Europe"]
CITIES = _ref_int.set_index("city")[
    ["raw_folder", "raw_country", "country_code", "continent", "pop", "housing", "lat", "lon"]
].to_dict("index")

# Taux FX — figé du ref (fallback) + override par taux DATÉ du snapshot du run
_fx = _ref.dropna(subset=["country_code", "fx_eur"]).drop_duplicates("country_code")
FX_EUR = dict(zip(_fx["country_code"], _fx["fx_eur"]))
_CC2CUR = {"GBR": "GBP", "HUN": "HUF", "TUR": "TRY", "DNK": "DKK", "CZE": "CZK", "SWE": "SEK",
           "NOR": "NOK", "CHE": "CHF", "USA": "USD", "CAN": "CAD", "AUS": "AUD", "JPN": "JPY",
           "CHN": "CNY", "TWN": "TWD", "SGP": "SGD", "THA": "THB", "BRA": "BRL", "MEX": "MXN", "ZAF": "ZAR"}
_fxd_path = BASE / "data" / "external" / "fx-by-date-airbnb-260717.csv"
if _fxd_path.exists():
    _fxd = pd.read_csv(_fxd_path)
    _col = f"fx_eur_{SNAP_TAG}"
    if _col in _fxd.columns:
        _cur2fx = dict(zip(_fxd["cur"], _fxd[_col]))
        for _cc, _cur in _CC2CUR.items():
            if _cur in _cur2fx and _cc in FX_EUR:
                FX_EUR[_cc] = round(float(_cur2fx[_cur]), 6)
        print(f"[FX daté] snapshot {SNAP_TAG} : taux BCE appliqués (fallback figé sinon)")

# Filtres par neighbourhood — sous-sélection géographique pour certaines villes
CITY_NBH_FILTERS = {
    "pays-basque": ["Biarritz", "Anglet", "Bayonne"],
}
# &e

# &s &LOAD_GZ
def load_gz_city(city, meta):
    """Charge un gz avec colonnes sélectionnées + métadonnées."""
    city_dir = RAW_BASE / meta["raw_folder"] / meta["raw_country"] / city
    snap_used = SNAPSHOT
    proxies = PROXY_SNAPSHOT.get(SNAPSHOT, {})
    if city in proxies:
        # Ville connue inexploitable pour ce snapshot (vide/corrompue) -> on FORCE le proxy
        snap_used = proxies[city]
        gz_path = city_dir / snap_used / "listings.csv.gz"
        print(f"  [PROXY] {city}: {SNAPSHOT} inexploitable à la source -> proxy {snap_used} (is_proxy=1, pas d'évolution)")
        if not gz_path.exists():
            return None, f"proxy {snap_used} absent"
    else:
        gz_path = city_dir / snap_used / "listings.csv.gz"
        if not gz_path.exists():
            # Fallback : snapshot le plus récent disponible
            snap_dirs = sorted([d.name for d in city_dir.iterdir()
                               if d.is_dir() and (d / "listings.csv.gz").exists()], reverse=True)
            if snap_dirs:
                snap_used = snap_dirs[0]
                gz_path = city_dir / snap_used / "listings.csv.gz"
                print(f"  [FALLBACK] {city}: {SNAPSHOT} absent, utilise {snap_used}")
            else:
                return None, f"pas de gz {SNAPSHOT}"

    # Lire header pour filtrer aux colonnes existantes
    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    cols_present = [c for c in KEEP_COLS if c in header]

    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f, usecols=cols_present, low_memory=False)

    # Parser prix "$135.00" -> float
    if "price" in df.columns:
        df["price"] = df["price"].replace(r'[\$,]', '', regex=True).astype(float)

    # Filtre neighbourhood_group si périmètre restreint
    if city in CITY_NBH_FILTERS:
        keep = CITY_NBH_FILTERS[city]
        # gz utilise neighbourhood_cleansed, pas neighbourhood_group
        # On filtre aussi sur neighbourhood_group si elle existe dans le header
        n_before = len(df)
        if "neighbourhood_group_cleansed" in df.columns:
            df = df[df["neighbourhood_group_cleansed"].isin(keep)]
        elif "neighbourhood_cleansed" in df.columns:
            df = df[df["neighbourhood_cleansed"].isin(keep)]

    # Renommer neighbourhood pour compatibilité downstream (sp08, rapports)
    rename_map = {}
    if "neighbourhood_cleansed" in df.columns:
        rename_map["neighbourhood_cleansed"] = "neighbourhood"
    if "neighbourhood_group_cleansed" in df.columns:
        rename_map["neighbourhood_group_cleansed"] = "neighbourhood_group"
    if rename_map:
        df = df.rename(columns=rename_map)

    # Métadonnées
    df["city"] = city
    df["country_code"] = meta["country_code"]
    df["continent"] = meta["continent"]

    # Traçabilité snapshot (proxy/fallback rendus visibles pour sp08 + évolution)
    df["snapshot_target"] = SNAPSHOT
    df["snapshot_src"] = snap_used
    df["is_proxy"] = np.int8(1 if snap_used != SNAPSHOT else 0)
    # Prix corrompu à la source (Zurich/Geneva) : non-prix 2026 conservé, prix/revenu -> NA
    is_price_invalid = city in PRICE_INVALID.get(SNAPSHOT, set())
    df["price_invalid"] = np.int8(1 if is_price_invalid else 0)

    # Prix EUR
    fx = FX_EUR.get(meta["country_code"], 1.0)
    df["price_eur"] = (df["price"] * fx).round(2)

    if is_price_invalid:
        # prix + revenu inexploitables -> NA (on garde volumes/avis/occupation/structure 2026)
        df["price"] = np.nan
        df["price_eur"] = np.nan
        if "estimated_revenue_l365d" in df.columns:
            df["estimated_revenue_l365d"] = np.nan

    # Flags
    df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(np.int8)
    df["is_multihost"] = (df["calculated_host_listings_count"] > 1).astype(np.int8)
    df["is_longterm"] = (df["minimum_nights"] >= 30).astype(np.int8)

    # Booleans t/f -> int8
    for col in ["host_is_superhost", "host_identity_verified", "instant_bookable"]:
        if col in df.columns:
            df[col] = df[col].map({"t": 1, "f": 0}).astype("Int8")

    # host_response_rate "95%" -> float (certains fichiers ont déjà des float)
    if "host_response_rate" in df.columns:
        if df["host_response_rate"].dtype == object:
            df["host_response_rate"] = (
                df["host_response_rate"].str.rstrip("%").astype(float) / 100
            ).round(3)

    # Population, logements, coordonnées
    df["city_pop"] = meta.get("pop", np.nan)
    df["city_housing"] = meta.get("housing", np.nan)
    df["city_lat"] = meta.get("lat", np.nan)
    df["city_lon"] = meta.get("lon", np.nan)

    return df, None
# &e

# &s &CLEANING
def clean_gz(df, price_invalid=False):
    """Nettoyage : ACTIVITÉ (comptage) = dispo>0 + pas hôtel, INDÉPENDANT du prix.

    Les prix null / hors [10,2000] sont mis à NA (exclus des stats de prix) mais l'annonce
    reste COMPTÉE. Raison : le taux de prix-null change entre 2025 (~21%) et 2026 (~17%) à
    cause du nouveau mécanisme price_quote d'Inside Airbnb -> filtrer sur le prix fausserait
    l'évolution du VOLUME (ex. Nashville +6% réel affiché +43%). La médiane de prix, elle,
    n'utilise que les prix valides (les NA sont ignorés). price_invalid : prix déjà NA (Zurich/Geneva/BA).
    """
    n_before = len(df)
    # ACTIVITÉ = a des jours dispo OU a été réservée sur 12 mois (rattrape les sold-out : dispo=0
    # peut vouloir dire RÉSERVÉ, pas seulement bloqué). Défini 2026-07-18 après audit des biais.
    active = (df["availability_365"] > 0) | (df["number_of_reviews_ltm"] > 0)
    df = df[active & (df["room_type"] != "Hotel room")].copy()
    if not price_invalid:
        bad = df["price_eur"].isna() | (df["price_eur"] < 10) | (df["price_eur"] > 2000)
        df.loc[bad, ["price", "price_eur"]] = np.nan
    n_after = len(df)
    return df, n_before, n_after
# &e

# &s &MAIN
if __name__ == "__main__":
    print("=" * 60)
    print(f"CONSOLIDATION GZ — {scope.upper()} (snapshot {SNAPSHOT})")
    print("=" * 60)
    print(f"Villes cibles: {len(CITIES)}")
    print(f"Colonnes sélectionnées: {len(KEEP_COLS)}")

    all_dfs = []
    errors = []

    for city, meta in sorted(CITIES.items()):
        df, err = load_gz_city(city, meta)
        if err:
            print(f"  [MISS] {city}: {err}")
            errors.append(city)
            continue

        price_invalid = city in PRICE_INVALID.get(SNAPSHOT, set())
        df, n_raw, n_clean = clean_gz(df, price_invalid=price_invalid)
        pct = round(n_clean / n_raw * 100, 1) if n_raw > 0 else 0
        all_dfs.append(df)
        tag = " [PRIX->NA, non-prix 2026 gardé]" if price_invalid else ""
        print(f"  [OK]   {city}: {n_raw:,} -> {n_clean:,} ({pct}%) "
              f"| {meta['country_code']} | {len(df.columns)} cols{tag}")

    if not all_dfs:
        print("\nAucune ville chargée!")
        sys.exit(1)

    print(f"\nConcaténation...")
    df_all = pd.concat(all_dfs, ignore_index=True)

    # Uniformiser types object avant parquet
    for col in df_all.select_dtypes(include=["object"]).columns:
        df_all[col] = df_all[col].astype(str).replace("nan", pd.NA)
        if df_all[col].nunique() < 50:
            df_all[col] = df_all[col].astype("category")

    n_cities = df_all["city"].nunique()
    n_countries = df_all["country_code"].nunique()

    # Export
    out_path = INTERIM_DIR / f"dblistingfull_{SNAP_TAG}_cons_{scope}.parquet"
    df_all.to_parquet(out_path, index=False)
    size_mb = out_path.stat().st_size / 1024 / 1024

    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT")
    print(f"{'=' * 60}")
    print(f"Total: {len(df_all):,} listings nettoyés")
    print(f"Villes: {n_cities} | Pays: {n_countries}")
    print(f"Colonnes: {len(df_all.columns)}")
    print(f"Export: {out_path.name} ({size_mb:.0f} MB)")

    # Villes en proxy total (snapshot réellement lu != cible) -> exclues de TOUTE l'évolution
    if "is_proxy" in df_all.columns and (df_all["is_proxy"] == 1).any():
        prox = (df_all[df_all["is_proxy"] == 1]
                .groupby("city")["snapshot_src"].first().to_dict())
        print(f"\n[PROXY total] {len(prox)} ville(s) (is_proxy=1, exclure de TOUTE l'évolution):")
        for c, s in sorted(prox.items()):
            print(f"    {c}: cible {SNAPSHOT} -> lu {s}")

    # Villes prix-invalide -> non-prix 2026 gardé, prix/revenu NA -> exclues de la seule évolution PRIX
    if "price_invalid" in df_all.columns and (df_all["price_invalid"] == 1).any():
        pinv = sorted(df_all[df_all["price_invalid"] == 1]["city"].unique().tolist())
        print(f"\n[PRIX invalide] {len(pinv)} ville(s) (price_invalid=1, non-prix 2026 gardé, prix->NA): {', '.join(pinv)}")

    if errors:
        print(f"\nManquants ({len(errors)}): {', '.join(errors)}")

    # Stats par continent
    print(f"\n--- Par continent ---")
    stats = df_all.groupby("continent").agg(
        villes=("city", "nunique"),
        listings=("id", "count"),
    ).sort_values("listings", ascending=False)
    print(stats.to_string())

    # Top 15 par volume
    print(f"\n--- Top 15 villes ---")
    top = df_all.groupby(["continent", "country_code", "city"]).agg(
        n=("id", "count"),
        prix_med=("price_eur", "median"),
        rev_med=("review_scores_rating", lambda x: x.dropna().median()),
        pct_super=("host_is_superhost", lambda x: round(x.mean() * 100, 1)),
    ).sort_values("n", ascending=False).head(15)
    print(top.to_string())

    print(f"\nColonnes: {list(df_all.columns)}")
    print("\nDone!")
# &e

# &e &CONSOLIDATE_GZ_aaMAIN
