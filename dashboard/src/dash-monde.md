---
title: "AIRBNB MONDE"
toc: false
sidebar: false
pager: false
style: styles/pbnb-dashboard.css
---

<!-- &s IMPORTS -->

```js
import * as d3 from "npm:d3";
import * as Plot from "npm:@observablehq/plot";
import { autoBins, makeGetColor, formatThreshold } from "./helpers/bins.js";
import { createOTTDMap, computeBounds, setMapLegend } from "./helpers/maplibre.js";
import { buildDataTable } from "./helpers/tableojs.js";
import { createBinsLegendBar } from "./helpers/legend.js";
import { createBanner, createNav, PBNB_PAGES } from "./helpers/layout.js";
import { createKpiStrip, createKpiHero } from "./helpers/kpi.js";
import { createScatterWithZoom } from "./helpers/scatterojs.js";
import { createSmallMultGrid } from "./helpers/smallmult.js";
import {
  showTooltip, hideTooltip,
  tooltipHeader, tooltipMetric, tooltipMeta, tooltipFooter, tooltipDivider
} from "./helpers/tooltip.js";
import { PAL_CAT_URBN_6, buildColorMap } from "./helpers/palettes.js";
```

<!-- &e IMPORTS -->

<!-- &s BANNER -->

```js
display(createBanner({
  voletTitle: "Explorateur mondial — 74 villes",
  color: "#0d6a5e",
  navElement: createNav(PBNB_PAGES, "monde")
}));
```

<!-- &e BANNER -->

<!-- &s DATA_LOAD -->

```js
const kpiCityGeo = FileAttachment("data/kpi_city_geo.json").json();
const kpiAgg = FileAttachment("data/kpi_agg.json").json();
const nbhData = FileAttachment("data/kpi_neighbourhood.json").json();
const ddictRaw = FileAttachment("data/ddict-airbnb.json").json();
const kpiRefMonde = FileAttachment("data/kpi_ref_monde.json").json();
```

```js
// DDICT exposé en CONST top-level (reactivité Observable fiable, pas window timing)
const DDICT = (() => {
  const raw = ddictRaw.indicators || ddictRaw;
  const dd = {};
  for (const [k, e] of Object.entries(raw)) {
    if (k.startsWith("_") || !e || !e.type) continue;
    dd[k] = { label: e.medium || e.short || k, short: e.short || k,
              type: e.type, unit: e.unit || "", desc: e.description || e.long || "" };
  }
  return dd;
})();
window.DDICT = DDICT;  // backward compat (helpers legacy lisant window.DDICT)

window.divGauge = function(val, mean, std, k, isEvol) {
  if (std === 0 || isNaN(val) || isNaN(mean)) return { bar: "#d5d5d5", text: "#555", op: 0.5 };
  const z = (val - mean) / std;
  if (z < -2.5)  return { bar: "#084594", text: "#042a5e", op: 0.80 };
  if (z < -2)    return { bar: "#2171b5", text: "#084594", op: 0.70 };
  if (z < -1)    return { bar: "#6baed6", text: "#084594", op: 0.60 };
  if (z < -0.5)  return { bar: "#c6dbef", text: "#0a4c6a", op: 0.55 };
  if (z <= 0.5)  return { bar: "#b8c2cc", text: "#555",    op: 0.52 };
  if (z <= 1)    return { bar: "#e8b4c0", text: "#6d1a36", op: 0.55 };
  if (z <= 2)    return { bar: "#c97b8e", text: "#5a1430", op: 0.60 };
  if (z <= 2.5)  return { bar: "#a63d5a", text: "#4a0e24", op: 0.70 };
  return { bar: "#6d1a36", text: "#3a0a1a", op: 0.80 };
};
```

```js
// Couleurs continents + noms pays
const CONT_COL = { "Europe": "#1696d2", "Americas": "#ca5800", "Asia-Pacific": "#55b748", "Africa": "#fdbf11", "World": "#475569" };
window.CONT_COL = CONT_COL;

const COUNTRY_NAMES = {
  FRA: "France", USA: "Etats-Unis", GBR: "Royaume-Uni", DEU: "Allemagne", ITA: "Italie",
  ESP: "Espagne", PRT: "Portugal", NLD: "Pays-Bas", BEL: "Belgique", AUT: "Autriche",
  CHE: "Suisse", IRL: "Irlande", DNK: "Danemark", SWE: "Suede", NOR: "Norvege",
  CZE: "Tchequie", HUN: "Hongrie", POL: "Pologne", GRC: "Grece", TUR: "Turquie",
  HRV: "Croatie", CAN: "Canada", MEX: "Mexique", BRA: "Bresil", ARG: "Argentine",
  CHL: "Chili", COL: "Colombie", JPN: "Japon", AUS: "Australie", NZL: "Nouvelle-Zelande",
  THA: "Thailande", IDN: "Indonesie", IND: "Inde", CHN: "Chine", ZAF: "Afrique du Sud",
  ARE: "Emirats", KOR: "Coree du Sud", TWN: "Taiwan", SGP: "Singapour", ISL: "Islande",
  MLT: "Malte", LUX: "Luxembourg", FIN: "Finlande", ROU: "Roumanie"
};

// Datasets
const allCities = kpiCityGeo.filter(d => d.lat != null);
const europeCities = allCities.filter(d => d.continent === "Europe");
const cityNames = allCities.map(d => d.city_fr || d.city).sort();

// kpi_neighbourhood.json est désormais exporté par sp11 avec les noms 2606 (vol_n_ann, px_*, str_*, cr_*, act_*)
// → plus de migration nécessaire, on lit directement.
const nbhDataMigrated = nbhData || [];
const countryRows = (kpiAgg || []).filter(d => d.level === "country").map(d => ({
  ...d, libelle: COUNTRY_NAMES[d.country_code] || d.country_code
}));
const continentRows = (kpiAgg || []).filter(d => d.level === "continent");
const continentDetailRows = (kpiAgg || []).filter(d => d.level === "continent_detail" && d.continent_detail !== "Africa");
const worldRow = (kpiAgg || []).find(d => d.level === "world");

// Refs sticky pour table
const franceRow = countryRows.find(d => d.country_code === "FRA");
```

