# Référence — territoryTable() legacy (dash France)

Archive de la signature et structure de `territoryTable()` dans `pbnbdash-util-helper.js`,
avant migration future vers `jcn-tableojs.js` (ES module unifié).

## Localisation

`reports/helpers/pbnbdash-util-helper.js` — section `&TERRITORY_TABLE` (lignes ~558-619)

## Signature

```javascript
function territoryTable(data, containerId)
```

- `data` : Array avec champ `level` ("country" | "city" | "arr" | "iris")
- `containerId` : ID du conteneur DOM (string)

## Colonnes (keys)

```javascript
var keys = [
  "n_listings", "prix_med", "ratio_lh",
  "listings_1000hab", "listings_1000hsg",
  "pct_multi", "pct_entire", "pct_longterm", "n_hosts"
];
```

## Lignes sticky (multi-niveaux)

- `level === "country"` → `.sticky-fr` (France, sticky top = thead height)
- `level === "city"` → `.sticky-city` (Ville, sticky top = thead + France row)
- Autres → lignes normales (arr / iris)

## Supra-headers

Pas de supra-headers dans la version actuelle (mais prévu pour migration).

## Dépendances

- `DDICT` (window global) — labels short/unit
- `divGauge(value, mean, std)` — couleurs z-score bordeaux↔bleu
- `barCell(val, max, mean, std, key, isAggregate)` — rendu cellule barre
- `colStats(data, keys)` — stats par colonne (filtre level=arr|iris)

## Label colonne

- Header dynamique selon level : "Quartier IRIS" ou "Arrondissement"
- `data-col="label"` pour tri alphabétique

## Différences avec jcn-tableojs.js (à combler)

| Feature | territoryTable | jcn-tableojs |
|---------|---------------|--------------|
| Format | Plain JS (window) | ES module (export) |
| Sticky rows | Multi-level (country+city) | Single refRow |
| Stats filtre | Exclut country/city | Tous les rows |
| Label col | `d.label` fixe | Configurable labelCol |
| Supra-headers | Non | Oui (groups config) |
| Sticky col 1 | Non | Oui |
| P2/P98 capping | Non | Oui |
| Trait moyenne | Non | Oui |
| DDICT tips | Non | Oui (title sur th) |

## TODO migration

1. Ajouter `config.refRows` (array) pour supporter N lignes sticky avec niveaux
2. Ajouter `config.statsFilter` pour exclure certains levels du calcul stats
3. Le label dynamique (IRIS vs Arrondissement) peut être passé via `config.labelHeader`
4. Les colonnes et supra-headers seront passés via `config.keys` et `config.groups`
5. Tester avec le dash France (autre conversation)
