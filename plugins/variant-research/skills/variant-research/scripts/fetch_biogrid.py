#!/usr/bin/env python3
"""Fetch protein-protein interactions from BioGRID for a given gene symbol."""


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
import time
import requests

BIOGRID_API = "https://webservice.thebiogrid.org/interactions/"


def fetch_biogrid_interactions(gene_symbol: str, max_results: int = 50, max_retries: int = 1) -> dict:
    """Query BioGRID for interactions involving the given gene."""
    result = {
        "database": "BioGRID",
        "gene_symbol": gene_symbol,
        "interactions": [],
        "total_count": 0,
        "errors": [],
    }

    api_key = os.environ.get("BIOGRID_API_KEY")
    if not api_key:
        result["errors"].append(
            "BIOGRID_API_KEY not set. Get a free key at https://wiki.thebiogrid.org/doku.php/biogridrest"
        )
        return result

    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(
                BIOGRID_API,
                params={
                    "accesskey": api_key,
                    "format": "json",
                    "searchNames": "true",
                    "geneList": gene_symbol,
                    "organism": 9606,  # Human
                    "start": 0,
                    "max": max_results,
                    "includeInteractors": "true",
                    "includeInteractorInteractions": "false",
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            result["total_count"] = len(data)

            for interaction_id, interaction in data.items():
                result["interactions"].append({
                    "biogrid_id": str(interaction_id),
                    "gene_a": interaction.get("OFFICIAL_SYMBOL_A", ""),
                    "gene_b": interaction.get("OFFICIAL_SYMBOL_B", ""),
                    "experimental_system": interaction.get("EXPERIMENTAL_SYSTEM", ""),
                    "throughput": interaction.get("THROUGHPUT", ""),
                    "pubmed_id": interaction.get("PUBMED_ID", ""),
                    "organism_a": interaction.get("ORGANISM_A", ""),
                    "organism_b": interaction.get("ORGANISM_B", ""),
                    "score": interaction.get("SCORE", None),
                })

            return result

        except requests.RequestException as e:
            if attempt < max_retries:
                time.sleep(5)
                continue
            result["errors"].append(f"BioGRID API request failed: {str(e)}")
            return result

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_biogrid.py <gene_symbol>", file=sys.stderr)
        sys.exit(1)

    gene_symbol = sys.argv[1]
    result = fetch_biogrid_interactions(gene_symbol)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
