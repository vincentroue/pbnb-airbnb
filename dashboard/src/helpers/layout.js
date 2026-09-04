// &s LAYOUT_aaMAIN - Composants banniere + navigation dashboard pbnb
// Adapte de ptod layout.js, simplifie pour pbnb Airbnb
// Exports: createBanner, createNav, PBNB_PAGES

// &s BANNER - Banniere collee en haut

/**
 * Cree la banniere pbnb
 * @param {Object} opts
 * @param {string} opts.voletTitle - Titre du volet actif
 * @param {string} [opts.color="#0a4c6a"] - Couleur accent volet
 * @param {HTMLElement|null} [opts.navElement] - Navigation (createNav)
 * @returns {HTMLElement}
 */
export function createBanner(opts) {
  const { voletTitle = "", color = "#0a4c6a", navElement = null } = opts;

  const banner = document.createElement("div");
  banner.className = "pbnb-banner";
  banner.style.setProperty("--volet-color", color);

  const inner = document.createElement("div");
  inner.className = "pbnb-banner-inner";

  // Brand + titre volet
  const titles = document.createElement("div");
  titles.className = "pbnb-banner-titles";
  const brand = document.createElement("a");
  brand.className = "pbnb-brand";
  brand.href = "./";
  brand.textContent = "Airbnb";
  titles.appendChild(brand);

  if (voletTitle) {
    const dash = document.createElement("span");
    dash.className = "pbnb-dash";
    dash.textContent = " \u2014 ";
    titles.appendChild(dash);
    const volet = document.createElement("span");
    volet.className = "pbnb-volet";
    volet.textContent = voletTitle;
    titles.appendChild(volet);
  }

  inner.appendChild(titles);

  // Nav
  if (navElement) inner.appendChild(navElement);

  // Source
  const src = document.createElement("span");
  src.className = "pbnb-banner-source";
  src.textContent = "Inside Airbnb, juin 2025";
  inner.appendChild(src);

  banner.appendChild(inner);
  return banner;
}

// &e BANNER

// &s NAV - Navigation entre pages

/**
 * Cree la barre de navigation
 * @param {Array<{id, label, href, color?}>} pages
 * @param {string} activePage - ID page active
 * @returns {HTMLElement}
 */
export function createNav(pages, activePage) {
  const nav = document.createElement("nav");
  nav.className = "pbnb-nav";

  for (const page of pages) {
    const a = document.createElement("a");
    a.className = "pbnb-nav-btn";
    a.textContent = page.label;
    a.href = page.href;
    if (page.id === activePage) a.classList.add("active");
    nav.appendChild(a);
  }
  return nav;
}

// &e NAV

// &s PAGES_CONFIG

export const PBNB_PAGES = [
  { id: "france", label: "France", href: "./dash-france", color: "#0a4c6a" },
  { id: "monde", label: "Monde", href: "./dash-monde", color: "#0d6a5e" }
];

// &e PAGES_CONFIG

// &e LAYOUT_aaMAIN
