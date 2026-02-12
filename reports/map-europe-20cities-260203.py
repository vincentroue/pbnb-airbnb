"""
Carte Folium interactive — 20 villes Europe Airbnb
Genere reports/outputs/map-europe-20cities.html
dcr: 26-02-03
"""

# &s CONFIG
from pathlib import Path
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster

BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
DATA_PATH = BASE / "data" / "interim" / "dbsumlistings_2506_cons20city.parquet"
OUT_DIR = BASE / "reports" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FX_EUR = {
    "GBR": 1.17, "HUN": 0.0026, "TUR": 0.028, "DNK": 0.134, "CZE": 0.040,
    "NOR": 0.085, "SWE": 0.087, "CHE": 1.06,
}

COUNTRY_NAMES = {
    "FRA": "France", "GBR": "Royaume-Uni", "ITA": "Italie", "ESP": "Espagne",
    "TUR": "Turquie", "PRT": "Portugal", "GRC": "Grece", "DNK": "Danemark",
    "HUN": "Hongrie", "AUT": "Autriche", "CZE": "Tchequie", "DEU": "Allemagne",
    "NLD": "Pays-Bas", "BEL": "Belgique", "IRL": "Irlande",
}
# &e

# &s LOAD_CLEAN
print("Loading data...")
df = pd.read_parquet(DATA_PATH)

if "price_eur" not in df.columns:
    df["price_eur"] = df.apply(
        lambda r: r["price"] * FX_EUR.get(r["country_code"], 1.0)
        if pd.notna(r["price"]) else None, axis=1
    )

df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(int)
df["is_multihost"] = (df["calculated_host_listings_count"] > 1).astype(int)
df["is_longterm"] = (df["minimum_nights"] >= 30).astype(int)

# Filtre actifs
df = df[df["price"].notna() & (df["availability_365"] > 0)]
df = df[df["room_type"] != "Hotel room"]
df = df[(df["price_eur"] >= 10) & (df["price_eur"] <= 1000)]

print(f"Clean: {len(df):,} listings / {df['city'].nunique()} villes")
# &e

# &s PROFILES
profiles = df.groupby(["country_code", "city"]).agg(
    n=("id", "count"),
    lat=("latitude", "median"),
    lon=("longitude", "median"),
    prix_med=("price_eur", "median"),
    prix_q25=("price_eur", lambda x: x.quantile(0.25)),
    prix_q75=("price_eur", lambda x: x.quantile(0.75)),
    pct_entire=("is_entire_home", "mean"),
    pct_multi=("is_multihost", "mean"),
    pct_longterm=("is_longterm", "mean"),
    n_hosts=("host_id", "nunique"),
    dispo_med=("availability_365", "median"),
    reviews_med=("number_of_reviews", "median"),
).reset_index()

profiles["pct_entire"] = (profiles["pct_entire"] * 100).round(1)
profiles["pct_multi"] = (profiles["pct_multi"] * 100).round(1)
profiles["pct_longterm"] = (profiles["pct_longterm"] * 100).round(1)
profiles["ratio_lh"] = (profiles["n"] / profiles["n_hosts"]).round(2)
profiles["prix_med"] = profiles["prix_med"].round(0)

print(f"\n{'City':<15} {'N':>8} {'Prix':>6} {'Multi%':>7} {'LT%':>6}")
print("-" * 50)
for _, r in profiles.sort_values("n", ascending=False).iterrows():
    print(f"{r['city']:<15} {r['n']:>8,} {r['prix_med']:>6.0f} {r['pct_multi']:>6.1f}% {r['pct_longterm']:>5.1f}%")
# &e

# &s MAP_BUILD
print("\nBuilding Folium map...")

# Centre Europe
m = folium.Map(
    location=[47.5, 12.0],
    zoom_start=5,
    tiles="cartodbpositron",
    width="100%",
    height="100%",
)

# Echelle taille bulles — log scale pour contraste fort London/Paris vs petites villes
max_n = profiles["n"].max()
min_n = profiles["n"].min()
min_r, max_r = 10, 50  # plus grand ecart pour visibilite

# Palette prix (bleu=pas cher -> rouge=cher)
prix_min = profiles["prix_med"].min()
prix_max = profiles["prix_med"].max()

def prix_color(prix):
    """Couleur lineaire bleu -> jaune -> rouge selon prix."""
    t = (prix - prix_min) / (prix_max - prix_min) if prix_max > prix_min else 0.5
    if t < 0.5:
        r = int(50 + 205 * (t * 2))
        g = int(130 + 125 * (t * 2))
        b = int(180 - 130 * (t * 2))
    else:
        t2 = (t - 0.5) * 2
        r = int(255)
        g = int(255 - 200 * t2)
        b = int(50 - 50 * t2)
    return f"#{r:02x}{g:02x}{b:02x}"

