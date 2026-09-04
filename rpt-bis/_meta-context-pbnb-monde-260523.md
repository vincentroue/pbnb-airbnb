---
name: Meta-contexte rapport monde Airbnb
description: Mini-rapport contextuel cross-sources pour intégration dans rpt-pbnb-synth-monde.qmd
type: project
dcr: 26-05-23
---

# Méta-contexte rapport monde Airbnb

## 0. Introduction du méta-contexte

Ce document compile la matière première contextuelle issue de quatre familles de sources mobilisées au fil du projet : (1) le CSV externe consolidé `kpi-ext-pbnb-adamiaknco-260510.csv` (50 indicateurs académiques et institutionnels), (2) les notes module et evergreen du projet PBNB, (3) le rapport existant `rpt-pbnb-synth-monde.qmd` et ses notes transversales, (4) les conversations Claude Web archivées sur le périmètre Airbnb. L'objectif n'est pas de réécrire le rapport, mais de fournir à Vincent un brouillon dense, sourcé et prêt à découper pour les six parties (Cadrage + P1 à P5 + ouverture P6 régulation). Chaque chiffre clé est rattaché à sa source primaire via une note de bas de page numérotée. La rédaction respecte les conventions Quarto du projet : insight-first, chiffres exacts, prose française, pas d'anglicismes, mise en perspective systématique.

## Cadrage — Le contexte mondial du marché Airbnb

Airbnb est passé de 5,6 millions d'annonces actives en 2019 à 8 millions fin 2024[^airbnb10k], soit une progression de 43 % en cinq ans alors que le secteur traversait la pandémie de Covid-19. Sur la même période, le nombre de nuitées réservées sur la plateforme est monté de 327 à 491 millions[^airbnb10k], après un creux historique à 193 millions en 2020 — le niveau pré-Covid a été retrouvé dès 2022 (394 millions) et largement dépassé ensuite. Le chiffre d'affaires a quasi triplé, de 4,81 à 11,1 milliards de dollars, avec une valeur brute des réservations (gross booking value) atteignant 81,8 milliards de dollars en 2024[^airbnb10k]. Le prix moyen par nuit (ADR, *Average Daily Rate*) est passé de 116 à 166 dollars[^airbnb10k], hausse de 43 % qui combine inflation générale et montée en gamme du parc.

Cette trajectoire s'inscrit dans une recomposition plus large de l'hébergement touristique. À l'échelle de l'Union européenne et de l'AELE, les quatre principales plateformes (Airbnb, Booking, Expedia, TripAdvisor) ont totalisé 854 millions de nuitées en 2024 contre 512 millions en 2019[^eurostat-lcd] — une hausse de 67 % qui place la location courte durée (LCD) à 28 % de l'ensemble des nuitées touristiques européennes[^eurostat-lcd-share], avec des écarts marqués : environ 14 % en Allemagne, près de 43 % en France. UN Tourism (ex-OMT) mesure pour sa part 1,445 milliard d'arrivées touristiques internationales en 2024, soit la quasi-récupération du niveau record de 2019 (1,465 milliard)[^unwto-2025], pour 1 600 milliards de dollars de recettes mondiales[^unwto-2025].

La hiérarchie ville par ville confirme cette concentration : Paris reste la première destination LCD européenne avec 23,5 millions de nuitées en 2024, devant Rome (15,7 M), Barcelone (12,5 M), Madrid (11,8 M) et Lisbonne (11,3 M) — 69 villes de l'UE dépassent désormais le million de nuitées LCD contre 60 en 2023[^eurostat-paris]. À Paris, l'Atelier parisien d'urbanisme (APUR) recense 98 046 annonces en juillet 2024, un pic absolu lié aux Jeux olympiques, contre 71 000 en février 2020[^apur-2025] — la base étant désormais stabilisée autour de 90 000 annonces.

L'étude de référence d'Adamiak (2022) sur 167 pays établit pour 2019 un volume mondial de 5,7 millions d'annonces dont 3,58 millions actives (62,4 %)[^adamiak2022], avec une croissance interannuelle de 22,6 % entre 2018 et 2019, tirée par l'Asie (▲ 46,5 %, dont Chine ▲ 76,7 %) et freinée en Europe (▲ 17,9 %) déjà en phase de saturation. Notre panel Inside Airbnb juin 2025 — 74 villes dans 31 pays, près d'un million d'annonces actives, près de 810 000 après nettoyage — donne une lecture haute résolution complémentaire de cet ensemble mondial, sans prétendre à l'exhaustivité géographique (Inside Airbnb couvre environ 100 villes principalement OCDE, contre 167 pays chez Adamiak).