<!-- &e DATA_LOAD -->

<!-- &s CADRAGE_MONDIAL - Bannière L1 + KPI hero monde -->

<div class="pbnb-cadrage">
  <div class="pbnb-cadrage-title">Cadrage mondial</div>
  <div class="pbnb-cadrage-sub">benchmark 74 villes · 31 pays · 4 continents · données Inside Airbnb juin 2025</div>
</div>

<div id="kpi-monde-hero" class="pbnb-kpi-hero"></div>

```js
{
  const c = document.getElementById("kpi-monde-hero");
  if (c) {
    c.innerHTML = "";
    const w = worldRow || {};
    const fN = n => n != null && !isNaN(+n) ? Math.round(+n).toLocaleString("fr-FR") : "—";
    const fP = n => n != null && !isNaN(+n) ? Math.round(+n) + " %" : "—";
    const f1 = n => n != null && !isNaN(+n) ? (+n).toFixed(1) : "—";
    // Médianes sur villes (worldRow n'a pas tous les indicateurs)
    const noteMed = d3.median(allCities.map(d => +d.actrv_note_glb).filter(v => !isNaN(v)));
    const revMed = d3.median(allCities.map(d => +d.act_revenu_med).filter(v => !isNaN(v)));
    const multiMed = d3.median(allCities.map(d => +d.cr_offre_1plus).filter(v => !isNaN(v)));
    const topMed = d3.median(allCities.map(d => +d.cr_offre_top10pct_pct).filter(v => !isNaN(v)));
    const proMed = d3.median(allCities.map(d => +d.cr_offre_5plus).filter(v => !isNaN(v)));
    const presMed = d3.median(allCities.map(d => +d.prs_listings_1000hab_dense).filter(v => !isNaN(v)));
    const minNuitsMed = d3.median(allCities.map(d => +d.str_minnuits30_pct).filter(v => !isNaN(v)));

    // 4 groupes alignés sur dash-france : profil / pression / pro / activité
    const groups = [
      {
        label: "Profil marché",
        items: [
          { v: w.vol_n_ann ? fN(Math.round(w.vol_n_ann / 1000)) + " k" : "—", l: "annonces actives", p: "total mondial" },
          { v: w.px_entire_med ? Math.round(w.px_entire_med) + " €" : "—", l: "prix médian / nuit", p: "logement entier", accent: true },
          { v: fP(w.str_entire_pct), l: "% logements entiers", p: "vs chambres" },
        ]
      },
      {
        label: "Pression territoriale",
        items: [
          { v: f1(presMed), l: "‰ ann. / hab. dense", p: "médiane villes" },
        ]
      },
      {
        label: "Professionnalisation",
        items: [
          { v: fP(multiMed), l: "% multi-hôtes (≥2)", p: "médiane villes" },
          { v: fP(proMed), l: "% ann. hôtes ≥5", p: "offre semi-pro" },
          { v: fP(topMed), l: "CR top 10 % hôtes", p: "médiane villes" },
        ]
      },
      {
        label: "Activité",
        items: [
          { v: fP(minNuitsMed), l: "% longue durée", p: "≥ 30 nuits min." },
          { v: revMed ? fN(Math.round(revMed)) + " €" : "—", l: "revenu annuel médian", p: "estim. par annonce", accent: true },
          { v: noteMed ? noteMed.toFixed(2) + " / 5" : "—", l: "note moyenne", p: "satisfaction" },
        ]
      }
    ];

    for (const g of groups) {
      const gDiv = document.createElement("div");
      gDiv.className = "pbnb-kpi-hero-group";
      gDiv.innerHTML = `<span class="pbnb-kpi-hero-group-label">${g.label}</span>`;
      const itDiv = document.createElement("div");
      itDiv.className = "pbnb-kpi-hero-group-items";
      for (const it of g.items) {
        const d = document.createElement("div");
        d.className = "pbnb-kpi-hero-item";
        d.innerHTML = `<span class="pbnb-kpi-hero-val${it.accent ? ' accent' : ''}">${it.v}</span>` +
          `<span class="pbnb-kpi-hero-lbl">${it.l}</span>` +
          `<span class="pbnb-kpi-hero-phrase">${it.p}</span>`;
        itDiv.appendChild(d);
      }
      gDiv.appendChild(itDiv);
      c.appendChild(gDiv);
    }
  }
}
```

