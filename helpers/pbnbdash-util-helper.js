// pbnbdash-util-helper.js
// Dashboard Airbnb France — Paris · Lyon · Bordeaux
// Helpers JS extraits du QMD monolithique v1 (260215)
// v2 — 2026-02-18

// &s &DDICT_CONFIG_aaMAIN - Dictionnaire indicateurs et palettes

// &s &DDICT_INDICATORS - DDICT chargé dynamiquement depuis ddict-airbnb.json
var DDICT = {};

function initDdict(raw) {
  var d = {};
  var keys = Object.keys(raw);
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    if (k.charAt(0) === "_") continue;
    var e = raw[k];
    if (!e || typeof e !== "object" || !e.type) continue;
    var entry = {
      label: e.medium || e.label || e.short || k,
      short: e.short || k,
      type: e.type || "stock",
      unit: e.unit || "",
      pol: typeof e.polarity === "number" ? e.polarity : 0,
      theme: e.theme || "",
      desc: e.description || e.long || ""
    };
    d[k] = entry;
    if (e.csv_col && e.csv_col !== k) d[e.csv_col] = entry;
  }
  DDICT = d;
  window.DDICT = d;
  return d;
}

// Auto-chargement depuis ddict-airbnb.json (même dossier helpers/)
(function() {
  try {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "helpers/ddict-airbnb.json", false);
    xhr.send();
    if (xhr.status === 200) {
      initDdict(JSON.parse(xhr.responseText).indicators);
    }
  } catch (e) { console.warn("DDICT auto-load:", e); }
})();
// &e

// &s &IRIS_MAPPINGS - Clés IRIS et mappings
var IRIS_KEYS=["n","n_hosts","prix_med","pct_multi","pct_entire","pct_longterm","dispo_med","reviews_med","entire_1000rp","listings_1000rps"];
var IRIS2D={n:"n_listings",n_hosts:"n_hosts",prix_med:"prix_med",pct_multi:"pct_multi",pct_entire:"pct_entire",pct_longterm:"pct_longterm",dispo_med:"dispo_med",reviews_med:"reviews_med",entire_1000rp:"entire_1000rp",listings_1000rps:"listings_1000rps"};
var PAL_MODES={niveau:"Niveau",ecart:"\u00c9cart \u00e0 la ville"};
// &e

// &s &COLOR_PALETTES - Palettes séquentielles et divergentes
// prix = pal_seq7_byrv (source: mutils/jrr/jcn-setup.R L103-105)
var SEQ_COL={
  prix:["#f0ebe0","#ffe68a","#fecc5c","#fd8d3c","#fc4e2a","#bd0026","#5b1a8c"],
  stock:["#f7fbff","#c6dbef","#6baed6","#2171b5","#08306b"],
  pct_pos:["#f7fcf5","#a1d99b","#41ab5d","#006d2c","#00441b"],
  pct_neg:["#f7fbff","#c6dbef","#6baed6","#2171b5","#08306b"]
};
var DIV_COL=["#084594","#1696d2","#a8d4e8","#f0f0f0","#c97b8e","#a63d5a","#6d1a36"];
// &e

// &s &COUNTRY_NAMES - Noms pays en français (ISO 3166-1 alpha-3)
var COUNTRY_NAMES = {
  AUS:"Australie",AUT:"Autriche",BEL:"Belgique",BRA:"Br\u00e9sil",
  CAN:"Canada",CHE:"Suisse",CHN:"Chine",CZE:"Tch\u00e9quie",
  DEU:"Allemagne",DNK:"Danemark",ESP:"Espagne",FRA:"France",
  GBR:"Royaume-Uni",GRC:"Gr\u00e8ce",HUN:"Hongrie",IRL:"Irlande",
  ITA:"Italie",JPN:"Japon",LVA:"Lettonie",MEX:"Mexique",
  NLD:"Pays-Bas",NOR:"Norv\u00e8ge",PRT:"Portugal",SGP:"Singapour",
  SWE:"Su\u00e8de",THA:"Tha\u00eflande",TUR:"Turquie",TWN:"Ta\u00efwan",
  USA:"\u00c9tats-Unis",ZAF:"Afrique du Sud"
};
window.COUNTRY_NAMES = COUNTRY_NAMES;
// &e

// &e (FIN-DDICT_CONFIG_aaMAIN)

// &s &CHOROPLETH_ENGINE_aaMAIN - Bins, palettes, légendes IRIS

// &s &IRIS_BINS - Calcul classes choroplèthe
function irisBins(feats,key,pm,cityRef){
  var vs=feats.filter(function(f){return(f.properties.n||0)>=10}).map(function(f){return f.properties[key]}).filter(function(v){return v!=null&&!isNaN(v)});
  if(vs.length<5)return null;
  vs.sort(function(a,b){return a-b});
  var n=vs.length,mn=vs[0],mx=vs[n-1];
  function q(p){return vs[Math.min(Math.round(p*(n-1)),n-1)];}
  var dk=IRIS2D[key]||key,dd=DDICT[dk]||{};
  // Mode écart : divergent autour de la valeur ville (7 classes)
  if(pm==="ecart"){
    var piv=cityRef!=null?cityRef:(vs.reduce(function(a,b){return a+b},0)/n);
    var std=Math.sqrt(vs.reduce(function(s,v){return s+(v-piv)*(v-piv)},0)/(n-1));
    if(std<0.01)std=1;
    return{brk:[piv-2*std,piv-std,piv-0.5*std,piv+0.5*std,piv+std,piv+2*std],
      col:DIV_COL,piv:piv,mn:mn,mx:mx,std:std};
  }
  // Mode niveau : BYRV 7 bins pour TOUS les indicateurs — P5/P20/P40/P60/P80/P95
  var vp=vs.filter(function(v){return v>0;});
  if(vp.length<5)vp=vs;
  vp.sort(function(a,b){return a-b});
  var np=vp.length,mnp=vp[0],mxp=vp[np-1];
  function qp(p){return vp[Math.min(Math.round(p*(np-1)),np-1)];}
  var fmt=dd.type==="pct"?1:0;
  var brk=fmt?[+(qp(.05).toFixed(1)),+(qp(.2).toFixed(1)),+(qp(.4).toFixed(1)),+(qp(.6).toFixed(1)),+(qp(.8).toFixed(1)),+(qp(.95).toFixed(1))]
    :[Math.round(qp(.05)),Math.round(qp(.2)),Math.round(qp(.4)),Math.round(qp(.6)),Math.round(qp(.8)),Math.round(qp(.95))];
  for(var i=1;i<brk.length;i++){if(brk[i]<=brk[i-1])brk[i]=+(brk[i-1]+(fmt?0.1:1)).toFixed(fmt?1:0);}
  return{brk:brk,col:SEQ_COL.prix,piv:null,mn:mnp,mx:mxp,p5:brk[0],p95:brk[5]};
}
// &e

