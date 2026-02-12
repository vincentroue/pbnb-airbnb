#!/usr/bin/env python3
"""
Télécharge fichiers Inside Airbnb depuis une liste de liens directs.
Range automatiquement par pays/ville/date.

Usage:
    python sp04-download-insideairbnb-from-links-251231.py links.txt
    python sp04-download-insideairbnb-from-links-251231.py --clipboard

Le fichier links.txt contient des URLs comme :
    https://data.insideairbnb.com/france/auvergne-rhone-alpes/lyon/2025-09-18/data/listings.csv.gz
    https://data.insideairbnb.com/france/ile-de-france/paris/2025-09-12/data/listings.csv.gz

Structure sortie :
    data/raw/insideairbnb/
        france/
            paris/
                2025-09-12/
                    listings.csv.gz
                    calendar.csv.gz
            lyon/
                2025-09-18/
                    listings.csv.gz
"""

import argparse
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

# ======= CONFIG =======&s
BASE_OUTPUT_DIR = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy\data\raw\zudb-inside-airbnbbnb")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Pattern URL Inside Airbnb
# https://data.insideairbnb.com/{country}/{region}/{city}/{date}/data/{file}
URL_PATTERN = re.compile(
    r'https?://data\.insideairbnb\.com/([^/]+)/([^/]+)/([^/]+)/(\d{4}-\d{2}-\d{2})/(data|visualisations)/([^/\s]+)'
)

EUROPE_COUNTRIES = [
    'france', 'germany', 'italy', 'spain', 'portugal', 'united-kingdom',
    'belgium', 'the-netherlands', 'switzerland', 'austria', 'greece',
    'ireland', 'poland', 'czech-republic', 'hungary', 'sweden', 'norway',
    'denmark', 'finland', 'croatia', 'slovenia', 'slovakia', 'romania',
    'bulgaria', 'serbia', 'turkey', 'cyprus', 'malta', 'luxembourg', 'iceland'
]

USA_COUNTRIES = ['united-states']

def get_continent(country: str) -> str:
    """Retourne le continent pour un pays."""
    country_lower = country.lower()
    if country_lower in EUROPE_COUNTRIES:
        return 'europe'
    elif country_lower in USA_COUNTRIES:
        return 'usa'
    else:
        return 'world'
# ======= CONFIG =======&e


def parse_url(url: str) -> dict | None:
    """Parse URL Inside Airbnb et extrait composants."""
    url = url.strip()
    match = URL_PATTERN.match(url)
    if not match:
        return None

    country, region, city, date, folder, filename = match.groups()
    return {
        'url': url,
        'country': country,
        'region': region,
        'city': city,
        'date': date,
        'folder': folder,
        'filename': filename
    }


def extract_links_from_text(text: str, only_listings: bool = False, with_geojson: bool = False,
                           with_summary: bool = False, with_neighbourhoods: bool = False) -> list[str]:
    """Extrait tous les liens Inside Airbnb d'un texte."""
    # Cherche toutes les URLs data.insideairbnb.com
    pattern = r'https?://data\.insideairbnb\.com/[^\s\)>\]\"\']+\.(?:csv\.gz|csv|geojson)'
    links = re.findall(pattern, text)

    if only_listings:
        # Ne garder que les listings.csv.gz (données détaillées)
        filtered = [l for l in links if l.endswith('/data/listings.csv.gz')]

        # Ajouter fichiers optionnels (1 par ville, le plus récent)
        seen_geojson = set()
        seen_summary = set()
        seen_nbh = set()

        for link in links:
            parsed = parse_url(link)
            if not parsed:
                continue
            city_key = f"{parsed['country']}/{parsed['city']}"

            # GeoJSON (1 par ville)
            if with_geojson and link.endswith('neighbourhoods.geojson'):
                if city_key not in seen_geojson:
                    filtered.append(link)
                    seen_geojson.add(city_key)

            # Summary listings.csv - TOUS (1 par date par ville)
            if with_summary and link.endswith('/visualisations/listings.csv'):
                filtered.append(link)

            # Neighbourhoods.csv (1 par ville)
            if with_neighbourhoods and link.endswith('/visualisations/neighbourhoods.csv'):
                if city_key not in seen_nbh:
                    filtered.append(link)
                    seen_nbh.add(city_key)

        links = filtered

    return links