<!-- &e CADRAGE_MONDIAL -->

<!-- &s CONTROLS - Sticky -->
<div class="pbnb-ctrl-wrap">
<div class="pbnb-ctrl">

```js
const mapIndic = view(Inputs.select(new Map([
  ["Volume annonces", "vol_n_ann"],
  ["Prix méd. logement entier (€)", "px_entire_med"],
  ["% logement entier", "str_entire_pct"],
  ["‰ ann. / hab. zone dense (†)", "prs_listings_1000hab_dense"],
  ["% multi-hôtes (≥2)", "cr_offre_1plus"],
  ["% ann. hôtes ≥5", "cr_offre_5plus"],
  ["% ann. hôtes ≥10", "cr_offre_10plus"],
  ["CR top 10 % hôtes", "cr_offre_top10pct_pct"],
  ["% longue durée (≥30 nuits)", "str_minnuits30_pct"],
  ["Calendrier ouvert méd. (j)", "act_cal_ouvert_med"],
  ["Revenu estimé méd. (€/an)", "act_revenu_med"],
  ["Note moyenne (/5)", "actrv_note_glb"],
]), { value: "vol_n_ann", label: "Indicateur" }));
```

```js
const tableMode = view(Inputs.radio(new Map([["Villes", "city"], ["Pays", "country"]]),
  { value: "city", label: "Vue table" }));
```

```js
// Focus ville — Londres par défaut (capitale Airbnb mondiale)
const _defaultFocus = cityNames.find(n => n.toLowerCase().includes("londre")) || cityNames[0] || "(aucune)";
const selectedCity = view(Inputs.select(
  ["(aucune)", ...cityNames],
  { value: _defaultFocus, label: "Focus ville" }
));
```

</div>
</div>
<!-- &e CONTROLS -->

<!-- Bandeau indicateur sélectionné — GROS et visible (pilote les 3 viz ci-dessous) -->
<div class="pbnb-indic-banner">
  <span class="pbnb-indic-banner-lbl">Cartes &amp; classements — indicateur :</span>
  <span id="subhead-indic-current" class="pbnb-indic-banner-val"></span>
  <span class="pbnb-indic-banner-meta">taille des bulles = volume d'annonces · couleur = valeur de l'indicateur · 74 villes</span>
</div>

```js
// Affiche en gros le label de l'indicateur sélectionné (les 3 viz suivantes en dépendent)
{
  const el = document.getElementById("subhead-indic-current");
  if (el) {
    const dd = DDICT[mapIndic] || {};
    el.textContent = (dd.label || dd.short || mapIndic) + (dd.unit ? " (" + dd.unit + ")" : "");
  }
}
```

<!-- &s GRID_CONTINENT - Small-multiples par sous-continent (multi-indicateurs fixes, comme France) -->
<div class="pbnb-topcell-light" style="margin-top:4px;">Profil par sous-continent<span class="sub">trait pointillé rouge = médiane · évol 25→26 sur volume</span></div>
<div id="grid-continent" style="margin:0 0 12px;"></div>

<!-- &e GRID_CONTINENT -->

<!-- &s ROW_MAPS - 2 cartes (monde cropé Amériques + Europe recadrée), pilotées par l'indicateur -->
<div style="display:grid; grid-template-columns:1.5fr 1fr; gap:3px; background:#e5e7eb; min-height:280px; margin:6px 0 10px;">

<div style="background:white; position:relative;">
<div class="pbnb-topcell-light">Carte monde<span class="sub">taille = volume · couleur = indicateur</span></div>
<div id="mc-monde" style="width:100%;height:270px;"></div>
</div>

<div style="background:white; position:relative;">
<div class="pbnb-topcell-light">Zoom Europe<span class="sub">bins synchros monde</span></div>
<div id="mc-europe" style="width:100%;height:270px;"></div>
</div>

</div>
<!-- &e ROW_MAPS -->

<!-- &s ROW_TABLE_SCATTER - Classement villes (light) + scatter structurel côte à côte -->
<div style="display:grid; grid-template-columns:1fr 1.15fr; gap:12px; margin:0 0 14px; align-items:start;">

<div style="background:white; border:1px solid #e5e7eb; border-radius:6px; padding:6px 8px 8px;">
<div class="pbnb-topcell-light" style="padding:2px 4px 4px;">Classement villes<span class="sub" id="rank-indic-sub">par indicateur sélectionné</span></div>
<div id="rank-villes" style="width:100%;"></div>
</div>

<div style="background:white; border:1px solid #e5e7eb; border-radius:6px; padding:4px 8px 8px;">
<div class="pbnb-topcell-light" style="padding:2px 4px 0;">Analyse structurelle · pression × concentration<span class="sub">axes FIXES · indépendant du sélecteur</span></div>
<div style="font-size:9px;color:#b8bfc9;padding:1px 4px 4px;">‰ ann./hab. dense (x) × % ann. hôtes ≥5 (y) · couleur = sous-continent · molette = zoom</div>
<div id="scat-monde" style="width:100%; height:320px;"></div>
</div>

</div>
<!-- &e ROW_TABLE_SCATTER -->

