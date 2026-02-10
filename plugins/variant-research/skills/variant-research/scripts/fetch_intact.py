#!/usr/bin/env python3
"""Fetch protein-protein interactions from IntAct (EBI) via PSICQUIC for a given gene symbol."""


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
import time
import requests

PSICQUIC_API = "https://www.ebi.ac.uk/Tools/webservices/psicquic/intact/webservices/current/search/interactor"


def fetch_intact_interactions(gene_symbol: str, max_results: int = 50, max_retries: int = 1) -> dict:
    """Query IntAct via PSICQUIC for interactions involving the given gene/protein."""
    result = {
        "database": "IntAct",
        "gene_symbol": gene_symbol,
        "interactions": [],
        "total_count": 0,
        "errors": [],
    }

    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(
                f"{PSICQUIC_API}/{gene_symbol}",
                params={
                    "format": "tab27",
                    "firstResult": 0,
                    "maxResults": max_results,
                },
                timeout=30,
            )
            resp.raise_for_status()

            lines = resp.text.strip().split("\n")
            result["total_count"] = len(lines)

            for line in lines:
                if not line.strip():
                    continue
                fields = line.split("\t")
                if len(fields) < 15:
                    continue

                # MITAB 2.7 format fields
                id_a = fields[0]  # Unique ID interactor A
                id_b = fields[1]  # Unique ID interactor B
                alt_a = fields[2]  # Alt ID A
                alt_b = fields[3]  # Alt ID B
                alias_a = fields[4]  # Alias A
                alias_b = fields[5]  # Alias B
                detection = fields[6]  # Interaction detection method
                publication = fields[8]  # Publication ID
                taxid_a = fields[9]  # Taxid A
                taxid_b = fields[10]  # Taxid B
                int_type = fields[11]  # Interaction type
                confidence = fields[14] if len(fields) > 14 else ""  # Confidence

                # Extract readable names
                name_a = _extract_name(alias_a) or _extract_id(id_a)
                name_b = _extract_name(alias_b) or _extract_id(id_b)

                # Extract PubMed ID
                pmid = ""
                for part in publication.split("|"):
                    if "pubmed:" in part:
                        pmid = part.replace("pubmed:", "").strip()
                        break

                # Extract detection method short name
                det_method = _extract_psi_value(detection)
                interaction_type = _extract_psi_value(int_type)

                # Extract confidence score
                score = None
                if confidence:
                    for part in confidence.split("|"):
                        if "intact-miscore:" in part:
                            try:
                                score = float(part.split(":")[1])
                            except (ValueError, IndexError):
                                pass

                result["interactions"].append({
                    "interactors": [name_a, name_b],
                    "interaction_type": interaction_type,
                    "detection_method": det_method,
                    "publication": pmid,
                    "confidence_score": score,
                })

            return result

        except requests.RequestException as e:
            if attempt < max_retries:
                time.sleep(5)
                continue
            result["errors"].append(f"IntAct PSICQUIC request failed: {str(e)}")
            return result

    return result


def _extract_name(alias_field: str) -> str:
    """Extract a human-readable name from a MITAB alias field."""
    for part in alias_field.split("|"):
        if "display_short" in part:
            name = part.split("(")[0].split(":")[1] if ":" in part else part.split("(")[0]
            return name.strip()
    # Fallback: try gene name
    for part in alias_field.split("|"):
        if "gene name" in part.lower():
            name = part.split("(")[0].split(":")[1] if ":" in part else part.split("(")[0]
            return name.strip()
    return ""


def _extract_id(id_field: str) -> str:
    """Extract identifier from MITAB ID field."""
    if ":" in id_field:
        return id_field.split(":")[1].split("|")[0]
    return id_field.split("|")[0]


def _extract_psi_value(field: str) -> str:
    """Extract short label from PSI-MI formatted field like psi-mi:'MI:0004'(name)."""
    if "(" in field and ")" in field:
        start = field.index("(") + 1
        end = field.rindex(")")
        return field[start:end]
    return field


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_intact.py <gene_symbol>", file=sys.stderr)
        sys.exit(1)

    gene_symbol = sys.argv[1]
    result = fetch_intact_interactions(gene_symbol)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