def normalize_path(path_str: str) -> str:
    """Normalise les caractères accentués dans les chemins."""
    import unicodedata
    # Décompose les caractères accentués, enlève les accents
    normalized = unicodedata.normalize('NFD', path_str)
    ascii_str = normalized.encode('ascii', 'ignore').decode('ascii')
    return ascii_str


def download_file(url: str, output_path: Path, retry: int = 3) -> bool:
    """Télécharge un fichier avec retry."""
    from urllib.parse import quote, urlparse, urlunparse

    # Normaliser le chemin pour éviter les problèmes d'encodage
    output_path = Path(normalize_path(str(output_path)))

    # Encoder l'URL pour les caractères non-ASCII
    parsed = urlparse(url)
    encoded_path = quote(parsed.path, safe='/')
    url_encoded = urlunparse(parsed._replace(path=encoded_path))

    for attempt in range(retry):
        try:
            req = urllib.request.Request(url_encoded, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as response:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.read())
            return True
        except HTTPError as e:
            print(f"  ❌ HTTP {e.code}: {url}")
            if e.code == 403:
                return False  # Pas de retry sur 403
        except URLError as e:
            print(f"  ⚠️ Erreur réseau (tentative {attempt+1}/{retry}): {e.reason}")
            time.sleep(2)
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return False
    return False


def process_links(links: list[str], output_dir: Path, dry_run: bool = False) -> dict:
    """Traite liste de liens et télécharge fichiers."""
    results = {'success': [], 'failed': [], 'skipped': []}

    parsed_links = []
    for link in links:
        parsed = parse_url(link)
        if parsed:
            parsed_links.append(parsed)
        else:
            print(f"⚠️ URL invalide ignorée: {link[:80]}...")

    print(f"\n📋 {len(parsed_links)} liens valides trouvés\n")

    # Grouper par ville pour affichage
    by_city = {}
    for p in parsed_links:
        key = f"{p['country']}/{p['city']}"
        if key not in by_city:
            by_city[key] = []
        by_city[key].append(p)

    print("Villes détectées:")
    for city, items in by_city.items():
        dates = sorted(set(p['date'] for p in items))
        print(f"  • {city}: {len(items)} fichiers, dates: {', '.join(dates)}")

    if dry_run:
        print("\n[DRY RUN] Pas de téléchargement")
        return results

    print(f"\n{'='*50}")
    print("TÉLÉCHARGEMENT")
    print(f"{'='*50}\n")

    for i, p in enumerate(parsed_links, 1):
        # Structure: continent/country/city/date/filename
        # Normaliser les chemins pour éviter les problèmes d'encodage
        continent = get_continent(p['country'])
        country_norm = normalize_path(p['country'])
        region_norm = normalize_path(p['region'])
        city_norm = normalize_path(p['city'])
        output_path = output_dir / continent / country_norm / city_norm / p['date'] / p['filename']

        if output_path.exists():
            print(f"[{i}/{len(parsed_links)}] ⏭️ Existe: {p['city']}/{p['date']}/{p['filename']}")
            results['skipped'].append(p)
            continue

        print(f"[{i}/{len(parsed_links)}] ⬇️ {p['city']}/{p['date']}/{p['filename']}...", end=' ', flush=True)

        if download_file(p['url'], output_path):
            size_mb = output_path.stat().st_size / (1024*1024)
            print(f"✅ ({size_mb:.1f} MB)")
            results['success'].append(p)
        else:
            print("❌")
            results['failed'].append(p)

        # Pause entre téléchargements
        time.sleep(0.5)

    return results


