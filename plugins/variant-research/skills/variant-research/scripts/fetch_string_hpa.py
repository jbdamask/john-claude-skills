#!/usr/bin/env python3
"""Fetch protein interactions from STRING-db and expression data from Human Protein Atlas."""


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
import sys
import requests


def fetch_string_interactions(gene_symbol: str, species: int = 9606) -> dict:
    """Query STRING-db API for protein-protein interactions."""
    result = {
        "interactions": [],
        "errors": [],
    }

    try:
        # Resolve identifier
        resolve_url = "https://string-db.org/api/json/get_string_ids"
        resp = requests.get(resolve_url, params={
            "identifiers": gene_symbol,
            "species": species,
            "limit": 1,
        }, timeout=30)
        resp.raise_for_status()
        ids = resp.json()
        if not ids:
            result["errors"].append(f"Could not resolve {gene_symbol} in STRING-db")
            return result

        string_id = ids[0]["stringId"]

        # Get interaction partners
        network_url = "https://string-db.org/api/json/network"
        resp = requests.get(network_url, params={
            "identifiers": gene_symbol,
            "species": species,
            "required_score": 400,
            "network_type": "functional",
            "limit": 25,
        }, timeout=30)
        resp.raise_for_status()
        interactions_raw = resp.json()

        for item in interactions_raw:
            result["interactions"].append({
                "protein_a": item.get("preferredName_A", ""),
                "protein_b": item.get("preferredName_B", ""),
                "combined_score": item.get("score", 0),
                "nscore": item.get("nscore", 0),
                "fscore": item.get("fscore", 0),
                "pscore": item.get("pscore", 0),
                "ascore": item.get("ascore", 0),
                "escore": item.get("escore", 0),
                "dscore": item.get("dscore", 0),
                "tscore": item.get("tscore", 0),
            })

    except requests.RequestException as e:
        result["errors"].append(f"STRING-db request failed: {str(e)}")

    return result


def fetch_hpa_data(gene_symbol: str) -> dict:
    """Query Human Protein Atlas for tissue expression and subcellular localization."""
    result = {
        "protein_class": "",
        "subcellular_location": "",
        "tissue_expression": "",
        "rna_expression": "",
        "errors": [],
    }

    try:
        # Use the HPA search download API (reliable, free, no auth)
        search_url = "https://www.proteinatlas.org/api/search_download.php"
        resp = requests.get(search_url, params={
            "search": gene_symbol,
            "format": "json",
            "columns": "g,gs,up,t,scl,pc,re",
            "compress": "no",
        }, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Find exact match for our gene
        entry = None
        for item in data:
            if item.get("Gene", "").upper() == gene_symbol.upper():
                entry = item
                break
        if not entry and data:
            entry = data[0]

        if entry:
            protein_class = entry.get("Protein class", "")
            if isinstance(protein_class, list):
                protein_class = ", ".join(protein_class)
            result["protein_class"] = str(protein_class) if protein_class else ""

            subcellular = entry.get("Subcellular location", "")
            if isinstance(subcellular, list):
                subcellular = ", ".join(str(s) for s in subcellular)
            result["subcellular_location"] = str(subcellular) if subcellular else ""

            tissue = entry.get("Tissue expression", "")
            if not tissue:
                tissue = entry.get("RNA tissue specificity", "")
            result["tissue_expression"] = str(tissue) if tissue else ""

            rna = entry.get("RNA expression", "")
            if not rna:
                rna = entry.get("RNA tissue specific nTPM", "")
            result["rna_expression"] = str(rna) if rna else ""
        else:
            result["errors"].append(f"No results found in HPA for {gene_symbol}")

    except (requests.RequestException, ValueError) as e:
        result["errors"].append(f"HPA request failed: {str(e)}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_string_hpa.py <gene_symbol>", file=sys.stderr)
        sys.exit(1)

    gene_symbol = sys.argv[1]

    string_data = fetch_string_interactions(gene_symbol)
    hpa_data = fetch_hpa_data(gene_symbol)

    output = {
        "string_interactions": string_data,
        "hpa_expression": hpa_data,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