```js
// Init monde + europe maps (une seule fois)
const worldMaps = await (async () => {
  const refs = {};
  async function initBubbleMap(containerId, data, padding, bboxOverride) {
    const container = document.getElementById(containerId);
    if (!container || container._mapReady) return container?._ref;

    const { map, Popup } = await createOTTDMap(container, { maxZoom: 14 });
    await new Promise(r => { if (map.loaded()) r(); else map.on("load", r); });

    // Masquer les labels MapLibre (noms continents/pays/villes du fond de carte)
    try {
      const layers = map.getStyle().layers || [];
      layers.forEach(l => {
        if (l.type === "symbol") map.setLayoutProperty(l.id, "visibility", "none");
      });
    } catch (e) {}

    const geo = { type: "FeatureCollection", features: data.map(d => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [+d.lon, +d.lat] },
      properties: { ...d }
    }))};
    map.addSource("cities", { type: "geojson", data: geo });

    const maxL = Math.max(...data.map(d => +d.vol_n_ann || 0));
    map.addLayer({
      id: "circles", type: "circle", source: "cities",
      paint: {
        "circle-radius": ["interpolate", ["linear"],
          ["sqrt", ["/", ["to-number", ["get", "vol_n_ann"], 0], maxL || 1]],
          0, 2.5, 0.2, 5, 0.5, 9, 1, 18],
        "circle-color": "#1696d2",
        "circle-opacity": 0.82,
        "circle-stroke-color": "white",
        "circle-stroke-width": 0.8
      }
    });

    // Tooltip riche via helper unifié (jcn-tooltipojs) — métrique PRINCIPALE = indicateur sélectionné
    const fN = n => n != null && !isNaN(+n) ? Math.round(+n).toLocaleString("fr-FR") : "—";
    map.on("mousemove", "circles", (e) => {
      const p = e.features[0].properties;
      map.getCanvas().style.cursor = "pointer";
      // Indicateur courant (stocké par le bloc de recoloration réactif)
      const ind = map._curIndic || "vol_n_ann";
      const dd = window.DDICT?.[ind] || {};
      const rawV = p[ind];
      const indVal = (rawV != null && !isNaN(+rawV))
        ? (dd.type === "pct" ? (+rawV).toFixed(1) + " %"
           : dd.unit && dd.unit !== "n" ? fN(rawV) + " " + dd.unit
           : fN(rawV))
        : "n.d.";
      const html =
        tooltipHeader({ title: p.city_fr || p.city, subtitle: p.country_code || "" }) +
        // Indicateur sélectionné en gros (métrique principale)
        tooltipMetric({ label: dd.label || dd.short || ind, value: indVal }) +
        tooltipMeta([
          `${fN(p.vol_n_ann)} annonces`,
          `Prix méd. ${fN(p.px_entire_med)} €`,
          p.cr_offre_1plus != null ? `Multi-hôtes ${(+p.cr_offre_1plus).toFixed(0)}%` : null
        ].filter(Boolean)) +
        tooltipFooter([p.continent_detail || p.continent].filter(Boolean));
      showTooltip(e.originalEvent, html);
    });
    map.on("mouseleave", "circles", () => {
      map.getCanvas().style.cursor = "";
      hideTooltip();
    });

    // bbox : override explicite (crop) sinon auto depuis les données
    let bbox;
    if (bboxOverride) {
      bbox = bboxOverride;
    } else {
      const lats = data.map(d => +d.lat), lngs = data.map(d => +d.lon);
      bbox = [[Math.min(...lngs) - padding, Math.min(...lats) - padding],
              [Math.max(...lngs) + padding, Math.max(...lats) + padding]];
    }
    map.fitBounds(bbox, { padding: 8, duration: 0 });

    const ref = { map, container, Popup };
    container._mapReady = true;
    container._ref = ref;
    return ref;
  }

  // Monde : crop à gauche (Amériques) → borne ouest resserrée, latitudes habitées.
  refs.monde = await initBubbleMap("mc-monde", allCities, 8, [[-125, -45], [155, 62]]);
  // Europe : recadré serré (moins de vide Atlantique à gauche).
  refs.europe = await initBubbleMap("mc-europe", europeCities, 3, [[-10.5, 35], [30, 60.5]]);
  return refs;
})();
```

```js
// Update couleur cercles selon indicateur (réactif)
{
  if (worldMaps?.monde?.map) {
    const vals = allCities.map(d => +d[mapIndic]).filter(v => !isNaN(v));
    const binsResult = vals.length > 5 ? autoBins(vals, mapIndic) : null;
    if (binsResult) {
      const steps = ["step", ["to-number", ["get", mapIndic], 0]];
      steps.push(binsResult.palette[0]);
      for (let i = 0; i < binsResult.thresholds.length; i++) {
        steps.push(binsResult.thresholds[i]);
        steps.push(binsResult.palette[i + 1] || binsResult.palette[i]);
      }
      for (const ref of [worldMaps.monde, worldMaps.europe]) {
        if (ref?.map) {
          ref.map.setPaintProperty("circles", "circle-color", [
            "case", ["==", ["get", mapIndic], null], "#b0b0b0", steps
          ]);
          ref.map._curIndic = mapIndic;  // pour que le tooltip affiche l'indicateur courant
        }
      }
      const dd = window.DDICT?.[mapIndic] || {};
      const leg = createBinsLegendBar({
        colors: binsResult.palette, thresholds: binsResult.thresholds,
        counts: binsResult.counts, unit: dd.unit || "",
        echelonValue: binsResult.mean, echelonLabel: "Moy."
      });
      setMapLegend(document.getElementById("mc-monde"), leg);
    }
  }
}
```

