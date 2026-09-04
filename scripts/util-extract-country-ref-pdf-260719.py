# &s &EXTRACT_COUNTRY_REF_aaMAIN - Extraction tableau pays PDF Inside Airbnb (threat report)
#
# Extrait "General Airbnb Indicators by Country or Territory (Oct-Dec 2025)" du rapport
# "The Threat of Short-Term Rentals to Housing" (pages 27-32) -> CSV propre + mapping
# continent selon NOTRE classification (Europe / Americas / Asia-Pacific / Africa +
# continent_detail 7 groupes). Sert de base de reference monde pour apprecier la
# couverture de notre echantillon (76 villes / 31 pays).
#
# Sortie: data/external/airbnb-country-indicators-2025q4.csv (UTF-8 BOM)

import pdfplumber
import pandas as pd
import re
from pathlib import Path
import pycountry_convert as pcc

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
PDF = BASE / "ytest" / "insideairbnb-threat-str-housing-260707.pdf"
KPI = BASE / "data" / "interim" / "kpi_global_by_city_2606.csv"
OUT = BASE / "data" / "external" / "bnb-inside-study-full-country.csv"
OUT_AGG = BASE / "data" / "external" / "bnb-inside-study-cont-world.csv"
OLD = BASE / "data" / "external" / "airbnb-country-indicators-2025q4.csv"  # a supprimer
PAGES = range(27, 33)  # 0-indexed

# &s &MAPPING_CONTINENT
# pycountry_convert -> continent standard ; on replie sur NOTRE schema.
STD2OURS = {
    "Europe": "Europe", "Africa": "Africa",
    "North America": "Americas", "South America": "Americas",
    "Asia": "Asia-Pacific", "Oceania": "Asia-Pacific",
}
# Codes que pycountry_convert ne resout pas -> continent standard force
ISO_FALLBACK = {"TWN": "Asia", "HKG": "Asia", "MAC": "Asia", "XKX": "Europe", "XKO": "Europe",
                "PRI": "North America", "VIR": "North America", "TLS": "Asia",
                "SXM": "North America", "NLY": "North America", "BES": "North America",  # Caraibes
                "ESH": "Africa", "ATA": None}  # Sahara occidental ; Antarctique = sans continent

# continent_detail : Europe West&North (le reste de l'Europe = South&East)
EUR_WN = {"GBR", "IRL", "FRA", "DEU", "NLD", "BEL", "LUX", "AUT", "CHE",
          "DNK", "SWE", "NOR", "FIN", "ISL"}
# Americas -> North America si USA/CAN, sinon Latin America
AMER_NORTH = {"USA", "CAN"}


def to_continent(iso3):
    try:
        std = pcc.convert_continent_code_to_continent_name(
            pcc.country_alpha2_to_continent_code(pcc.country_alpha3_to_country_alpha2(iso3)))
    except Exception:
        std = ISO_FALLBACK.get(iso3)
    return STD2OURS.get(std) if std else None, std


def to_detail(iso3, std):
    if std == "Europe":
        return "Europe West & North" if iso3 in EUR_WN else "Europe South & East"
    if std in ("North America", "South America"):
        return "North America" if iso3 in AMER_NORTH else "Latin America"
    if std == "Asia":
        return "Asia"
    if std == "Oceania":
        return "Oceania"
    if std == "Africa":
        return "Africa"
    return None
# &e

# &s &EXTRACT
def num(s):
    if s is None:
        return None
    s = s.replace(",", "").replace("%", "").strip()
    if s in ("", "-", "N/A"):
        return None
    return float(s)


rows = []
with pdfplumber.open(PDF) as pdf:
    for pg in PAGES:
        for t in pdf.pages[pg].extract_tables():
            for r in t:
                # p.29+ : pdfplumber insere une colonne vide (13 cols) -> retirer les None
                cells = [c for c in r if c is not None]
                if len(cells) == 12 and cells[0].strip().isdigit() and len(cells[1].strip()) == 3:
                    rows.append(cells)

cols = ["rank", "geo_code", "country", "n_listings", "share_global_pct", "n_entire",
        "share_entire_pct", "share_multi_listings_pct", "listings_per_10k_hab", "n_hosts",
        "n_cohosts", "est_nights"]
df = pd.DataFrame(rows, columns=cols)
df["country"] = df["country"].str.replace("\n", " ", regex=False).str.strip()
df["geo_code"] = df["geo_code"].str.strip()
for c in ["rank", "n_listings", "n_entire", "n_hosts", "n_cohosts", "est_nights"]:
    df[c] = df[c].map(num).astype("Int64")
for c in ["share_global_pct", "share_entire_pct", "share_multi_listings_pct", "listings_per_10k_hab"]:
    df[c] = df[c].map(num)

# Mapping continent
conts = df["geo_code"].map(to_continent)
df["continent"] = [c[0] for c in conts]
df["continent_detail"] = [to_detail(iso, c[1]) for iso, c in zip(df["geo_code"], conts)]
# &e

# &s &VALIDATE
assert list(df["rank"]) == list(range(1, len(df) + 1)), "rangs non continus !"
print(f"Pays extraits : {len(df)} (rangs 1..{df['rank'].max()})")
unmapped = df[df["continent"].isna()]
if len(unmapped):
    print("[WARN] continent non mappe :", unmapped[["geo_code", "country"]].values.tolist())

# Reordonner + sauver le FULL country
df = df[["rank", "geo_code", "country", "continent", "continent_detail"] + cols[3:]]
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"-> {OUT.relative_to(BASE)} ({len(df)} pays)")
# &e

