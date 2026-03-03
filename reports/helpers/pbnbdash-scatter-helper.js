// &s SCATTER_WORLD_aaMAIN - Helper scatter monde
// Adapté de ptod scatter.js pour Quarto (plain JS, pas ES module)
// Reçoit Plot et d3 en arguments (disponibles dans les cellules OJS)
// Utilise CONT_COL et DDICT (globals depuis maplibre-helper et util-helper)
// Date: 2026-02-22

// &s BUILD_SCATTER - Scatter configurable avec moyennes et régression

/**
 * Génère un scatter plot monde avec couleurs continent, quadrants, régression
 * @param {Object} Plot - Observable Plot (passé depuis OJS)
 * @param {Object} d3 - d3 (passé depuis OJS)
 * @param {Array} data - Données villes [{city, continent, n_listings, ...}]
 * @param {Object} config
 * @param {string} config.xCol - Colonne axe X
 * @param {string} config.yCol - Colonne axe Y
 * @param {string} [config.mode="Villes"] - "Villes" ou "Pays"
 * @param {number} [config.width=560]
 * @param {number} [config.height=420]
 * @returns {SVGElement} Plot.plot() object
 */
function buildWorldScatter(Plot, d3, data, config) {
  var xCol = config.xCol || "pct_entire";
  var yCol = config.yCol || "prix_med";
  var mode = config.mode || "Villes";
  var width = config.width || 560;
  var height = config.height || 420;

  // Labels depuis DDICT
  var xdd = DDICT[xCol] || {};
  var ydd = DDICT[yCol] || {};
  var xLabel = xdd.short || xCol;
  var yLabel = ydd.short || yCol;
  var xUnit = (xdd.unit && xdd.unit !== "n" && xdd.type !== "pct") ? xdd.unit : "";
  var yUnit = (ydd.unit && ydd.unit !== "n" && ydd.type !== "pct") ? ydd.unit : "";
  if (xUnit) xLabel += " (" + xUnit + ")";
  if (yUnit) yLabel += " (" + yUnit + ")";

  // Agrégation par pays si mode Pays
  var plotData;
  if (mode === "Pays") {
    plotData = d3.groups(data, function(d) { return d.country_code; }).map(function(g) {
      var cc = g[0], rows = g[1];
      var obj = {
        label: cc,
        continent: rows[0].continent,
        n_listings: d3.sum(rows, function(d) { return +d.n_listings; }),
        n_cities: rows.length
      };
      obj[xCol] = d3.median(rows, function(d) { return +d[xCol]; });
      obj[yCol] = d3.median(rows, function(d) { return +d[yCol]; });
      return obj;
    });
  } else {
    plotData = data.map(function(d) {
      return Object.assign({label: d.city_fr || d.city}, d);
    });
  }

  var validData = plotData.filter(function(d) {
    return d[xCol] != null && d[yCol] != null &&
      !isNaN(+d[xCol]) && !isNaN(+d[yCol]);
  });

  // Moyennes pour lignes quadrant
  var meanX = d3.mean(validData, function(d) { return +d[xCol]; });
  var meanY = d3.mean(validData, function(d) { return +d[yCol]; });

  // Labels : top 20% par n_listings
  var sortedN = validData.map(function(d) { return +d.n_listings || 0; }).sort(d3.ascending);
  var q80 = d3.quantile(sortedN, 0.8) || 0;

  // Tooltip formaté
  function fmtVal(v) {
    if (v == null || isNaN(+v)) return "\u2014";
    var n = +v;
    if (n >= 1000) return Math.round(n).toLocaleString("fr-FR");
    if (n % 1 === 0) return String(Math.round(n));
    return n.toFixed(1);
  }

  return Plot.plot({
    width: width,
    height: height,
    marginLeft: 56,
    marginBottom: 46,
    marginRight: 20,
    marginTop: 16,
    grid: true,
    style: {fontFamily: "system-ui, sans-serif", fontSize: "12px"},
    x: {label: xLabel, nice: true},
    y: {label: yLabel, nice: true},
    r: {range: [3, 18]},
    color: {
      domain: Object.keys(CONT_COL),
      range: Object.values(CONT_COL),
      legend: true
    },
    marks: [
      // Lignes moyennes (quadrants)
      Plot.ruleX([meanX], {
        stroke: "#94a3b8", strokeDasharray: "6,4", strokeWidth: 1
      }),
      Plot.ruleY([meanY], {
        stroke: "#94a3b8", strokeDasharray: "6,4", strokeWidth: 1
      }),

      // Points
      Plot.dot(validData, {
        x: xCol, y: yCol,
        r: "n_listings",
        fill: "continent",
        fillOpacity: 0.78,
        stroke: "white", strokeWidth: 0.6,
        tip: true,
        title: function(d) {
          return (d.label || d.city || d.country_code) +
            "\n" + xLabel + " : " + fmtVal(d[xCol]) +
            "\n" + yLabel + " : " + fmtVal(d[yCol]) +
            "\nAnnonces : " + (+d.n_listings || 0).toLocaleString("fr-FR");
        }
      }),

      // Régression (ligne seule, pas de bande IC)
      Plot.linearRegressionY(validData, {
        x: xCol, y: yCol,
        stroke: "#374151",
        strokeDasharray: "5,5",
        strokeWidth: 1.2,
        fillOpacity: 0
      }),

      // Labels villes majeures (anti-collision via halo)
      Plot.text(validData, {
        x: xCol, y: yCol,
        text: function(d) {
          return (+d.n_listings || 0) > q80 ? (d.label || "") : "";
        },
        dy: -10,
        fontSize: 9,
        fill: "#374151",
        stroke: "white",
        strokeWidth: 2.5,
        pointerEvents: "none"
      })
    ]
  });
}

// &e

// &e
