// &s MAPLIBRE_WORLD_aaMAIN - Helper carte monde MapLibre (bubbles)
// Chargé après pbnbdash-util-helper.js (DDICT, irisBins, buildLegend, stepEx)
// Date: 2026-02-22

// &s CONT_COL - Couleurs continents
var CONT_COL = {
  "Europe": "#1696d2",
  "Americas": "#fdbf11",
  "Asia-Pacific": "#55b748",
  "Africa": "#ec008b",
  "Middle-East-Africa": "#ec008b"
};
// &e

// &s WORLD_METRICS - Indicateurs monde dérivés du DDICT
var WORLD_KEYS = [
  "n_listings", "prix_med", "pct_multi", "pct_entire", "pct_longterm",
  "listings_1000hab", "listings_1000hsg", "ratio_lh", "dispo_med", "reviews_med",
  "cr_top10_pct", "cr_host_10plus", "cr_offre_10plus", "rev_rating_med", "revenue_est_med"
];

var WORLD_METRICS = WORLD_KEYS.map(function(k) {
  var d = DDICT[k] || {};
  return {
    key: k,
    label: d.short || d.label || k,
    unit: d.unit || "",
    type: d.type || "stock"
  };
});
// &e

// &s BUILD_WORLD_MAP - Carte monde à bulles avec légende irisBins

function buildWorldMap(container, data, initialMetric) {
  var metric = initialMetric || "listings_1000hab";

  // Auto-compute bounds
  var lats = data.map(function(d) { return +d.latitude; }).filter(Boolean);
  var lngs = data.map(function(d) { return +d.longitude; }).filter(Boolean);
  var bbox = lats.length ? [
    [Math.min.apply(null, lngs) - 8, Math.min.apply(null, lats) - 8],
    [Math.max.apply(null, lngs) + 8, Math.max.apply(null, lats) + 8]
  ] : null;

  var map = new maplibregl.Map({
    container: container,
    style: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    center: [15, 25], zoom: 1.5,
    minZoom: 1, maxZoom: 12,
    attributionControl: false,
    cooperativeGestures: true,
    dragRotate: false, pitchWithRotate: false, touchPitch: false,
    renderWorldCopies: false, fadeDuration: 0
  });
  map.addControl(new maplibregl.NavigationControl({showCompass: false}), "top-right");

  // Reset button
  var resetBtn = document.createElement("button");
  resetBtn.textContent = "\u21ba";
  resetBtn.title = "Recentrer";
  resetBtn.style.cssText = "position:absolute;top:80px;right:8px;z-index:5;width:30px;height:30px;" +
    "background:white;border:1px solid #ccc;border-radius:4px;font-size:16px;cursor:pointer;" +
    "box-shadow:0 1px 2px rgba(0,0,0,0.1);display:flex;align-items:center;justify-content:center;";
  resetBtn.addEventListener("click", function() {
    if (bbox) map.fitBounds(bbox, {padding: 20, duration: 600});
    else map.flyTo({center: [15, 25], zoom: 1.5, duration: 600});
  });
  container.parentNode.appendChild(resetBtn);

  // Controls — indicator selector
  var ctrl = document.createElement("div");
  ctrl.className = "world-map-ctrl";
  var optHtml = WORLD_METRICS.map(function(m) {
    return '<option value="' + m.key + '"' + (m.key === metric ? ' selected' : '') + '>' + m.label + '</option>';
  }).join("");
  ctrl.innerHTML = '<span class="mt">Indicateur</span><select class="wm-sel">' + optHtml + '</select>';
  container.parentNode.appendChild(ctrl);

  // Legend placeholder
  var leg = document.createElement("div");
  leg.className = "bubble-legend";
  container.parentNode.appendChild(leg);

  map.on("load", function() {
    if (bbox) map.fitBounds(bbox, {padding: 20, duration: 0});

    var geo = {
      type: "FeatureCollection",
      features: data.map(function(d) {
        return {
          type: "Feature",
          geometry: {type: "Point", coordinates: [+d.longitude || 0, +d.latitude || 0]},
          properties: Object.assign({}, d)
        };
      })
    };
    map.addSource("cities", {type: "geojson", data: geo});

    // Fake features for irisBins() compatibility (needs .properties.n >= 10)
    var fakeFeats = data.map(function(d) {
      return {properties: Object.assign({n: 999}, d)};
    });

    function updateBubbles(k) {
      metric = k;
      var dd = DDICT[k] || {};
      var mInfo = WORLD_METRICS.find(function(m) { return m.key === k; }) ||
        {label: dd.short || k, unit: dd.unit || ""};

      var bins = irisBins(fakeFeats, k, "niveau", null);
      if (!bins) {
        leg.innerHTML = '<div style="font-size:10px;color:#999;">Donn\u00e9es insuffisantes</div>';
        return;
      }

      var step = stepEx(k, bins.brk, bins.col);
      step[1] = ["to-number", step[1], 0];
      map.setPaintProperty("city-circles", "circle-color", [
        "case", ["==", ["get", k], null], "#b0b0b0", step
      ]);

      leg.innerHTML = "";
      leg.appendChild(buildLegend(bins, mInfo.label, fakeFeats, k, null));
    }

    // Size by n_listings (sqrt scale) — compact bubbles
    var maxL = Math.max.apply(null, data.map(function(d) { return +d.n_listings || 0; }));

    map.addLayer({
      id: "city-circles", type: "circle", source: "cities",
      paint: {
        "circle-radius": ["interpolate", ["linear"],
          ["sqrt", ["/", ["to-number", ["get", "n_listings"], 0], maxL]],
          0, 2, 0.2, 5, 0.5, 10, 1, 18],
        "circle-color": "#1696d2",
        "circle-opacity": 0.8,
        "circle-stroke-color": "white",
        "circle-stroke-width": 1
      }
    });

    updateBubbles(metric);

    ctrl.querySelector(".wm-sel").addEventListener("change", function(e) {
      updateBubbles(e.target.value);
    });

    // Rich tooltip on hover (fond noir, 6 KPIs, rang, moyenne)
    var pop = null;
    map.on("mousemove", "city-circles", function(e) {
      var p = e.features[0].properties;
      map.getCanvas().style.cursor = "pointer";
      if (pop) pop.remove();
      var tooltipHtml = typeof buildCityTooltip === "function"
        ? buildCityTooltip(p, data, "monde")
        : '<b>' + (p.city_fr || p.city) + '</b>';
      pop = new maplibregl.Popup({offset: 12, closeButton: false, closeOnClick: false, className: "city-popup-dark"})
        .setLngLat(e.lngLat)
        .setHTML(tooltipHtml)
        .addTo(map);
    });
    map.on("mouseleave", "city-circles", function() {
      map.getCanvas().style.cursor = "";
      if (pop) { pop.remove(); pop = null; }
    });
  });

  return map;
}

// &e

// &e
