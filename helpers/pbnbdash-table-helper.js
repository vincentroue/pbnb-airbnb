// &s TABLE_WORLD_aaMAIN - Helper tableau triable générique
// Chargé après pbnbdash-util-helper.js (DDICT, barCell, divGauge)
// Date: 2026-02-23

// &s BUILD_TABLE - Tableau triable avec search, sticky, trait moyenne

/**
 * Construit un tableau triable avec barres z-score + trait de moyenne
 * @param {HTMLElement} container - Élément DOM conteneur
 * @param {Array} data - Données [{city, continent, n_listings, ...}]
 * @param {Object} config
 * @param {Array<string>} config.keys - Colonnes à afficher (clés CSV)
 * @param {string} [config.labelCol="city_fr"] - Colonne pour le label ville
 * @param {string} [config.labelFallback="city"] - Fallback si labelCol absent
 * @param {string} [config.colorCol="continent"] - Colonne pour la pastille couleur
 * @param {Object} [config.colorMap=CONT_COL] - Map valeur→couleur pour pastille
 * @param {string} [config.defaultSort="n_listings"] - Tri initial
 * @param {boolean} [config.defaultAsc=false] - Tri ascendant par défaut
 * @param {Object} [config.refRow=null] - Ligne de référence sticky {label, data, level}
 * @param {number} [config.maxHeight=420] - Hauteur max scroll
 */