// &s &STEP_EXPR - Expression MapLibre step pour choroplèthe
function stepEx(key,brk,col){
  var e=["step",["get",key],col[0]];
  for(var i=0;i<brk.length;i++){e.push(brk[i]);e.push(col[i+1]);}
  return e;
}
// &e

function defaultPal(){return"niveau";}

// &s &LEGEND_INTERACTIVE - Légende interactive avec bins cliquables
function legHtml(bins,lbl,feats,key){
  // Compat wrapper — returns HTML string for non-interactive fallback
  var el=buildLegend(bins,lbl,feats,key,null);
  var tmp=document.createElement("div");
  tmp.appendChild(el);
  return tmp.innerHTML;
}

function buildLegend(bins,lbl,feats,key,map){
  var nc=bins.col.length;
  var cnt=[];for(var i=0;i<nc;i++)cnt.push(0);
  var noData=0;
  // Compute IRIS counts per bin
  if(feats&&key){
    feats.forEach(function(f){
      var n=f.properties["n"]||0;
      if(n<10){noData++;return;}
      var v=f.properties[key];if(v==null||isNaN(v))return;
      var idx=0;
      for(var j=0;j<bins.brk.length;j++){if(v>=bins.brk[j])idx=j+1;}
      if(idx>=nc)idx=nc-1;
      cnt[idx]++;
    });
  }
  var wrap=document.createElement("div");
  wrap.style.cssText="font-size:10px;";
  // Title
  var title=document.createElement("div");
  title.style.cssText="font-weight:600;margin-bottom:3px;font-size:10px;";
  title.textContent=lbl;
  wrap.appendChild(title);

  // Seuils row (above bar)
  var thRow=document.createElement("div");
  thRow.style.cssText="display:flex;font-size:8px;color:#6b7280;margin-bottom:1px;position:relative;height:11px;";
  if(bins.piv!=null){
    // Divergent: sigma labels
    var sigLabels=["-2\u03c3","-1\u03c3","\u25c6"+Math.round(bins.piv),"+1\u03c3","+2\u03c3"];
    sigLabels.forEach(function(s){
      var sp=document.createElement("span");sp.style.cssText="flex:1;text-align:center;font-size:8px;";
      sp.textContent=s;thRow.appendChild(sp);
    });
  } else {
    // Sequential: threshold values between bins
    var allVals=[Math.round(bins.mn)];
    for(var i=0;i<bins.brk.length;i++)allVals.push(Math.round(bins.brk[i]));
    allVals.push(Math.round(bins.mx));
    allVals.forEach(function(v,i){
      var sp=document.createElement("span");
      sp.style.cssText="font-size:8px;color:#6b7280;"+(i===0?"":"margin-left:auto;");
      sp.textContent=v;
      thRow.appendChild(sp);
    });
    thRow.style.cssText="display:flex;justify-content:space-between;font-size:8px;color:#6b7280;margin-bottom:1px;";
  }
  wrap.appendChild(thRow);

  // Color bar (boxes)
  var barRow=document.createElement("div");
  barRow.style.cssText="display:flex;height:14px;border-radius:2px;overflow:hidden;width:200px;gap:0;";
  var boxEls=[];
  for(var i=0;i<nc;i++){
    var box=document.createElement("div");
    box.style.cssText="flex:1;background:"+bins.col[i]+";cursor:pointer;transition:opacity 0.12s;border-right:"+(i<nc-1?"0.5px solid rgba(0,0,0,0.15)":"none")+";";
    box.dataset.idx=i;
    boxEls.push(box);
    barRow.appendChild(box);
  }
  if(noData>0){
    var naBox=document.createElement("div");
    naBox.style.cssText="flex:0.6;background:#d9d9d9;border:0.5px solid #bbb;cursor:default;";
    barRow.appendChild(naBox);
  }
  wrap.appendChild(barRow);

  // Counts row
  var cntRow=document.createElement("div");
  cntRow.style.cssText="display:flex;font-size:7px;color:#1696d2;font-weight:500;margin-top:1px;width:200px;";
  var cntEls=[];
  for(var i=0;i<nc;i++){
    var sp=document.createElement("span");
    sp.style.cssText="flex:1;text-align:center;transition:opacity 0.12s;";
    sp.textContent=cnt[i];
    cntEls.push(sp);
    cntRow.appendChild(sp);
  }
  if(noData>0){
    var naSp=document.createElement("span");
    naSp.style.cssText="flex:0.6;text-align:center;color:#999;";
    naSp.textContent=noData;
    cntRow.appendChild(naSp);
  }
  wrap.appendChild(cntRow);

  // Sigma line for divergent
  if(bins.piv!=null){
    var sigLine=document.createElement("div");
    sigLine.style.cssText="text-align:center;font-size:7px;color:#999;";
    sigLine.textContent="\u03c3 = "+Math.round(bins.std);
    wrap.appendChild(sigLine);
  }

  // Hint
  if(map){
    var hint=document.createElement("div");
    hint.style.cssText="font-size:7px;color:#9ca3af;font-style:italic;margin-top:2px;cursor:help;";
    hint.textContent="Clic: filtrer \u00b7 Ctrl+clic: ajouter";
    wrap.appendChild(hint);
  }

  // Interactive click handling
  if(map&&key&&feats){
    var selectedSet=null;
    var allIdx=new Set();for(var i=0;i<nc;i++)allIdx.add(i);

    var refresh=function(){
      var active=selectedSet||allIdx;
      boxEls.forEach(function(box,i){
        var on=active.has(i);
        box.style.background=on?bins.col[i]:"#d1d5db";
        box.style.opacity=on?"1":"0.3";
      });
      cntEls.forEach(function(el,i){
        el.style.opacity=(!selectedSet||selectedSet.has(i))?"1":"0.25";
      });
      // Build MapLibre filter: show only IRIS in selected bins
      if(map.getLayer("iris-fill")){
        if(!selectedSet){
          map.setFilter("iris-fill",null);
          map.setFilter("iris-border",null);
        } else {
          // Build value ranges for selected bins
          var conditions=["any"];
          active.forEach(function(idx){
            var lo=(idx===0)?-Infinity:bins.brk[idx-1];
            var hi=(idx<bins.brk.length)?bins.brk[idx]:Infinity;
            if(lo===-Infinity){
              conditions.push(["<",["get",key],hi]);
            } else if(hi===Infinity){
              conditions.push([">=",["get",key],lo]);
            } else {
              conditions.push(["all",[">=",["get",key],lo],["<",["get",key],hi]]);
            }
          });
          var filter=["any",conditions,["<",["get","n"],10]];
          map.setFilter("iris-fill",filter);
          map.setFilter("iris-border",filter);
        }
      }
    };

    boxEls.forEach(function(box,i){
      box.addEventListener("click",function(e){
        if(e.ctrlKey||e.metaKey){
          if(!selectedSet){selectedSet=new Set(allIdx);selectedSet.delete(i);}
          else if(selectedSet.has(i)){selectedSet.delete(i);if(selectedSet.size===0)selectedSet=null;}
          else{selectedSet.add(i);if(selectedSet.size===allIdx.size)selectedSet=null;}
        } else {
          if(selectedSet&&selectedSet.size===1&&selectedSet.has(i))selectedSet=null;
          else selectedSet=new Set([i]);
        }
        refresh();
      });
    });
  }

  return wrap;
}
// &e

