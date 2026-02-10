#!/usr/bin/env python3
"""Resolve an rsID to gene and variant information using MyVariant.info API."""


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

MYVARIANT_API = "https://myvariant.info/v1"


def resolve_variant(rsid: str, max_retries: int = 1) -> dict:
    """Query MyVariant.info for variant details given an rsID."""
    rsid = rsid.strip().lower()
    if not rsid.startswith("rs"):
        return {"error": f"Invalid rsID format: {rsid}. Expected format: rs12345"}

    result = {
        "rsid": rsid,
        "gene_symbol": None,
        "gene_name": None,
        "ensembl_gene_id": None,
        "chromosome": None,
        "position": None,
        "alleles": None,
        "consequence": None,
        "clinvar_significance": None,
        "protein_change": None,
        "errors": [],
    }

    for attempt in range(max_retries + 1):
        try:
            # Query by rsID
            resp = requests.get(
                f"{MYVARIANT_API}/query",
                params={
                    "q": rsid,
                    "scopes": "dbsnp.rsid",
                    "fields": (
                        "dbsnp,cadd.gene,clinvar,snpeff,"
                        "dbnsfp.genename,dbnsfp.ensembl.geneid,"
                        "dbnsfp.uniprot"
                    ),
                    "size": 1,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            hits = data.get("hits", [])
            if not hits:
                result["errors"].append(f"No hits found for {rsid}")
                return result

            hit = hits[0]

            # Extract dbSNP info
            dbsnp = hit.get("dbsnp", {})
            result["chromosome"] = dbsnp.get("chrom")
            hg19 = dbsnp.get("hg19", {})
            result["position"] = hg19.get("start") or hg19.get("end")

            # Alleles
            ref = dbsnp.get("ref")
            alt = dbsnp.get("alt")
            if ref and alt:
                result["alleles"] = f"{ref}>{alt}"

            # Gene symbol — try multiple sources
            gene_sym = None
            dbnsfp = hit.get("dbnsfp", {})
            if isinstance(dbnsfp, dict):
                gene_sym = dbnsfp.get("genename")
                if isinstance(gene_sym, list):
                    gene_sym = gene_sym[0]

            if not gene_sym:
                cadd_gene = hit.get("cadd", {}).get("gene", {})
                if isinstance(cadd_gene, dict):
                    gene_sym = cadd_gene.get("genename")
                elif isinstance(cadd_gene, list) and cadd_gene:
                    gene_sym = cadd_gene[0].get("genename")

            if not gene_sym:
                gene_info = dbsnp.get("gene", {})
                if isinstance(gene_info, dict):
                    gene_sym = gene_info.get("symbol")
                elif isinstance(gene_info, list) and gene_info:
                    gene_sym = gene_info[0].get("symbol")

            result["gene_symbol"] = gene_sym

            # Ensembl gene ID
            ensembl = dbnsfp.get("ensembl", {})
            if isinstance(ensembl, dict):
                ens_id = ensembl.get("geneid")
            elif isinstance(ensembl, list) and ensembl:
                ens_id = ensembl[0].get("geneid")
            else:
                ens_id = None
            if isinstance(ens_id, list):
                ens_id = ens_id[0]
            result["ensembl_gene_id"] = ens_id

            # Consequence / functional annotation
            snpeff = hit.get("snpeff", {})
            if isinstance(snpeff, dict):
                ann = snpeff.get("ann", {})
                if isinstance(ann, list) and ann:
                    ann = ann[0]
                if isinstance(ann, dict):
                    result["consequence"] = ann.get("effect")
                    result["protein_change"] = ann.get("hgvs_p")

            # ClinVar significance
            clinvar = hit.get("clinvar", {})
            if isinstance(clinvar, dict):
                rcv = clinvar.get("rcv", {})
                if isinstance(rcv, list) and rcv:
                    rcv = rcv[0]
                if isinstance(rcv, dict):
                    clin_sig = rcv.get("clinical_significance")
                    result["clinvar_significance"] = clin_sig

            # Gene name — try to get full name from a follow-up if we have the symbol
            if gene_sym and not result.get("gene_name"):
                result["gene_name"] = _lookup_gene_name(gene_sym)

            return result

        except requests.RequestException as e:
            if attempt < max_retries:
                time.sleep(5)
                continue
            result["errors"].append(f"API request failed: {str(e)}")
            return result

    return result


def _lookup_gene_name(symbol: str) -> str | None:
    """Try to resolve gene symbol to full name via MyGene.info."""
    try:
        resp = requests.get(
            "https://mygene.info/v3/query",
            params={"q": symbol, "fields": "name", "size": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", [])
        if hits:
            return hits[0].get("name")
    except Exception:
        pass
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: resolve_variant.py <rsID>", file=sys.stderr)
        sys.exit(1)

    rsid = sys.argv[1]
    result = resolve_variant(rsid)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
