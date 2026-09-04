// &s SCATTER_OJS_aaMAIN - Scatter plot paramétré (ES module)
// Adapté de ptod scatter.js pour usage multi-projets
// Dépendances : Plot + d3 passés en config, DDICT + CONT_COL via window
// Date: 2026-03-06

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
 * @param {Array} [config.xDomain] - Domaine X explicite [min, max]
 * @param {Array} [config.yDomain] - Domaine Y explicite [min, max]
 * @param {Set} [config.labelSet] - Set de labels à afficher (override quantile)
 * @param {string} [config.axisLabelMode="short"] - "short" ou "medium" pour labels axes DDICT
 * @param {boolean} [config.rawMode=false] - skip data prep (déjà fait par createScatterWithZoom)
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
  const axisLabelMode = config.axisLabelMode || "short";

  // DDICT labels
  const DDICT = window.DDICT || {};
  const xdd = DDICT[xCol] || {};
  const ydd = DDICT[yCol] || {};
  const labelField = axisLabelMode === "medium" ? "label" : "short";
  let xLabel = xdd[labelField] || xdd.short || xCol;
  let yLabel = ydd[labelField] || ydd.short || yCol;
  const xUnit = (xdd.unit && xdd.unit !== "n" && xdd.type !== "pct") ? xdd.unit : "";
  const yUnit = (ydd.unit && ydd.unit !== "n" && ydd.type !== "pct") ? ydd.unit : "";
  if (xUnit) xLabel += " (" + xUnit + ")";
  if (yUnit) yLabel += " (" + yUnit + ")";

  // Data prep: skip if rawMode (data already prepared by createScatterWithZoom)
  let validData;
  if (config.rawMode) {
    validData = data;
  } else {
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
    validData = plotData.filter(d =>
      d[xCol] != null && d[yCol] != null &&
      !isNaN(+d[xCol]) && !isNaN(+d[yCol])
    );
  }

  // Moyennes pour lignes quadrant
  const meanX = d3.mean(validData, d => +d[xCol]);
  const meanY = d3.mean(validData, d => +d[yCol]);

  // Labels: use labelSet if provided, else quantile
  const labelSet = config.labelSet || null;
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

  // Points
  marks.push(Plot.dot(validData, {
    x: xCol, y: yCol,
    r: sizeCol,
    fill: colorCol,
    fillOpacity: 0.78,
    stroke: "white", strokeWidth: 0.6
  }));

  // Régression
  if (showRegression) {
    marks.push(Plot.linearRegressionY(validData, {
      x: xCol, y: yCol,
      stroke: "#374151",
      strokeDasharray: "5,5",
      strokeWidth: 1.2,
      fillOpacity: 0
    }));
  }

  // Labels
  if (showLabels) {
    marks.push(Plot.text(validData, {
      x: xCol, y: yCol,
      text: d => {
        if (labelSet) return labelSet.has(d.label) ? (d.label || "") : "";
        return (+d[sizeCol] || 0) > q80 ? (d.label || "") : "";
      },
      dy: -10,
      fontSize: 9,
      fill: "#374151",
      stroke: "white",
      strokeWidth: 2.5,
      pointerEvents: "none"
    }));
  }

  // Domain config
  const xCfg = {label: xLabel, nice: true};
  const yCfg = {label: yLabel, nice: true};
  if (config.xDomain) xCfg.domain = config.xDomain;
  if (config.yDomain) yCfg.domain = config.yDomain;

  const svg = Plot.plot({
    width, height,
    marginLeft: 56, marginBottom: 46, marginRight: 20, marginTop: 16,
    grid: true,
    style: {fontFamily: "system-ui, sans-serif", fontSize: "12px"},
    x: xCfg,
    y: yCfg,
    r: {range: [3, 18]},
    color: {
      domain: Object.keys(colorMap),
      range: Object.values(colorMap),
      legend: true
    },
    marks
  });

  // Custom HTML tooltip on circles
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

// &s CREATE_SCATTER_ZOOM - Scatter interactif avec zoom molette, pan, labels progressifs

/**
 * Crée un scatter interactif avec zoom molette, drag-pan, labels progressifs
 * et boutons +/-/reset. Wraps renderScatter avec gestion d'état.
 * @param {Object} config - Mêmes params que renderScatter + :
 * @param {HTMLElement} config.container - Conteneur DOM
 * @param {Function} [config.onZoomChange] - Callback(zoomLevel)
 * @returns {Object} controller {update(xCol, yCol, mode), destroy()}
 */