// &e (FIN-CHOROPLETH_ENGINE_aaMAIN)

// &s &TOOLTIP_aaMAIN - Tooltip IRIS enrichi singleton (inspiré ptod tooltip.js)

// &s &TOOLTIP_SINGLETON - Init / show / hide tooltip DOM
var _tooltipEl=null,_tooltipFrame=null;
function initTooltip(){
  if(_tooltipEl)return;
  _tooltipEl=document.createElement("div");
  _tooltipEl.className="iris-tooltip";
  document.body.appendChild(_tooltipEl);
}
function showTooltip(event,html){
  if(_tooltipFrame)cancelAnimationFrame(_tooltipFrame);
  _tooltipFrame=requestAnimationFrame(function(){
    if(!_tooltipEl)initTooltip();
    _tooltipEl.innerHTML=html;
    _tooltipEl.style.display="block";
    _tooltipEl.style.opacity="1";
    var rect=_tooltipEl.getBoundingClientRect();
    var x=Math.min(event.clientX+14,window.innerWidth-rect.width-10);
    var y=Math.max(event.clientY-rect.height-8,10);
    _tooltipEl.style.left=x+"px";
    _tooltipEl.style.top=y+"px";
    _tooltipFrame=null;
  });
}
function hideTooltip(){
  if(_tooltipEl){_tooltipEl.style.display="none";_tooltipEl.style.opacity="0";}
  if(_tooltipFrame){cancelAnimationFrame(_tooltipFrame);_tooltipFrame=null;}
}
// &e

// &s &POLARITY_DOT - Pastille polarité (●● strong, ● mild, ○ neutral)
function polarityDot(pol,percentile){
  if(pol===0||percentile==null)return{dot:'<span style="color:#94a3b8;font-size:9px;margin-right:2px;">&#9675;</span>',color:"#d1d5db",level:"neutral"};
  var eff=pol===1?percentile:(100-percentile);
  var c,l;
  if(eff>=95){c="#4ade80";l="strong";}
  else if(eff>=80){c="#4ade80";l="mild";}
  else if(eff<=5){c="#f87171";l="strong";}
  else if(eff<=20){c="#f87171";l="mild";}
  else{c="#d1d5db";l="neutral";}
  var sym=l==="strong"?'<span style="color:'+c+';font-size:9px;margin-right:2px;">&#9679;&#9679;</span>'
    :l==="mild"?'<span style="color:'+c+';font-size:9px;margin-right:2px;">&#9679;</span>'
    :'<span style="color:#94a3b8;font-size:9px;margin-right:2px;">&#9675;</span>';
  return{dot:sym,color:c,level:l};
}
// &e