```js
// Grid small-multiples par sous-continent (FIXE, multi-indicateurs — comme France)
// Labels courts + tri par volume décroissant
{
  const c = document.getElementById("grid-continent");
  if (c) {
    const SHORT = {
      "Europe West & North": "Eur. W&N", "Europe South & East": "Eur. S&E",
      "North America": "N. America", "Latin America": "L. America",
      "Asia": "Asia", "Oceania": "Oceania", "Africa": "Africa"
    };
    const rows = continentDetailRows
      .filter(d => d.continent_detail !== "Africa")   // n trop faible
      .map(d => ({ ...d, _lab: SHORT[d.continent_detail] || d.continent_detail }))
      .sort((a, b) => (+b.vol_n_ann || 0) - (+a.vol_n_ann || 0));

    createSmallMultGrid({
      container: c, Plot, d3, ddict: DDICT,
      data: rows, labelKey: "_lab",
      panels: [
        { key: "vol_n_ann", evolKey: "vol_n_ann_vevol_2526" },  // volume + évol 25→26
        { key: "prs_listings_1000hab_dense" },                  // pression dense
        { key: "str_entire_pct" },                              // % logements entiers
        { key: "cr_offre_1plus" },                              // % multi-hôtes
        { key: "cr_offre_top10pct_pct" },                       // top 10 %
      ],
      stackPanel: {
        title: "Profil hôtes (% offre)",
        segments: [
          { key: "cr_offre_single_pct", label: "single", color: "#cbd5e1" },
          { key: "cr_offre_semipro_pct", label: "semi", color: "#fdba74" },
          { key: "cr_offre_pro_pct", label: "pro", color: "#f97316" },
          { key: "cr_offre_10plus", label: "10+", color: "#9d2240" },
        ]
      }
    });
  }
}
```

```js
// Classement villes (reactable LIGHT 2 colonnes : volume + indicateur sélectionné) — scrollable
{
  const c = document.getElementById("rank-villes");
  const sub = document.getElementById("rank-indic-sub");
  if (c) {
    const dd = DDICT[mapIndic] || {};
    if (sub) sub.textContent = "trié par « " + (dd.short || dd.label || mapIndic) + " »";

    // Colonnes : Volume + indicateur sélectionné (si != volume)
    const keys = mapIndic === "vol_n_ann" ? ["vol_n_ann"] : ["vol_n_ann", mapIndic];
    // Pastille pays (FRA jaune) — palette auto
    const countries = [...new Set(allCities.map(d => d.country_code).filter(Boolean))];
    const palette = d3.schemeTableau10.concat(["#9333ea","#ec4899","#0891b2","#65a30d","#dc2626","#0d9488"]);
    const colMap = { "FRA": "#fbbf24" };
    let pi = 0;
    countries.forEach(cc => { if (!colMap[cc]) { colMap[cc] = palette[pi % palette.length]; pi++; } });

    buildDataTable(c, allCities, {
      ddict: DDICT,
      keys,
      labelCol: "city_fr", labelFallback: "city", labelHeader: "Ville",
      colorCol: "country_code", colorMap: colMap,
      defaultSort: mapIndic, maxHeight: 340,
      barMode: "fill",
      lightHeader: true,
      expandable: false
    });
  }
}
```

```js
// Scatter pression × % offre pro — helper mutils avec zoom + France en jaune
{
  const c = document.getElementById("scat-monde");
  if (c) {
    c.innerHTML = "";

    // Labels courts pour ville (raccourcissement intelligent)
    const shortLabel = (name) => {
      if (!name) return "";
      const s = String(name);
      // Si très long, prendre les premiers mots significatifs
      if (s.length > 12) {
        // Cas "Biarr.-Anglet-Bayon." → couper avant le premier "-"
        const dash = s.indexOf("-");
        if (dash > 4 && dash < 10) return s.substring(0, dash);
        // Cas "Hong Kong Singapour" / "Rio de Janeiro" → premiers mots
        return s.split(/\s/)[0];
      }
      return s;
    };

    const data = allCities.map(d => ({
      ...d,
      _label_short: shortLabel(d.city_fr || d.city)
    }));
    const frLabels = new Set(allCities.filter(d => d.country_code === "FRA").map(d => shortLabel(d.city_fr || d.city)));

    // Palette PAL_CAT_URBN_6 cyclée sur les sous-continents (ordre par volume desc pour cohérence visuelle)
    const subContinents = ["Europe West & North", "Europe South & East", "North America",
                           "Latin America", "Asia", "Oceania", "Africa"];
    const CONT_DETAIL_COL = buildColorMap(subContinents, PAL_CAT_URBN_6);

    // Labels raccourcis dans la légende
    const CONT_SHORT_LABELS = {
      "Europe West & North": "Eur. W&N",
      "Europe South & East": "Eur. S&E",
      "North America":       "N. America",
      "Latin America":       "L. America",
      "Asia":                "Asia",
      "Oceania":             "Oceania",
      "Africa":              "Africa"
    };

    createScatterWithZoom({
      Plot, d3,
      container: c,
      data,
      xCol: "prs_listings_1000hab_dense",
      yCol: "cr_offre_5plus",
      sizeCol: "vol_n_ann",
      colorCol: "continent_detail",
      colorMap: CONT_DETAIL_COL,
      colorLabelMap: CONT_SHORT_LABELS,
      labelCol: "_label_short",
      labelFallback: "city",
      labelQuantile: 0.85,
      labelSet: frLabels,
      width: c.clientWidth || 320,
      height: 325,
      showMeans: true,
      showRegression: false,
      showLegend: true,
      legendInteractive: true,  // clic sur légende → filtre catégorie
      axisLabelMode: "medium",
      fontSize: 10,
      labelFontSize: 9.5,
      rRange: [2.5, 10]
    });
  }
}
```