def print_summary(results: dict):
    """Affiche résumé téléchargements."""
    print(f"\n{'='*50}")
    print("RÉSUMÉ")
    print(f"{'='*50}")
    print(f"✅ Téléchargés: {len(results['success'])}")
    print(f"⏭️ Déjà existants: {len(results['skipped'])}")
    print(f"❌ Échecs: {len(results['failed'])}")

    if results['failed']:
        print("\nFichiers en échec:")
        for p in results['failed']:
            print(f"  - {p['url']}")


def main():
    parser = argparse.ArgumentParser(description='Télécharge fichiers Inside Airbnb depuis liens')
    parser.add_argument('input', nargs='?', help='Fichier texte avec liens (1 par ligne) ou "-" pour stdin')
    parser.add_argument('--dry-run', action='store_true', help='Affiche ce qui serait téléchargé sans télécharger')
    parser.add_argument('--only-listings', '-l', action='store_true', help='Ne télécharger que les listings.csv.gz (recommandé)')
    parser.add_argument('--with-geojson', '-g', action='store_true', help='Ajouter 1 geojson par ville')
    parser.add_argument('--with-summary', '-s', action='store_true', help='Ajouter 1 listings.csv light par ville (visualisations)')
    parser.add_argument('--with-neighbourhoods', '-n', action='store_true', help='Ajouter 1 neighbourhoods.csv par ville')
    parser.add_argument('--output', '-o', type=Path, default=BASE_OUTPUT_DIR, help='Dossier de sortie')
    parser.add_argument('--countries', '-c', nargs='+', help='Filtrer par pays (ex: france germany)')
    parser.add_argument('--europe', '-e', action='store_true', help='Seulement pays européens')

    args = parser.parse_args()

    # Filtre pays
    country_filter = None
    if args.europe:
        country_filter = EUROPE_COUNTRIES
        print(f"🌍 Filtre Europe: {len(country_filter)} pays")
    elif args.countries:
        country_filter = [c.lower() for c in args.countries]
        print(f"🌍 Filtre pays: {', '.join(country_filter)}")

    # Utiliser output personnalisé si spécifié
    output_dir = args.output

    # Lire les liens
    if args.input == '-' or not args.input:
        print("📋 Collez les liens (Ctrl+Z puis Enter pour terminer):")
        text = sys.stdin.read()
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ Fichier non trouvé: {args.input}")
            sys.exit(1)
        text = input_path.read_text(encoding='utf-8')

    # Extraire liens
    links = extract_links_from_text(
        text,
        only_listings=args.only_listings,
        with_geojson=args.with_geojson,
        with_summary=args.with_summary,
        with_neighbourhoods=args.with_neighbourhoods
    )

    if not links:
        print("❌ Aucun lien Inside Airbnb trouvé dans l'entrée")
        sys.exit(1)

    # Filtrer par pays si demandé
    if country_filter:
        original_count = len(links)
        filtered_links = []
        for link in links:
            parsed = parse_url(link)
            if parsed and parsed['country'].lower() in country_filter:
                filtered_links.append(link)
        links = filtered_links
        print(f"🔍 {len(links)}/{original_count} liens après filtre pays")

    filter_parts = []
    if args.only_listings:
        filter_parts.append("listings.csv.gz")
    if args.with_summary:
        filter_parts.append("+ sum-listings")
    if args.with_neighbourhoods:
        filter_parts.append("+ nbh")
    if args.with_geojson:
        filter_parts.append("+ geo")
    filter_msg = f" (filtré: {' '.join(filter_parts)})" if filter_parts else ""
    print(f"🔗 {len(links)} liens extraits{filter_msg}")

    # Traiter
    results = process_links(links, output_dir=output_dir, dry_run=args.dry_run)
    print_summary(results)


if __name__ == '__main__':
    main()