// &s &BUILD_IRIS_TOOLTIP - HTML complet tooltip IRIS (commune, indicateur, rang, ratio ville)
function buildIrisTooltip(props,curK,feats,cityKpi){
  var dk=IRIS2D[curK]||curK;
  var dd=DDICT[dk]||{short:curK,unit:"",pol:0};
  var val=props[curK];
  var valStr=val==null?"\u2014":(dd.unit==="%"?(+val).toFixed(1)+"%":
    (dd.unit==="\u20ac/nuit"||dd.type==="prix")?Math.round(val).toLocaleString("fr-FR")+"\u00a0\u20ac":
    typeof val==="number"&&val%1!==0?(+val).toFixed(1):Math.round(val).toLocaleString("fr-FR"));
  var pol=dd.pol||0;
  // Percentile among active IRIS (n>=10)
  var vals=feats.filter(function(f){return(f.properties.n||0)>=10})
    .map(function(f){return f.properties[curK]}).filter(function(v){return v!=null&&!isNaN(v)})
    .sort(function(a,b){return a-b});
  var rank=null,total=vals.length,percentile=null;
  if(val!=null&&total>0){
    var below=vals.filter(function(v){return v<val}).length;
    percentile=Math.round((below/total)*100);
    rank=total-below;
  }
  var pi=polarityDot(pol,percentile);
  // Ratio vs ville
  var cityRef=cityKpi?cityKpi[dk]:null;
  var ratioStr="";
  if(cityRef!=null&&val!=null&&cityRef!==0){
    var rel=(val-cityRef)/Math.abs(cityRef);
    var dir=rel>=0?"sup.":"inf.";
    ratioStr=Math.abs(rel)>=1?" \u00b7 "+Math.abs(rel).toFixed(1)+"\u00d7 "+dir+" \u00e0 ville"
      :" \u00b7 "+Math.abs(Math.round(rel*100))+"% "+dir+" \u00e0 ville";
  }
  // Commune + arrondissement
  var commune=props.commune||"";
  var arr=props.arr||"";
  var loc=commune;
  if(arr&&arr!==commune)loc+=loc?" \u00b7 "+arr:arr;
  // Build HTML
  var html='<b style="color:#fff;font-size:12.5px;">'+(props.nom_iris||"\u2014")+'</b>';
  if(loc)html+='<br><span style="font-size:10.5px;color:#94a3b8;">'+loc+'</span>';
  html+='<br><span style="font-size:11px;">'+dd.short+' : <span style="color:#e2e8f0;font-weight:600;">'+valStr+'</span></span>';
  if(cityRef!=null){
    var cityValStr=dd.unit==="%"?(+cityRef).toFixed(1)+"%":Math.round(cityRef).toLocaleString("fr-FR");
    html+='  <span style="font-size:10px;color:#94a3b8;font-style:italic;">Ville '+cityValStr+'</span>';
  }
  if(rank!=null){
    html+='<br><span style="font-size:10px;padding-left:4px;">'+pi.dot+'<span style="color:#cbd5e1;">'+rank+'<sup>e</sup>/'+total+'</span>';
    html+='<span style="color:#94a3b8;">'+ratioStr+'</span></span>';
  }
  html+='<br><span style="font-size:10px;color:#94a3b8;">'+(props.n||0)+' annonces \u00b7 '+(props.prix_med||0)+'\u20ac/nuit</span>';
  return html;
}
// &e

// &s &CITY_TOOLTIP - Tooltip ville enrichi 7 KPIs + rang + ▲/▼ moyenne (monde/France)
var CITY_TOOLTIP_KEYS = ["n_listings","prix_med_entire","listings_1000hab","pct_entire","pct_multi","cr_top10_pct","rev_rating_med"];

function fmtTooltipVal(v, dd, key) {
  if (v == null || isNaN(+v)) return "\u2014";
  var n = +v;
  if (key === "rev_rating_med") return n.toFixed(2) + "/5";
  if (dd.type === "pct") return n.toFixed(1) + "\u00a0%";
  if (dd.type === "prix") return Math.round(n).toLocaleString("fr-FR") + "\u00a0\u20ac";
  if (n >= 1000) return Math.round(n).toLocaleString("fr-FR");
  if (n % 1 !== 0) return n.toFixed(1);
  return String(Math.round(n));
}

/**
 * Tooltip ville enrichi (carte monde, scatter, etc.)
 * @param {Object} d - Données ville (row KPI)
 * @param {Array} allData - Toutes les villes (pour rang + moyenne)
 * @param {string} [scope="monde"] - "monde" ou "france"
 * @returns {string} HTML tooltip
 */
