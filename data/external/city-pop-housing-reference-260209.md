# Référentiel population et logements — 35 villes européennes

**Date** : 2026-02-09
**Périmètre** : Commune propre (city proper), PAS aire métropolitaine
**Usage** : Calcul ratios pression Airbnb (listings/1000 hab, listings/1000 logements, entire homes/logements)
**Script source** : `scripts/city_reference_data.py`

## Données confirmées (18 villes — sources statistiques officielles)

| Ville | Pays | Population | Logements | Ratio L/1000 | Source pop | Source logements | Année |
|-------|------|-----------|-----------|-------------|------------|-----------------|-------|
| London | GBR | 8 800 000 | 3 800 000 | 432 | GLA mid-year 2023 | London Datastore / MHCLG 2023 | 2023 |
| Paris | FRA | 2 133 000 | 1 399 000 | 656 | INSEE RP2022 | INSEE RP2022 LOG T1 dept 75 | 2022 |
| Berlin | DEU | 3 755 000 | 2 044 000 | 544 | Statistik Berlin-Brandenburg | Statistik Berlin-Brandenburg end 2023 | 2023 |
| Munich | DEU | 1 594 000 | 837 000 | 525 | Statistisches Amt München | Statistisches Amt München 2023 | 2023 |
| Amsterdam | NLD | 921 000 | 475 000 | 516 | CBS 2023 | CBS/Amsterdam Wonen 2023: 474 735 | 2023 |
| Vienna | AUT | 2 010 000 | 1 000 000 | 498 | Statistik Austria 2023 | Wien.gv.at "about one million" | 2023 |
| Copenhagen | DNK | 660 000 | 347 000 | 526 | Statistics Denmark 2023 | Statistics Denmark 2023: 346 500 | 2023 |
| Prague | CZE | 1 360 000 | 630 000 | 463 | CZSO 2023 | CZSO Census 2021: ~630K occupés (total ~700K) | 2021 |
| Dublin | IRL | 590 000 | 251 000 | 425 | CSO Census 2022 | CSO Census 2022: 250 632 (Dublin City) | 2022 |
| Oslo | NOR | 709 000 | 353 000 | 498 | SSB 2024 | Oslo Kommune Jan 2024: 353 256 | 2024 |
| Stockholm | SWE | 985 000 | 487 000 | 494 | SCB 2023 | SCB/Stockholm Stad 2023: 486 542 | 2023 |
| Zurich | CHE | 443 000 | 234 000 | 528 | Stadt Zürich 2023 | Stadt Zürich 2023: ~233 900 | 2023 |
| Manchester | GBR | 552 000 | 215 000 | 389 | ONS Census 2021 | Manchester Council Census 2021: 214 700 | 2021 |
| Edinburgh | GBR | 513 000 | 253 000 | 493 | Scotland Census 2022 | Scotland Census 2022: 252 731 | 2022 |
| Lisbon | PRT | 545 000 | 320 000 | 587 | INE Census 2021 | INE Portugal Census 2021 | 2021 |
| Porto | PRT | 232 000 | 133 000 | 573 | INE Census 2021 | INE Portugal Census 2021 | 2021 |
| Lyon | FRA | 523 000 | 319 000 | 610 | INSEE RP2022 | INSEE RP2022 LOG T1: 318 612 | 2022 |
| Bordeaux | FRA | 260 000 | 168 000 | 646 | INSEE RP2022 | INSEE RP2022 LOG T1: 168 458 | 2022 |

## Données estimées (17 villes — ratios nationaux appliqués)