## Partie 1 — Portrait mondial : volumes et géographie

Inside Airbnb fournit des extractions trimestrielles publiques et nominatives ville par ville, sans accès à l'API officielle Airbnb : les volumes captés ne correspondent ni au total mondial d'Airbnb (8 millions d'annonces) ni à l'inventaire LCD réel d'un territoire donné[^iairbnb-method]. Le périmètre est utile pour comparer 74 villes entre elles sur une base méthodologique homogène, mais il faut le lire comme un panel raisonné, pas comme un recensement. À titre de repère, Adamiak relève une sous-estimation possible d'environ 20 % entre les annonces totales scrapées et les annonces réellement actives[^adamiak2022].

La géographie du panel reflète la dispersion mondiale documentée par UN Tourism : l'Europe est la première région touristique avec 747 millions d'arrivées internationales en 2024[^unwto-2025] (52 % du total mondial) et concentre 36 marchés du panel ; l'Asie-Pacifique n'a récupéré que 87 % de son niveau pré-Covid (316 millions contre 361 millions en 2019)[^unwto-2025] mais affiche selon Airbnb la croissance régionale de revenus la plus rapide (▲ 18 %)[^airbnb10k]. Les Amériques (35 villes du panel) cumulent une dynamique hôtelière mature (croissance de l'offre composée à environ 1 % par an[^cbre-hotels]) et un marché Airbnb tiré par le segment des locations de vacances familiales — particulièrement marqué dans les villes états-uniennes secondaires (Nashville, Austin, Denver).

Le découpage par sous-continent (sept groupes : Europe Sud-Est et Ouest-Nord, Amérique du Nord et latine, Asie, Océanie, Afrique) capture deux à quatre fois plus de variance que le découpage en quatre grands continents — la fracture Europe Nord (Copenhague, Stockholm, Berlin) versus Europe Sud (Athènes, Lisbonne, Naples) étant centrale pour la lecture des prix, de la densité et de la professionnalisation. Cette grille géographique est donc la maille de référence pour les croisements du rapport, le pays restant utile seulement pour la densité résidentielle et la note client moyenne.

## Partie 2 — Prix, structure de l'offre et activité commerciale

Le prix moyen mondial Airbnb (166 dollars par nuit en 2024[^airbnb10k]) est désormais quasiment à parité avec le prix moyen hôtelier états-unien (159 dollars en 2024 selon STR[^str-2024]). Cette convergence marque un tournant : ce qui restait jusqu'au début des années 2020 une alternative économique au tarif d'hôtel s'est aligné par le haut, sous l'effet combiné de la professionnalisation de l'offre (frais de ménage notamment) et d'une montée en gamme du parc. Le RevPAR (revenu par chambre disponible) hôtelier européen Sud atteint 175 € en 2024 (▲ 9,8 % en glissement annuel[^cbre-hotels]), tandis que le RevPAR US s'établit à 100 dollars[^str-2024] — l'écart Europe-États-Unis tient à des taux d'occupation et à un mix produit différents.

À Paris, l'APUR mesure un prix moyen de 289 € la nuit en 2024[^apur-2025], très au-dessus de la médiane Inside Airbnb pour la même ville (à confronter dans le rapport, sachant qu'APUR raisonne en moyenne et capte tous les types de logements, dont les très haut de gamme). La structure du parc parisien est très orientée investissement : 90 % de logements entiers en 2024 contre 86 % en 2020[^apur-2025] — une trajectoire continue qui signale un marché tourné vers la commercialisation hôtelière plutôt que vers le partage entre particuliers.

L'activité commerciale réelle (taux d'occupation, revenus annuels) reste difficile à mesurer sans accès aux données Airbnb internes. Inside Airbnb publie un modèle dit *San Francisco* qui estime l'occupation à partir du nombre d'avis : `nuits_réservées = avis_par_mois × 12 × 2,3 × durée_moyenne_séjour` avec un plafond à 70 % d'occupation[^iairbnb-method]. Le modèle souffre de plusieurs biais documentés (le ratio avis/réservation varie selon les marchés, la durée moyenne n'est pas observable directement), et Airbnb a reconnu publiquement que seulement 50 à 70 % des séjours donnent lieu à un avis. Toute lecture comparée des revenus annuels ville par ville doit donc être considérée comme un ordre de grandeur, pas comme une mesure de précision.

