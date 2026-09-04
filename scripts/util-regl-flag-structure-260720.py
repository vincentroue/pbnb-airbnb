# &s &REGL_STRUCTURE_aaMAIN - Décompose regl_type (texte libre) en colonnes binaires par mécanisme
# Vocabulaire contrôlé -> filtrable/comptable. Extrait aussi le plafond de nuits (regl_cap_nights).
import pandas as pd, re
from pathlib import Path

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
FLAG = BASE / "data" / "external" / "regl-flag-pbnb-cities-260720.csv"

df = pd.read_csv(FLAG)
t = df["regl_type"].fillna("").astype(str).str.lower()

# Mécanismes -> binaires (tokens contrôlés)
df["regl_registration"] = t.str.contains("registration").astype(int)
df["regl_licence"]      = t.str.contains("licence").astype(int)
df["regl_night_cap"]    = t.str.contains("night-cap").astype(int)
df["regl_primary_res"]  = t.str.contains("primary-residence").astype(int)
df["regl_ban_zone"]     = (t.str.contains("ban") | t.str.contains("moratoire")).astype(int)
df["regl_min_stay30"]   = t.str.contains("min-stay").astype(int)
df["regl_levy"]         = t.str.contains("levy").astype(int)

# Plafond de nuits chiffré, extrait du résumé (dernier nombre avant "nuits/jours/an")
def cap(s):
    s = str(s)
    nums = re.findall(r"(\d+)\s*(?:nuits|jours|j)(?:/an|/année)?", s)
    return int(nums[-1]) if nums else pd.NA  # dernier = souvent le cap courant (ex 120→90)
df["regl_cap_nights"] = df["regl_resume"].map(cap).astype("Int64")

cols = ["city", "city_fr", "continent", "regl_niveau", "regl_echelle", "regl_annee", "regl_enforce",
        "regl_registration", "regl_licence", "regl_night_cap", "regl_cap_nights",
        "regl_primary_res", "regl_ban_zone", "regl_min_stay30", "regl_levy",
        "regl_type", "regl_resume", "regl_source", "regl_confiance",
        "pct_license", "pct_reg_engage", "str_minnuits30_pct", "act_cal_ouvert_med", "vol_n_ann"]
df = df[cols].sort_values(["regl_niveau", "vol_n_ann"], ascending=[False, False])
df.to_csv(FLAG, index=False, encoding="utf-8-sig")

print("Colonnes binaires ajoutées. Comptage par mécanisme (villes) :")
for c in ["regl_registration", "regl_licence", "regl_night_cap", "regl_primary_res", "regl_ban_zone", "regl_min_stay30", "regl_levy"]:
    print(f"  {c:22s}: {int(df[c].sum())}")
print(f"\nPlafond de nuits renseigné : {df['regl_cap_nights'].notna().sum()} villes")
print(df[df.regl_cap_nights.notna()].groupby("regl_cap_nights").size().to_string())
# &e &REGL_STRUCTURE_aaMAIN