function buildCityTooltip(d, allData, scope) {
  scope = scope || "monde";
  var name = d.city_fr || d.label || d.city || "";
  var cc = d.country_code || "";
  var countryName = COUNTRY_NAMES[cc] || cc;
  var contColor = (window.CONT_COL || {})[d.continent] || "#999";
  var total = allData.length;
  var scopeLabel = scope === "france" ? "moy. France" : "moy. monde";

  var html = '<div style="font-size:11.5px;line-height:1.5;min-width:260px;">';
  html += '<div style="margin-bottom:5px;"><b style="color:#fff;font-size:13px;">' + name + '</b>';
  html += ' <span style="color:#94a3b8;font-size:11px;">' + countryName + '</span>';
  html += '<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:' + contColor + ';margin-left:5px;vertical-align:middle;"></span></div>';

  // Header row
  html += '<table style="width:100%;border-collapse:collapse;">';
  html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.12);">';
  html += '<td style="color:#64748b;font-size:8px;padding:1px 4px 2px 0;"></td>';
  html += '<td style="color:#64748b;font-size:8px;padding:1px 4px 2px;text-align:right;">val</td>';
  html += '<td style="color:#64748b;font-size:8px;padding:1px 2px 2px;text-align:center;"></td>';
  html += '<td style="color:#64748b;font-size:8px;padding:1px 4px 2px;">' + scopeLabel + '</td>';
  html += '<td style="color:#64748b;font-size:8px;padding:1px 0 2px 4px;text-align:right;">/' + total + '</td>';
  html += '</tr>';

  for (var i = 0; i < CITY_TOOLTIP_KEYS.length; i++) {
    var k = CITY_TOOLTIP_KEYS[i];
    var val = d[k];
    if (val == null || isNaN(+val)) continue;
    var dd = DDICT[k] || {short: k, unit: "", type: "stock", pol: 0};
    var fmt = fmtTooltipVal(+val, dd, k);

    // Rank (desc)
    var vals = allData.map(function(x) { return +x[k]; }).filter(function(v) { return !isNaN(v); });
    var sorted = vals.slice().sort(function(a, b) { return a - b; });
    var desc = vals.slice().sort(function(a, b) { return b - a; });
    var rank = 1;
    for (var j = 0; j < desc.length; j++) { if (desc[j] > +val) rank++; else break; }

    // Percentile (for bar)
    var pct = 0;
    if (sorted.length > 1) {
      var below = sorted.filter(function(v) { return v < +val; }).length;
      pct = Math.round((below / (sorted.length - 1)) * 100);
    }

    // Average
    var avg = vals.reduce(function(a, b) { return a + b; }, 0) / (vals.length || 1);
    var avgFmt = fmtTooltipVal(avg, dd, k);

    // Triangle + color based on polarity
    var pol = dd.pol || 0;
    var aboveAvg = +val >= avg;
    var tri, triColor, barColor;
    if (pol === 0) {
      tri = "";
      triColor = "#94a3b8";
      barColor = "#64748b";
    } else {
      var isGood = (pol === 1 && aboveAvg) || (pol === -1 && !aboveAvg);
      tri = aboveAvg ? "\u25b2" : "\u25bc";
      triColor = isGood ? "#4ade80" : "#f87171";
      barColor = isGood ? "#4ade80" : "#f87171";
    }

    // Mini bar (percentile)
    var barW = 40;
    var fillW = Math.round(pct / 100 * barW);
    var barHtml = '<span style="display:inline-block;width:' + barW + 'px;height:6px;background:rgba(255,255,255,0.1);border-radius:2px;vertical-align:middle;position:relative;">' +
      '<span style="display:block;width:' + fillW + 'px;height:100%;background:' + barColor + ';border-radius:2px;opacity:0.7;"></span></span>';

    html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">';
    html += '<td style="color:#94a3b8;font-size:10px;padding:2px 4px 2px 0;white-space:nowrap;">' + dd.short + '</td>';
    // Triangle before value
    html += '<td style="color:#e2e8f0;font-weight:600;font-size:11px;padding:2px 4px;text-align:right;white-space:nowrap;">' +
      (tri ? '<span style="color:' + triColor + ';font-size:8px;margin-right:2px;">' + tri + '</span>' : '') + fmt + '</td>';
    // Bar
    html += '<td style="padding:2px 3px;">' + barHtml + '</td>';
    // Average
    html += '<td style="color:#b0b8c4;font-size:9.5px;padding:2px 4px;white-space:nowrap;">' + avgFmt + '</td>';
    // Rank (no /total, shown in header)
    html += '<td style="color:#cbd5e1;font-size:9.5px;padding:2px 0 2px 4px;text-align:right;white-space:nowrap;">' + rank + '<sup>e</sup></td>';
    html += '</tr>';
  }
  html += '</table></div>';
  return html;
}
window.buildCityTooltip = buildCityTooltip;
// &e

// &e (FIN-TOOLTIP_aaMAIN)

// &s &TABLE_HELPERS_aaMAIN - Fonctions tableaux (territoire + hôtes)

// &s &DIV_GAUGE - Jauge z-score bordeaux↔bleu
function divGauge(value,mean,std){
  if(std===0||mean==null)return{bar:"#d5d5d5",text:"#555",op:0.5};
  var z=(value-mean)/std;
  if(z<-2)   return{bar:"#2171b5",text:"#084594",op:0.7};
  if(z<-1)   return{bar:"#6baed6",text:"#084594",op:0.6};
  if(z<-0.5) return{bar:"#c6dbef",text:"#0a4c6a",op:0.55};
  if(z<=0.5) return{bar:"#b8c2cc",text:"#555",op:0.52};
  if(z<=1)   return{bar:"#e8b4c0",text:"#6d1a36",op:0.55};
  if(z<=2)   return{bar:"#c97b8e",text:"#5a1430",op:0.6};
  return{bar:"#a63d5a",text:"#4a0e24",op:0.7};
}
// &e

// &s &BAR_CELL - Cellule barre avec z-score
function barCell(val,max,mean,std,key,isAggregate){
  if(val==null)return"\u2014";
  var info=DDICT[key]||{type:"stock",pol:0};
  var fmt=info.type==="pct"?val.toFixed(1)+"%":
    (info.unit||"").indexOf("/5")>=0?val.toFixed(2):
    typeof val==="number"&&val>=1000?Math.round(val).toLocaleString("fr-FR"):
    typeof val==="number"&&val%1!==0?val.toFixed(1):String(Math.round(val));
  // Agrégats (France/Ville) sur volumes : nombre gras sans barre
  if(isAggregate&&(info.type==="stock")){
    return'<span style="font-weight:700;color:#1696d2;">'+fmt+'</span>';
  }
  var w=max>0?Math.min(val/max*100,100):0;
  var g=divGauge(val,mean,std);
  return'<span class="bar-bg"><span class="bar-fill" style="width:'+w+'%;background:'+g.bar+';opacity:'+g.op+'"></span></span> <span style="color:'+g.text+'">'+fmt+'</span>';
}
// &e

// &s &COL_STATS - Statistiques colonnes pour z-score
function colStats(data,keys){
  var s={};
  for(var i=0;i<keys.length;i++){
    var k=keys[i];
    var vals=data.filter(function(d){return d.level==="arr"||d.level==="iris"})
      .map(function(d){return d[k]}).filter(function(v){return v!=null&&!isNaN(v)});
    var max=vals.length?Math.max.apply(null,vals):1;
    var mean=vals.length?vals.reduce(function(a,b){return a+b},0)/vals.length:0;
    var std=vals.length>1?Math.sqrt(vals.reduce(function(s,v){return s+Math.pow(v-mean,2)},0)/(vals.length-1)):0;
    s[k]={max:max,mean:mean,std:std};
  }
  return s;
}
// &e

