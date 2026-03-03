// &s TABLE_OJS_aaMAIN - Tableau triable générique (ES module)
// Usage multi-projets, accède DDICT + divGauge via window
// Date: 2026-02-24

// &s BUILD_TABLE - Tableau triable avec search, sticky, barres z-score

/**
 * Construit un tableau triable avec barres z-score + trait de moyenne
 * @param {HTMLElement} container - Élément DOM conteneur
 * @param {Array} data - Données [{city, continent, n_listings, ...}]
 * @param {Object} config
 * @param {Array<string>} config.keys - Colonnes à afficher (clés CSV)
 * @param {string} [config.labelCol="city_fr"] - Colonne pour le label
 * @param {string} [config.labelFallback="city"] - Fallback si labelCol absent
 * @param {string} [config.labelHeader="Ville"] - Intitulé colonne label
 * @param {string} [config.colorCol="continent"] - Colonne pour la pastille couleur
 * @param {Object} [config.colorMap] - Map valeur→couleur (défaut: window.CONT_COL)
 * @param {string} [config.defaultSort="n_listings"] - Tri initial
 * @param {boolean} [config.defaultAsc=false] - Tri ascendant par défaut
 * @param {Object} [config.refRow=null] - Ligne de référence sticky {label, data}
 * @param {number} [config.maxHeight=420] - Hauteur max scroll
 * @param {Array<Object>} [config.groups=null] - Supra-headers [{label, cols},...] pour regrouper colonnes
 */
