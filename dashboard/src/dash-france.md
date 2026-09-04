---
title: "AIRBNB FRANCE"
toc: false
sidebar: false
pager: false
style: styles/pbnb-dashboard.css
---

<!-- &s IMPORTS -->

```js
import * as d3 from "npm:d3";
import * as Plot from "npm:@observablehq/plot";
import { autoBins, makeGetColor, formatThreshold, GREY_NA } from "./helpers/bins.js";
import { createOTTDMap, buildChoroplethSource, attachTooltip, computeBounds, setMapLegend } from "./helpers/maplibre.js";
import { buildDataTable } from "./helpers/tableojs.js";
import { createBinsLegendBar } from "./helpers/legend.js";
import { createBanner, createNav, PBNB_PAGES } from "./helpers/layout.js";
import { createKpiStrip, createKpiHero } from "./helpers/kpi.js";
import { createScatterWithZoom } from "./helpers/scatterojs.js";
import { createSmallMultGrid } from "./helpers/smallmult.js";
import {
  showTooltip, hideTooltip,
  tooltipHeader, tooltipMetric, tooltipMeta, tooltipFooter
} from "./helpers/tooltip.js";
```

<!-- &e IMPORTS -->

<!-- &s BANNER -->

```js
display(createBanner({
  voletTitle: "Observatoire territorial France",
  color: "#0a4c6a",
  navElement: createNav(PBNB_PAGES, "france")
}));
```

<!-- &e BANNER -->

<!-- &s DATA_LOAD -->

```js
const kpiCity = FileAttachment("data/kpi_city.json").json();
const kpiArr = FileAttachment("data/kpi_arr.json").json();
const kpiIris = FileAttachment("data/kpi_iris.json").json();
const kpiCountry = FileAttachment("data/kpi_country.json").json();
const kpiCityGeo = FileAttachment("data/kpi_city_geo.json").json();
const kpiAgg = FileAttachment("data/kpi_agg.json").json();
const ddictRaw = FileAttachment("data/ddict-airbnb.json").json();
const geoParisIris = FileAttachment("data/iris_paris.geojson").json();
const geoParisArr = FileAttachment("data/arr_paris.geojson").json();
const geoBabIris = FileAttachment("data/iris_bab.geojson").json();
const geoBabCom = FileAttachment("data/com_bab.geojson").json();
const geoLyonIris = FileAttachment("data/iris_lyon.geojson").json();
const geoLyonArr = FileAttachment("data/arr_lyon.geojson").json();
const geoBdxIris = FileAttachment("data/iris_bordeaux.geojson").json();
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
window.DDICT = DDICT;  // backward compat (helpers legacy)

// divGauge bleu↔bordeaux (sync pbnb dashboard v1)
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
// Refs précalculées depuis kpi_agg (world / continent / country)
const worldRow = (kpiAgg || []).find(d => d.level === "world");
const europeRow = (kpiAgg || []).find(d => d.level === "continent" && d.continent === "Europe");
const franceRow = (kpiAgg || []).find(d => d.level === "country" && d.country_code === "FRA");
const refFrance = franceRow || kpiCountry[0];
```

```js
// Spec KPI partagée — UNE source de structure pour France ET Europe (→ colonnes alignées)
// 4 groupes × items ; fmt = "n"|"€"|"%"|"‰"|"/5" ; derive = calcul à la volée
const KPI_SPEC = [
  { group: "Profil marché", items: [
    { key: "vol_n_ann",       label: "annonces actives",   phrase: "total marché",        fmt: "n" },
    { key: "px_entire_med",   label: "prix médian / nuit", phrase: "logement entier",     fmt: "€", accent: true },
    { key: "str_entire_pct",  label: "% logements entiers",phrase: "vs chambres",         fmt: "%" },
  ]},
  { group: "Pression territoriale", items: [
    { key: "prs_listings_1000hab_dense", label: "‰ ann. / hab. dense", phrase: "intensité zone dense", fmt: "‰" },
  ]},
  { group: "Professionnalisation", items: [
    { key: "cr_offre_1plus",        label: "% multi-hôtes (≥2)", phrase: "hôtes 2+ annonces", fmt: "%" },
    { key: "cr_offre_5plus",        label: "% ann. hôtes ≥5",    phrase: "offre semi-pro",   fmt: "%" },
    { key: "cr_offre_top10pct_pct", label: "CR top 10 % hôtes",  phrase: "concentration",    fmt: "%" },
  ]},
  { group: "Activité", items: [
    { key: "str_minnuits30_pct", label: "% longue durée",       phrase: "≥ 30 nuits",       fmt: "%" },
    { key: "act_revenu_med",     label: "revenu annuel médian", phrase: "estim. / annonce", fmt: "€", accent: true },
  ]},
];

// kpi_city.json utilise "city" + "scope" (pas "territory" — réservé à kpi_arr / kpi_iris)
const parisCity = kpiCity.find(d => d.city === "paris" && d.scope === "city");
const parisArrData = kpiArr.filter(d => d.city === "paris");
const parisIrisData = kpiIris.filter(d => d.city === "paris");

// Patch BAB : sub_cities (Biarritz/Anglet/Bayonne) n'ont pas les cr_* car calculés au niveau host
// Inside Airbnb = "pays-basque". On hérite les concentrations depuis l'agrégat pays-basque parent.
const _bab_parent = kpiCity.find(d => d.city === "pays-basque" && d.scope === "city");
const _CR_KEYS = ["cr_offre_1plus","cr_offre_5plus","cr_offre_10plus","cr_offre_top10pct_pct",
                  "cr_offre_single_pct","cr_offre_semipro_pct","cr_offre_pro_pct",
                  "cr_host_1plus","cr_host_5plus","cr_host_10plus","cr_host_single_pct",
                  "cr_host_semipro_pct","cr_host_pro_pct","cr_gini","str_ratio_ann_hote"];
const babCities = kpiCity.filter(d => ["biarritz","bayonne","anglet"].includes(d.city) && d.scope === "sub_city")
  .map(d => {
    const patched = { ...d };
    if (_bab_parent) for (const k of _CR_KEYS) if (patched[k] == null) patched[k] = _bab_parent[k];
    return patched;
  });
const babIrisData = kpiIris.filter(d => ["biarritz","bayonne","anglet","pays-basque"].includes(d.city));

const lyonCity = kpiCity.find(d => d.city === "lyon" && d.scope === "city");
const lyonArrData = kpiArr.filter(d => d.city === "lyon");
const lyonIrisData = kpiIris.filter(d => d.city === "lyon");

const bdxCity = kpiCity.find(d => d.city === "bordeaux" && d.scope === "city");
const bdxIrisData = kpiIris.filter(d => d.city === "bordeaux");

// Pseudo-row pour BAB agrégé (somme + médiane des 3 communes)
const babAgg = (() => {
  if (!babCities.length) return null;
  const sum = (k) => d3.sum(babCities, d => +d[k] || 0);
  const med = (k) => d3.median(babCities.map(d => +d[k]).filter(v => !isNaN(v)));
  return {
    territory: "bab", libelle: "Biarritz · Anglet · Bayonne",
    vol_n_ann: sum("vol_n_ann"),
    px_entire_med: med("px_entire_med"),
    str_entire_pct: med("str_entire_pct"),
    cr_offre_1plus: med("cr_offre_1plus"),
    prs_listings_1000hab_dense: med("prs_listings_1000hab_dense"),
    act_revenu_med: med("act_revenu_med"),
    actrv_note_glb: med("actrv_note_glb"),
  };
})();

// Bounds pré-calculés
const parisBounds = computeBounds(geoParisIris.features);
const babBounds = computeBounds(geoBabIris.features);
const lyonBounds = computeBounds(geoLyonIris.features);
const bdxBounds = computeBounds(geoBdxIris.features);
```