// &s &TERRITORY_TABLE - Wrapper → délègue à buildDataTable (jcn-tableojs.js)
function territoryTable(data,containerId){
  var container=document.getElementById(containerId);
  if(!container)return;
  if(typeof window.buildDataTable!=="function"){
    console.warn("territoryTable: buildDataTable not loaded (jcn-tableojs.js manquant)");
    return;
  }
  // Extraire lignes de référence (country/city) du data
  var fr=data.find(function(d){return d.level==="country"});
  var city=data.find(function(d){return d.level==="city"});
  var rest=data.filter(function(d){return d.level!=="country"&&d.level!=="city"});
  var refRows=[];
  if(fr)refRows.push({label:fr.label,data:fr,bgColor:"#f0f9ff"});
  if(city)refRows.push({label:city.label,data:city,bgColor:"#fefce8"});
  var maille=rest.length>0&&rest[0].level==="iris"?"Quartier IRIS":"Arrondissement";

  window.buildDataTable(container,rest,{
    keys:["n_listings","prix_med","ratio_lh","entire_1000rp","listings_1000rps","pct_multi","pct_entire","pct_longterm","n_hosts"],
    labelCol:"label",
    labelFallback:"label",
    labelHeader:maille,
    colorCol:null,
    colorMap:{},
    defaultSort:"n_listings",
    refRows:refRows,
    maxHeight:420,
    maxRows:1500
  });
}
// &e

// &s &HOST_TABLE - Tableau top hôtes triable
function hostTable(data,containerId){
  var sortCol="n_listings",sortAsc=false;
  function render(){
    var rows=data.slice().sort(function(a,b){return sortAsc?a[sortCol]-b[sortCol]:b[sortCol]-a[sortCol]});
    var c=document.getElementById(containerId);
    if(!c)return;
    var tb=c.querySelector(".th");
    if(!tb)return;
    tb.innerHTML='<table><thead><tr><th data-col="host_name">H\u00f4te</th><th data-col="n_listings" style="text-align:right;">Ann.</th></tr></thead><tbody>'+
      rows.map(function(d){return'<tr><td style="max-width:90px;overflow:hidden;text-overflow:ellipsis;font-size:9px;">'+(d.host_name||"\u2014")+'</td><td style="font-weight:600;text-align:right;font-size:9px;">'+d.n_listings+'</td></tr>'}).join("")+"</tbody></table>";
    tb.querySelectorAll("th").forEach(function(th){
      th.addEventListener("click",function(){
        var col=th.dataset.col;
        if(sortCol===col)sortAsc=!sortAsc;else{sortCol=col;sortAsc=false}
        render();
      });
    });
  }
  render();
}
// &e

// &e (FIN-TABLE_HELPERS_aaMAIN)

// &s &MAP_BUILDER_aaMAIN - Construction carte MapLibre