| Ville | Pays | Population | Logements | Ratio L/1000 | Source pop | Méthode estimation logements |
|-------|------|-----------|-----------|-------------|------------|------------------------------|
| Rome | ITA | 2 750 000 | 1 380 000 | 502 | ISTAT 2021 | Metro City Rome 2,2M × 63% commune |
| Istanbul | TUR | 15 840 000 | 5 540 000 | 350 | TUIK 2023 | TUIK ~350/1000 (méga-ville, grands ménages) |
| Madrid | ESP | 3 400 000 | 1 650 000 | 485 | INE Padron 2024 | ~55% Communauté de Madrid 3M stock |
| Athens | GRC | 643 000 | 385 000 | 599 | ELSTAT Census 2021 | Grèce 680/1000 national, Athènes ~600 |
| Barcelona | ESP | 1 660 000 | 810 000 | 488 | INE Padron 2024 | INE/Idescat ~490/1000 (dense) |
| Budapest | HUN | 1 750 000 | 880 000 | 503 | KSH 2023 | Hongrie 479/1000, Budapest ~500 |
| Florence | ITA | 372 000 | 208 000 | 559 | ISTAT 2023 | Italie 587/1000, Florence ~560 |
| Brussels | BEL | 1 220 000 | 570 000 | 467 | Statbel 2023 (Région-Capitale) | ~11% du stock belge 4,9M |
| Milan | ITA | 1 396 000 | 790 000 | 566 | ISTAT 2023 | Italie 587/1000, Milan ~565 |
| Naples | ITA | 918 000 | 440 000 | 479 | ISTAT 2023 | ~480/1000 (sud Italie, grands ménages) |
| Malaga | ESP | 587 000 | 330 000 | 562 | INE Padron 2024 | ~560/1000 (ville touristique) |
| Valencia | ESP | 800 000 | 430 000 | 538 | INE Padron 2024 | ~540/1000 (moyenne espagnole) |
| Sevilla | ESP | 685 000 | 370 000 | 540 | INE Padron 2024 | ~540/1000 (moyenne espagnole) |
| Venice | ITA | 258 000 | 168 000 | 651 | ISTAT 2023 | ~650/1000 (résidences secondaires extrêmes) |
| Thessaloniki | GRC | 319 000 | 190 000 | 596 | ELSTAT Census 2021 | ~600/1000 (forte vacance) |
| Bologna | ITA | 397 000 | 225 000 | 567 | ISTAT 2023 | ~567/1000 |
| Bergamo | ITA | 122 000 | 68 000 | 557 | ISTAT 2023 | ~557/1000 |

## Ratios nationaux de référence (logements / 1000 habitants)

| Pays | Ratio national | Source | Commentaire |
|------|---------------|--------|-------------|
| France | 590 | INSEE | Inclut résidences secondaires et vacants |
| Italie | 587 | ISTAT | Fort taux de vacance et résidences secondaires |
| Espagne | 540 | INE | Variable selon côte (>600) vs intérieur (<500) |
| Grèce | 680 | ELSTAT | Le plus élevé d'Europe — vacance massive |
| Turquie | 350 (ville) | TUIK | Grands ménages, ratio bas |
| Hongrie | 479 | KSH | Sous la moyenne OCDE |
| Portugal | 590 | INE | Similaire à la France |
| Belgique | 490 | Statbel | Bruxelles = Région 19 communes |
| Royaume-Uni | 440 | ONS | Plus bas d'Europe occidentale (petits logements) |
| Suède | 520 | SCB | |
| Norvège | 500 | SSB | |
| Danemark | 520 | DST | |
| Suisse | 540 | OFS | |
| Tchéquie | 490 | CZSO | Prague = logements occupés seulement |
| Moyenne OCDE | 487 | OCDE | Affordable Housing Database |

## Limites et précautions

### Biais connus

| Limite | Impact | Villes concernées |
|--------|--------|-------------------|
| **Commune ≠ périmètre Inside Airbnb** | Inside Airbnb peut couvrir un peu plus/moins que la commune administrative | Toutes, surtout Manchester ("Greater Manchester" dans IA) |
| **Population commune propre vs aire métro** | Surestime la pression pour les grandes villes où les touristes viennent de toute l'agglo | Paris (2,1M commune vs 11M agglo), Lyon, Bordeaux |
| **Logements estimés ≠ confirmés** | Marge d'erreur ±10-15% sur les 17 villes estimées | Italie (7), Espagne (4), Grèce (2), Turquie, Hongrie, Belgique |
| **Logements totaux vs occupés** | Les logements vacants et résidences secondaires gonflent le dénominateur | Grèce (28% vacance), Italie (25-30%), Espagne côtière |
| **Date des données** | 2021-2024 selon les villes, pas toutes synchrones | Prague (Census 2021), Lisbon/Porto (Census 2021) |
| **Istanbul** | Périmètre flou — province vs ville, données TUIK parcellaires | 15,8M = province, ville propre difficile à isoler |
| **Manchester** | Inside Airbnb = "Greater Manchester" (2,8M hab), nos données = commune (552K) | Ratio sera surestimé si on utilise commune |

### Recommandations

1. **Indicateur principal** : `entire homes / logements occupés × 1000` (pression résidentielle)
2. **Indicateur secondaire** : `tous listings / population × 1000` (intensité touristique)
3. **Documenter** que les 17 villes estimées ont une marge ±10-15%
4. **Manchester** : utiliser population Greater Manchester (2,8M) plutôt que commune (552K) pour matcher le périmètre Inside Airbnb

## Validation croisée Eurostat Urban Audit

Comparaison effectuée le 2026-02-09 via API REST (`urb_cpop1` + `urb_clivcon`).

- **Population** : Eurostat confirme nos chiffres pour les 12 villes "city proper" (écart <3%)
- **Logements** : Eurostat Urban Audit **inutilisable** — données 2011, incohérences flagrantes (Berlin 302K au lieu de 2M)
- **Détails** : voir `comparaison-eurostat-vs-estimations-260209.md`