<!-- &e DATA_LOAD -->

<!-- &s CONTROLS - Sticky sous bandeau -->
<div class="pbnb-ctrl-wrap">
<div class="pbnb-ctrl">

```js
// Liste groupée par thématique — cohérente avec KPI hero (profil/pression/pro/activité)
// (†) pression dispo ville/arr seulement, pas IRIS — cartes IRIS resteront vides sur ces indicateurs
const indicateur = view(Inputs.select(new Map([
  // Profil marché — dispo tous niveaux
  ["Volume annonces", "vol_n_ann"],
  ["Prix méd. logement entier (€)", "px_entire_med"],
  ["% logement entier", "str_entire_pct"],
  // Pression territoriale (†) — ville/arr uniquement
  ["‰ ann. / hab. zone dense (†)", "prs_listings_1000hab_dense"],
  ["‰ ann. / hab. (†)", "prs_listings_1000hab"],
  // Professionnalisation
  ["% ann. multi-hôtes (≥2)", "cr_offre_1plus"],
  ["% ann. hôtes ≥5", "cr_offre_5plus"],
  ["% ann. hôtes ≥10", "cr_offre_10plus"],
  ["CR top 10 % hôtes", "cr_offre_top10pct_pct"],
  ["Ratio annonces / hôte", "str_ratio_ann_hote"],
  // Activité
  ["% longue durée (≥30 nuits)", "str_minnuits30_pct"],
  ["Calendrier ouvert méd. (j)", "act_cal_ouvert_med"],
  ["Revenu estimé méd. (€/an)", "act_revenu_med"],
  ["Note moyenne (/5)", "actrv_note_glb"],
]), { value: "vol_n_ann", label: "Indicateur" }));
```

```js
const maille = view(Inputs.radio(new Map([["IRIS", "iris"], ["Arr./Commune", "comm"]]),
  { value: "iris", label: "Maille" }));
```

</div>
</div>
<!-- &e CONTROLS -->

<!-- &s TOP_BLOCK - Carte Europe + Table light extensible + Scatter dense -->
<div class="pbnb-cadrage" style="margin:6px 0 4px;">
  <div class="pbnb-cadrage-title">Cadrage européen</div>
  <div class="pbnb-cadrage-sub">benchmark France vs 40 villes Europe · France et Méd. Europe en lignes sticky</div>
</div>

<!-- KPI agrégé Europe (sous cadrage européen) -->
<div id="kpi-eur-hero" style="margin:0 -16px 6px;"></div>

```js
{
  const c = document.getElementById("kpi-eur-hero");
  if (c && europeRow) {
    c.innerHTML = "";
    // Même spec que France → colonnes alignées · réf = MONDE (worldRow) en (light)
    c.appendChild(createKpiHero({
      spec: KPI_SPEC, data: europeRow, refData: worldRow,
      refNote: "monde", className: "eur-strip"
    }));
  }
}
```

<div class="pbnb-top-block" style="grid-template-columns:0.85fr 1.6fr 1.3fr;">

<div class="pbnb-top-cell">
<div class="pbnb-top-cell-title">Carte Europe &amp; France<div style="font-size:9px;font-weight:400;color:#94a3b8;text-transform:none;letter-spacing:0;">Volume annonces · top 10 villes annotées · France en jaune</div></div>
<div id="mc-europe-fr" style="width:100%;height:320px;position:relative;"></div>
</div>

<div class="pbnb-top-cell">
<div class="pbnb-top-cell-title">Villes Europe &amp; France<div style="font-size:9px;font-weight:400;color:#94a3b8;text-transform:none;letter-spacing:0;">refRow France &amp; Méd. Europe sticky · ⛶ plein écran · scroll horizontal</div></div>
<div id="tbl-france-eur" style="min-height:260px;"></div>
</div>

<div class="pbnb-top-cell">
<div class="pbnb-top-cell-title">Pression &amp; concentration de l'offre<div style="font-size:9px;font-weight:400;color:#94a3b8;text-transform:none;letter-spacing:0;">‰ ann./hab. dense (x) × % ann. multi-hôtes ≥2 (y) · France en jaune · molette = zoom</div></div>
<div id="scat-fr-eur" style="min-height:340px;"></div>
</div>

</div>

```js
// Couleurs sous-régions + France distincte (pastille orange)
const CONT_DETAIL_COL = {
  "France": "#fbbf24",
  "Europe West & North": "#1696d2",
  "Europe South & East": "#a63d5a",
  "Europe Central": "#fdbf11",
  "North America": "#ca5800",
  "Latin America": "#fdbf11",
  "Asia": "#55b748",
  "Oceania": "#0d6a5e",
  "Africa": "#9a3412",
  "Europe": "#1696d2"
};
window.CONT_COL = CONT_DETAIL_COL;

// Couleurs par ville française (pour onglet France IRIS)
// Palette focus 5 villes : Paris cyan → Lyon gris → Bordeaux gris clair → BAB jaune
const VILLE_FR_COL = {
  "paris": "#1696d2",       // cyan
  "lyon": "#64748b",        // gris
  "bordeaux": "#cbd5e1",    // gris clair
  "pays-basque": "#fbbf24", // jaune
  "biarritz": "#fbbf24",
  "bayonne": "#fbbf24",
  "anglet": "#fbbf24"
};
// Teintes claires pour fond des cell-heads (même logique)
const VILLE_FR_BG = {
  "paris": "#e3f2fb",
  "lyon": "#eef1f5",
  "bordeaux": "#f4f6f8",
  "bab": "#fef6da"
};
```