// &s &BUILD_MAP - Carte MapLibre avec couches IRIS/heatmap/points
function buildMap(container,rows,mode,config){
  config=config||{};
  // Compute bbox for maxBounds (with padding)
  var lats=rows.map(function(d){return d.latitude}).filter(Boolean);
  var lngs=rows.map(function(d){return d.longitude}).filter(Boolean);
  var pad=0.03;
  var bbox=lats.length?[[Math.min.apply(null,lngs)-pad,Math.min.apply(null,lats)-pad],[Math.max.apply(null,lngs)+pad,Math.max.apply(null,lats)+pad]]:null;
  var initCenter=config.center||[2.35,48.86];
  var initZoom=config.zoom||11;
  var map=new maplibregl.Map({
    container:container,
    style:"https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    center:initCenter,
    zoom:initZoom,
    minZoom:9,maxZoom:18,
    maxBounds:bbox,
    attributionControl:false,
    cooperativeGestures:true,
    dragRotate:false,
    pitchWithRotate:false,
    touchPitch:false,
    renderWorldCopies:false,
    fadeDuration:0
  });
  map.addControl(new maplibregl.NavigationControl({showCompass:false}),"top-right");
  // Reset zoom button
  var resetBtn=document.createElement("button");
  resetBtn.textContent="\u21ba";
  resetBtn.title="Recentrer";
  resetBtn.style.cssText="position:absolute;top:80px;right:8px;z-index:5;width:30px;height:30px;background:white;border:1px solid #ccc;border-radius:4px;font-size:16px;cursor:pointer;box-shadow:0 1px 2px rgba(0,0,0,0.1);display:flex;align-items:center;justify-content:center;";
  resetBtn.addEventListener("click",function(){map.flyTo({center:initCenter,zoom:initZoom,duration:600})});
  container.parentNode.appendChild(resetBtn);
  map.on("load",function(){
    var geo={type:"FeatureCollection",features:rows.map(function(d){return{type:"Feature",geometry:{type:"Point",coordinates:[d.longitude,d.latitude]},properties:{room_type:d.room_type,price:d.price,is_multi:d.is_multi}}})};
    map.addSource("pts",{type:"geojson",data:geo,maxzoom:14});
    // Heatmap layer (below IRIS for mouse interaction — hidden in iris mode)
    if(mode==="heatmap"||mode==="iris"){
      map.addLayer({id:"heat",type:"heatmap",source:"pts",
        layout:{visibility:mode==="heatmap"?"visible":"none"},
        paint:{
        "heatmap-weight":["interpolate",["linear"],["get","price"],10,0.2,200,0.7,500,1],
        "heatmap-intensity":["interpolate",["linear"],["zoom"],10,0.4,14,1.2],
        "heatmap-radius":["interpolate",["linear"],["zoom"],10,6,13,12,16,20],
        "heatmap-color":["interpolate",["linear"],["heatmap-density"],0,"rgba(0,0,0,0)",0.15,"#ffffb2",0.35,"#fd8d3c",0.55,"#f03b20",0.75,"#bd0026",1,"#800026"],
        "heatmap-opacity":["interpolate",["linear"],["zoom"],11,0.6,16,0.25]}});
    }
    // IRIS choropleth layer
    if(mode==="iris"&&config.irisJson){
      var irisGeo=JSON.parse(config.irisJson);
      map.addSource("iris",{type:"geojson",data:irisGeo});
      var curK="prix_med",curP="niveau";
      function doChoro(){
        var ckpi=config.cityKpi||{};
        var refKey=IRIS2D[curK]||curK;
        var bins=irisBins(irisGeo.features,curK,curP,ckpi[refKey]);
        if(!bins)return;
        var expr=["case",["<",["get","n"],10],"#d9d9d9",stepEx(curK,bins.brk,bins.col)];
        map.setPaintProperty("iris-fill","fill-color",expr);
        // Reset filter when indicator changes
        if(map.getLayer("iris-fill")){map.setFilter("iris-fill",null);map.setFilter("iris-border",null);}
        var dd=DDICT[IRIS2D[curK]]||{short:curK,unit:""};
        var lg=container.parentNode.querySelector(".map-legend");
        if(lg){lg.innerHTML="";lg.appendChild(buildLegend(bins,dd.label||dd.short,irisGeo.features,curK,map));}
        var itag=document.getElementById("indic-"+(config.cityId||""));
        if(itag){itag.textContent=dd.label||dd.short||curK;}
      }
      var b0=irisBins(irisGeo.features,curK,curP,(config.cityKpi||{})[IRIS2D[curK]||curK]);
      var initColor=b0?["case",["<",["get","n"],10],"#d9d9d9",stepEx(curK,b0.brk,b0.col)]:["literal","#ccc"];
      map.addLayer({id:"iris-fill",type:"fill",source:"iris",paint:{
        "fill-color":initColor,"fill-opacity":0.65}});
      map.addLayer({id:"iris-border",type:"line",source:"iris",paint:{"line-color":"#888","line-width":0.5,"line-opacity":0.4}});
      map.addLayer({id:"iris-hl",type:"line",source:"iris",paint:{"line-color":"#0a4c6a","line-width":2.5,"line-opacity":0},filter:["==","code_iris",""]});
      var lg=document.createElement("div");lg.className="map-legend";
      container.parentNode.appendChild(lg);
      var ct=document.createElement("div");ct.className="map-ctrl";
      var ch='<span class="mt">Indicateur</span><select class="si">';
      IRIS_KEYS.forEach(function(k){var dd=DDICT[IRIS2D[k]]||{short:k};
        ch+='<option value="'+k+'"'+(k==="prix_med"?" selected":"")+'>'+dd.short+'</option>';});
      ch+='</select><span class="mt">Palette</span><select class="sp">';
      Object.keys(PAL_MODES).forEach(function(p){
        ch+='<option value="'+p+'"'+(p===curP?" selected":"")+'>'+PAL_MODES[p]+'</option>';});
      ch+='</select>';
      ct.innerHTML=ch;container.parentNode.appendChild(ct);
      var palSel=ct.querySelector(".sp");
      ct.querySelector(".si").addEventListener("change",function(e){
        curK=e.target.value;
        curP="niveau";palSel.value=curP;
        doChoro();
      });
      palSel.addEventListener("change",function(e){curP=e.target.value;doChoro();});
      doChoro();
      initTooltip();
      map.on("mousemove","iris-fill",function(e){
        var p=e.features[0].properties;
        map.setFilter("iris-hl",["==","code_iris",p.code_iris]);
        map.setPaintProperty("iris-hl","line-opacity",1);
        showTooltip(e.originalEvent,buildIrisTooltip(p,curK,irisGeo.features,config.cityKpi));
      });
      map.on("mouseleave","iris-fill",function(){map.setPaintProperty("iris-hl","line-opacity",0);hideTooltip();});
    }
    // Points layer (always added)
    map.addLayer({id:"pts-layer",type:"circle",source:"pts",
      layout:{visibility:mode==="points"?"visible":"none"},
      paint:{"circle-radius":["interpolate",["linear"],["zoom"],10,1,14,2.5,17,5],"circle-color":["match",["get","room_type"],"Entire home/apt","#ca5800","Private room","#1696d2","Shared room","#55b748","#999"],"circle-opacity":0.6}});
    // Click popup on points
    map.on("click","pts-layer",function(e){
      var p=e.features[0].properties;
      new maplibregl.Popup({offset:8}).setLngLat(e.lngLat)
        .setHTML('<b>'+p.room_type+'</b><br>'+p.price+'\u20ac \u00b7 Multi:'+(p.is_multi?"Oui":"Non")).addTo(map);
    });
  });
  // Points + Heatmap toggles (for iris/heatmap modes)
  if(mode!=="points"){
    var tgl=document.createElement("div");
    tgl.style.cssText="position:absolute;bottom:8px;right:8px;z-index:5;background:rgba(255,255,255,0.92);padding:4px 8px;border-radius:4px;font-size:10px;box-shadow:0 1px 2px rgba(0,0,0,0.12);display:flex;flex-direction:column;gap:2px;";
    var tglH='';
    if(mode==="iris")tglH+='<label style="cursor:pointer;display:flex;align-items:center;gap:3px;margin:0;"><input type="checkbox" class="hm-tgl" style="margin:0;"> Heatmap</label>';
    tglH+='<label style="cursor:pointer;display:flex;align-items:center;gap:3px;margin:0;"><input type="checkbox" class="pts-tgl" style="margin:0;"> Points</label>';
    tgl.innerHTML=tglH;
    container.parentNode.appendChild(tgl);
    tgl.querySelector(".pts-tgl").addEventListener("change",function(e){
      if(map.isStyleLoaded()) map.setLayoutProperty("pts-layer","visibility",e.target.checked?"visible":"none");
    });
    var hmTgl=tgl.querySelector(".hm-tgl");
    if(hmTgl)hmTgl.addEventListener("change",function(e){
      if(map.isStyleLoaded()) map.setLayoutProperty("heat","visibility",e.target.checked?"visible":"none");
    });
  }
  return map;
}
// &e