<!-- &e SCATTER_ISOLE -->

<!-- &s TABLE_TOGGLE - Villes ↔ Pays avec pastilles country_code + 2 refRows -->

<div class="pbnb-subhead">Tableau benchmark · ⛶ plein écran · scroll horizontal<span class="pbnb-subhead-sub"> · pastilles par pays · France + Méd. monde sticky</span></div>

<div id="tbl-monde" style="margin-bottom:16px;"></div>

```js
{
  const c = document.getElementById("tbl-monde");
  if (c) {
    c.innerHTML = "";
    const isCity = tableMode === "city";
    const data = isCity ? allCities : countryRows;
    const labelCol = isCity ? "city_fr" : "libelle";
    const labelHeader = isCity ? "Ville" : "Pays";

    // Pastille par pays (FRA jaune) si vue Villes ; sinon par continent
    let colCol, colMap;
    if (isCity) {
      const countries = [...new Set(data.map(d => d.country_code).filter(Boolean))];
      const palette = d3.schemeTableau10.concat(["#9333ea","#ec4899","#0891b2","#65a30d","#dc2626","#0d9488","#7c3aed","#f59e0b"]);
      colMap = { "FRA": "#fbbf24" };
      let pi = 0;
      countries.forEach(cc => { if (!colMap[cc]) { colMap[cc] = palette[pi % palette.length]; pi++; } });
      colCol = "country_code";
    } else {
      colCol = "continent"; colMap = CONT_COL;
    }

    // refRows multi-niveaux : France + Méd. monde
    const refRows = [];
    if (franceRow) refRows.push({ label: "France", data: franceRow });
    if (worldRow) refRows.push({ label: "Méd. monde", data: worldRow });

    buildDataTable(c, data, {
      ddict: DDICT,
      keys: ["vol_n_ann", "px_entire_med", "str_entire_pct",
             "prs_listings_1000hab_dense",
             "cr_offre_1plus", "cr_offre_5plus", "cr_offre_10plus", "cr_offre_top10pct_pct",
             "str_minnuits30_pct", "act_cal_ouvert_med", "act_revenu_med", "actrv_note_glb"],
      groups: [
        { label: "Profil", cols: ["vol_n_ann","px_entire_med","str_entire_pct"] },
        { label: "Pression", cols: ["prs_listings_1000hab_dense"] },
        { label: "Pro", cols: ["cr_offre_1plus","cr_offre_5plus","cr_offre_10plus","cr_offre_top10pct_pct"] },
        { label: "Activité", cols: ["str_minnuits30_pct","act_cal_ouvert_med","act_revenu_med","actrv_note_glb"] }
      ],
      labelCol, labelFallback: isCity ? "city" : "country_code", labelHeader,
      colorCol: colCol, colorMap: colMap,
      defaultSort: "vol_n_ann", maxHeight: 380,
      barMode: "fill",
      refRows,
      expandable: true
    });
  }
}
```

<!-- &e TABLE_TOGGLE -->

<!-- &s CITY_FOCUS - Carte quartiers + KPI par ville -->

