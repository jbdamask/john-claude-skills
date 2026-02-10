#!/usr/bin/env python3
"""Fetch drug target data from Open Targets Platform via GraphQL API.

Produces reports/{rsid}_drug_targets.json with target_info, known_drugs,
disease_associations, and tractability.
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
import sys
from pathlib import Path

import requests

OT_GRAPHQL = "https://api.platform.opentargets.org/api/v4/graphql"


def _graphql_query(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query against Open Targets."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(OT_GRAPHQL, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def fetch_target_info(ensembl_gene_id: str) -> dict:
    """Fetch target information including description and protein class."""
    query = """
    query TargetInfo($ensemblId: String!) {
      target(ensemblId: $ensemblId) {
        id
        approvedSymbol
        approvedName
        biotype
        functionDescriptions
        proteinIds {
          id
          source
        }
        targetClass {
          id
          label
        }
        tractability {
          label
          modality
          value
        }
      }
    }
    """
    data = _graphql_query(query, {"ensemblId": ensembl_gene_id})
    return data.get("data", {}).get("target", {})


def fetch_known_drugs(ensembl_gene_id: str) -> list[dict]:
    """Fetch known drugs targeting this gene."""
    query = """
    query KnownDrugs($ensemblId: String!, $size: Int!) {
      target(ensemblId: $ensemblId) {
        knownDrugs(size: $size) {
          uniqueDrugs
          rows {
            drug {
              id
              name
              drugType
              mechanismsOfAction {
                rows {
                  mechanismOfAction
                  targets {
                    approvedSymbol
                  }
                }
              }
              maximumClinicalTrialPhase
              hasBeenWithdrawn
              indications {
                rows {
                  disease {
                    name
                  }
                  maxPhaseForIndication
                }
              }
            }
            disease {
              name
            }
            phase
            status
            urls {
              name
              url
            }
          }
        }
      }
    }
    """
    data = _graphql_query(query, {"ensemblId": ensembl_gene_id, "size": 25})
    target = data.get("data", {}).get("target", {})
    known_drugs = target.get("knownDrugs", {})
    rows = known_drugs.get("rows", [])

    drugs = []
    seen_drugs = set()
    for row in rows:
        drug_data = row.get("drug", {})
        drug_name = drug_data.get("name", "")
        if not drug_name or drug_name in seen_drugs:
            continue
        seen_drugs.add(drug_name)

        # Get mechanism of action
        moa = ""
        moa_data = drug_data.get("mechanismsOfAction", {})
        if isinstance(moa_data, dict):
            moa_rows = moa_data.get("rows", [])
            if moa_rows:
                moa = moa_rows[0].get("mechanismOfAction", "")

        # Get phase
        max_phase = drug_data.get("maximumClinicalTrialPhase")
        phase_str = f"Phase {max_phase}" if max_phase else row.get("phase", "")

        # Get indication
        indication = ""
        disease = row.get("disease", {})
        if disease:
            indication = disease.get("name", "")

        drugs.append({
            "drug_name": drug_name,
            "drug_type": drug_data.get("drugType", ""),
            "mechanism_of_action": moa,
            "phase": str(phase_str),
            "indication": indication,
            "company": "",  # Not directly available from OT API
        })

    return drugs


def fetch_disease_associations(ensembl_gene_id: str) -> list[dict]:
    """Fetch top disease associations for this target."""
    query = """
    query DiseaseAssociations($ensemblId: String!, $size: Int!) {
      target(ensemblId: $ensemblId) {
        associatedDiseases(page: {size: $size, index: 0}) {
          rows {
            disease {
              id
              name
            }
            score
            datasourceScores {
              id
              score
            }
          }
        }
      }
    }
    """
    data = _graphql_query(query, {"ensemblId": ensembl_gene_id, "size": 15})
    target = data.get("data", {}).get("target", {})
    assoc_data = target.get("associatedDiseases", {})
    rows = assoc_data.get("rows", [])

    associations = []
    for row in rows:
        disease = row.get("disease", {})

        # Build data types string from datasource scores
        datasource_scores = row.get("datasourceScores", [])
        data_types = []
        for ds in datasource_scores:
            if ds.get("score", 0) > 0:
                data_types.append(ds.get("id", ""))

        associations.append({
            "disease_name": disease.get("name", ""),
            "overall_score": row.get("score"),
            "data_types": ", ".join(data_types) if data_types else "",
        })

    return associations


def fetch_all_drug_targets(rsid: str, gene_symbol: str, ensembl_gene_id: str) -> dict:
    """Fetch all drug target data for the given gene."""
    result = {
        "rsid": rsid,
        "gene_symbol": gene_symbol,
        "ensembl_gene_id": ensembl_gene_id,
        "target_info": {},
        "known_drugs": [],
        "disease_associations": [],
        "tractability": {},
        "data_sources": {
            "open_targets_url": f"https://platform.opentargets.org/target/{ensembl_gene_id}",
        },
        "errors": [],
    }

    if not ensembl_gene_id:
        result["errors"].append("No ensembl_gene_id available; cannot query Open Targets")
        return result

    # Target info + tractability
    try:
        target = fetch_target_info(ensembl_gene_id)
        if target:
            descriptions = target.get("functionDescriptions", [])
            description = descriptions[0] if descriptions else ""

            protein_class = ""
            target_classes = target.get("targetClass", [])
            if target_classes:
                protein_class = ", ".join(tc.get("label", "") for tc in target_classes)

            result["target_info"] = {
                "description": description,
                "protein_class": protein_class,
            }

            # Parse tractability
            tractability_data = target.get("tractability", [])
            tractability = {"small_molecule": "", "antibody": "", "other_modalities": ""}
            for t in tractability_data:
                modality = t.get("modality", "")
                label = t.get("label", "")
                value = t.get("value", False)
                if value:
                    if modality == "SM":
                        tractability["small_molecule"] += f"{label}; "
                    elif modality == "AB":
                        tractability["antibody"] += f"{label}; "
                    else:
                        tractability["other_modalities"] += f"{label} ({modality}); "
            result["tractability"] = tractability
        else:
            result["errors"].append(f"Target not found in Open Targets for {ensembl_gene_id}")
    except requests.RequestException as e:
        result["errors"].append(f"Open Targets target info failed: {str(e)}")

    # Known drugs
    try:
        result["known_drugs"] = fetch_known_drugs(ensembl_gene_id)
    except requests.RequestException as e:
        result["errors"].append(f"Open Targets drug query failed: {str(e)}")

    # Disease associations
    try:
        result["disease_associations"] = fetch_disease_associations(ensembl_gene_id)
    except requests.RequestException as e:
        result["errors"].append(f"Open Targets disease associations failed: {str(e)}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_drug_targets.py <rsID> [reports_dir]", file=sys.stderr)
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
    ensembl_gene_id = variant_info.get("ensembl_gene_id", "")

    result = fetch_all_drug_targets(rsid, gene_symbol, ensembl_gene_id)

    # Write output
    output_file = reports_dir / f"{rsid}_drug_targets.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Drug target results written to {output_file}")


if __name__ == "__main__":
    main()