# &s &AGGREGATE - version continent + continent_detail + monde
df["_n_multi"] = df["share_multi_listings_pct"].fillna(0) / 100 * df["n_listings"].astype(float)
# pop derivee : listings / (per10k/10000) quand per10k > 0
df["_pop"] = df.apply(lambda r: r["n_listings"] / (r["listings_per_10k_hab"] / 10000)
                      if r["listings_per_10k_hab"] and r["listings_per_10k_hab"] > 0 else None, axis=1)

WORLD_LIST = df["n_listings"].sum()

def agg_group(sub, level, cont=None, detail=None):
    nl = sub["n_listings"].sum()
    pop = sub["_pop"].dropna().sum()
    nl_withpop = sub.loc[sub["_pop"].notna(), "n_listings"].sum()
    return {
        "level": level, "continent": cont, "continent_detail": detail,
        "n_pays": len(sub), "n_listings": int(nl),
        "share_global_pct": round(nl / WORLD_LIST * 100, 2),
        "n_entire": int(sub["n_entire"].sum()),
        "share_entire_pct": round(sub["n_entire"].sum() / nl * 100, 1) if nl else None,
        "share_multi_listings_pct": round(sub["_n_multi"].sum() / nl * 100, 1) if nl else None,
        "listings_per_10k_hab": round(nl_withpop / pop * 10000, 1) if pop else None,
        "n_hosts": int(sub["n_hosts"].sum()), "n_cohosts": int(sub["n_cohosts"].sum()),
        "est_nights": int(sub["est_nights"].sum()), "pop_est": int(pop) if pop else None,
    }

agg = [agg_group(df, "world", "World")]
for c in df.dropna(subset=["continent"]).groupby("continent"):
    agg.append(agg_group(c[1], "continent", cont=c[0]))
for d in df.dropna(subset=["continent_detail"]).groupby("continent_detail"):
    cont0 = d[1]["continent"].iloc[0]
    agg.append(agg_group(d[1], "continent_detail", cont=cont0, detail=d[0]))

agg_df = pd.DataFrame(agg)

# Couverture de notre echantillon (villes/pays vs marche PDF) -> colonnes methode
kpi = pd.read_csv(KPI)
kc = kpi[kpi["scope"] == "city"] if "scope" in kpi.columns else kpi
our_cc = set(kc["country_code"].unique())
df["_sampled"] = df["geo_code"].isin(our_cc)
TOTAL_PANEL = kc["vol_n_ann"].sum()  # total annonces de notre panel


def coverage_row(row):
    if row["level"] == "world":
        mref = pd.Series(True, index=df.index); mkpi = pd.Series(True, index=kc.index)
    elif row["level"] == "continent":
        mref = df["continent"] == row["continent"]; mkpi = kc["continent"] == row["continent"]
    else:
        mref = df["continent_detail"] == row["continent_detail"]; mkpi = kc["continent_detail"] == row["continent_detail"]
    ann = df.loc[mref, "n_listings"].sum()          # marche total (PDF, total publie Q4-25)
    ann_cov = df.loc[mref & df["_sampled"], "n_listings"].sum()  # PDF des pays qu'on touche
    nos_ann = kc.loc[mkpi, "vol_n_ann"].sum()        # NOS annonces actives (juin-26)
    part_panel = round(nos_ann / TOTAL_PANEL * 100, 1)       # poids dans NOTRE panel
    part_monde = row["share_global_pct"]                     # poids dans le marche mondial (PDF)
    return pd.Series({
        "nos_pays": int(kc.loc[mkpi, "country_code"].nunique()),
        "nos_villes": int(kc.loc[mkpi, "city"].nunique()),
        "nos_annonces": int(nos_ann),
        "part_panel_pct": part_panel,                        # repartition de notre echantillon
        # ecart de representativite : >0 = SUR-represente dans le panel, <0 = SOUS-represente
        "ecart_repr_pts": round(part_panel - part_monde, 1),
        # part de marche des PAYS qu'on echantillonne (representativite selection pays)
        "part_marche_pays_pct": round(ann_cov / ann * 100, 1) if ann else None,
        # VRAIE couverture : nos annonces actives / total publie (base != -> sous-estime ~x0.74)
        "part_nos_annonces_pct": round(nos_ann / ann * 100, 1) if ann else None,
    })


agg_df = pd.concat([agg_df, agg_df.apply(coverage_row, axis=1)], axis=1)
agg_df.to_csv(OUT_AGG, index=False, encoding="utf-8-sig")
print(f"-> {OUT_AGG.relative_to(BASE)} ({len(agg_df)} lignes : 1 world + {df['continent'].nunique()} continents + {df['continent_detail'].nunique()} detail)")
# &e

# &s &CLEANUP + controles
if OLD.exists():
    try:
        OLD.unlink()
        print(f"[SUPPR] {OLD.name} (ancienne version 82 pays)")
    except PermissionError:
        print(f"[!] {OLD.name} verrouille (ferme-le) - a supprimer manuellement")
print("\nControle sommes globales :")
print(f"  Annonces monde  : {df['n_listings'].sum():,} | part cumulee {df['share_global_pct'].sum():.1f}%")
print(f"  Nuitees estimees: {df['est_nights'].sum():,}")
print("\n--- Agregat continent ---")
print(agg_df[agg_df.level.isin(["world", "continent"])][
    ["continent", "n_pays", "n_listings", "share_global_pct", "share_entire_pct", "share_multi_listings_pct", "est_nights"]].to_string(index=False))
# &e
# &e &EXTRACT_COUNTRY_REF_aaMAIN