export function createScatterWithZoom(config) {
  const Plot = config.Plot;
  const d3 = config.d3;
  const container = config.container;
  const rawData = config.data || [];
  const labelCol = config.labelCol || "city_fr";
  const labelFallback = config.labelFallback || "city";
  const groupCol = config.groupCol || "country_code";
  const colorCol = config.colorCol || "continent";
  const sizeCol = config.sizeCol || "n_listings";

  let xCol = config.xCol || "cr_offre_10plus";
  let yCol = config.yCol || "cr_host_10plus";
  let mode = config.mode || "Villes";
  let zoomLevel = 1;
  const ZOOM_STEP = 1.3;
  const MAX_ZOOM = 12;

  // Prepare data once (reused on redraw)
  function prepareData(xC, yC, m) {
    let plotData;
    if (m === "Pays") {
      plotData = d3.groups(rawData, d => d[groupCol]).map(([key, rows]) => {
        const obj = {
          label: key,
          [colorCol]: rows[0][colorCol],
          [sizeCol]: d3.sum(rows, d => +d[sizeCol]),
          n_cities: rows.length
        };
        obj[xC] = d3.median(rows, d => +d[xC]);
        obj[yC] = d3.median(rows, d => +d[yC]);
        return obj;
      });
    } else {
      plotData = rawData.map(d => Object.assign(
        {label: d[labelCol] || d[labelFallback] || d[groupCol] || ""}, d
      ));
    }
    return plotData.filter(d =>
      d[xC] != null && d[yC] != null &&
      !isNaN(+d[xC]) && !isNaN(+d[yC])
    );
  }

  let validData = prepareData(xCol, yCol, mode);

  // Full domain (for reset)
  function fullDomain(col) {
    const vals = validData.map(d => +d[col]);
    const mn = d3.min(vals), mx = d3.max(vals);
    const pad = (mx - mn) * 0.06 || 1;
    return [mn - pad, mx + pad];
  }

  let baseXDom = fullDomain(xCol);
  let baseYDom = fullDomain(yCol);
  let curXDom = [...baseXDom];
  let curYDom = [...baseYDom];

  // Pan state
  let isPanning = false;
  let panStart = null;
  let panDomStart = null;

  // Progressive labels: select which cities get labels based on zoom level
  function computeLabels(xC, yC, zoom) {
    const n = validData.length;
    if (n === 0) return new Set();
    const labels = new Set();
    // Base: top/bottom 5 by X + top 5 by size
    const byX = [...validData].sort((a, b) => +a[xC] - +b[xC]);
    const byY = [...validData].sort((a, b) => +a[yC] - +b[yC]);
    const bySize = [...validData].sort((a, b) => (+b[sizeCol] || 0) - (+a[sizeCol] || 0));
    const baseN = Math.min(5, n);
    for (let i = 0; i < baseN; i++) {
      labels.add(byX[i].label);
      labels.add(byX[n - 1 - i].label);
      labels.add(bySize[i].label);
    }
    // Bottom/top 3 by Y
    const yN = Math.min(3, n);
    for (let i = 0; i < yN; i++) {
      labels.add(byY[i].label);
      labels.add(byY[n - 1 - i].label);
    }
    // More labels at higher zoom (log2)
    const extra = Math.floor(Math.log2(zoom) * 4);
    if (extra > 0) {
      for (let i = 0; i < Math.min(extra, n); i++) {
        labels.add(bySize[i].label);
      }
      // Also add items visible in current viewport that are extreme in the view
      const inView = validData.filter(d =>
        +d[xC] >= curXDom[0] && +d[xC] <= curXDom[1] &&
        +d[yC] >= curYDom[0] && +d[yC] <= curYDom[1]
      );
      const viewByX = [...inView].sort((a, b) => +a[xC] - +b[xC]);
      const viewByY = [...inView].sort((a, b) => +a[yC] - +b[yC]);
      const addN = Math.min(Math.floor(extra / 2) + 2, inView.length);
      for (let i = 0; i < addN; i++) {
        if (viewByX[i]) labels.add(viewByX[i].label);
        if (viewByX[inView.length - 1 - i]) labels.add(viewByX[inView.length - 1 - i].label);
        if (viewByY[i]) labels.add(viewByY[i].label);
        if (viewByY[inView.length - 1 - i]) labels.add(viewByY[inView.length - 1 - i].label);
      }
    }
    return labels;
  }

  // Build controls overlay
  const ctrlDiv = document.createElement("div");
  ctrlDiv.className = "scatter-zoom-ctrl";
  ctrlDiv.innerHTML = `<button class="sz-btn" data-action="in" title="Zoom in">+</button>
    <button class="sz-btn" data-action="out" title="Zoom out">\u2212</button>
    <button class="sz-btn" data-action="reset" title="Reset">\u2302</button>`;

  // Render
  function draw() {
    const labelSet = computeLabels(xCol, yCol, zoomLevel);
    const w = Math.max(300, container.clientWidth - 8);
    const h = Math.max(300, container.clientHeight - 8);

    // Clear old plot (Plot.plot returns <figure> when legend:true, or <svg> otherwise)
    const oldPlot = container.querySelector("figure") || container.querySelector("svg");
    if (oldPlot) oldPlot.remove();

    const svg = renderScatter({
      ...config,
      data: validData,
      xCol, yCol, mode,
      width: w, height: h,
      xDomain: curXDom,
      yDomain: curYDom,
      labelSet,
      axisLabelMode: "medium",
      rawMode: true,
      showLabels: true,
      labelQuantile: 0.8
    });

    container.insertBefore(svg, ctrlDiv);

    // Attach wheel + pan events to the plot element (figure or svg)
    const plotEl = svg.tagName === "FIGURE" ? svg : svg;
    plotEl.addEventListener("wheel", onWheel, {passive: false});
    plotEl.addEventListener("mousedown", onPanStart);
    plotEl.style.cursor = "grab";
  }

  function onWheel(e) {
    e.preventDefault();
    e.stopPropagation();
    const factor = e.deltaY < 0 ? 1 / ZOOM_STEP : ZOOM_STEP;
    const newZoom = Math.max(1, Math.min(MAX_ZOOM, zoomLevel * (1 / factor)));
    if (newZoom === zoomLevel) return;

    // Zoom centered on mouse position (proportional in domain)
    const rect = e.currentTarget.getBoundingClientRect();
    const mx = (e.clientX - rect.left) / rect.width;
    const my = 1 - (e.clientY - rect.top) / rect.height; // Y inverted

    const xSpan = curXDom[1] - curXDom[0];
    const ySpan = curYDom[1] - curYDom[0];
    const newXSpan = xSpan * factor;
    const newYSpan = ySpan * factor;

    // Clamp to base domain
    const xCenter = curXDom[0] + xSpan * mx;
    const yCenter = curYDom[0] + ySpan * my;
    curXDom = [xCenter - newXSpan * mx, xCenter + newXSpan * (1 - mx)];
    curYDom = [yCenter - newYSpan * my, yCenter + newYSpan * (1 - my)];

    zoomLevel = newZoom;
    draw();
  }

  function onPanStart(e) {
    if (e.button !== 0) return;
    isPanning = true;
    panStart = {x: e.clientX, y: e.clientY};
    panDomStart = {x: [...curXDom], y: [...curYDom]};
    e.currentTarget.style.cursor = "grabbing";

    const onMove = (ev) => {
      if (!isPanning) return;
      const rect = container.querySelector("svg").getBoundingClientRect();
      const dx = (ev.clientX - panStart.x) / rect.width;
      const dy = (ev.clientY - panStart.y) / rect.height;
      const xSpan = panDomStart.x[1] - panDomStart.x[0];
      const ySpan = panDomStart.y[1] - panDomStart.y[0];
      curXDom = [panDomStart.x[0] - dx * xSpan, panDomStart.x[1] - dx * xSpan];
      curYDom = [panDomStart.y[0] + dy * ySpan, panDomStart.y[1] + dy * ySpan]; // Y inverted
      draw();
    };
    const onUp = () => {
      isPanning = false;
      const svg = container.querySelector("svg");
      if (svg) svg.style.cursor = "grab";
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
    };
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
  }

  // Button handlers
  ctrlDiv.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    const action = btn.dataset.action;
    if (action === "reset") {
      zoomLevel = 1;
      curXDom = [...baseXDom];
      curYDom = [...baseYDom];
    } else {
      const factor = action === "in" ? 1 / ZOOM_STEP : ZOOM_STEP;
      zoomLevel = Math.max(1, Math.min(MAX_ZOOM, zoomLevel * (1 / factor)));
      const xMid = (curXDom[0] + curXDom[1]) / 2;
      const yMid = (curYDom[0] + curYDom[1]) / 2;
      const xSpan = (curXDom[1] - curXDom[0]) * factor;
      const ySpan = (curYDom[1] - curYDom[0]) * factor;
      curXDom = [xMid - xSpan / 2, xMid + xSpan / 2];
      curYDom = [yMid - ySpan / 2, yMid + ySpan / 2];
    }
    draw();
  });

  // Attach controls
  container.style.position = "relative";
  container.appendChild(ctrlDiv);

  // Initial draw
  draw();

  // Public API
  return {
    update(newXCol, newYCol, newMode) {
      xCol = newXCol;
      yCol = newYCol;
      mode = newMode || mode;
      validData = prepareData(xCol, yCol, mode);
      baseXDom = fullDomain(xCol);
      baseYDom = fullDomain(yCol);
      curXDom = [...baseXDom];
      curYDom = [...baseYDom];
      zoomLevel = 1;
      draw();
    },
    destroy() {
      container.innerHTML = "";
    }
  };
}

// &e

// &e
