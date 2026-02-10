#!/usr/bin/env python3
"""Fetch protein-protein interactions from BioPlex 3.0 for a given gene symbol.

Downloads the BioPlex 293T network data file on first use and caches it locally.
Subsequent queries use the cached file.
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

import csv
import json
import os
import sys
import requests

BIOPLEX_URL = "https://bioplex.hms.harvard.edu/data/BioPlex_293T_Network_10K_Dec_2019.tsv"


def _get_cache_path() -> str:
    """Return path to the cached BioPlex data file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(script_dir, ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "bioplex_293t.tsv")


def _download_data(cache_path: str) -> None:
    """Download BioPlex data file if not cached."""
    if os.path.exists(cache_path):
        return
    print(f"Downloading BioPlex data (first time only)...", file=sys.stderr)
    resp = requests.get(BIOPLEX_URL, stream=True, timeout=120)
    resp.raise_for_status()
    with open(cache_path, "w") as f:
        for chunk in resp.iter_content(chunk_size=8192, decode_unicode=True):
            f.write(chunk)
    print(f"BioPlex data cached at {cache_path}", file=sys.stderr)


def fetch_bioplex_interactions(gene_symbol: str, max_results: int = 50) -> dict:
    """Query cached BioPlex data for interactions involving the given gene."""
    result = {
        "database": "BioPlex",
        "gene_symbol": gene_symbol,
        "interactions": [],
        "total_count": 0,
        "errors": [],
    }

    try:
        cache_path = _get_cache_path()
        _download_data(cache_path)

        gene_upper = gene_symbol.upper()
        matches = []

        with open(cache_path, "r") as f:
            reader = csv.DictReader(f, delimiter="\t", quotechar='"')
            for row in reader:
                sym_a = row.get("SymbolA", "").strip().upper()
                sym_b = row.get("SymbolB", "").strip().upper()
                if sym_a == gene_upper or sym_b == gene_upper:
                    matches.append(row)

        result["total_count"] = len(matches)

        for row in matches[:max_results]:
            try:
                p_wrong = float(row.get("pW", 0))
            except (ValueError, TypeError):
                p_wrong = None
            try:
                p_no_int = float(row.get("pNI", 0))
            except (ValueError, TypeError):
                p_no_int = None
            try:
                p_int = float(row.get("pInt", 0))
            except (ValueError, TypeError):
                p_int = None

            result["interactions"].append({
                "gene_a": row.get("GeneA", ""),
                "gene_b": row.get("GeneB", ""),
                "symbol_a": row.get("SymbolA", ""),
                "symbol_b": row.get("SymbolB", ""),
                "uniprot_a": row.get("UniprotA", ""),
                "uniprot_b": row.get("UniprotB", ""),
                "p_wrong": p_wrong,
                "p_no_interaction": p_no_int,
                "p_interaction": p_int,
            })

        return result

    except requests.RequestException as e:
        result["errors"].append(f"Failed to download BioPlex data: {str(e)}")
        return result
    except Exception as e:
        result["errors"].append(f"BioPlex query failed: {str(e)}")
        return result


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_bioplex.py <gene_symbol>", file=sys.stderr)
        sys.exit(1)

    gene_symbol = sys.argv[1]
    result = fetch_bioplex_interactions(gene_symbol)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