// &e (FIN-MAP_BUILDER_aaMAIN)

// &s &CITY_ROW_aaMAIN - Assemblage section ville (carte + tableaux)

// &s &CITY_STORY - Bandeau KPI story par ville
function cityStory(ck, cityName, nPts, frKpi, territoryData) {
  var arrData = (territoryData||[]).filter(function(d){return d.level==="arr"||d.level==="iris"})
    .slice().sort(function(a,b){return(b.n_listings||0)-(a.n_listings||0)});
  var top2 = arrData.slice(0,2).map(function(d){return d.label});
  var html = '<span><span class="sk">' + (ck.n_listings||0).toLocaleString("fr-FR") + '</span> <span class="sl">annonces</span></span>';
  html += '<span><span class="sk accent">' + (ck.prix_med||0) + '\u00a0\u20ac</span> <span class="sl">m\u00e9dian/nuit</span></span>';
  html += '<span><span class="sk">' + (ck.pct_multi||0) + '%</span> <span class="sl">multi</span></span>';
  html += '<span><span class="sk">' + (ck.pct_entire||0) + '%</span> <span class="sl">entiers</span></span>';
  if(ck.top10_share) html += '<span><span class="sk" style="color:#6d1a36;">' + ck.top10_share + '%</span> <span class="sl">concentr.</span></span>';
  if(top2.length) html += '<span class="sp">(' + top2.join(", ") + ')</span>';
  return html;
}
// &e

// &s &BUILD_CITY_ROW - Construction complète section ville
function buildCityRow(id, cityName, points, mapMode, mapConfig, territoryData, hostsData, frKpi, irisData) {
  var row = document.createElement("div");
  row.className = "city-row";
  var nPts = points.length;
  var labels = {iris:"IRIS + Points",points:"Points",heatmap:"Heatmap + Points"};
  var modeLabel = labels[mapMode] || mapMode;

  // Extract city KPI from territory data
  var ck = territoryData.find(function(d){return d.level==="city"}) || {};

  // MAP CARD (col 1 — spans full height)
  var mapCard = document.createElement("div");
  mapCard.className = "city-card";
  var cityColor = mapConfig.color || "#6b7280";
  mapCard.innerHTML = '<div class="city-card-header map-header" style="background:' + cityColor + '"><span>' + cityName + '</span><span class="indic-tag" id="indic-' + id + '">Prix m\u00e9dian</span></div>';
  var mapWrap = document.createElement("div");
  mapWrap.style.cssText = "flex:1;position:relative;min-height:0;";
  /* IRIS legend created dynamically in buildMap */
  if (mapMode==="heatmap") {
    var leg2 = document.createElement("div");
    leg2.className = "map-legend";
    leg2.innerHTML = '<div style="font-weight:600;">Densit\u00e9 prix</div><div class="lg-bar"><div style="background:#ffffb2"></div><div style="background:#fd8d3c"></div><div style="background:#f03b20"></div><div style="background:#bd0026"></div><div style="background:#800026"></div></div><div class="lg-labels"><span>Faible</span><span>Fort</span></div>';
    mapWrap.appendChild(leg2);
  }
  var mapDiv = document.createElement("div");
  mapDiv.style.cssText = "position:absolute;top:0;left:0;right:0;bottom:0;";
  mapWrap.appendChild(mapDiv);
  mapCard.appendChild(mapWrap);
  row.appendChild(mapCard);

  // RIGHT PANEL (col 2 — sub-grid: story + territory + hosts)
  var rightPanel = document.createElement("div");
  rightPanel.className = "city-right";

  // STORY BLOCK (spans both sub-columns)
  var story = document.createElement("div");
  story.className = "city-story";
  story.style.borderTop = "3px solid " + cityColor;
  story.innerHTML = cityStory(ck, cityName, nPts, frKpi, territoryData);
  rightPanel.appendChild(story);

  // TERRITORY TABLE CARD
  var tblCard = document.createElement("div");
  tblCard.className = "city-card";
  tblCard.id = "terr-" + id;
  var hasIris = irisData && irisData.length > 0;
  var toggleHtml = hasIris ?
    ' <select class="maille-toggle" style="font-size:10px;padding:1px 3px;margin-left:6px;"><option value="iris" selected>IRIS</option><option value="arr">Arrondissement</option></select>' : '';
  tblCard.innerHTML = '<div class="city-card-header">Territoires \u00b7 ' + cityName + toggleHtml + '</div>' +
    '<div class="t-toolbar"><input placeholder="Filtrer..."><span class="info"></span></div><div class="t" style="flex:1;"></div>';
  rightPanel.appendChild(tblCard);

  // HOSTS TABLE CARD
  var hostCard = document.createElement("div");
  hostCard.className = "city-card";
  hostCard.id = "hosts-" + id + "-c";
  hostCard.innerHTML = '<div class="city-card-header">Top 50 h\u00f4tes \u00b7 ' + cityName + '</div><div class="th" style="overflow:auto;flex:1;"></div>';
  rightPanel.appendChild(hostCard);

  row.appendChild(rightPanel);

  return { element:row, init:function(){
    buildMap(mapDiv, points, mapMode, mapConfig);
    // Default: IRIS si dispo, sinon arr
    var activeData = hasIris ? irisData : territoryData;
    territoryTable(activeData, "terr-"+id);
    hostTable(hostsData, "hosts-"+id+"-c");
    if (hasIris) {
      var tog = tblCard.querySelector(".maille-toggle");
      if (tog) tog.addEventListener("change", function(e) {
        activeData = e.target.value === "iris" ? irisData : territoryData;
        territoryTable(activeData, "terr-"+id);
      });
    }
  } };
}
// &e

// &e (FIN-CITY_ROW_aaMAIN)