```js
// City focus: carte bulles quartier + KPI
{
  if (selectedCity === "(aucune)") {
    display(html`<div style="color:#9ca3af; font-style:italic; padding:12px;">Sélectionnez une ville pour afficher la carte des quartiers</div>`);
  } else {
    const cityData = allCities.find(d => (d.city_fr || d.city) === selectedCity);
    if (!cityData) { display(html`<div>Ville non trouvée</div>`); }
    else {
      const cityKey = cityData.city;
      const cityNbh = nbhDataMigrated.filter(d => d.city === cityKey && d.vol_n_ann >= 5);
      const fN = n => n != null ? Math.round(+n).toLocaleString("fr-FR") : "—";

      // Bannière Cadrage focus ville (style pattern dash-france)
      const countryName = COUNTRY_NAMES[cityData.country_code] || cityData.country_code;
      const cadr = document.createElement("div");
      cadr.className = "pbnb-cadrage";
      cadr.style.marginTop = "14px";
      cadr.innerHTML = `<div class="pbnb-cadrage-title">Focus ville · ${cityData.city_fr || cityData.city}</div>` +
        `<div class="pbnb-cadrage-sub">${countryName} · ${cityData.continent} · ${cityNbh.length} quartiers avec ≥5 annonces</div>`;
      display(cadr);

      // KPI ville — déclinaison "strip" du helper jcn (même pattern que villes France)
      const fI = n => n != null && !isNaN(+n) ? Math.round(+n).toLocaleString("fr-FR") : "—";
      const pI = n => n != null && !isNaN(+n) ? Math.round(+n) + " %" : "—";
      // Même ordre que l'agrégat : profil → pression → pro → activité
      const cityItems = [
        { v: fI(cityData.vol_n_ann), l: "Annonces" },
        { v: fI(cityData.px_entire_med) + " €", l: "Prix entier", accent: true },
        { v: pI(cityData.str_entire_pct), l: "% entiers" },
        { v: cityData.prs_listings_1000hab_dense != null ? (+cityData.prs_listings_1000hab_dense).toFixed(1) : "—", l: "‰ ann./hab" },
        { v: pI(cityData.cr_offre_1plus), l: "% multi (≥2)" },
        { v: pI(cityData.cr_offre_5plus), l: "% ≥5" },
        { v: fI(cityData.act_revenu_med) + " €", l: "Revenu/an", accent: true },
        { v: cityData.actrv_note_glb != null ? (+cityData.actrv_note_glb).toFixed(2) + " / 5" : "—", l: "Note" },
        { v: cityNbh.length.toString(), l: "Quartiers" },
      ];
      const heroWrap = document.createElement("div");
      heroWrap.style.cssText = "background:#fdfcf7; border-bottom:2px solid #fbbf24; margin:0 0 8px; overflow-x:auto;";
      heroWrap.appendChild(createKpiHero({ items: cityItems, strip: true }));
      display(heroWrap);

      // Sous-header quartiers
      const sh = document.createElement("div");
      sh.className = "pbnb-subhead";
      sh.innerHTML = `Carte des quartiers · taille = volume · couleur = indicateur sélectionné` +
        `<span class="pbnb-subhead-sub"> · top 3 / bottom 3 en overlay</span>`;
      display(sh);

      // Layout: carte + table
      const row = document.createElement("div");
      row.className = "pbnb-city-row";
      const mapCol = document.createElement("div");
      mapCol.className = "pbnb-map-col";
      const mapDiv = document.createElement("div");
      mapDiv.style.cssText = "width:100%;height:480px;";
      mapCol.appendChild(mapDiv);
      row.appendChild(mapCol);
      const tableCol = document.createElement("div");
      tableCol.className = "pbnb-table-col";
      row.appendChild(tableCol);
      display(row);

      await new Promise(r => setTimeout(r, 80));

      // Carte bulles quartier (centroids)
      const { map, Popup } = await createOTTDMap(mapDiv, { maxZoom: 16 });
      await new Promise(r => { if (map.loaded()) r(); else map.on("load", r); });

      // Masquer labels MapLibre (continents, pays, villes du fond) — on les remet juste pour rues à zoom serré
      try {
        const layers = map.getStyle().layers || [];
        layers.forEach(l => {
          if (l.type === "symbol" && !l.id.includes("road")) map.setLayoutProperty(l.id, "visibility", "none");
        });
      } catch (e) {}

      // Mapping nouveau nom → ancien (kpi_neighbourhood pas encore migré sp11)
      // Colonnes réellement dispo au niveau quartier (kpi_neighbourhood 2606)
      const NBH_COLS = new Set(["vol_n_ann","vol_n_hotes","px_med","px_entire_med",
        "str_entire_pct","cr_offre_1plus","str_minnuits30_pct","act_cal_ouvert_med",
        "actrv_avis","actrv_avis_mois"]);
      // L'indicateur sélectionné existe-t-il au niveau quartier ? sinon pas de choroplèthe (bulles bleues)
      const nbhIndic = NBH_COLS.has(mapIndic) ? mapIndic : null;

      const vals = nbhIndic ? cityNbh.map(d => +d[nbhIndic]).filter(v => !isNaN(v)) : [];
      const binsResult = vals.length > 3 ? autoBins(vals, nbhIndic) : null;
      const getColor = binsResult ? makeGetColor(binsResult) : () => "#1696d2";

      const maxN = Math.max(...cityNbh.map(d => d.vol_n_ann));
      const geo = { type: "FeatureCollection", features: cityNbh.map(d => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [d.lon, d.lat] },
        properties: {
          ...d,
          _fill: nbhIndic ? getColor(d[nbhIndic]) : "#1696d2",
          _radius: Math.max(4, Math.sqrt(d.vol_n_ann / maxN) * 25)
        }
      }))};

      map.addSource("nbh", { type: "geojson", data: geo });
      map.addLayer({
        id: "nbh-circles", type: "circle", source: "nbh",
        paint: {
          "circle-radius": ["get", "_radius"],
          "circle-color": ["get", "_fill"],
          "circle-opacity": 0.78,
          "circle-stroke-color": "white",
          "circle-stroke-width": 1
        }
      });

      // Tooltip quartier via helper unifié
      map.on("mousemove", "nbh-circles", (e) => {
        const p = e.features[0].properties;
        map.getCanvas().style.cursor = "pointer";
        const dd = window.DDICT?.[mapIndic] || {};
        const valStr = nbhIndic && p[nbhIndic] != null
          ? (dd.type === "pct" ? (+p[nbhIndic]).toFixed(1) + "%" : Number(+p[nbhIndic]).toLocaleString("fr-FR"))
          : "n.d.";
        const html =
          tooltipHeader({ title: p.neighbourhood || "Quartier" }) +
          tooltipMetric({ label: dd.short || mapIndic, value: valStr }) +
          tooltipMeta([
            `${fN(p.vol_n_ann)} annonces`,
            p.px_med != null ? `Prix méd. ${fN(p.px_med)} €` : null
          ].filter(Boolean));
        showTooltip(e.originalEvent, html);
      });
      map.on("mouseleave", "nbh-circles", () => {
        map.getCanvas().style.cursor = "";
        hideTooltip();
      });

      const bds = computeBounds(geo.features);
      if (bds.bounds) {
        // Padding généreux + maxZoom bas pour s'assurer que tous les quartiers tiennent dans la vue
        map.fitBounds(bds.bounds, { padding: 60, duration: 0, maxZoom: 10 });
      } else if (cityData.lat && cityData.lon) {
        // Fallback : centrer sur la ville si pas de quartiers
        map.flyTo({ center: [+cityData.lon, +cityData.lat], zoom: 10, duration: 0 });
      }

      if (binsResult) {
        const dd = window.DDICT?.[mapIndic] || {};
        setMapLegend(mapDiv, createBinsLegendBar({
          colors: binsResult.palette, thresholds: binsResult.thresholds,
          counts: binsResult.counts, unit: dd.unit || "",
          echelonValue: binsResult.mean, echelonLabel: "Moy."
        }));
      }

      // Top 3 / Bottom 3 — bandeau bas pleine largeur (pas une bulle à gauche)
      if (nbhIndic && cityNbh.length >= 6) {
        const arr = cityNbh
          .map(d => ({ label: d.neighbourhood, val: +d[nbhIndic] }))
          .filter(d => !isNaN(d.val));
        if (arr.length >= 6) {
          arr.sort((a, b) => b.val - a.val);
          const top3 = arr.slice(0, 3);
          const bot3 = arr.slice(-3).reverse();
          const dd = window.DDICT?.[mapIndic] || {};
          const fmtV = v => dd.type === "pct" ? v.toFixed(0) + "%" : Math.round(v).toLocaleString("fr-FR");
          const itemHtml = (r, rk, col) =>
            `<span style="white-space:nowrap;"><span style="color:${col};font-weight:700;">${rk}.</span> ` +
            `<span style="color:#1f2937;">${r.label}</span> <b style="color:#0a4c6a;">${fmtV(r.val)}</b></span>`;
          const sep = '<span style="color:#cbd5e1;margin:0 8px;">·</span>';
          const ov = document.createElement("div");
          ov.className = "pbnb-topbot";
          ov.style.cssText = "position:absolute; bottom:0; left:0; right:0; z-index:5; " +
            "background:rgba(255,255,255,0.92); padding:5px 10px; font-size:11px; line-height:1.5; " +
            "box-shadow:0 -1px 4px rgba(0,0,0,0.1); border-top:2px solid #fbbf24; overflow-x:auto;";
          ov.innerHTML =
            `<div><span style="color:#16a34a;font-weight:700;margin-right:6px;">▲ Top 3</span>` +
            top3.map((r, i) => itemHtml(r, i + 1, "#16a34a")).join(sep) + `</div>` +
            `<div><span style="color:#dc2626;font-weight:700;margin-right:6px;">▼ Bottom 3</span>` +
            bot3.map((r, i) => itemHtml(r, "n-" + (i + 1), "#dc2626")).join(sep) + `</div>`;
          mapDiv.style.position = "relative";
          mapDiv.appendChild(ov);
        }
      }

      // Moyenne ville pour refRow table quartier — colonnes RÉELLEMENT dispo au niveau quartier
      const cityAvgForNbh = {
        vol_n_ann: d3.mean(cityNbh, d => +d.vol_n_ann),
        px_entire_med: d3.mean(cityNbh, d => +d.px_entire_med),
        str_entire_pct: d3.mean(cityNbh, d => +d.str_entire_pct),
        cr_offre_1plus: d3.mean(cityNbh, d => +d.cr_offre_1plus),
        str_minnuits30_pct: d3.mean(cityNbh, d => +d.str_minnuits30_pct),
        act_cal_ouvert_med: d3.mean(cityNbh, d => +d.act_cal_ouvert_med),
        actrv_avis_mois: d3.mean(cityNbh, d => +d.actrv_avis_mois),
      };

      buildDataTable(tableCol, cityNbh, {
        ddict: DDICT,
        keys: ["vol_n_ann", "px_entire_med", "str_entire_pct", "cr_offre_1plus", "str_minnuits30_pct", "act_cal_ouvert_med", "actrv_avis_mois"],
        labelCol: "neighbourhood", labelHeader: "Quartier",
        colorCol: null, defaultSort: "vol_n_ann", maxHeight: 440,
        barMode: "fill",
        groups: [
          { label: "Profil", cols: ["vol_n_ann", "px_entire_med", "str_entire_pct"] },
          { label: "Pro", cols: ["cr_offre_1plus"] },
          { label: "Activité", cols: ["str_minnuits30_pct", "act_cal_ouvert_med", "actrv_avis_mois"] }
        ],
        refRow: { label: `Moy. ${cityData.city_fr || cityData.city}`, data: cityAvgForNbh, bgColor: "#fef3c7" }
      });
    }
  }
}
```

<!-- &e CITY_FOCUS -->