```js
// Tableau Europe + France (refs France + Médiane Europe sticky)
{
  const tblC = document.getElementById("tbl-france-eur");
  if (tblC) {
    tblC.innerHTML = "";
    // IMPORTANT : exclure FRA de eur sinon Paris/Lyon/Bdx apparaissent en doublon
    const eur = (kpiCityGeo || []).filter(d =>
      (d.continent === "Europe" || (d.continent_detail || "").startsWith("Europe"))
      && d.country_code !== "FRA"
    );
    // France en haut puis Europe — pastille par pays (country_code)
    const rows = [
      { ...(parisCity || {}), libelle: "Paris", country_code: "FRA" },
      { ...(lyonCity || {}), libelle: "Lyon", country_code: "FRA" },
      { ...(bdxCity || {}), libelle: "Bordeaux", country_code: "FRA" },
      babAgg ? { ...babAgg, country_code: "FRA" } : null,
      ...eur.map(d => ({ ...d, libelle: d.libelle || d.city_fr || d.city })),
    ].filter(Boolean);

    // Palette pays auto (FRA en jaune Airbnb)
    const countries = [...new Set(rows.map(d => d.country_code).filter(Boolean))];
    const palette = d3.schemeTableau10.concat(["#9333ea","#ec4899","#0891b2","#65a30d","#dc2626"]);
    const COUNTRY_COL = { "FRA": "#fbbf24" };
    let pi = 0;
    countries.forEach(c => {
      if (!COUNTRY_COL[c]) { COUNTRY_COL[c] = palette[pi % palette.length]; pi++; }
    });

    // refRows : France (orange clair) + Méd. Europe (bleu clair, pas jaune)
    const refRows = [];
    if (franceRow) refRows.push({ label: "France", data: franceRow, bgColor: "#fed7aa" });
    if (europeRow) refRows.push({ label: "Méd. Europe", data: europeRow, bgColor: "#dbeafe" });

    buildDataTable(tblC, rows, {
      ddict: DDICT,
      keys: ["vol_n_ann","px_entire_med","cr_offre_1plus","prs_listings_1000hab_dense","str_entire_pct","cr_offre_5plus","cr_offre_top10pct_pct","act_revenu_med","actrv_note_glb"],
      labelCol: "libelle", labelHeader: "Ville",
      colorCol: "country_code", colorMap: COUNTRY_COL,
      defaultSort: "vol_n_ann", maxHeight: 360,
      barMode: "fill",
      groups: [
        { label: "Vol", cols: ["vol_n_ann","px_entire_med","cr_offre_1plus"] },
        { label: "Pression", cols: ["prs_listings_1000hab_dense","str_entire_pct"] },
        { label: "Pro", cols: ["cr_offre_5plus","cr_offre_top10pct_pct"] },
        { label: "Act", cols: ["act_revenu_med","actrv_note_glb"] }
      ],
      refRows,
      expandable: true
    });
  }
}
```

```js
// Scatter dense — tout gris sauf villes France en jaune, sans légende
{
  const c = document.getElementById("scat-fr-eur");
  if (c) {
    c.innerHTML = "";

    const eur = (kpiCityGeo || []).filter(d => d.continent === "Europe");
    const fr4 = [
      parisCity && { ...parisCity, city_fr: "Paris", country_code: "FRA" },
      lyonCity && { ...lyonCity, city_fr: "Lyon", country_code: "FRA" },
      bdxCity && { ...bdxCity, city_fr: "Bordeaux", country_code: "FRA" },
      babAgg && { ...babAgg, city_fr: "BAB", country_code: "FRA" },
    ].filter(Boolean);

    // Enrichir avec flag _grp = FR / Autre
    const data = [...eur, ...fr4].map(d => ({
      ...d,
      _grp: d.country_code === "FRA" ? "FR" : "Autre"
    }));

    const labelSet = new Set(["Paris", "Lyon", "Bordeaux", "BAB"]);

    createScatterWithZoom({
      Plot, d3,
      container: c,
      data,
      xCol: "prs_listings_1000hab_dense",
      yCol: "cr_offre_1plus",
      sizeCol: "vol_n_ann",
      colorCol: "_grp",
      colorMap: { "FR": "#fbbf24", "Autre": "#cbd5e1" },
      labelCol: "city_fr",
      labelFallback: "city",
      labelQuantile: 0.90,
      labelSet,
      width: c.clientWidth || 360,
      height: 340,
      showMeans: true,
      showRegression: false,
      showLegend: false,
      axisLabelMode: "medium",
      fontSize: 10,
      labelFontSize: 10
    });
  }
}
```

```js
// Carte Europe bulles (volume listings, 4 villes FR en jaune, sans labels MapLibre)
const europeMapRef = await (async () => {
  const container = document.getElementById("mc-europe-fr");
  if (!container || container._mapReady) return container?._ref;

  const eur = (kpiCityGeo || []).filter(d =>
    d.continent === "Europe" && d.lat != null && d.lon != null
  );

  const { map, Popup } = await createOTTDMap(container, { maxZoom: 8 });
  await new Promise(r => { if (map.loaded()) r(); else map.on("load", r); });

  // Masquer labels MapLibre (noms villes/pays)
  try {
    const layers = map.getStyle().layers || [];
    layers.forEach(l => {
      if (l.type === "symbol") map.setLayoutProperty(l.id, "visibility", "none");
    });
  } catch (e) {}

  const geo = { type: "FeatureCollection", features: eur.map(d => ({
    type: "Feature",
    geometry: { type: "Point", coordinates: [+d.lon, +d.lat] },
    properties: { ...d, _isFr: d.country_code === "FRA" ? 1 : 0 }
  }))};
  map.addSource("eur-cities", { type: "geojson", data: geo });

  const maxL = Math.max(...eur.map(d => +d.vol_n_ann || 0)) || 1;
  map.addLayer({
    id: "eur-circles", type: "circle", source: "eur-cities",
    paint: {
      "circle-radius": ["interpolate", ["linear"],
        ["sqrt", ["/", ["to-number", ["get", "vol_n_ann"], 0], maxL]],
        0, 2, 0.2, 4, 0.5, 7, 1, 14],
      "circle-color": ["case", ["==", ["get", "_isFr"], 1], "#fbbf24", "#94a3b8"],
      "circle-opacity": 0.85,
      "circle-stroke-color": "#fff",
      "circle-stroke-width": ["case", ["==", ["get", "_isFr"], 1], 1.5, 0.6]
    }
  });

  // Top 10 villes (par volume) + France toutes
  const top10 = [...eur].sort((a,b) => (+b.vol_n_ann || 0) - (+a.vol_n_ann || 0)).slice(0, 10);
  const topSet = new Set([...top10.map(d => d.city), ...eur.filter(d => d.country_code === "FRA").map(d => d.city)]);
  const topGeo = { type: "FeatureCollection", features: eur.filter(d => topSet.has(d.city)).map(d => ({
    type: "Feature",
    geometry: { type: "Point", coordinates: [+d.lon, +d.lat] },
    properties: { _label: d.city_fr || d.city, _isFr: d.country_code === "FRA" ? 1 : 0 }
  }))};
  map.addSource("eur-labels", { type: "geojson", data: topGeo });
  map.addLayer({
    id: "eur-labels", type: "symbol", source: "eur-labels",
    layout: {
      "text-field": ["get", "_label"],
      "text-size": 9,
      "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
      "text-anchor": "left",
      "text-offset": [0.7, 0],
      "text-padding": 2,
      "text-allow-overlap": false
    },
    paint: {
      "text-color": ["case", ["==", ["get", "_isFr"], 1], "#92400e", "#374151"],
      "text-halo-color": "rgba(255,255,255,0.92)",
      "text-halo-width": 1.5
    }
  });

  // Tooltip via helper unifié
  const _fN = n => n != null && !isNaN(+n) ? Math.round(+n).toLocaleString("fr-FR") : "—";
  map.on("mousemove", "eur-circles", (e) => {
    const p = e.features[0].properties;
    map.getCanvas().style.cursor = "pointer";
    const html =
      tooltipHeader({ title: p.city_fr || p.city, subtitle: p.country_code || "" }) +
      tooltipMetric({ label: "Annonces actives", value: _fN(p.vol_n_ann) }) +
      tooltipMeta([
        `Prix méd. ${_fN(p.px_entire_med)} €/nuit`,
        p.cr_offre_1plus != null ? `Multi-hôtes ${(+p.cr_offre_1plus).toFixed(0)}%` : null
      ].filter(Boolean));
    showTooltip(e.originalEvent, html);
  });
  map.on("mouseleave", "eur-circles", () => {
    map.getCanvas().style.cursor = "";
    hideTooltip();
  });

  map.fitBounds([[-12, 35], [40, 60]], { padding: 6, duration: 0 });

  const ref = { map, container, Popup };
  container._mapReady = true;
  container._ref = ref;
  return ref;
})();
```