function buildWorldTable(container, data, config) {
  config = config || {};
  var keys = config.keys || ["n_listings", "prix_med", "pct_multi"];
  var labelCol = config.labelCol || "city_fr";
  var labelFallback = config.labelFallback || "city";
  var colorCol = config.colorCol || "continent";
  var colorMap = config.colorMap || (typeof CONT_COL !== "undefined" ? CONT_COL : {});
  var defaultSort = config.defaultSort || "n_listings";
  var maxHeight = config.maxHeight || 420;
  var refRow = config.refRow || null;

  // Headers depuis DDICT
  var headers = {};
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    headers[k] = (DDICT[k] || {}).short || k;
  }

  // Stats pour z-score et trait moyenne
  var stats = {};
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    var vals = data.map(function(d) { return +d[k]; }).filter(function(v) { return !isNaN(v); });
    var max = vals.length ? Math.max.apply(null, vals) : 1;
    var sum = vals.length ? vals.reduce(function(a, b) { return a + b; }, 0) : 0;
    var mean = vals.length ? sum / vals.length : 0;
    var variance = vals.length > 1
      ? vals.reduce(function(s, v) { return s + Math.pow(v - mean, 2); }, 0) / (vals.length - 1) : 0;
    stats[k] = {max: max, mean: mean, std: Math.sqrt(variance)};
  }

  // Build toolbar
  container.innerHTML = '<div class="t-toolbar">' +
    '<input placeholder="Filtrer ville...">' +
    '<span class="info"></span>' +
    '</div>' +
    '<div class="t" style="max-height:' + maxHeight + 'px;overflow-y:auto;"></div>';

  var sortCol = defaultSort;
  var sortAsc = config.defaultAsc || false;
  var search = "";

  // Rendu cellule barre avec trait de moyenne
  function renderCell(val, k, isRef) {
    if (val == null || isNaN(+val)) return "\u2014";
    var v = +val;
    var info = DDICT[k] || {type: "stock", pol: 0};
    var s = stats[k];

    // Formatage valeur
    var fmt = info.type === "pct" ? v.toFixed(1) + "%" :
      v >= 1000 ? Math.round(v).toLocaleString("fr-FR") :
      v % 1 !== 0 ? v.toFixed(1) : String(Math.round(v));

    // Ligne ref : gras sans barre
    if (isRef && info.type === "stock") {
      return '<span style="font-weight:700;color:#1696d2;">' + fmt + '</span>';
    }

    // Largeur barre proportionnelle au max
    var w = s.max > 0 ? Math.min(v / s.max * 100, 100) : 0;

    // Couleur z-score
    var g = divGauge(v, s.mean, s.std);

    // Position du trait moyenne (proportionnel au max)
    var meanPct = s.max > 0 ? Math.min(s.mean / s.max * 100, 100) : 0;
    var meanLine = '<span style="position:absolute;left:' + meanPct +
      '%;top:0;width:1px;height:100%;background:#555;opacity:0.35;"></span>';

    return '<span class="bar-bg" style="position:relative;">' +
      '<span class="bar-fill" style="width:' + w + '%;background:' + g.bar + ';opacity:' + g.op + ';"></span>' +
      meanLine +
      '</span> <span style="color:' + g.text + '">' + fmt + '</span>';
  }

  function render() {
    var rows = data.slice();

    // Filter search
    if (search) {
      var q = search.toLowerCase();
      rows = rows.filter(function(d) {
        return ((d[labelCol] || d[labelFallback] || "").toLowerCase().indexOf(q) >= 0) ||
          ((d.country_code || "").toLowerCase().indexOf(q) >= 0);
      });
    }

    // Sort
    rows.sort(function(a, b) {
      if (sortCol === labelCol || sortCol === labelFallback) {
        var va = (a[labelCol] || a[labelFallback] || "").toLowerCase();
        var vb = (b[labelCol] || b[labelFallback] || "").toLowerCase();
        return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
      }
      var va = +a[sortCol] || 0, vb = +b[sortCol] || 0;
      return sortAsc ? va - vb : vb - va;
    });

    // Header row
    var ths = '<th data-col="' + labelCol + '" class="' +
      (sortCol === labelCol ? "active" : "") + '">Ville' +
      (sortCol === labelCol ? (sortAsc ? " \u2191" : " \u2193") : "") + '</th>';
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      ths += '<th data-col="' + k + '" class="' + (sortCol === k ? "active" : "") + '">' +
        headers[k] + (sortCol === k ? (sortAsc ? " \u2191" : " \u2193") : "") + '</th>';
    }

    // Data rows
    var tbody = "";

    // Reference row (sticky)
    if (refRow) {
      var rd = refRow.data || {};
      tbody += '<tr class="sticky-ref" data-ref="true"><td style="font-weight:600;white-space:nowrap;">' +
        refRow.label + '</td>';
      for (var i = 0; i < keys.length; i++) {
        tbody += '<td>' + renderCell(rd[keys[i]], keys[i], true) + '</td>';
      }
      tbody += '</tr>';
    }

    // Regular rows
    for (var r = 0; r < rows.length; r++) {
      var d = rows[r];
      var colorVal = d[colorCol] || "";
      var dotColor = colorMap[colorVal] || "#999";
      var label = d[labelCol] || d[labelFallback] || "";
      var cc = d.country_code || "";

      tbody += '<tr><td style="font-weight:500;white-space:nowrap;">' +
        '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' +
        dotColor + ';margin-right:4px;"></span>' +
        label + ' <small style="color:#999;">' + cc + '</small></td>';

      for (var i = 0; i < keys.length; i++) {
        tbody += '<td>' + renderCell(d[keys[i]], keys[i], false) + '</td>';
      }
      tbody += '</tr>';
    }

    // Inject into DOM
    var tb = container.querySelector(".t");
    var info = container.querySelector(".info");
    if (info) info.textContent = rows.length + " villes";

    if (tb) {
      tb.innerHTML = '<table><thead><tr>' + ths + '</tr></thead><tbody>' + tbody + '</tbody></table>';

      // Dynamic sticky: measure thead height, apply to ref row
      var thead = tb.querySelector("thead");
      var thH = thead ? thead.offsetHeight : 0;
      var stickyRef = tb.querySelector(".sticky-ref");
      if (stickyRef) {
        stickyRef.style.position = "sticky";
        stickyRef.style.top = thH + "px";
        stickyRef.style.zIndex = "9";
        stickyRef.style.background = "#f0f7ff";
        stickyRef.style.boxShadow = "0 1px 2px rgba(0,0,0,0.08)";
      }

      // Sort click handlers
      tb.querySelectorAll("th").forEach(function(th) {
        th.addEventListener("click", function() {
          var col = th.dataset.col;
          if (sortCol === col) sortAsc = !sortAsc;
          else { sortCol = col; sortAsc = (col === labelCol); }
          render();
        });
      });
    }
  }

  // Search handler
  var inp = container.querySelector("input");
  if (inp) {
    inp.addEventListener("input", function(e) {
      search = e.target.value;
      render();
    });
  }

  // Initial render
  render();
}

// &e

// &e
