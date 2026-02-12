#!/usr/bin/env python3
"""
Restructure les données Inside Airbnb en flat view.
Extrait .gz → .csv avec nommage YY-MM-XXX-ville_listings.csv

Structure source : pays/ville/YYYY-MM-DD/listings.csv.gz
Structure cible  : pays/ville/YY-MM-XXX-ville_listings.csv

Usage:
    python sp06-flatten-insideairbnb-251231.py
    python sp06-flatten-insideairbnb-251231.py --dry-run
"""

import argparse
import gzip
import shutil
from pathlib import Path

BASE_DIR = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy\data\raw\zudb-inside-airbnbbnb")

# Mapping pays Inside Airbnb → ISO 3166-1 alpha-3
COUNTRY_CODES = {
    # Europe
    'france': 'FRA',
    'germany': 'DEU',
    'italy': 'ITA',
    'united-kingdom': 'GBR',
    'spain': 'ESP',
    'netherlands': 'NLD',
    'the-netherlands': 'NLD',
    'portugal': 'PRT',
    'belgium': 'BEL',
    'austria': 'AUT',
    'greece': 'GRC',
    'switzerland': 'CHE',
    'ireland': 'IRL',
    'poland': 'POL',
    'czech-republic': 'CZE',
    'hungary': 'HUN',
    'sweden': 'SWE',
    'norway': 'NOR',
    'denmark': 'DNK',
    'finland': 'FIN',
    'croatia': 'HRV',
    'slovenia': 'SVN',
    'slovakia': 'SVK',
    'romania': 'ROU',
    'bulgaria': 'BGR',
    'serbia': 'SRB',
    'turkey': 'TUR',
    'cyprus': 'CYP',
    'malta': 'MLT',
    'luxembourg': 'LUX',
    'iceland': 'ISL',
    # Americas
    'united-states': 'USA',
    'canada': 'CAN',
    'mexico': 'MEX',
    'brazil': 'BRA',
    'argentina': 'ARG',
    'chile': 'CHL',
    'colombia': 'COL',
    'peru': 'PER',
    'cuba': 'CUB',
    'belize': 'BLZ',
    # Asia-Pacific
    'australia': 'AUS',
    'new-zealand': 'NZL',
    'japan': 'JPN',
    'china': 'CHN',
    'hong-kong': 'HKG',
    'taiwan': 'TWN',
    'singapore': 'SGP',
    'thailand': 'THA',
    'india': 'IND',
    # Africa
    'south-africa': 'ZAF',
}


def parse_date_folder(folder_name: str) -> str:
    """Extrait YY-MM depuis YYYY-MM-DD."""
    # folder_name = "2025-09-18"
    parts = folder_name.split('-')
    if len(parts) >= 2:
        year = parts[0][2:]  # "2025" → "25"
        month = parts[1]      # "09"
        return f"{year}-{month}"
    return folder_name


def get_country_code(country: str) -> str:
    """Retourne code ISO 3 lettres."""
    return COUNTRY_CODES.get(country.lower(), country[:3].upper())


def flatten_structure(base_dir: Path, dry_run: bool = False, country_filter: list = None) -> dict:
    """Restructure en flat view."""
    results = {'converted': [], 'skipped': [], 'failed': [], 'extras': []}

    # Trouver tous les fichiers dans structure date
    # Structure: continent/country/city/date/fichiers
    gz_files = list(base_dir.rglob("*/*/*/*/listings.csv.gz"))
    geojson_files = list(base_dir.rglob("*/*/*/*/neighbourhoods.geojson"))
    # Summary listings.csv (version light) - même dossier que .gz
    summary_files = [f for f in base_dir.rglob("*/*/*/*/listings.csv") if not str(f).endswith('.gz')]
    nbh_files = list(base_dir.rglob("*/*/*/*/neighbourhoods.csv"))

    total_extras = len(geojson_files) + len(summary_files) + len(nbh_files)
    print(f"📦 {len(gz_files)} fichiers .gz + {total_extras} extras (geo/sum/nbh) trouvés\n")

    # === ÉTAPE 1: Traiter extras AVANT renommage dossiers ===
    def process_extras(files, prefix, icon, file_suffix, with_date=False, all_files=False):
        seen = set()
        for fpath in sorted(files):
            parts = fpath.relative_to(base_dir).parts
            if len(parts) < 5:
                continue

            continent = parts[0]
            country = parts[1]
            city = parts[2]
            date_folder = parts[3]
            city_key = f"{continent}/{country}/{city}"

            # Filtrer par pays si demandé
            if country_filter and country.lower() not in [c.lower() for c in country_filter]:
                continue

            # Skip si déjà vu (sauf si all_files=True)
            if not all_files:
                if city_key in seen:
                    continue
                seen.add(city_key)

            country_code = get_country_code(country)
            if with_date:
                yy_mm = parse_date_folder(date_folder)
                new_name = f"{yy_mm}-{country_code}-{city}_{file_suffix}"
            else:
                new_name = f"{prefix}-{country_code}-{city}_{file_suffix}"
            target_path = base_dir / continent / country / city / new_name

            if target_path.exists():
                print(f"⏭️  {new_name} → existe déjà")
                continue

            if dry_run:
                print(f"{icon}  {city}/{date_folder} → {new_name}")
                results['extras'].append(fpath)
                continue

            try:
                print(f"{icon}  {city}/{date_folder} → {new_name}...", end=' ', flush=True)
                shutil.copy2(fpath, target_path)
                size_kb = target_path.stat().st_size / 1024
                print(f"✅ ({size_kb:.0f} KB)")
                results['extras'].append(fpath)
            except Exception as e:
                print(f"❌ {e}")
                results['failed'].append(fpath)

    # GeoJSON (1 par ville, pas de date)
    process_extras(geojson_files, "geo", "🗺️", "neighbourhoods.geojson")
    # Summary listings - TOUS avec date
    process_extras(summary_files, "sum", "📊", "sumlistings.csv", with_date=True, all_files=True)
    # Neighbourhoods CSV (1 par ville, pas de date)
    process_extras(nbh_files, "nbh", "🏘️", "neighbourhoods.csv")

    # === ÉTAPE 2: Renommer dossiers gz + nettoyer doublons ===
    for gz_path in sorted(gz_files):
        # Extraire composants du chemin
        # base_dir/continent/country/city/date/listings.csv.gz
        parts = gz_path.relative_to(base_dir).parts
        if len(parts) < 5:
            continue

        continent = parts[0]
        country = parts[1]
        city = parts[2]
        date_folder = parts[3]

        # Filtrer par pays si demandé
        if country_filter and country.lower() not in [c.lower() for c in country_filter]:
            continue

        # Renommer dossier date YYYY-MM-DD → yy-mm (garder gz dedans)
        yy_mm = parse_date_folder(date_folder)
        old_date_dir = gz_path.parent
        new_date_dir = base_dir / continent / country / city / yy_mm

        if new_date_dir.exists():
            print(f"⏭️  {city}/{yy_mm}/ → existe déjà")
            results['skipped'].append(gz_path)
            continue

        if dry_run:
            print(f"📦 {city}/{date_folder}/ → {yy_mm}/ (gz)")
            results['converted'].append(gz_path)
            continue

        try:
            print(f"📦 {city}/{date_folder}/ → {yy_mm}/...", end=' ', flush=True)
            old_date_dir.rename(new_date_dir)
            size_mb = (new_date_dir / 'listings.csv.gz').stat().st_size / (1024*1024)

            # Nettoyer doublons dans le dossier yy-mm (déjà copiés flat)
            for dup in ['listings.csv', 'neighbourhoods.csv', 'neighbourhoods.geojson']:
                dup_path = new_date_dir / dup
                if dup_path.exists():
                    dup_path.unlink()

            print(f"✅ ({size_mb:.1f} MB gz)")
            results['converted'].append(gz_path)
        except Exception as e:
            print(f"❌ {e}")
            results['failed'].append(gz_path)

    return results