export function buildDataTable(container, data, config) {
  config = config || {};
  const keys = config.keys || ["n_listings", "prix_med"];
  const labelCol = config.labelCol || "city_fr";
  const labelFallback = config.labelFallback || "city";
  const labelHeader = config.labelHeader || "Ville";
  const colorCol = config.colorCol || "continent";
  const colorMap = config.colorMap || (window.CONT_COL || {});
  const defaultSort = config.defaultSort || "n_listings";
  const maxHeight = config.maxHeight || 420;
  const refRow = config.refRow || null;
  const groups = config.groups || null;

  const DDICT = window.DDICT || {};
  const _divGauge = window.divGauge || function() {
    return {bar: "#b8c2cc", text: "#555", op: 0.5};
  };

  // Headers depuis DDICT (short + unit L2 filtré si redondant)
  const UNIT_SKIP = {"n":1, "%":1, "ratio":1};
  const headers = {};
  const tips = {};
  for (const k of keys) {
    const dd = DDICT[k] || {};
    const lbl = dd.short || k;
    const unit = (dd.unit && !UNIT_SKIP[dd.unit]) ? dd.unit : "";
    headers[k] = unit ? lbl + '<span class="th-unit">' + unit + '</span>' : lbl;
    tips[k] = (dd.desc || dd.label || "").replace(/"/g, "&quot;");
  }

  // Stats pour z-score, trait moyenne, cap P2/P98
  const stats = {};
  for (const k of keys) {
    const vals = data.map(d => +d[k]).filter(v => !isNaN(v));
    const sorted = vals.slice().sort((a, b) => a - b);
    const max = vals.length ? Math.max(...vals) : 1;
    const sum = vals.reduce((a, b) => a + b, 0);
    const mean = vals.length ? sum / vals.length : 0;
    const variance = vals.length > 1
      ? vals.reduce((s, v) => s + Math.pow(v - mean, 2), 0) / (vals.length - 1) : 0;
    // P2/P98 pour capper les barres (évite Paris 51K écrasant IRIS 62)
    const p02 = sorted.length > 4 ? sorted[Math.floor(sorted.length * 0.02)] : sorted[0] || 0;
    const p98 = sorted.length > 4 ? sorted[Math.min(Math.floor(sorted.length * 0.98), sorted.length - 1)] : max;
    stats[k] = {max, mean, std: Math.sqrt(variance), p02, p98};
  }

  // Build toolbar
  container.innerHTML =
    '<div class="t-toolbar">' +
    '<input placeholder="Filtrer...">' +
    '<span class="info"></span>' +
    '</div>' +
    '<div class="t" style="max-height:' + maxHeight + 'px;overflow-y:auto;overflow-x:auto;"></div>';

  let sortCol = defaultSort;
  let sortAsc = config.defaultAsc || false;
  let search = "";

  // Rendu cellule barre avec trait de moyenne
  function renderCell(val, k, isRef) {
    if (val == null || isNaN(+val)) return "\u2014";
    const v = +val;
    const info = DDICT[k] || {type: "stock"};
    const s = stats[k];

    // Formatage
    const fmt = info.type === "pct" ? v.toFixed(1) + "%"
      : (info.unit || "").indexOf("/5") >= 0 ? v.toFixed(2)
      : v >= 1000 ? Math.round(v).toLocaleString("fr-FR")
      : v % 1 !== 0 ? v.toFixed(1) : String(Math.round(v));

    // Ref row : gras sans barre
    if (isRef && info.type === "stock") {
      return '<span style="font-weight:700;color:#1696d2;">' + fmt + '</span>';
    }

    // Barre cappée à P98 (valeurs > P98 = barre pleine)
    const barMax = s.p98 > 0 ? s.p98 : s.max;
    const w = barMax > 0 ? Math.min(v / barMax * 100, 100) : 0;
    const g = _divGauge(v, s.mean, s.std);

    // Trait moyenne (position relative à P98)
    const meanPct = barMax > 0 ? Math.min(s.mean / barMax * 100, 100) : 0;
    const meanLine = '<span style="position:absolute;left:' + meanPct +
      '%;top:0;width:1px;height:100%;background:#555;opacity:0.35;"></span>';

    return '<span class="bar-bg" style="position:relative;">' +
      '<span class="bar-fill" style="width:' + w + '%;background:' + g.bar +
      ';opacity:' + g.op + ';"></span>' + meanLine +
      '</span> <span style="color:' + g.text + '">' + fmt + '</span>';
  }

  function render() {
    let rows = data.slice();

    if (search) {
      const q = search.toLowerCase();
      rows = rows.filter(d =>
        ((d[labelCol] || d[labelFallback] || "").toLowerCase().indexOf(q) >= 0) ||
        ((d.country_code || "").toLowerCase().indexOf(q) >= 0)
      );
    }

    rows.sort((a, b) => {
      if (sortCol === labelCol || sortCol === labelFallback) {
        const va = (a[labelCol] || a[labelFallback] || "").toLowerCase();
        const vb = (b[labelCol] || b[labelFallback] || "").toLowerCase();
        return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
      }
      const va = +a[sortCol] || 0, vb = +b[sortCol] || 0;
      return sortAsc ? va - vb : vb - va;
    });

    // Header
    const stickyLbl = "position:sticky;left:0;z-index:5;";
    let ths = '<th data-col="' + labelCol + '" class="' +
      (sortCol === labelCol ? "active" : "") + '" style="' + stickyLbl + 'background:#e5e7eb;">' + labelHeader +
      (sortCol === labelCol ? (sortAsc ? " \u2191" : " \u2193") : "") + '</th>';
    for (const k of keys) {
      ths += '<th data-col="' + k + '" class="' + (sortCol === k ? "active" : "") + '" title="' + (tips[k] || k) + '">' +
        headers[k] + (sortCol === k ? (sortAsc ? " \u2191" : " \u2193") : "") + '</th>';
    }

    let tbody = "";

    // Ref row (sticky)
    if (refRow) {
      const rd = refRow.data || {};
      tbody += '<tr class="sticky-ref" data-ref="true"><td style="font-weight:600;white-space:nowrap;' + stickyLbl + 'z-index:10;background:#f0f7ff;">' +
        refRow.label + '</td>';
      for (const k of keys) {
        tbody += '<td>' + renderCell(rd[k], k, true) + '</td>';
      }
      tbody += '</tr>';
    }

    // Data rows
    for (const d of rows) {
      const dotColor = colorMap[d[colorCol]] || "#999";
      const label = d[labelCol] || d[labelFallback] || "";
      const cc = d.country_code || "";
      tbody += '<tr><td style="font-weight:500;white-space:nowrap;' + stickyLbl + 'z-index:1;background:white;">' +
        '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' +
        dotColor + ';margin-right:4px;"></span>' +
        label + ' <small style="color:#999;">' + cc + '</small></td>';
      for (const k of keys) {
        tbody += '<td>' + renderCell(d[k], k, false) + '</td>';
      }
      tbody += '</tr>';
    }

    const tb = container.querySelector(".t");
    const info = container.querySelector(".info");
    if (info) info.textContent = rows.length + " lignes";

    if (tb) {
      // Supra-headers (optional grouped columns)
      let supraRow = "";
      if (groups) {
        supraRow = '<tr class="supra"><th style="' + stickyLbl + 'background:#d1d5db;"></th>';
        for (const g of groups) {
          supraRow += '<th colspan="' + g.cols.length + '">' + g.label + '</th>';
        }
        supraRow += '</tr>';
      }
      tb.innerHTML = '<table><thead>' + supraRow + '<tr>' + ths + '</tr></thead><tbody>' + tbody + '</tbody></table>';

      // Dynamic sticky
      const thead = tb.querySelector("thead");
      const thH = thead ? thead.offsetHeight : 0;
      const stickyRef = tb.querySelector(".sticky-ref");
      if (stickyRef) {
        stickyRef.style.position = "sticky";
        stickyRef.style.top = thH + "px";
        stickyRef.style.zIndex = "9";
        stickyRef.style.background = "#f0f7ff";
        stickyRef.style.boxShadow = "0 1px 2px rgba(0,0,0,0.08)";
      }

      // Sort handlers
      tb.querySelectorAll("th").forEach(th => {
        th.addEventListener("click", () => {
          const col = th.dataset.col;
          if (sortCol === col) sortAsc = !sortAsc;
          else { sortCol = col; sortAsc = (col === labelCol); }
          render();
        });
      });
    }
  }

  const inp = container.querySelector("input");
  if (inp) inp.addEventListener("input", e => { search = e.target.value; render(); });

  render();
}

// &e

// &e
