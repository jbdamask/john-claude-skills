#!/usr/bin/env python3
"""Generate an HTML research report from JSON result files."""


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
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def load_json_file(filepath: str) -> dict:
    """Load a JSON file, returning empty dict with error info if missing/invalid."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"_unavailable": True, "errors": [f"File not found: {filepath}"]}
    except json.JSONDecodeError as e:
        return {"_unavailable": True, "errors": [f"Invalid JSON in {filepath}: {str(e)}"]}


def generate_report(rsid: str, reports_dir: str, template_dir: str, output_path: str = None) -> str:
    """Generate HTML report from JSON result files."""
    rsid = rsid.lower().strip()
    reports_dir = Path(reports_dir)

    # Load all result files
    variant_info = load_json_file(reports_dir / f"{rsid}_variant.json")
    literature = load_json_file(reports_dir / f"{rsid}_literature.json")
    patents = load_json_file(reports_dir / f"{rsid}_patents.json")
    clinical = load_json_file(reports_dir / f"{rsid}_clinical.json")
    protein = load_json_file(reports_dir / f"{rsid}_protein.json")
    drug_targets = load_json_file(reports_dir / f"{rsid}_drug_targets.json")

    # Build competitive intelligence from patents + clinical trials
    competitive_intel = _build_competitive_intel(patents, clinical)

    # Collect all references
    references = _collect_references(literature, patents, clinical, protein, drug_targets)

    # Prepare template context
    context = {
        "rsid": rsid,
        "gene_symbol": variant_info.get("gene_symbol", "Unknown"),
        "gene_name": variant_info.get("gene_name", ""),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "variant_info": variant_info,
        "literature": literature,
        "patents": patents,
        "clinical": clinical,
        "protein": protein,
        "drug_targets": drug_targets,
        "competitive_intel": competitive_intel,
        "references": references,
    }

    # Render template
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True,
    )
    template = env.get_template("report_template.html")
    html = template.render(**context)

    # Write output
    if output_path is None:
        output_path = str(reports_dir / f"{rsid}_report.html")

    with open(output_path, "w") as f:
        f.write(html)

    return output_path


def _build_competitive_intel(patents: dict, clinical: dict) -> dict:
    """Extract competitive intelligence from patent and clinical trial data."""
    companies = {}

    # From patents
    for patent in patents.get("patents", []):
        assignee = patent.get("assignee", "Unknown")
        if assignee not in companies:
            companies[assignee] = {"patents": [], "trials": []}
        companies[assignee]["patents"].append({
            "title": patent.get("title", ""),
            "date": patent.get("date", ""),
            "patent_number": patent.get("patent_number", ""),
        })

    # From clinical trials
    for trial in clinical.get("clinical_trials", []):
        sponsor = trial.get("sponsor", "Unknown")
        if sponsor not in companies:
            companies[sponsor] = {"patents": [], "trials": []}
        companies[sponsor]["trials"].append({
            "title": trial.get("title", ""),
            "phase": trial.get("phase", ""),
            "status": trial.get("status", ""),
            "nct_id": trial.get("nct_id", ""),
        })

    return {"companies": companies}


def _collect_references(literature: dict, patents: dict, clinical: dict,
                        protein: dict, drug_targets: dict) -> list:
    """Collect all references from all data sources."""
    refs = []
    seen_ids = set()

    # From literature
    for article in literature.get("pubmed_articles", []):
        pmid = article.get("pmid", "")
        if pmid and pmid not in seen_ids:
            seen_ids.add(pmid)
            refs.append({
                "source": "PubMed",
                "id": pmid,
                "title": article.get("title", ""),
                "authors": article.get("authors", ""),
                "journal": article.get("journal", ""),
                "year": article.get("year", ""),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })

    for article in literature.get("scholar_articles", []):
        title = article.get("title", "")
        url = article.get("url", "")
        key = url or title
        if key and key not in seen_ids:
            seen_ids.add(key)
            refs.append({
                "source": "Google Scholar",
                "id": "",
                "title": title,
                "authors": article.get("authors", ""),
                "journal": "",
                "year": article.get("year", ""),
                "url": url,
            })

    # From protein interactions (PubMed IDs)
    for db_name in ["intact", "biogrid"]:
        db_data = protein.get(db_name, {})
        for interaction in db_data.get("interactions", []):
            pmid = str(interaction.get("publication", interaction.get("pubmed_id", "")))
            if pmid and pmid not in seen_ids:
                seen_ids.add(pmid)
                refs.append({
                    "source": db_name.capitalize(),
                    "id": pmid,
                    "title": "",
                    "authors": "",
                    "journal": "",
                    "year": "",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                })

    return refs


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <rsID> [reports_dir]", file=sys.stderr)
        sys.exit(1)

    rsid = sys.argv[1]
    script_dir = Path(__file__).parent
    reports_dir = sys.argv[2] if len(sys.argv) > 2 else str(Path.cwd() / "reports")
    template_dir = str(script_dir.parent / "templates")

    output_path = generate_report(rsid, reports_dir, template_dir)
    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