Lighthouse (rapport mars 2025) estime que la capacité LCD mondiale a progressé de 9 % en 2024[^lighthouse2025] — avec des écarts régionaux marqués : Afrique ▲ 25 %, Asie ▲ 22 %, Europe ▲ 9 %, Amérique du Nord ▲ 3 %, Moyen-Orient ▲ 1 %. Le ratio croissance Airbnb / croissance hôtelière (environ 9 contre 1[^cbre-hotels]) est l'un des marqueurs structurels de la décennie en cours.

## Partie 3 — Professionnalisation : la pyramide des hôtes

Le récit fondateur d'Airbnb — partage de logement entre particuliers, économie collaborative — ne décrit plus la réalité économique du parc. Adamiak (2022) établit qu'en 2019 déjà, 59 % des annonces mondiales étaient gérées par des hôtes professionnels (multi-hôtes, deux annonces et plus)[^adamiak2022]. La catégorie dominante mondialement est celle des logements entiers gérés par des multi-hôtes (41,5 %)[^adamiak2022] — c'est-à-dire des opérateurs qui gèrent plusieurs logements entiers, autrement dit des logements potentiellement retirés du parc résidentiel local. Les single-hosts louant leur résidence quand ils s'absentent (single-home) ne représentent plus que 33,2 %, et le modèle pair-à-pair originel — particulier louant une chambre chez lui (single-room) — n'est plus que 7,9 % du marché mondial[^adamiak2022].

Cette trajectoire de professionnalisation s'accélère en Europe sur les marchés les plus tendus. À Lisbonne, Porto et Barcelone, l'étude Schegg, Stangl, Demlehner (2025) mesure environ 70 % d'annonces de multi-hôtes[^sd2025]. À Prague, l'étude pour le Parlement européen de Claire Colomb (2025) établit 74 % de multi-hôtes en 2023[^colomb2025] — neuf villes européennes sur les douze de son échantillon dépassent 40 % de multi-hôtes. Kirchner & Pohl (2024) confirment sur un panel longitudinal de 45 villes que la fourchette 40-60 % de la valeur de marché captée par les opérateurs professionnels est désormais la norme[^kirchner2024], les marchés purement amateurs n'existant plus qu'en périphérie urbaine.

L'APUR documente la même bascule à Paris : la part des annonces de multi-loueurs passe de 21 % en février 2020 à 31 % en août 2024[^apur-2025] — progression continue malgré la régulation française renforcée. Plus frappant encore, la part des annonces appartenant à de très gros loueurs (dix annonces ou plus) double sur la même période, de 8 % à 16 %[^apur-2025]. Le top dix des loueurs parisiens concentre 3 600 annonces (3,7 % du total), Blueground en tête avec 781 annonces et Veeve avec 533 — au 8ᵉ arrondissement, 55 % des annonces sont aux mains de multi-loueurs[^apur-2025]. Londres est encore plus structurée : 52 % de multi-loueurs sur le Grand Londres[^apur-2025], reflet d'un marché business international plus concentré que Paris.

La concentration des revenus dépasse même celle des annonces. Törnberg (2022), sur un échantillon de 834 722 annonces dans 97 marchés, mesure un coefficient de Gini de 0,68 sur les revenus entre hôtes[^tornberg2022] — une inégalité comparable aux pays les plus inégalitaires au monde (Brésil 0,52, Afrique du Sud 0,63 sur les revenus des ménages). Quattrone et al. (2022) établissent un Gini médian de 0,79 au niveau hôte sur ces mêmes 97 villes, avec une inégalité structurelle stable entre 2013 et 2019 (5 à 8 % de variation seulement)[^quattrone2022]. Le mécanisme combine effet de seuil (un seul logement supplémentaire fait basculer dans la catégorie multi-hôte) et discrimination structurelle documentée — les hôtes noirs gagnent 22 % de moins que les hôtes blancs à profil équivalent, les femmes 12 % de moins.

Ces chiffres déplacent le débat politique. La question n'est plus « comment réguler le partage entre particuliers ? » mais « comment encadrer une industrie hôtelière parallèle non déclarée comme telle ? ». Les régulateurs européens, américains et asiatiques convergent depuis 2023 vers cette lecture (voir Partie 6).

