// &s SCATTER_OJS_aaMAIN - Scatter plot paramétré (ES module)
// Adapté de ptod scatter.js pour usage multi-projets
// Dépendances : Plot + d3 passés en config, DDICT + CONT_COL via window
// Date: 2026-02-23

// &s RENDER_SCATTER - Génération scatter plot

/**
 * Génère un scatter plot configurable avec moyennes, régression, labels
 * @param {Object} config
 * @param {Object} config.Plot - Observable Plot
 * @param {Object} config.d3 - d3
 * @param {Array} config.data - Données
 * @param {string} config.xCol - Colonne X
 * @param {string} config.yCol - Colonne Y
 * @param {string} [config.mode="Villes"] - "Villes" ou "Pays" (agrège par country_code)
 * @param {string} [config.labelCol="city_fr"] - Colonne label
 * @param {string} [config.labelFallback="city"] - Fallback label
 * @param {string} [config.groupCol="country_code"] - Colonne groupage mode Pays
 * @param {string} [config.colorCol="continent"] - Colonne couleur
 * @param {Object} [config.colorMap] - Map valeur→couleur (défaut: window.CONT_COL)
 * @param {string} [config.sizeCol="n_listings"] - Colonne taille bulles
 * @param {number} [config.width=560]
 * @param {number} [config.height=420]
 * @param {boolean} [config.showMeans=true] - Lignes moyennes quadrant
 * @param {boolean} [config.showRegression=true] - Droite régression
 * @param {boolean} [config.showLabels=true] - Labels villes majeures
 * @param {number} [config.labelQuantile=0.8] - Seuil quantile pour labels
 * @returns {SVGElement} Plot.plot object
 */