# Ajouter les cercles
for _, row in profiles.iterrows():
    # Log scale : London(61K) ~ 50px, Lyon(5K) ~ 15px — bien different
    radius = min_r + (max_r - min_r) * (np.log(row["n"]) - np.log(min_n)) / (np.log(max_n) - np.log(min_n))
    color = prix_color(row["prix_med"])
    country_name = COUNTRY_NAMES.get(row["country_code"], row["country_code"])

    popup_html = f"""
    <div style="font-family: Arial; font-size: 12px; min-width: 200px;">
        <h4 style="margin:0 0 5px; color: #2E86AB;">
            {row['city'].title()} <span style="color: #666; font-size: 0.8em;">({country_name})</span>
        </h4>
        <table style="border-collapse: collapse; width: 100%;">
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">Listings actifs</td>
                <td style="padding: 2px 0;">{row['n']:,.0f}</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">Prix median</td>
                <td style="padding: 2px 0;">{row['prix_med']:.0f} EUR/nuit</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">IQR prix</td>
                <td style="padding: 2px 0;">{row['prix_q25']:.0f} - {row['prix_q75']:.0f} EUR</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">% Entire home</td>
                <td style="padding: 2px 0;">{row['pct_entire']:.1f}%</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">% Multi-host</td>
                <td style="padding: 2px 0;">{row['pct_multi']:.1f}%</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">% Longterm</td>
                <td style="padding: 2px 0;">{row['pct_longterm']:.1f}%</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">Ratio L/H</td>
                <td style="padding: 2px 0;">{row['ratio_lh']:.2f}</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">Dispo mediane</td>
                <td style="padding: 2px 0;">{row['dispo_med']:.0f} j/an</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">Reviews med</td>
                <td style="padding: 2px 0;">{row['reviews_med']:.0f}</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: bold;">Nb hosts</td>
                <td style="padding: 2px 0;">{row['n_hosts']:,.0f}</td></tr>
        </table>
    </div>
    """

    tooltip_text = (
        f"{row['city'].title()} | {row['n']:,.0f} listings | "
        f"{row['prix_med']:.0f} EUR | {row['pct_multi']:.0f}% multi"
    )

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.65,
        weight=2,
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=tooltip_text,
    ).add_to(m)

    # Label ville + nb listings
    n_label = f"{row['n']/1000:.0f}K" if row["n"] >= 1000 else str(int(row["n"]))
    folium.Marker(
        location=[row["lat"], row["lon"]],
        icon=folium.DivIcon(
            html=f'<div style="font-size: 11px; font-weight: bold; color: #333; '
                 f'text-shadow: 1px 1px 2px white, -1px -1px 2px white; white-space: nowrap;">'
                 f'{row["city"].title()}'
                 f' <span style="color: #2E86AB; font-size: 10px;">({n_label})</span>'
                 f'</div>',
            icon_size=(120, 18),
            icon_anchor=(60, -int(radius) - 3),
        ),
    ).add_to(m)
# &e

# &s LEGEND
legend_html = """
<div style="position: fixed; bottom: 30px; right: 30px; z-index: 1000;
     background: white; padding: 12px 16px; border-radius: 8px;
     box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: Arial; font-size: 12px;">
    <h4 style="margin: 0 0 8px; font-size: 13px;">20 Villes Europe — Juin 2025</h4>
    <p style="margin: 2px 0; font-size: 11px;">
        <b>Taille</b> : volume listings (sqrt)
    </p>
    <p style="margin: 2px 0; font-size: 11px;">
        <b>Couleur</b> : prix median EUR/nuit
    </p>
    <div style="display: flex; align-items: center; margin-top: 6px;">
        <span style="font-size: 10px;">57 EUR</span>
        <div style="flex: 1; height: 10px; margin: 0 6px;
             background: linear-gradient(to right, #3282b4, #ffff32, #ff0000);
             border-radius: 3px;"></div>
        <span style="font-size: 10px;">223 EUR</span>
    </div>
    <p style="margin: 6px 0 0; font-size: 10px; color: #888;">
        Source : Inside Airbnb | Cliquer pour details
    </p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Titre + bouton reset zoom
title_html = """
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
     z-index: 1000; background: rgba(255,255,255,0.92); padding: 8px 20px;
     border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);
     font-family: Arial;">
    <h3 style="margin: 0; color: #2E86AB; font-size: 16px;">
        Airbnb Europe — 20 Villes / 15 Pays (Juin 2025)
    </h3>
    <p style="margin: 2px 0 0; font-size: 11px; color: #666;">
        340K listings actifs | Prix median global 119 EUR/nuit
    </p>
</div>
<button onclick="resetMap()" style="position: fixed; top: 10px; right: 10px; z-index: 1000;
    background: #2E86AB; color: white; border: none; padding: 8px 16px;
    border-radius: 6px; cursor: pointer; font-family: Arial; font-size: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);"
    onmouseover="this.style.background='#1a6d8a'"
    onmouseout="this.style.background='#2E86AB'">
    Recentrer carte
</button>
<script>
function resetMap() {
    // Find the Leaflet map object
    var maps = document.querySelectorAll('.folium-map');
    if (maps.length > 0) {
        var mapId = maps[0].id;
        var mapObj = window[mapId];
        if (mapObj) {
            mapObj.setView([47.5, 12.0], 5);
        }
    }
}
</script>
"""
m.get_root().html.add_child(folium.Element(title_html))
# &e

# &s SAVE
out_path = OUT_DIR / "map-europe-20cities.html"
m.save(str(out_path))
sz = out_path.stat().st_size / 1024
print(f"\nSaved: {out_path.name} ({sz:.0f} KB)")
print(f"Path: {out_path}")
# &e
