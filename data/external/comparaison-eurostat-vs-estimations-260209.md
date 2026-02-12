# Comparaison Eurostat Urban Audit vs estimations city_reference_data.py

**Date** : 2026-02-09
**Source Eurostat** : API REST `urb_cpop1` (population) + `urb_clivcon` (logements, indic SA1011V)
**Source estimations** : `scripts/city_reference_data.py` — 18 confirmées (stats officielles) + 17 estimées (ratios nationaux)

## Verdict

- **Population commune propre** : Eurostat confirme nos chiffres pour les villes sans flag "greater city". Fiable.
- **Logements** : Eurostat Urban Audit **inutilisable** — données 2011 pour la plupart, incohérences flagrantes (Berlin 302K au lieu de 2M). Nos estimations sont meilleures.
- **Greater city** : ~50 % des villes dans Eurostat utilisent le périmètre agglomération, pas commune. Non comparable avec Inside Airbnb (commune).

## Villes city proper (non GC) — population fiable

| Ville | Pays | Nos Pop | Eurostat Pop | Année EU | Écart | Status |
|-------|------|---------|-------------|----------|-------|--------|
| Berlin | DEU | 3 755 000 | 3 662 381 | 2024 | -2,5% | Confirmé |
| Bologna | ITA | 397 000 | 390 151 | 2025 | -1,7% | Confirmé |
| Edinburgh | GBR | 513 000 | 515 855 | 2018 | +0,6% | Confirmé |
| Florence | ITA | 372 000 | 361 705 | 2025 | -2,8% | Confirmé |
| Istanbul | TUR | 15 840 000 | 9 897 599 | 2004 | — | EU obsolète (2004) |
| London | GBR | 8 800 000 | 8 866 541 | 2018 | +0,8% | Confirmé |
| Manchester | GBR | 552 000 | 546 564 | 2018 | -1,0% | Confirmé |
| Prague | CZE | 1 360 000 | 1 275 406 | 2022 | -6,2% | Confirmé (écart croissance) |
| Rome | ITA | 2 750 000 | 2 747 290 | 2025 | -0,1% | Confirmé |
| Sevilla | ESP | 685 000 | 881 124 | 2023 | +28,6% | Suspect — EU périmètre élargi ? |
| Thessaloniki | GRC | 319 000 | 315 196 | 2011 | -1,2% | Confirmé (EU ancien) |
| Venice | ITA | 258 000 | 249 490 | 2025 | -3,3% | Confirmé |

## Villes greater city (GC) — Eurostat = agglomération

| Ville | Pays | Nos Pop (commune) | Eurostat Pop (agglo) | Année EU | Facteur EU/nous |
|-------|------|-------------------|---------------------|----------|-----------------|
| Amsterdam | NLD | 921 000 | 1 073 736 | 2024 | ×1,2 |
| Athens | GRC | 643 000 | 2 622 404 | 2013 | ×4,1 |
| Barcelona | ESP | 1 660 000 | 3 767 382 | 2023 | ×2,3 |
| Bergamo | ITA | 122 000 | 253 256 | 2025 | ×2,1 |
| Bordeaux | FRA | 260 000 | 773 626 | 2022 | ×3,0 |
| Brussels | BEL | 1 220 000 | 1 264 371 | 2024 | ×1,0 (19 communes = OK) |
| Budapest | HUN | 1 750 000 | 1 671 004 | 2023 | ×1,0 (commune ≈ agglo) |
| Dublin | IRL | 590 000 | 1 325 700 | 2016 | ×2,2 |
| Lisbon | PRT | 545 000 | 1 965 363 | 2025 | ×3,6 |
| Lyon | FRA | 523 000 | 1 296 104 | 2022 | ×2,5 |
| Madrid | ESP | 3 400 000 | 5 115 272 | 2023 | ×1,5 |
| Milan | ITA | 1 396 000 | 3 565 055 | 2025 | ×2,6 |
| Naples | ITA | 918 000 | 2 977 204 | 2025 | ×3,2 |
| Oslo | NOR | 709 000 | 699 827 | 2023 | ×1,0 (commune ≈ agglo) |
| Paris | FRA | 2 133 000 | 10 353 710 | 2022 | ×4,9 |
| Porto | PRT | 232 000 | 1 017 569 | 2025 | ×4,4 |
| Stockholm | SWE | 985 000 | 1 626 241 | 2025 | ×1,7 |
| Valencia | ESP | 800 000 | 1 439 503 | 2023 | ×1,8 |
| Vienna | AUT | 2 010 000 | 1 766 746 | 2014 | ×0,9 (EU ancien, 2014) |
| Zurich | CHE | 443 000 | 725 893 | 2025 | ×1,6 |

## Villes absentes d'Eurostat

| Ville | Pays | Raison probable |
|-------|------|-----------------|
| Copenhagen | DNK | Code non trouvé dans urb_cpop1 |
| Malaga | ESP | Pas dans le panel Urban Audit |
| Munich | DEU | Code DE004C non disponible |

## Logements Eurostat — problèmes identifiés

| Problème | Exemples | Impact |
|----------|----------|--------|
| Données anciennes (2011) | Rome, Milan, Barcelona, London | Sous-estiment le parc actuel |
| Valeurs incohérentes | Berlin 302K (devrait être 2M), Amsterdam 86K (devrait être 475K) | Inutilisable |
| Données très anciennes | Istanbul 2000, Brussels 2001, Oslo 2001 | Inutilisable |
| Seules données récentes fiables | Paris 1,99M (2022), Bordeaux 161K (2022), Lyon 252K (2022) | France OK (INSEE) |

## Recommandation

1. **Garder `city_reference_data.py`** comme source principale pour les ratios de pression
2. **Utiliser Eurostat** uniquement pour valider la population des villes city proper (non GC)
3. **Documenter** dans la méthodologie que les logements proviennent de sources nationales, pas d'Eurostat
4. **Prochaine étape** : intégrer `city_reference_data.py` dans le pipeline sp07 pour recalculer le parquet avec données commune propre

## Codes Eurostat Urban Audit retenus

```
AT001C: vienna       BE001C: brussels     CH002C: zurich
CZ001C: prague       DE001C: berlin       EL001C: athens
EL002C: thessaloniki ES001C: madrid       ES002C: barcelona
ES003C: valencia     ES004C: sevilla      FR001C: paris
FR002C: lyon         FR005C: bordeaux     HU001C: budapest
IE001C: dublin       IT001C: rome         IT002C: milan
IT003C: naples       IT007C: florence     IT009C: bologna
IT011C: venice       IT073C: bergamo      NL001C: amsterdam
NO001C: oslo         PT001C: lisbon       PT002C: porto
SE001C: stockholm    TR012C: istanbul     UK001C: london
UK007C: edinburgh    UK008C: manchester
```

## API Eurostat utilisée

```
Population : urb_cpop1 → indic_ur=DE1001V
Logements  : urb_clivcon → indic_ur=SA1011V (total) / SA1012V (occupés)
Format     : JSON via REST API
URL base   : https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/
```