```js
// Recolore les bulles Europe selon l'indicateur sélectionné (taille = volume conservée)
// → lien entre le menu Indicateur et la carte Europe
{
  const ref = europeMapRef;
  if (ref?.map && indicateur) {
    const eur = (kpiCityGeo || []).filter(d => d.continent === "Europe" && d.lat != null && d.lon != null);
    const vals = eur.map(d => +d[indicateur]).filter(v => !isNaN(v));
    const dd = window.DDICT?.[indicateur] || {};
    if (vals.length > 5) {
      const bins = autoBins(vals, indicateur);
      const getCol = makeGetColor(bins);
      const geo = { type: "FeatureCollection", features: eur.map(d => {
        const v = +d[indicateur];
        return {
          type: "Feature",
          geometry: { type: "Point", coordinates: [+d.lon, +d.lat] },
          properties: { ...d, _isFr: d.country_code === "FRA" ? 1 : 0,
            _fill: !isNaN(v) ? getCol(v) : "#cbd5e1" }
        };
      })};
      const src = ref.map.getSource("eur-cities");
      if (src) src.setData(geo);
      // Couleur = indicateur ; France repérée par contour jaune épais
      ref.map.setPaintProperty("eur-circles", "circle-color", ["coalesce", ["get", "_fill"], "#94a3b8"]);
      ref.map.setPaintProperty("eur-circles", "circle-stroke-color",
        ["case", ["==", ["get", "_isFr"], 1], "#f59e0b", "#ffffff"]);
      ref.map.setPaintProperty("eur-circles", "circle-stroke-width",
        ["case", ["==", ["get", "_isFr"], 1], 2.5, 0.6]);
      // Met à jour le sous-titre de la cellule
      const titleEl = document.querySelector("#mc-europe-fr")?.previousElementSibling?.querySelector("div");
      if (titleEl) titleEl.textContent = `${dd.label || indicateur} · taille = volume · France contour jaune`;
    }
  }
}
```

<!-- &e TOP_BLOCK -->

<!-- &s CADRAGE_FR - Bannière France L1 -->
<div class="pbnb-cadrage" style="margin:14px 0 4px;">
  <div class="pbnb-cadrage-title">Cadrage France</div>
  <div class="pbnb-cadrage-sub">profil agrégé des 4 villes France · 6 zones (Paris · Lyon · Bordeaux · Biarritz · Anglet · Bayonne)</div>
</div>

<!-- &s KPI_FR_HERO - Gros chiffres clés France (markup pbnb-kpi-hero + refs Europe) -->
<div id="kpi-fr-hero" class="pbnb-kpi-hero"></div>

