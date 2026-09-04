# &s &PIPELINE_aaMAIN - Orchestrateur pipeline consolidation + KPI Airbnb

# Execute sequentiellement les scripts de consolidation et KPI.
# sp04/sp06 exclus (download/flatten = ponctuel).
#
# Usage:
#   python scripts/sp00-run-pipeline.py [--from spXX] [--dry-run] [--europe-only]
#
# Date: 2026-03-08

import subprocess
import sys
import time
from pathlib import Path

# &s &CONFIG
BASE = Path(r"C:\Users\vince\hh\pq\PDS\pbnb-airbnb-log-jrr-jpy")
PYTHON = r"C:\ScoopApps\apps\python\current\python.exe"

STEPS = [
    ("sp07b", "scripts/sp07b-consolidate-gz-global-260217.py",  "Consolidation gz (global)"),
    ("sp08",  "scripts/sp08-recap-kpi-global-260212.py",        "KPI global (all indicators)"),
    ("sp09",  "scripts/sp09-hosts-global-260222.py",            "Agrégation hôtes"),
]
# &e

# &s &MAIN
def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    europe_only = "--europe-only" in args
    extra_args = ["--europe-only"] if europe_only else []

    # --from spXX
    start_step = None
    for a in args:
        if a.startswith("--from"):
            idx = args.index(a)
            if idx + 1 < len(args):
                start_step = args[idx + 1]
            elif "=" in a:
                start_step = a.split("=", 1)[1]

    # Filtrer étapes
    steps = STEPS
    if start_step:
        found = False
        for i, (key, _, _) in enumerate(steps):
            if key == start_step:
                steps = steps[i:]
                found = True
                break
        if not found:
            valid = [k for k, _, _ in STEPS]
            print(f"Etape '{start_step}' inconnue. Valides : {', '.join(valid)}")
            sys.exit(1)

    scope = "EUROPE" if europe_only else "GLOBAL"
    print(f"{'=' * 60}")
    print(f"PIPELINE AIRBNB — {scope}")
    print(f"{'=' * 60}")
    print(f"Etapes : {' >'.join(k for k, _, _ in steps)}")
    if dry_run:
        print("[DRY-RUN] Aucune execution")
    print()

    for key, script, desc in steps:
        script_path = BASE / script
        if not script_path.exists():
            print(f"[SKIP] {key}: {script} introuvable")
            continue

        cmd = [PYTHON, str(script_path)] + extra_args
        print(f"{'-' * 50}")
        print(f"[{key}] {desc}")
        print(f"  >{' '.join(cmd)}")

        if dry_run:
            continue

        t0 = time.time()
        result = subprocess.run(cmd, cwd=str(BASE))
        elapsed = time.time() - t0

        if result.returncode != 0:
            print(f"\n[ERREUR] {key} a echoue (code {result.returncode}) après {elapsed:.0f}s")
            print("Pipeline interrompu.")
            sys.exit(result.returncode)

        print(f"  [OK] {key} termine en {elapsed:.0f}s")

    print(f"\n{'=' * 60}")
    print("Pipeline termine.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
# &e

# &e
