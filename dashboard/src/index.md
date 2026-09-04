---
title: Airbnb Dashboard
toc: false
style: styles/pbnb-dashboard.css
---

```js
import { createBanner, createNav, PBNB_PAGES } from "./helpers/layout.js";

display(createBanner({
  voletTitle: "Observatoire des marches locatifs",
  color: "#0a4c6a",
  navElement: createNav(PBNB_PAGES, "__index__")
}));
```

Analyse multi-echelle des marches Airbnb — Inside Airbnb, juin 2025.

- [**France**](./dash-france) — Paris, Lyon, Bordeaux, BAB (IRIS + arrondissements)
- [**Monde**](./dash-monde) — 74 villes, 31 pays (carte + table + scatter)