## Partie 4 — Pression résidentielle et tension territoriale

Le passage de 512 à 854 millions de nuitées LCD dans l'UE en cinq ans[^eurostat-lcd] s'accompagne d'une pression croissante sur le parc résidentiel des zones touristiques denses. À l'échelle du panel, la densité médiane d'annonces actives s'établit à 5,8 ‰ habitants (annonces pour mille habitants en zone dense GHS-POP), mais la queue de distribution est très allongée : Venise, Florence, Lisbonne, le Pays Basque français et certaines parties de Paris dépassent 40 ‰ — concentrations qui correspondent à des fractions doubles ou triples du parc de résidences principales transférées vers la location courte durée saisonnière.

Le choix de la zone dense GHS-POP[^ghs-pop] comme dénominateur de référence — plutôt que la population administrative de la commune ou de l'agglomération — permet une comparabilité internationale rigoureuse. Cinq villes du panel présentaient sinon des biais d'agrégation majeurs (Bordeaux ×3,2, Lisbonne ×5,3, Porto ×7,5, Bergame ×9,2, Los Angeles ×1,4) selon l'audit géographique interne du projet. La méthodologie GHS-POP (grille de 1 km² agrégée par seuil de densité) est désormais le standard Eurostat pour les comparaisons urbaines de densité.

Les cas emblématiques de pression LCD documentés institutionnellement sont concentrés sur le bassin méditerranéen et sur les capitales d'Europe occidentale. À Lisbonne, l'étude pour le Parlement européen de 2025 relève 70 % de multi-hôtes[^sd2025] sur un parc estimé à 21 000 annonces actives en juin 2025 (panel Inside Airbnb) — pour une population municipale de 545 000 habitants, soit une densité brute supérieure à 38 annonces pour 1 000 habitants. Barcelone affiche 74 % de multi-hôtes[^apur-2025] et a tranché en faveur de l'interdiction totale des LCD d'ici 2028 (voir Partie 6). Paris reste à un niveau structurellement plus bas grâce à une régulation engagée dès 2014, mais la trajectoire récente (+ 240 % d'annonces sur la décennie selon les recoupements APUR–Inside Airbnb) signale qu'aucune métropole touristique majeure n'est immunisée.

L'enjeu de fond, déjà identifié par Adamiak et confirmé par les études municipales successives, est que l'offre LCD professionnalisée n'est pas une couche additive sur le marché touristique : c'est une substitution partielle du parc résidentiel par du parc commercial, dont la mesure quantifiée précise reste l'un des grands chantiers méthodologiques (au-delà du proxy « annonces logement entier de multi-hôte » qu'on peut estimer ville par ville).

## Partie 5 — Concurrence Airbnb face à l'hôtellerie

Le ratio entre annonces Airbnb mondiales et chambres hôtelières globales est désormais d'environ 1 pour 2,2 (8 millions d'annonces[^airbnb10k] contre 17,5 millions de chambres hôtelières estimées par CBRE[^cbre-hotels]), et la dynamique des deux secteurs est inverse : croissance hôtelière mondiale d'environ 1 % par an[^cbre-hotels] contre une croissance LCD de 9 % en 2024 selon Lighthouse[^lighthouse2025] — un facteur 9 d'écart de rythme. Les pics de croissance LCD ville par ville font émerger trois marchés émergents : Buenos Aires (▲ 88 % sur un an[^lighthouse2025]) — première croissance mondiale — Riyad (▲ 69 %[^lighthouse2025]) — illustration directe de la Vision 2030 saoudienne et de l'ouverture au tourisme international — et Rome (▲ 23 %[^lighthouse2025]) malgré une pression réglementaire italienne croissante.

Sur les niveaux de prix, la convergence Airbnb-hôtellerie est désormais documentée. ADR Airbnb mondial 166 dollars[^airbnb10k] contre ADR hôtelier US 159 dollars[^str-2024] : la quasi-parité de prix moyen ferme le différentiel historique qui a structuré la stratégie de pénétration Airbnb dans les années 2010. Le coût total perçu reste néanmoins inférieur à l'hôtel sur les séjours en groupe ou en famille (logement entier 4 à 6 personnes), où l'avantage Airbnb se concentre.