```js
{
  const c = document.getElementById("kpi-fr-hero");
  if (c && franceRow) {
    c.innerHTML = "";
    const fN = n => n != null && !isNaN(+n) ? Math.round(+n).toLocaleString("fr-FR") : "—";
    const fP = n => n != null && !isNaN(+n) ? Math.round(+n) + " %" : "—";
    const f1 = n => n != null && !isNaN(+n) ? (+n).toFixed(1) : "—";
    // Réf Europe entre parenthèses — valeur light SANS préfixe (note unique le précise)
    const e = europeRow || {};
    const refP = n => n != null && !isNaN(+n) ? Math.round(+n) + " %" : null;
    const refE = n => n != null && !isNaN(+n) ? Math.round(+n).toLocaleString("fr-FR") + " €" : null;
    const ref1 = n => n != null && !isNaN(+n) ? (+n).toFixed(1) : null;
    const ann1kLog = (franceRow.vol_n_ann && franceRow.housing_total)
      ? franceRow.vol_n_ann / franceRow.housing_total * 1000 : null;

    // 4 groupes : profil marché · pression · pro · activité
    const groups = [
      {
        label: "Profil marché",
        items: [
          { v: fN(franceRow.vol_n_ann), l: "annonces actives", phrase: "total 4 villes" },
          { v: fN(franceRow.px_entire_med) + " €", l: "prix médian / nuit", phrase: "logement entier", accent: true, ref: refE(e.px_entire_med) },
          { v: fP(franceRow.str_entire_pct), l: "% logements entiers", phrase: "vs chambres / partagés", ref: refP(e.str_entire_pct) },
        ]
      },
      {
        label: "Pression territoriale",
        items: [
          { v: f1(franceRow.prs_listings_1000hab_dense), l: "‰ ann. / hab. dense", phrase: "intensité zone dense", ref: ref1(e.prs_listings_1000hab_dense) },
          { v: f1(ann1kLog), l: "‰ ann. / 1 000 log.", phrase: "pression parc total" },
        ]
      },
      {
        label: "Professionnalisation",
        items: [
          { v: fP(franceRow.cr_offre_1plus), l: "% multi-hôtes (≥2)", phrase: "hôtes gérant 2+ annonces", ref: refP(e.cr_offre_1plus) },
          { v: fP(franceRow.cr_offre_5plus || franceRow.cr_offre_5plus_pct), l: "% ann. hôtes ≥5", phrase: "offre semi-pro", ref: refP(e.cr_offre_5plus) },
          { v: fP(franceRow.cr_offre_top10pct_pct), l: "CR top 10 % hôtes", phrase: "concentration offre", ref: refP(e.cr_offre_top10pct_pct) },
        ]
      },
      {
        label: "Activité",
        items: [
          { v: fP(franceRow.str_minnuits30_pct), l: "% longue durée", phrase: "≥ 30 nuits min.", ref: refP(e.str_minnuits30_pct) },
          { v: fN(franceRow.act_revenu_med) + " €", l: "revenu annuel médian", phrase: "estim. par annonce", accent: true, ref: refE(e.act_revenu_med) },
        ]
      }
    ];

    // Rendu inline (markup pbnb-kpi-hero d'origine) + ref Europe en (petit gris)
    for (const g of groups) {
      const gDiv = document.createElement("div");
      gDiv.className = "pbnb-kpi-hero-group";
      gDiv.innerHTML = `<span class="pbnb-kpi-hero-group-label">${g.label}</span>`;
      const itDiv = document.createElement("div");
      itDiv.className = "pbnb-kpi-hero-group-items";
      for (const it of g.items) {
        const d = document.createElement("div");
        d.className = "pbnb-kpi-hero-item";
        const refHtml = it.ref ? `<span class="pbnb-kpi-hero-ref">(${it.ref})</span>` : "";
        d.innerHTML = `<span class="pbnb-kpi-hero-val${it.accent ? ' accent' : ''}">${it.v}${refHtml}</span>` +
          `<span class="pbnb-kpi-hero-lbl">${it.l}</span>` +
          `<span class="pbnb-kpi-hero-phrase">${it.phrase}</span>`;
        itDiv.appendChild(d);
      }
      gDiv.appendChild(itDiv);
      c.appendChild(gDiv);
    }
    // Note unique : précise ce que les parenthèses signifient
    c.style.position = "relative";
    const note = document.createElement("div");
    note.className = "pbnb-kpi-hero-refnote";
    note.innerHTML = `<span style="opacity:0.6">(&nbsp;)</span> = médiane Europe`;
    c.appendChild(note);
  }
}
```

<!-- &e KPI_FR_HERO -->

<!-- &s SMALL_MULT - Ligne 6 small multiples sur villes France -->

<div class="pbnb-subhead">Profil des villes françaises<span class="pbnb-subhead-sub"> · trait pointillé rouge = médiane des 6 villes affichées</span></div>

<div id="small-mult-row" style="display:grid; grid-template-columns:1.3fr 1fr 1fr 1fr 1fr 1.2fr; gap:0; margin:0 0 12px;"></div>

