#!/usr/bin/env python3
"""Fetch protein interaction and expression data from STRING, HPA, IntAct, BioPlex, BioGRID.

Combines output from existing scripts into a single reports/{rsid}_protein.json.
"""


import glob as _glob
import os as _os
import sys as _sys

# Auto-detect venv when present (following nano-banana pattern)
_SCRIPT_DIR = _os.path.dirname(_os.path.abspath(__file__))
_SKILL_DIR = _os.path.dirname(_SCRIPT_DIR)
_VENV_SITE = _os.path.join(_SKILL_DIR, ".venv", "lib")
if _os.path.isdir(_VENV_SITE):
    _matches = _glob.glob(_os.path.join(_VENV_SITE, "python*", "site-packages"))
    if _matches:
        _sys.path.insert(0, _matches[0])

import json
import os
import sys
from pathlib import Path

# Add script directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from fetch_string_hpa import fetch_string_interactions, fetch_hpa_data
from fetch_intact import fetch_intact_interactions
from fetch_bioplex import fetch_bioplex_interactions
from fetch_biogrid import fetch_biogrid_interactions


def fetch_all_protein(rsid: str, gene_symbol: str) -> dict:
    """Fetch protein data from all sources for the given gene."""
    result = {
        "rsid": rsid,
        "gene_symbol": gene_symbol,
        "string_interactions": {},
        "hpa_expression": {},
        "intact": {},
        "bioplex": {},
        "biogrid": {},
        "errors": [],
    }

    # STRING-db
    try:
        string_data = fetch_string_interactions(gene_symbol)
        result["string_interactions"] = string_data
        if string_data.get("errors"):
            result["errors"].extend(string_data["errors"])
    except Exception as e:
        result["errors"].append(f"STRING-db failed: {str(e)}")

    # Human Protein Atlas
    try:
        hpa_data = fetch_hpa_data(gene_symbol)
        result["hpa_expression"] = hpa_data
        if hpa_data.get("errors"):
            result["errors"].extend(hpa_data["errors"])
    except Exception as e:
        result["errors"].append(f"HPA failed: {str(e)}")

    # IntAct
    try:
        intact_data = fetch_intact_interactions(gene_symbol)
        result["intact"] = intact_data
        if intact_data.get("errors"):
            result["errors"].extend(intact_data["errors"])
    except Exception as e:
        result["errors"].append(f"IntAct failed: {str(e)}")

    # BioPlex
    try:
        bioplex_data = fetch_bioplex_interactions(gene_symbol)
        result["bioplex"] = bioplex_data
        if bioplex_data.get("errors"):
            result["errors"].extend(bioplex_data["errors"])
    except Exception as e:
        result["errors"].append(f"BioPlex failed: {str(e)}")

    # BioGRID
    try:
        biogrid_data = fetch_biogrid_interactions(gene_symbol)
        result["biogrid"] = biogrid_data
        if biogrid_data.get("errors"):
            result["errors"].extend(biogrid_data["errors"])
    except Exception as e:
        result["errors"].append(f"BioGRID failed: {str(e)}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_protein.py <rsID> [reports_dir]", file=sys.stderr)
        sys.exit(1)

    rsid = sys.argv[1].lower().strip()
    reports_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd() / "reports"

    # Read variant info
    variant_file = reports_dir / f"{rsid}_variant.json"
    try:
        with open(variant_file) as f:
            variant_info = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Could not read variant info: {e}"}))
        sys.exit(1)

    gene_symbol = variant_info.get("gene_symbol", "")
    if not gene_symbol:
        print(json.dumps({"error": "No gene_symbol in variant info"}))
        sys.exit(1)

    result = fetch_all_protein(rsid, gene_symbol)

    # Write output
    output_file = reports_dir / f"{rsid}_protein.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Protein results written to {output_file}")


if __name__ == "__main__":
    main()
