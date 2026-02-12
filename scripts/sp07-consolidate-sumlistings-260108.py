"""
sp07-consolidate-sumlistings-260108.py
Consolide tous les fichiers *_sumlistings.csv en une base unique
Ajoute colonnes: country_code, city, date_snapshot, region
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime

# =======&s _aaMAIN =======
# Script consolidation sumlistings Airbnb
# Input: data/raw/zudb-inside-airbnbbnb/**/*_sumlistings.csv
# Output: data/processed/consolidated_sumlistings.parquet

BASE_PATH = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
RAW_PATH = BASE_PATH / "data" / "raw" / "zudb-inside-airbnbbnb"
OUTPUT_PATH = BASE_PATH / "data" / "processed"

def parse_filename(filepath: Path) -> dict:
    """
    Parse filename pattern: 25-03-FRA-paris_sumlistings.csv
    Returns dict with country_code, city, date_snapshot
    """
    fname = filepath.name
    # Pattern: YY-MM-XXX-city_sumlistings.csv
    match = re.match(r'(\d{2})-(\d{2})-([A-Z]{3})-(.+)_sumlistings\.csv', fname)
    if match:
        year, month, country_code, city = match.groups()
        return {
            'country_code': country_code,
            'city': city.replace('-', '_'),  # pays-basque -> pays_basque
            'date_snapshot': f"20{year}-{month}",
            'date_snapshot_short': f"{year}-{month}"
        }
    return None

def get_region_from_path(filepath: Path) -> str:
    """Extract region from path (europe, usa, world)"""
    parts = filepath.parts
    try:
        idx = parts.index('zudb-inside-airbnbbnb')
        return parts[idx + 1] if idx + 1 < len(parts) else 'unknown'
    except ValueError:
        return 'unknown'

def consolidate_all():
    """Main consolidation function"""
    print("=" * 60)
    print("CONSOLIDATION SUMLISTINGS AIRBNB")
    print("=" * 60)

    # Find all sumlistings files
    files = list(RAW_PATH.rglob("*_sumlistings.csv"))
    print(f"\nFichiers trouvés: {len(files)}")

    # Process each file
    dfs = []
    errors = []

    for i, f in enumerate(files):
        meta = parse_filename(f)
        if meta is None:
            errors.append(f"Cannot parse: {f.name}")
            continue

        try:
            df = pd.read_csv(f, low_memory=False)

            # Add metadata columns
            df['country_code'] = meta['country_code']
            df['city'] = meta['city']
            df['date_snapshot'] = meta['date_snapshot']
            df['region'] = get_region_from_path(f)

            dfs.append(df)

            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(files)} files...")

        except Exception as e:
            errors.append(f"Error reading {f.name}: {e}")

    if errors:
        print(f"\n⚠️ Erreurs ({len(errors)}):")
        for err in errors[:10]:
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... et {len(errors) - 10} autres")

    # Concatenate all
    print(f"\nConcaténation de {len(dfs)} DataFrames...")
    df_all = pd.concat(dfs, ignore_index=True)

    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ CONSOLIDATION")
    print(f"{'=' * 60}")
    print(f"Total lignes: {len(df_all):,}")
    print(f"Total colonnes: {len(df_all.columns)}")
    print(f"\nPar région:")
    print(df_all.groupby('region').size().sort_values(ascending=False).to_string())
    print(f"\nPar pays (top 15):")
    print(df_all.groupby('country_code').size().sort_values(ascending=False).head(15).to_string())
    print(f"\nPar snapshot:")
    print(df_all.groupby('date_snapshot').size().sort_values().to_string())

    # Save
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Parquet (optimal)
    output_parquet = OUTPUT_PATH / "consolidated_sumlistings.parquet"
    df_all.to_parquet(output_parquet, index=False)
    print(f"\n✅ Sauvegardé: {output_parquet}")
    print(f"   Taille: {output_parquet.stat().st_size / 1024 / 1024:.1f} MB")

    # CSV (backup)
    output_csv = OUTPUT_PATH / "consolidated_sumlistings.csv"
    df_all.to_csv(output_csv, index=False)
    print(f"✅ Sauvegardé: {output_csv}")
    print(f"   Taille: {output_csv.stat().st_size / 1024 / 1024:.1f} MB")

    return df_all

# =======&e _aaMAIN =======

if __name__ == "__main__":
    df = consolidate_all()