```js
// Grid small-multiples villes France — via helper jcn-graph-smallmultojs (factorisé)
{
  const row = document.getElementById("small-mult-row");
  if (row) {
    const villesFr = [
      parisCity && { ...parisCity, libelle: "Paris" },
      lyonCity && { ...lyonCity, libelle: "Lyon" },
      bdxCity && { ...bdxCity, libelle: "Bordeaux" },
      ...babCities.map(d => ({ ...d, libelle: d.city[0].toUpperCase() + d.city.slice(1) }))
    ].filter(Boolean);

    createSmallMultGrid({
      container: row, Plot, d3, ddict: DDICT,
      data: villesFr, labelKey: "libelle",
      panels: [
        { key: "vol_n_ann" },
        { key: "px_entire_med" },
        { key: "str_entire_pct" },
        { key: "cr_offre_1plus" },
        { key: "cr_offre_top10pct_pct" },
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

<!-- &e SMALL_MULT -->

<!-- &s GLOBAL_BINS - Bins synchronisés sur les 4 villes -->

```js
// Calcule bins sur l'ensemble des 4 villes pour la maille active
const _binsGlobal = (() => {
  const isIris = maille === "iris";
  const datasets = isIris
    ? [parisIrisData, lyonIrisData, bdxIrisData, babIrisData]
    : [parisArrData, lyonArrData, bdxIrisData, babCities];
  const allVals = [];
  for (const ds of datasets) {
    for (const r of (ds || [])) {
      const v = +r[indicateur];
      if (!isNaN(v) && v != null) allVals.push(v);
    }
  }
  return allVals.length > 5 ? autoBins(allVals, indicateur) : null;
})();
const _getColorGlobal = _binsGlobal ? makeGetColor(_binsGlobal) : () => "#ccc";
```

<!-- &e GLOBAL_BINS -->

<!-- &s FOCUS_HEAD - Header du bloc focus France 2x2 -->
<div class="pbnb-subhead">Focus France · IRIS<span class="pbnb-subhead-sub"> · choroplèthe synchronisée 4 villes · bins communs</span></div>

<!-- &s SHARED_LEGEND -->
<div id="legend-shared" class="pbnb-legend-shared"></div>

```js
{
  const c = document.getElementById("legend-shared");
  if (c) {
    c.innerHTML = "";
    const dd = window.DDICT?.[indicateur] || {};
    // Warning si bins null (indicateur indispo à cette maille)
    if (!_binsGlobal) {
      c.innerHTML = `<span style="color:#b45309;font-weight:600;">⚠ « ${dd.label || indicateur} » non disponible à la maille « ${maille === "iris" ? "IRIS" : "Arr/Commune"} » — choisir une autre maille ou un autre indicateur (les indicateurs de pression existent uniquement à la ville).</span>`;
    } else {
    const lab = document.createElement("span");
    lab.style.cssText = "margin-right:10px; font-weight:600; color:#0a4c6a;";
    lab.textContent = `${dd.label || indicateur}${dd.unit ? " · " + dd.unit : ""} — bins synchro 4 villes`;
    c.appendChild(lab);
    c.appendChild(createBinsLegendBar({
      colors: _binsGlobal.palette, thresholds: _binsGlobal.thresholds,
      counts: _binsGlobal.counts, unit: dd.unit || "",
      echelonValue: _binsGlobal.mean, echelonLabel: "Moy. France"
    }));
    }
  }
}
```

<!-- &e SHARED_LEGEND -->

<!-- &s GRID_2X2 - 4 cartes côte à côte -->
<div class="pbnb-grid2x2">

<div class="pbnb-cell">
<div class="pbnb-cell-head" style="background:#e3f2fb;border-left:4px solid #1696d2;">
<div class="pbnb-cell-title">Paris<span class="pbnb-cell-sub"> · 20 arr.</span></div>
<div id="kpi-paris" style="flex:1;"></div>
</div>
<div id="mc-paris" class="pbnb-cell-map"></div>
</div>

<div class="pbnb-cell">
<div class="pbnb-cell-head" style="background:#eef1f5;border-left:4px solid #64748b;">
<div class="pbnb-cell-title">Lyon<span class="pbnb-cell-sub"> · 9 arr.</span></div>
<div id="kpi-lyon" style="flex:1;"></div>
</div>
<div id="mc-lyon" class="pbnb-cell-map"></div>
</div>

<div class="pbnb-cell">
<div class="pbnb-cell-head" style="background:#f4f6f8;border-left:4px solid #cbd5e1;">
<div class="pbnb-cell-title">Bordeaux<span class="pbnb-cell-sub"> · IRIS</span></div>
<div id="kpi-bdx" style="flex:1;"></div>
</div>
<div id="mc-bdx" class="pbnb-cell-map"></div>
</div>

<div class="pbnb-cell">
<div class="pbnb-cell-head" style="background:#fef6da;border-left:4px solid #fbbf24;">
<div class="pbnb-cell-title">Biarritz · Anglet · Bayonne<span class="pbnb-cell-sub"> · Pays Basque</span></div>
<div id="kpi-bab" style="flex:1;"></div>
</div>
<div id="mc-bab" class="pbnb-cell-map"></div>
</div>

</div>
<!-- &e GRID_2X2 -->

<!-- &s KPI_STRIPS - 4 KPI strips réactifs -->

```js
{
  // Tous entiers, pas de décimale — modèle hero compact (strip)
  const fI = n => n != null && !isNaN(+n) ? Math.round(+n).toLocaleString("fr-FR") : "—";
  const pI = n => n != null && !isNaN(+n) ? Math.round(+n) + " %" : "—";
  // Même ordre que l'agrégat France/Europe/Monde : profil → pression → pro → activité
  const f1 = n => n != null && !isNaN(+n) ? (+n).toFixed(1) : "—";
  const items = (d) => d ? [
    { v: fI(d.vol_n_ann), l: "Annonces" },
    { v: fI(d.px_entire_med) + " €", l: "Prix entier", accent: true },
    { v: pI(d.str_entire_pct), l: "% entiers" },
    { v: f1(d.prs_listings_1000hab_dense), l: "‰ ann./hab" },
    { v: pI(d.cr_offre_1plus), l: "% multi (≥2)" },
    { v: pI(d.cr_offre_5plus), l: "% ≥5" },
    { v: fI(d.act_revenu_med) + " €", l: "Revenu/an", accent: true },
  ] : [];
  const cellKpi = (id, data) => {
    const c = document.getElementById(id);
    if (!c) return;
    c.innerHTML = "";
    c.appendChild(createKpiHero({ items: items(data), strip: true }));
  };

  cellKpi("kpi-paris", parisCity);
  cellKpi("kpi-lyon", lyonCity);
  cellKpi("kpi-bdx", bdxCity);
  cellKpi("kpi-bab", babAgg);
}
```

<!-- &e KPI_STRIPS -->

<!-- &s MAP_HELPER - Factorise l'init et l'update d'une carte ville -->

```js
// Helper réutilisable : crée la carte une fois, expose ref
async function ensureCityMap({ containerId, sourceId, bounds, overlayGeo, overlayLabels, fitPadding = 20 }) {
  const container = document.getElementById(containerId);
  if (!container || container._mapReady) return container?._ref;

  const { map, Popup } = await createOTTDMap(container, { maxZoom: 16 });
  await new Promise(r => { if (map.loaded()) r(); else map.on("load", r); });

  map.addSource(sourceId, { type: "geojson", data: { type: "FeatureCollection", features: [] } });
  map.addLayer({ id: sourceId + "-fill", type: "fill", source: sourceId,
    paint: { "fill-color": ["get", "_fill"], "fill-opacity": 0.88 } });
  map.addLayer({ id: sourceId + "-line", type: "line", source: sourceId,
    paint: { "line-color": "#e0e3e8", "line-width": 0.3 } });
  map.addLayer({ id: sourceId + "-hover", type: "fill", source: sourceId,
    paint: { "fill-color": "#ffd700", "fill-opacity": 0.3 },
    filter: ["==", ["get", "_code"], ""] });

  if (overlayGeo) {
    map.addSource(sourceId + "-ov", { type: "geojson", data: overlayGeo });
    // Contour communes/arrondissements — un peu plus marqué (lisibilité limites)
    map.addLayer({ id: sourceId + "-ov-line", type: "line", source: sourceId + "-ov",
      paint: { "line-color": "#475569", "line-width": 1.6, "line-opacity": 0.8 } });
  }

  if (overlayLabels) {
    map.addSource(sourceId + "-lbl", { type: "geojson", data: overlayLabels });
    map.addLayer({ id: sourceId + "-lbl-symbol", type: "symbol", source: sourceId + "-lbl",
      layout: { "text-field": ["get", "_label"], "text-size": 10,
        "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
        "text-anchor": "center", "text-padding": 4 },
      paint: { "text-color": "#374151",
        "text-halo-color": "rgba(255,255,255,0.85)", "text-halo-width": 1.5 }
    });
  }

  // Tooltip IRIS via helper unifié — _tooltipFn (props) => htmlString
  container._tooltipFn = () => "";
  map.on("mousemove", sourceId + "-fill", e => {
    if (!e.features?.length) return;
    const f = e.features[0];
    map.setFilter(sourceId + "-hover", ["==", ["get", "_code"], f.properties._code || ""]);
    const html = container._tooltipFn(f.properties, e.lngLat);
    if (html) showTooltip(e.originalEvent, html);
  });
  map.on("mouseleave", sourceId + "-fill", () => {
    map.setFilter(sourceId + "-hover", ["==", ["get", "_code"], ""]);
    hideTooltip();
  });

  if (bounds?.bounds) map.fitBounds(bounds.bounds, { padding: fitPadding, duration: 0 });

  const ref = { map, container, Popup, sourceId };
  container._mapReady = true;
  container._ref = ref;
  return ref;
}