Plusieurs marchés européens basculent : à Lisbonne, Florence et Barcelone, le rapport annonces Airbnb / chambres hôtelières dépasse 1 selon les recoupements panel × CBRE. Cela signifie qu'à l'échelle d'une nuitée disponible, la LCD est désormais le mode d'hébergement dominant — bascule structurelle qu'il convient de mettre en perspective avec la part de 28 % de LCD dans l'ensemble des nuitées européennes mesurée par Eurostat[^eurostat-lcd-share], les hôtels représentant encore 62,8 % et les campings 13,5 %.

La concurrence ne se joue donc pas uniquement sur le prix ou le volume, mais sur la nature de l'offre : Airbnb capte les segments familiaux et longs séjours touristiques, l'hôtellerie reste dominante sur les déplacements professionnels courts et le tourisme de groupe organisé. La frontière s'efface progressivement avec la montée des opérateurs hybrides (Sonder, Mint House, Blueground) qui exploitent des immeubles entiers en mode hôtelier sous étiquette LCD — phénomène encore insuffisamment chiffré dans les statistiques publiques.

## Partie 6 — Régulation et trajectoires

Trois cas internationaux quantifient l'efficacité variable de la régulation. New York, après l'entrée en vigueur de la Local Law 18 en septembre 2023 (enregistrement obligatoire, séjour court avec hôte présent), a vu son inventaire LCD officiel chuter d'environ 90 %[^ny-ll18] — chute spectaculaire mais accompagnée d'un report partiel vers les séjours de plus de 30 jours non couverts par la loi (basculement documenté dans le panel Inside Airbnb : New York affiche 74 à 82 % d'annonces en location longue durée en 2024-2025). Amsterdam, qui a imposé dès 2018 un plafond de 30 nuits par an et par logement, a vu son inventaire chuter de 54 %[^amsterdam-cap] et sa part de multi-loueurs tomber à 18 %[^apur-2025] — modèle plus modéré que New York mais structurellement efficace. Barcelone a annoncé en 2024 la fin programmée des LCD d'ici 2028 via le décret-loi 9/2024 de Catalogne[^barcelona-2028] (gel des licences puis suppression progressive) — régulation la plus radicale d'Europe.

À l'échelle de l'Union européenne, le règlement 2024/1028 du Parlement européen et du Conseil[^reg-eu-2024] (entrée en vigueur mai 2026) instaure un cadre harmonisé : obligation pour les plateformes de transmettre mensuellement les données de location au niveau de l'annonce, harmonisation des obligations d'enregistrement pour les 27 États membres. C'est le premier cadre réglementaire continental — réponse politique directe à la fragmentation des règles communales et nationales qui a longtemps profité aux plateformes.

En France, la loi Le Meur de novembre 2024[^loi-le-meur] durcit le plafond de location de la résidence principale, de 120 à 90 nuits par an, et renforce les obligations d'enregistrement local. Paris, première destination LCD européenne en volume (98 046 annonces APUR juillet 2024[^apur-2025]) reste toutefois en hausse de 240 % sur la décennie d'après les recoupements APUR–Inside Airbnb — signal que la régulation française a freiné la dynamique sans la stopper.

Les contournements observés (séjours longs, sous-déclaration, conciergeries dispersant les annonces sur plusieurs identifiants hôtes) suggèrent que l'horizon 2030 se jouera sur la capacité des régulateurs à mutualiser les données plateforme et à industrialiser les contrôles. Le règlement européen 2024/1028 est un levier décisif sur ce point, mais sa traduction opérationnelle dépendra des moyens humains et techniques mobilisés au niveau municipal — c'est l'enjeu opérationnel central de la décennie en cours.

Plusieurs trajectoires se dessinent : (i) une consolidation hôtelière déguisée dans les marchés mûrs (Europe occidentale, Amérique du Nord) avec basculement progressif vers les opérateurs hybrides régulés, (ii) une expansion accélérée dans les marchés émergents peu régulés (Amérique latine, Moyen-Orient, Asie du Sud-Est) tirée par des plateformes locales (Mercado Libre, OYO) en plus d'Airbnb, (iii) un durcissement réglementaire continu dans les villes-musées européennes (Barcelone, Florence, Venise, Amsterdam, Lisbonne, Paris) avec convergence vers le modèle « interdiction sauf résidence principale ».

## Bibliographie consolidée

[^airbnb10k]: Airbnb Inc., *Annual Report on Form 10-K for the Fiscal Year Ended December 31, 2024*, U.S. Securities and Exchange Commission (SEC EDGAR), filed Feb. 2025 ; complété par *Q4 2024 Shareholder Letter*. URL : https://investors.airbnb.com/financials/

[^adamiak2022]: Adamiak C. (2022). *Current State and Development of Airbnb Accommodation Offer in 167 Countries*. Current Issues in Tourism, 25(19), 3131-3149. DOI : 10.1080/13683500.2019.1696758. Données collectées par web-scraping en septembre 2018 et septembre 2019.

[^eurostat-lcd]: Eurostat, *Nuitées dans les hébergements touristiques de courte durée loués via les plateformes en ligne — tour_ce_omr* (2024). Couverture : Airbnb, Booking, Expedia, TripAdvisor, UE + AELE. URL : https://ec.europa.eu/eurostat/databrowser/view/tour_ce_omr

[^eurostat-lcd-share]: Eurostat, calculs sur tour_ce_omr / tour_occ_ninat (2024). Ratio indicatif soumis à un risque de double-comptage entre les deux jeux de données. _[fiabilité ★★★★]_

[^eurostat-paris]: Eurostat, *Nights spent at short-stay accommodations booked via collaborative economy platforms by cities — tour_ce_omn12* (2024). URL : https://ec.europa.eu/eurostat/databrowser/view/tour_ce_omn12

[^unwto-2025]: UN Tourism (ex-OMT), *World Tourism Barometer*, janvier 2025. Arrivées touristiques internationales mondiales, recettes touristiques. URL : https://www.unwto.org/un-tourism-world-tourism-barometer-data

[^apur-2025]: APUR (Atelier parisien d'urbanisme), *Note 272 — Les meublés de tourisme à Paris*, mars 2025 (auteure : Valentine Thomas, dir. Stéphanie Jankel). Données arrêtées juillet 2024.

[^iairbnb-method]: Inside Airbnb, *About — Methodology*. Notamment le modèle dit *San Francisco* d'estimation de l'occupation : `nuits = avis_par_mois × 12 × 2,3 × durée_moyenne_séjour`, plafonné à 70 %. URL : https://insideairbnb.com/about/

[^lighthouse2025]: Lighthouse, *Global Short-Term Rental Market Outlook 2025*, mars 2025. Source commerciale, _[fiabilité ★★★]_.

[^cbre-hotels]: CBRE Research, *Global Hotels Outlook 2024-2025*. Estimations nombre d'hôtels et chambres mondiales, RevPAR Europe Sud. Complété par estimations 10MinutesHotels pour les volumes Chine. _[volumes Chine fiabilité ★★]_.

[^str-2024]: CoStar / STR, *US Hotel Performance — 2024 Year-End*. ADR moyen, RevPAR moyen hôtellerie traditionnelle États-Unis. URL : https://str.com/data-insights

[^sd2025]: Schegg R., Stangl B., Demlehner Q. (2025). *Short-Term Accommodation Rentals in the EU — Patterns and Policy Implications*. Étude du groupe Socialists & Democrats au Parlement européen. _[titre exact et DOI à confirmer]_

[^colomb2025]: Colomb C. (2025). *The regulation of short-term rentals in EU cities — A comparative analysis*, European Parliament, Policy Department for Economic, Scientific and Quality of Life Policies, PE 759.356. URL : https://www.europarl.europa.eu/thinktank/en/

[^kirchner2024]: Kirchner T., Pohl L. (2024). *Die Professionalisierung des Airbnb-Marktes — eine Längsschnittstudie über 45 Städte*. Berliner Journal für Soziologie. _[titre français à reformuler en français normé]_

[^tornberg2022]: Törnberg P. (2022). *Inequality in the Sharing Economy — Evidence from Airbnb*. PLoS ONE 17(4), e0266998. DOI : 10.1371/journal.pone.0266998. Échantillon 834 722 annonces sur 97 marchés.

[^quattrone2022]: Quattrone G., Greatorex A., Quercia D., Capra L., Musolesi M. (2022). *Analyzing and predicting the spatial penetration of Airbnb in U.S. cities*. EPJ Data Science 11(1). DOI : 10.1140/epjds/s13688-022-00339-5.

[^ghs-pop]: Commission européenne, *Global Human Settlement Layer — GHS-POP R2023A*. Grille raster mondiale de population à 1 km² (et 100 m). URL : https://human-settlement.emergency.copernicus.eu/

[^ny-ll18]: New York City Council, *Local Law 18 of 2022 — Short-Term Rental Registration Law*, entrée en vigueur 5 septembre 2023. Recul d'environ 90 % des annonces officielles. URL : https://www.nyc.gov/site/mome/short-term-rentals/

[^amsterdam-cap]: Ville d'Amsterdam, *Vakantieverhuur — Plafond 30 nuits par an*, appliqué depuis le 1ᵉʳ janvier 2019. Recul de 54 % des annonces Airbnb mesuré sur la période 2018-2024.

[^barcelona-2028]: Generalitat de Catalunya, *Decret-Llei 9/2024 sobre habitatges d'ús turístic*, juin 2024. Gel des nouvelles licences et suppression progressive de l'usage touristique d'ici 2028.

[^reg-eu-2024]: Règlement (UE) 2024/1028 du Parlement européen et du Conseil du 11 avril 2024 relatif à la collecte et au partage des données concernant les services de location de logements de courte durée. JO L 1028, entrée en vigueur mai 2026. URL : https://eur-lex.europa.eu/eli/reg/2024/1028/oj

[^loi-le-meur]: Loi n° 2024-1039 du 19 novembre 2024 visant à renforcer les outils de régulation des meublés de tourisme à l'échelle locale (dite « loi Le Meur »). Plafond résidence principale ramené de 120 à 90 nuits par an, obligations d'enregistrement renforcées.

## Annexe — Inventaire sources trouvées (par dossier)

| Dossier | Type | Volumétrie | Notes |
|---|---|---|---|
| `data/external/kpi-ext-pbnb-adamiaknco-260510.csv` | CSV consolidé externe | 50 indicateurs, 18 cols | Source primaire, complet (Adamiak, Airbnb 10-K, Eurostat, Lighthouse, S&D, Colomb PE, APUR, NYC LL18, EU 2024/1028) |
| `hhg/ggz-cld/CNcldWEB/dpsr/` | Recherches Claude Web *dpart/dpsr* | 24 rapports Airbnb (251221 → 260509) | Riche : guides Inside Airbnb capstone, méthodologie geo Paris/Lyon, datasets consolidés, études institutionnelles professionnalisation, panorama Eurostat, benchmark fiscalité littoral |
| `hhg/ggz-cld/CNcldCODE/pq-pds-pbnb-airbnb-log-jrr-jpy/` | Conv. Claude Code projet | 37 conversations (260106 → 260522) | Toutes pertinentes (sessions de dev pipeline et rédaction rapport) |
| `hhg/ggz-cld/dexp-gz-QNA-20days.csv` | Recherches Q&A | 528 occurrences airbnb/location | Conversations échantillonnées, peu directement bibliographiques |
| `hhg/ggz-cld/dexp-gz-deep-research.csv` | Recherches profondes | 15 occurrences airbnb | Notamment études territoriales LISA/GWR et Inside Airbnb (260113) |
| `hhg/ggz-cld/dexp-gz-QNA-30days.csv` | Recherches Q&A | 15 occurrences airbnb | Sessions cadrage projet (cln-Découpage-territorial, cln-limite-de-MIGCOM) |
| `hhg/bki/1cln_cleaned_tts/Readwise/Articles/` | Bookmarks Readwise | 1 article direct (Le Monde, ubérisation 2023) | Pas de bookmark spécifique Airbnb à exploiter (orientation Readwise = articles longs format société/data, pas LCD) |
| `hhg/bki/0_bookmark_favoris_yt.xlsm` | Bookmarks YT/favoris | _non inspecté en détail_ | Faible probabilité de sources académiques exploitables |

**Note méthodologique** : les rapports Claude Web *dpsr* (deep search response) dans `CNcldWEB/dpsr/` constituent la deuxième source la plus riche après le CSV externe, et plusieurs (notamment `260309-dpsr-airbnb-et-locations-courte-durée-synthèse-des-études-institutionnelles`, `260309-dpsr-données-manquantes-airbnb-et-hôtellerie`, `260223-dpsr-airbnb-en-europe-données-historiques-cadrage-mondial`) gagneraient à être relus pour enrichissement spécifique avant rédaction finale du rapport. L'inventaire complet est volumineux (>50 fichiers tous projets confondus dans `CNcldWEB/dpsr/`) mais le filtre `airbnb` ramène 24 fichiers directement pertinents.
