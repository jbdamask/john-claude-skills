#!/usr/bin/env python3
"""Fetch patent data from PatentsView Search API v1 for a given gene.

Produces reports/{rsid}_patents.json with patent entries.
Requires PATENTSVIEW_API_KEY environment variable (free registration at
https://patentsview.org/apis/keyrequest).
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
import time
from pathlib import Path

import requests

PATENTSVIEW_API = "https://search.patentsview.org/api/v1/patent/"


def search_patents(query_text: str, api_key: str, per_page: int = 25) -> list[dict]:
    """Search PatentsView v1 API for patents matching the query text."""
    params = {
        "q": json.dumps({"_text_any": {"patent_abstract": query_text}}),
        "f": json.dumps([
            "patent_id", "patent_title", "patent_abstract",
            "patent_date", "assignees",
        ]),
        "o": json.dumps({"size": per_page}),
        "s": json.dumps([{"patent_date": "desc"}]),
    }

    resp = requests.get(
        PATENTSVIEW_API,
        params=params,
        headers={"X-Api-Key": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    patents = []
    for patent in data.get("patents", []):
        assignees = patent.get("assignees", [])
        assignee = ""
        if assignees and isinstance(assignees, list):
            first = assignees[0] if assignees else {}
            if isinstance(first, dict):
                assignee = first.get("assignee_organization", "") or first.get("assignee_first_name", "Unknown")

        abstract = patent.get("patent_abstract", "")
        abstract_snippet = abstract[:250] + "..." if len(abstract) > 250 else abstract

        patents.append({
            "patent_number": patent.get("patent_id", ""),
            "title": patent.get("patent_title", ""),
            "assignee": assignee or "Unknown",
            "date": patent.get("patent_date", ""),
            "abstract_snippet": abstract_snippet,
            "classification": _classify_patent(patent.get("patent_title", ""), abstract),
        })

    return patents


def _classify_patent(title: str, abstract: str) -> str:
    """Classify a patent as drug, diagnostic, therapeutic, or other."""
    text = (title + " " + abstract).lower()

    drug_keywords = ["drug", "pharmaceutical", "compound", "inhibitor", "antagonist",
                     "agonist", "antibody", "sirna", "antisense", "oligonucleotide",
                     "small molecule", "formulation", "dosage"]
    diagnostic_keywords = ["diagnostic", "biomarker", "assay", "detection", "screening",
                          "probe", "marker", "test", "kit"]
    therapeutic_keywords = ["treatment", "therapy", "therapeutic", "method of treating",
                           "disease", "disorder"]

    drug_score = sum(1 for kw in drug_keywords if kw in text)
    diag_score = sum(1 for kw in diagnostic_keywords if kw in text)
    ther_score = sum(1 for kw in therapeutic_keywords if kw in text)

    if drug_score > diag_score and drug_score > ther_score:
        return "drug"
    elif diag_score > ther_score:
        return "diagnostic"
    elif ther_score > 0:
        return "therapeutic"
    return "other"


def fetch_all_patents(rsid: str, gene_symbol: str, gene_name: str = "") -> dict:
    """Fetch patents related to the gene from PatentsView."""
    result = {
        "rsid": rsid,
        "gene_symbol": gene_symbol,
        "patents": [],
        "search_queries_used": [],
        "errors": [],
    }

    api_key = os.environ.get("PATENTSVIEW_API_KEY")
    if not api_key:
        result["errors"].append(
            "PATENTSVIEW_API_KEY not set. Get a free key at "
            "https://patentsview.org/apis/keyrequest"
        )
        return result

    seen_numbers = set()
    queries = [
        f"{gene_symbol} {gene_name}" if gene_name else gene_symbol,
        f"{gene_symbol} drug therapeutic inhibitor",
        f"{gene_symbol} diagnostic biomarker",
    ]

    if gene_name and len(gene_name.split()) > 1:
        queries.append(f"{gene_name} antisense siRNA oligonucleotide")

    for query in queries:
        result["search_queries_used"].append(query)
        try:
            patents = search_patents(query, api_key, per_page=15)
            for patent in patents:
                num = patent.get("patent_number", "")
                if num and num not in seen_numbers:
                    seen_numbers.add(num)
                    result["patents"].append(patent)
            time.sleep(1.5)  # Respect rate limit (45 req/min)
        except requests.RequestException as e:
            result["errors"].append(f"PatentsView search failed for '{query}': {str(e)}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_patents.py <rsID> [reports_dir]", file=sys.stderr)
        sys.exit(1)

    rsid = sys.argv[1].lower().strip()
    script_dir = Path(__file__).parent
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
    gene_name = variant_info.get("gene_name", "")

    result = fetch_all_patents(rsid, gene_symbol, gene_name)

    # Write output
    output_file = reports_dir / f"{rsid}_patents.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Patent results written to {output_file}")


if __name__ == "__main__":
    main()