// Helper update : nourrit la source + tooltip + légende per-carte (bins globaux)
function updateCityMap({ ref, geo, dataMapGeo, codeProp, indicateur, isAgg }) {
  if (!ref?.map) return;
  for (const [code, row] of dataMapGeo) {
    if (!row.libelle) row.libelle = row.nom_iris || row.territory || code;
  }
  const enriched = buildChoroplethSource(geo.features, dataMapGeo, indicateur, _getColorGlobal,
    { codeProperty: codeProp, extraProps: ["nom_iris", "territory"] });
  const src = ref.map.getSource(ref.sourceId);
  if (src) src.setData(enriched);
  ref.map.setPaintProperty(ref.sourceId + "-fill", "fill-opacity", isAgg ? 1.0 : 0.88);

  ref.container._tooltipFn = (props) => {
    const label = props._label || props._code || "?";
    const val = props._val;
    const dd = window.DDICT?.[indicateur] || {};
    const valStr = val != null ? (dd.type === "pct" ? (+val).toFixed(1) + "%" : Number(+val).toLocaleString("fr-FR")) : "n.d.";
    return tooltipHeader({ title: label }) +
      tooltipMetric({ label: dd.short || indicateur, value: valStr }) +
      (dd.desc ? tooltipMeta([dd.desc]) : "");
  };

  // Légende per-carte (basée sur bins globaux 4 villes)
  if (_binsGlobal) {
    const dd = window.DDICT?.[indicateur] || {};
    setMapLegend(ref.container, createBinsLegendBar({
      colors: _binsGlobal.palette, thresholds: _binsGlobal.thresholds,
      counts: _binsGlobal.counts, unit: dd.unit || ""
    }));
  }

  // Top 3 / Bottom 3 — bandeau bas pleine largeur (pas une bulle à gauche), format classement
  {
    const dd = window.DDICT?.[indicateur] || {};
    const arr = [];
    for (const [code, row] of dataMapGeo) {
      const v = +row[indicateur];
      if (!isNaN(v)) arr.push({ label: row.libelle, val: v });
    }
    if (arr.length >= 6) {
      arr.sort((a, b) => b.val - a.val);
      const top3 = arr.slice(0, 3);
      const bot3 = arr.slice(-3).reverse();  // plus bas en premier
      const fmtV = v => dd.type === "pct" ? v.toFixed(0) + "%" : Math.round(v).toLocaleString("fr-FR");
      let ov = ref.container.querySelector(".pbnb-topbot");
      if (!ov) {
        ov = document.createElement("div");
        ov.className = "pbnb-topbot";
        ov.style.cssText = "position:absolute; bottom:0; left:0; right:0; z-index:5; " +
          "background:rgba(255,255,255,0.92); padding:5px 10px; " +
          "font-size:11px; line-height:1.5; box-shadow:0 -1px 4px rgba(0,0,0,0.1); " +
          "border-top:2px solid #fbbf24;";
        ref.container.appendChild(ov);
      }
      const itemHtml = (r, rk, col) =>
        `<span style="white-space:nowrap;"><span style="color:${col};font-weight:700;">${rk}.</span> ` +
        `<span style="color:#1f2937;">${r.label}</span> <b style="color:#0a4c6a;">${fmtV(r.val)}</b></span>`;
      const sep = '<span style="color:#cbd5e1;margin:0 8px;">·</span>';
      ov.innerHTML =
        `<div><span style="color:#16a34a;font-weight:700;margin-right:6px;">▲ Top 3</span>` +
        top3.map((r, i) => itemHtml(r, i + 1, "#16a34a")).join(sep) + `</div>` +
        `<div><span style="color:#dc2626;font-weight:700;margin-right:6px;">▼ Bottom 3</span>` +
        bot3.map((r, i) => itemHtml(r, "n-" + (i + 1), "#dc2626")).join(sep) + `</div>`;
    }
  }
}
```

<!-- &e MAP_HELPER -->

<!-- &s MAPS_INIT - 4 cartes initialisées une fois -->

```js
// Paris : avec overlay arr + labels
const parisOvLabels = {
  type: "FeatureCollection",
  features: geoParisArr.features.map(f => {
    const num = parseInt(f.properties.arr_code.slice(3));
    return { type: "Feature", geometry: { type: "Point", coordinates: d3.geoCentroid(f) },
      properties: { _label: num === 1 ? "1er" : num + "e" } };
  })
};
const parisRef = await ensureCityMap({ containerId: "mc-paris", sourceId: "paris",
  bounds: parisBounds, overlayGeo: geoParisArr, overlayLabels: parisOvLabels });
```

```js
// Lyon
const lyonOvLabels = {
  type: "FeatureCollection",
  features: geoLyonArr.features.map(f => {
    const num = parseInt(f.properties.arr_code.slice(3));
    return { type: "Feature", geometry: { type: "Point", coordinates: d3.geoCentroid(f) },
      properties: { _label: num === 1 ? "1er" : num + "e" } };
  })
};
const lyonRef = await ensureCityMap({ containerId: "mc-lyon", sourceId: "lyon",
  bounds: lyonBounds, overlayGeo: geoLyonArr, overlayLabels: lyonOvLabels, fitPadding: 6 });
```

```js
// Bordeaux : pas d'overlay arr
const bdxRef = await ensureCityMap({ containerId: "mc-bdx", sourceId: "bdx",
  bounds: bdxBounds });
```

```js
// BAB : overlay communes + labels
const COM_NAMES = { "64102": "Bayonne", "64122": "Biarritz", "64024": "Anglet" };
const babOvLabels = {
  type: "FeatureCollection",
  features: geoBabCom.features.map(f => ({
    type: "Feature", geometry: { type: "Point", coordinates: d3.geoCentroid(f) },
    properties: { _label: COM_NAMES[f.properties.com_code] || f.properties.com_code }
  }))
};
const babRef = await ensureCityMap({ containerId: "mc-bab", sourceId: "bab",
  bounds: babBounds, overlayGeo: geoBabCom, overlayLabels: babOvLabels });
