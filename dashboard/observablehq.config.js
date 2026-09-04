export default {
  title: "Airbnb — Dashboard",
  root: "src",
  // Servi en sous-chemin du portfolio (Netlify) : indispensable pour que les assets resolvent.
  base: "/rapports/dash_pbnb/",
  head: '<link rel="icon" type="image/svg+xml" href="./favicon.svg"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
  pages: [
    {name: "France", path: "/dash-france"},
    {name: "Monde", path: "/dash-monde"}
  ],
  theme: "light",
  toc: false,
  sidebar: false,
  pager: false,
  footer: "Airbnb Observatory | Inside Airbnb, juin 2025 | Vincent Roue"
};
