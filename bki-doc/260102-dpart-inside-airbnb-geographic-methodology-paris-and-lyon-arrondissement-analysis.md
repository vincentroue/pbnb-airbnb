---
ukp: |

aliases: []
dcr: 26-02-03_110847960
codx:
tags: []
pry: x
stf: x
sts: x
---

cnt::
url:: https://claude.ai/chat/f3ba1c11-b2c1-49ee-91da-c4af1886f26c

# Inside Airbnb Geographic Methodology: Paris and Lyon Arrondissement Analysis

# Inside Airbnb utilise les arrondissements, pas les quartiers administratifs

**Pour Paris et Lyon, Inside Airbnb définit les neighbourhoods comme les arrondissements municipaux** — 20 pour Paris, 9 pour Lyon — et non les quartiers administratifs plus fins ni les zones IRIS de l'INSEE. Cette approche, bien que cohérente pour la France, crée des incohérences significatives avec d'autres villes européennes où Inside Airbnb utilise des découpages géographiques de granularité très différente. Les fichiers geojson proviennent de "fichiers SIG municipaux ou open source", probablement les portails open data des villes françaises.

## Paris : les 20 arrondissements avec leurs noms traditionnels

Inside Airbnb découpe Paris en **exactement 20 neighbourhoods** correspondant aux 20 arrondissements municipaux, désignés par leurs noms historiques plutôt que par numérotation. Le 1er arrondissement apparaît comme "Louvre", le 18ème comme "Butte-Montmartre", le 20ème comme "Ménilmontant". Cette correspondance est parfaite : chaque arrondissement = un neighbourhood.

| Arrondissement | Nom Inside Airbnb | Arrondissement | Nom Inside Airbnb |
|----------------|-------------------|----------------|-------------------|
| 1er | Louvre | 11ème | Popincourt |
| 2ème | Bourse | 12ème | Reuilly |
| 3ème | Temple | 13ème | Gobelins |
| 4ème | Hôtel de Ville | 14ème | Observatoire |
| 5ème | Panthéon | 15ème | Vaugirard |
| 6ème | Luxembourg | 16ème | Passy |
| 7ème | Palais-Bourbon | 17ème | Batignolles-Monceau |
| 8ème | Élysée | 18ème | Butte-Montmartre |
| 9ème | Opéra | 19ème | Buttes-Chaumont |
| 10ème | Entrepôt | 20ème | Ménilmontant |

Les données ne correspondent **pas** aux 80 quartiers administratifs de Paris (4 par arrondissement), ni aux zones IRIS de l'INSEE qui se comptent en milliers. La source probable du fichier `neighbourhoods.geojson` est le portail **opendata.paris.fr**, qui fournit les limites des arrondissements en format GeoJSON sous licence ODbL.

## Lyon suit le même modèle avec ses 9 arrondissements

Pour Lyon, Inside Airbnb utilise très probablement les **9 arrondissements municipaux** (Lyon 1er à Lyon 9ème). Cette conclusion repose sur plusieurs indices convergents : les articles de presse utilisant les données Inside Airbnb rapportent systématiquement les statistiques par arrondissement (Lyon Capitale cite "1910 annonces dans le 1er, 1848 dans le 3ème, 1835 dans le 7ème"), et Lyon, avec Paris et Marseille, est l'une des trois seules villes françaises disposant d'arrondissements municipaux.

Les données ne correspondent pas aux quartiers plus fins (Terreaux, Bellecour, Guillotière...) ni aux **512 zones IRIS** de l'agglomération lyonnaise. Le fichier geojson provient probablement de **data.grandlyon.com**, le portail open data de la Métropole de Lyon, qui fournit les limites administratives en format SIG.

## La méthodologie Inside Airbnb : coordonnées géographiques contre limites officielles

Inside Airbnb documente explicitement sa méthodologie sur sa page Data Assumptions :

> *"Neighbourhood names for each listing are compiled by comparing the listing's geographic coordinates with a city's definition of neighbourhoods. Airbnb neighbourhood names are not used because of their inaccuracies."*

Cette approche présente trois caractéristiques importantes. Premièrement, Inside Airbnb **rejette explicitement les noms de quartiers fournis par Airbnb** qu'il juge imprécis. Deuxièmement, chaque annonce est assignée à un neighbourhood par correspondance entre ses coordonnées GPS et les polygones des limites officielles. Troisièmement, les fichiers geojson sont décrits comme "Sourced from city or open source GIS files" — une formulation volontairement vague permettant une flexibilité par ville.

Cette méthodologie ne mentionne pas explicitement **OpenStreetMap**. Les sources sont plutôt les portails open data municipaux (opendata.paris.fr, data.grandlyon.com, data.gouv.fr) et les données gouvernementales de l'IGN. Une limitation importante : Airbnb anonymise les coordonnées des annonces avec un décalage pouvant atteindre **150 mètres**, créant des erreurs d'assignation aux frontières des zones.

## Incohérence majeure entre villes européennes

L'analyse comparative révèle des **différences significatives** dans la granularité des neighbourhoods entre villes européennes, rendant les comparaisons inter-villes problématiques :

| Ville | Unité géographique | Nombre | Taille moyenne |
|-------|-------------------|--------|----------------|
| Paris | Arrondissements | 20 | ~5.3 km² |
| Lyon | Arrondissements | 9 | ~5.3 km² |
| Barcelone | Barris (quartiers) | 73 | ~1.4 km² |
| Berlin | LOR (aires de planification) | ~450 | Variable |
| Londres | Boroughs | 33 | ~48 km² |
| Amsterdam | Stadsdelen | 8 | ~26 km² |

Barcelone utilise un découpage **3.5 fois plus fin** que Paris, tandis que Berlin emploie les LOR (Lebensweltlich orientierte Räume), des zones de planification urbaine qui ne correspondent pas aux Bezirke officiels. Une étude publiée chez Taylor & Francis (2023) conclut que ces variations rendent les statistiques spatiales "suitable to compare spatial relationships within cities, while their explanatory power for differences across cities is limited."

## Implications pour les chercheurs et analystes

Plusieurs limitations doivent être considérées lors de l'utilisation des données Inside Airbnb. Le choix des arrondissements pour Paris masque des **variations importantes intra-arrondissement** — le 18ème arrondissement combine Montmartre touristique et Goutte d'Or résidentiel dans une seule entité. Les chercheurs Gurran et Phibbs (Université de Sydney) notent que "this data source has some critical limitations... Nevertheless, the data provide a useful basis for examining and monitoring Airbnb practices."

Pour une analyse plus granulaire, certains chercheurs rematchent les coordonnées GPS aux zones IRIS ou aux quartiers administratifs en utilisant les fichiers SIG officiels. Le projet Dataiku (2017) a ainsi cartographié les données parisiennes par stations de métro plutôt que par arrondissements pour obtenir une résolution plus fine.

## Conclusion : un compromis entre cohérence nationale et granularité

Inside Airbnb adopte une approche **cohérente pour la France** en utilisant systématiquement les arrondissements municipaux pour Paris et Lyon, le découpage administratif officiel le plus pertinent pour ces deux métropoles. Le choix de ne pas utiliser les 80 quartiers parisiens ou les zones IRIS représente un compromis entre lisibilité des données et finesse d'analyse.

Cette cohérence française contraste avec l'hétérogénéité européenne où chaque ville utilise un niveau administratif différent selon les données SIG disponibles localement. Pour les analyses comparatives internationales, il est recommandé de normaliser les données par densité d'annonces plutôt que par comptage brut, ou de recalculer les affiliations géographiques à partir des coordonnées en utilisant un référentiel commun comme les NUTS-3 européens.