```

<!-- &e MAPS_INIT -->

<!-- &s MAPS_UPDATE - Update réactif des 4 cartes (1 seul block) -->

```js
{
  const isIris = maille === "iris";

  // Paris
  if (parisRef?.map) {
    const geo = isIris ? geoParisIris : geoParisArr;
    const data = isIris ? parisIrisData : parisArrData;
    const codeProp = isIris ? "code_iris" : "arr_code";
    const dataMapGeo = new Map();
    if (isIris) {
      for (const d of data) { if (d.code_iris) dataMapGeo.set(d.code_iris, d); }
    } else {
      for (let i = 1; i <= 20; i++) {
        const suffix = i === 1 ? "1er" : i + "e";
        const geoCode = "751" + String(i).padStart(2, "0");
        const row = parisArrData.find(d => d.territory === "paris_" + suffix);
        if (row) dataMapGeo.set(geoCode, row);
      }
    }
    updateCityMap({ ref: parisRef, geo, dataMapGeo, codeProp, indicateur, isAgg: !isIris });
  }

  // Lyon
  if (lyonRef?.map) {
    const geo = isIris ? geoLyonIris : geoLyonArr;
    const data = isIris ? lyonIrisData : lyonArrData;
    const codeProp = isIris ? "code_iris" : "arr_code";
    const dataMapGeo = new Map();
    if (isIris) {
      for (const d of data) { if (d.code_iris) dataMapGeo.set(d.code_iris, d); }
    } else {
      for (let i = 1; i <= 9; i++) {
        const suffix = i === 1 ? "1er" : i + "e";
        const geoCode = "6938" + String(i);
        const row = lyonArrData.find(d => d.territory === "lyon_" + suffix);
        if (row) dataMapGeo.set(geoCode, row);
      }
    }
    updateCityMap({ ref: lyonRef, geo, dataMapGeo, codeProp, indicateur, isAgg: !isIris });
  }

  // Bordeaux : toujours IRIS
  if (bdxRef?.map) {
    const data = bdxIrisData;
    const dataMapGeo = new Map();
    for (const d of data) { if (d.code_iris) dataMapGeo.set(d.code_iris, d); }
    updateCityMap({ ref: bdxRef, geo: geoBdxIris, dataMapGeo, codeProp: "code_iris", indicateur, isAgg: false });
  }

  // BAB
  if (babRef?.map) {
    const geo = isIris ? geoBabIris : geoBabCom;
    const data = isIris ? babIrisData : babCities;
    const codeProp = isIris ? "code_iris" : "com_code";
    const dataMapGeo = new Map();
    if (isIris) {
      for (const d of data) { if (d.code_iris) dataMapGeo.set(d.code_iris, d); }
    } else {
      const COM_MAP = { "64102": "bayonne", "64122": "biarritz", "64024": "anglet" };
      for (const [code, terr] of Object.entries(COM_MAP)) {
        const row = babCities.find(d => d.city === terr);
        if (row) dataMapGeo.set(code, row);
      }
    }
    updateCityMap({ ref: babRef, geo, dataMapGeo, codeProp, indicateur, isAgg: !isIris });
  }
}
```

<!-- &e MAPS_UPDATE -->

<!-- &s QUARTIER_TABS - Tableaux IRIS : France (toutes) + Paris/Lyon/Bordeaux/BAB -->
<div class="pbnb-quartier-tabs">
<div class="pbnb-tabs-head" id="qtabs-head"></div>
<div class="pbnb-tab-body" id="qtabs-body" style="min-height:320px;"></div>
</div>

```js
{
  const head = document.getElementById("qtabs-head");
  const body = document.getElementById("qtabs-body");
  if (head && body) {

  const isIris = maille === "iris";

  // Enrichir chaque ligne avec city_label + pastille couleur via colorMap
  function enrich(rows, cityLabel) {
    return rows.map(d => ({
      ...d,
      _city: cityLabel || d.city,
      _city_label: cityLabel ? cityLabel[0].toUpperCase() + cityLabel.slice(1) : (d.city || "")
    }));
  }

  // Données par ville
  const dParis = isIris ? enrich(parisIrisData, "paris") : enrich(parisArrData, "paris");
  const dLyon = isIris ? enrich(lyonIrisData, "lyon") : enrich(lyonArrData, "lyon");
  const dBdx = enrich(bdxIrisData, "bordeaux");
  const dBab = isIris ? enrich(babIrisData, "pays-basque") : enrich(babCities, "pays-basque");
  const dAll = [...dParis, ...dLyon, ...dBdx, ...dBab];

  // 5 onglets : France (tous) + 4 villes — France au début
  const tabs = [
    { id: "france", label: "🇫🇷 France · " + dAll.length, data: dAll,
      labelCol: "nom_iris", labelFallback: "territory",
      labelHeader: isIris ? "IRIS (toutes villes)" : "Arr./Com.",
      colorCol: "_city", showCity: true },
    { id: "paris", label: "Paris · " + dParis.length, data: dParis,
      labelCol: isIris ? "nom_iris" : "territory",
      labelHeader: isIris ? "IRIS Paris" : "Arrondissement",
      colorCol: null },
    { id: "lyon", label: "Lyon · " + dLyon.length, data: dLyon,
      labelCol: isIris ? "nom_iris" : "territory",
      labelHeader: isIris ? "IRIS Lyon" : "Arrondissement",
      colorCol: null },
    { id: "bdx", label: "Bordeaux · " + dBdx.length, data: dBdx,
      labelCol: "nom_iris", labelHeader: "IRIS Bordeaux",
      colorCol: null },
    { id: "bab", label: "BAB · " + dBab.length, data: dBab,
      labelCol: isIris ? "nom_iris" : "territory",
      labelHeader: isIris ? "IRIS Pays Basque" : "Commune",
      colorCol: null },
  ];

  const activeId = head.dataset.activeId || "france";

  head.innerHTML = "";
  for (const c of tabs) {
    const btn = document.createElement("button");
    btn.className = "pbnb-tab" + (c.id === activeId ? " active" : "");
    btn.textContent = c.label;
    btn.onclick = () => {
      head.dataset.activeId = c.id;
      head.querySelectorAll(".pbnb-tab").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderTab(c);
    };
    head.appendChild(btn);
  }

  function renderTab(c) {
    body.innerHTML = "";
    // 12 indicateurs (muscler le scroll horizontal) — virer indicateurs vides au niveau IRIS
    buildDataTable(body, c.data, {
      ddict: DDICT,
      keys: ["vol_n_ann","px_entire_med","str_entire_pct","str_minnuits30_pct","cr_offre_1plus",
             "cr_offre_5plus","str_ratio_ann_hote","act_cal_ouvert_med","act_revenu_med","actrv_note_glb"],
      labelCol: c.labelCol, labelFallback: c.labelFallback || "code_iris",
      labelHeader: c.labelHeader,
      colorCol: c.colorCol, colorMap: c.colorCol === "_city" ? VILLE_FR_COL : null,
      subLabelCol: c.colorCol === "_city" ? "_city_label" : null,
      defaultSort: indicateur, maxHeight: 380,
      barMode: "fill",
      groups: [
        { label: "Stock", cols: ["vol_n_ann"] },
        { label: "Prix", cols: ["px_entire_med"] },
        { label: "Logement", cols: ["str_entire_pct","str_minnuits30_pct"] },
        { label: "Hôtes", cols: ["cr_offre_1plus","cr_offre_5plus","str_ratio_ann_hote"] },
        { label: "Activité", cols: ["act_cal_ouvert_med","act_revenu_med","actrv_note_glb"] }
      ],
      refRows: [
        franceRow ? { label: "France", data: franceRow, bgColor: "#fed7aa" } : null,
        europeRow ? { label: "Méd. Europe", data: europeRow, bgColor: "#dbeafe" } : null
      ].filter(Boolean),
      expandable: true
    });
  }

  const active = tabs.find(c => c.id === activeId) || tabs[0];
  renderTab(active);
  }
}
```

<!-- &e QUARTIER_TABS -->