export function renderScatter(config) {
  const Plot = config.Plot;
  const d3 = config.d3;
  const data = config.data || [];
  const xCol = config.xCol || "pct_entire";
  const yCol = config.yCol || "prix_med";
  const mode = config.mode || "Villes";
  const labelCol = config.labelCol || "city_fr";
  const labelFallback = config.labelFallback || "city";
  const groupCol = config.groupCol || "country_code";
  const colorCol = config.colorCol || "continent";
  const colorMap = config.colorMap || (window.CONT_COL || {});
  const sizeCol = config.sizeCol || "n_listings";
  const width = config.width || 560;
  const height = config.height || 420;
  const showMeans = config.showMeans !== false;
  const showRegression = config.showRegression !== false;
  const showLabels = config.showLabels !== false;
  const labelQuantile = config.labelQuantile || 0.8;

  // DDICT labels
  const DDICT = window.DDICT || {};
  const xdd = DDICT[xCol] || {};
  const ydd = DDICT[yCol] || {};
  let xLabel = xdd.short || xCol;
  let yLabel = ydd.short || yCol;
  const xUnit = (xdd.unit && xdd.unit !== "n" && xdd.type !== "pct") ? xdd.unit : "";
  const yUnit = (ydd.unit && ydd.unit !== "n" && ydd.type !== "pct") ? ydd.unit : "";
  if (xUnit) xLabel += " (" + xUnit + ")";
  if (yUnit) yLabel += " (" + yUnit + ")";

  // Agrégation par pays si demandé
  let plotData;
  if (mode === "Pays") {
    plotData = d3.groups(data, d => d[groupCol]).map(([key, rows]) => {
      const obj = {
        label: key,
        [colorCol]: rows[0][colorCol],
        [sizeCol]: d3.sum(rows, d => +d[sizeCol]),
        n_cities: rows.length
      };
      obj[xCol] = d3.median(rows, d => +d[xCol]);
      obj[yCol] = d3.median(rows, d => +d[yCol]);
      return obj;
    });
  } else {
    plotData = data.map(d => Object.assign(
      {label: d[labelCol] || d[labelFallback] || d[groupCol] || ""}, d
    ));
  }

  const validData = plotData.filter(d =>
    d[xCol] != null && d[yCol] != null &&
    !isNaN(+d[xCol]) && !isNaN(+d[yCol])
  );

  // Moyennes pour lignes quadrant
  const meanX = d3.mean(validData, d => +d[xCol]);
  const meanY = d3.mean(validData, d => +d[yCol]);

  // Seuil labels (quantile par taille)
  const sortedN = validData.map(d => +d[sizeCol] || 0).sort(d3.ascending);
  const q80 = d3.quantile(sortedN, labelQuantile) || 0;

  // Ticks adaptatifs (inspiré ptod)
  const autoTicks = (domain, axisPx) => {
    const span = domain[1] - domain[0];
    if (span <= 0) return undefined;
    const pixelCap = axisPx ? Math.max(3, Math.floor(axisPx / 60)) : 12;
    let step = Math.pow(10, Math.floor(Math.log10(span)));
    if (span / step < 3) step /= 2;
    if (span / step > 8) step *= 2;
    let ticks = d3.range(Math.ceil(domain[0] / step) * step, domain[1] + step * 0.01, step);
    while (ticks.length > pixelCap && step < span) {
      step *= 2;
      ticks = d3.range(Math.ceil(domain[0] / step) * step, domain[1] + step * 0.01, step);
    }
    return ticks;
  };

  // Formatage valeur tooltip
  function fmtVal(v) {
    if (v == null || isNaN(+v)) return "\u2014";
    const n = +v;
    if (n >= 1000) return Math.round(n).toLocaleString("fr-FR");
    if (n % 1 !== 0) return n.toFixed(1);
    return String(Math.round(n));
  }

  // Marks
  const marks = [];

  // Lignes moyennes (quadrants)
  if (showMeans && !isNaN(meanX)) {
    marks.push(Plot.ruleX([meanX], {
      stroke: "#94a3b8", strokeDasharray: "6,4", strokeWidth: 1
    }));
  }
  if (showMeans && !isNaN(meanY)) {
    marks.push(Plot.ruleY([meanY], {
      stroke: "#94a3b8", strokeDasharray: "6,4", strokeWidth: 1
    }));
  }

  // Points (pas de tip: true, tooltip custom ajouté après render)
  marks.push(Plot.dot(validData, {
    x: xCol, y: yCol,
    r: sizeCol,
    fill: colorCol,
    fillOpacity: 0.78,
    stroke: "white", strokeWidth: 0.6
  }));

  // Régression (ligne seule, pas de bande IC)
  if (showRegression) {
    marks.push(Plot.linearRegressionY(validData, {
      x: xCol, y: yCol,
      stroke: "#374151",
      strokeDasharray: "5,5",
      strokeWidth: 1.2,
      fillOpacity: 0
    }));
  }

  // Labels villes majeures
  if (showLabels) {
    marks.push(Plot.text(validData, {
      x: xCol, y: yCol,
      text: d => (+d[sizeCol] || 0) > q80 ? (d.label || "") : "",
      dy: -10,
      fontSize: 9,
      fill: "#374151",
      stroke: "white",
      strokeWidth: 2.5,
      pointerEvents: "none"
    }));
  }

  const svg = Plot.plot({
    width, height,
    marginLeft: 56, marginBottom: 46, marginRight: 20, marginTop: 16,
    grid: true,
    style: {fontFamily: "system-ui, sans-serif", fontSize: "12px"},
    x: {label: xLabel, nice: true},
    y: {label: yLabel, nice: true},
    r: {range: [3, 18]},
    color: {
      domain: Object.keys(colorMap),
      range: Object.values(colorMap),
      legend: true
    },
    marks
  });

  // Custom HTML tooltip on circles (uses global buildCityTooltip + showTooltip/hideTooltip)
  const _buildTip = window.buildCityTooltip;
  const _showTip = window.showTooltip;
  const _hideTip = window.hideTooltip;
  if (_buildTip && _showTip && _hideTip) {
    const scope = config.tooltipScope || "monde";
    const circles = svg.querySelectorAll("circle");
    circles.forEach((circle, idx) => {
      if (idx >= validData.length) return;
      const d = validData[idx];
      circle.style.cursor = "pointer";
      circle.addEventListener("mouseenter", (e) => {
        _showTip(e, _buildTip(d, validData, scope));
      });
      circle.addEventListener("mousemove", (e) => {
        _showTip(e, _buildTip(d, validData, scope));
      });
      circle.addEventListener("mouseleave", () => { _hideTip(); });
    });
    if (!window._tooltipEl) { window.initTooltip && window.initTooltip(); }
  }

  return svg;
}

// &e

// &e