def cleanup_date_folders(base_dir: Path, dry_run: bool = False, country_filter: list = None):
    """Supprime les sous-dossiers date après migration."""
    # Trouver tous les dossiers date (YYYY-MM-DD)
    import re
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    removed = 0
    for continent_dir in base_dir.iterdir():
        if not continent_dir.is_dir():
            continue
        for country_dir in continent_dir.iterdir():
            if not country_dir.is_dir():
                continue
            # Filtrer par pays si demandé
            if country_filter and country_dir.name.lower() not in [c.lower() for c in country_filter]:
                continue
            for city_dir in country_dir.iterdir():
                if not city_dir.is_dir():
                    continue
                for sub in city_dir.iterdir():
                    if sub.is_dir() and date_pattern.match(sub.name):
                        if dry_run:
                            print(f"🗑️  Supprimerait: {sub.relative_to(base_dir)}")
                        else:
                            shutil.rmtree(sub)
                            print(f"🗑️  Supprimé: {sub.relative_to(base_dir)}")
                        removed += 1

    return removed


EUROPE_COUNTRIES = [
    'france', 'germany', 'italy', 'spain', 'portugal', 'united-kingdom',
    'belgium', 'the-netherlands', 'switzerland', 'austria', 'greece',
    'ireland', 'poland', 'czech-republic', 'hungary', 'sweden', 'norway',
    'denmark', 'finland', 'croatia', 'slovenia', 'slovakia', 'romania',
    'bulgaria', 'serbia', 'turkey', 'cyprus', 'malta', 'luxembourg', 'iceland'
]

def main():
    parser = argparse.ArgumentParser(description='Flatten Inside Airbnb structure')
    parser.add_argument('--dry-run', action='store_true', help='Affiche sans modifier')
    parser.add_argument('--cleanup', action='store_true', help='Supprimer anciens dossiers date')
    parser.add_argument('--countries', '-c', nargs='+', help='Filtrer par pays (ex: france germany)')
    parser.add_argument('--europe', '-e', action='store_true', help='Seulement pays européens')
    parser.add_argument('--path', type=Path, default=BASE_DIR, help='Dossier racine')
    args = parser.parse_args()

    # Filtrer par pays
    country_filter = None
    if args.europe:
        country_filter = EUROPE_COUNTRIES
        print(f"🌍 Filtre Europe: {len(country_filter)} pays")
    elif args.countries:
        country_filter = [c.lower() for c in args.countries]
        print(f"🌍 Filtre pays: {', '.join(country_filter)}")

    print(f"📁 Dossier: {args.path}\n")

    # Étape 1: Conversion flat
    print("=== CONVERSION FLAT VIEW ===\n")
    results = flatten_structure(args.path, dry_run=args.dry_run, country_filter=country_filter)

    print(f"\n{'='*40}")
    print(f"✅ Listings convertis: {len(results['converted'])}")
    print(f"📦 Extras (geo/sum/nbh): {len(results['extras'])}")
    print(f"⏭️  Skippés: {len(results['skipped'])}")
    print(f"❌ Échecs: {len(results['failed'])}")

    # Étape 2: Cleanup si demandé
    if args.cleanup:
        print(f"\n=== NETTOYAGE DOSSIERS DATE ===\n")
        removed = cleanup_date_folders(args.path, dry_run=args.dry_run, country_filter=country_filter)
        print(f"\n🗑️  {removed} dossiers {'à supprimer' if args.dry_run else 'supprimés'}")


if __name__ == '__main__':
    main()
