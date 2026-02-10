---
name: variant-research
description: Performs comprehensive genomic variant research given an rsID. Resolves the variant to its gene, searches biomedical databases, and generates an interactive HTML report. Use when researching a genetic variant, gene drug target, or biomarker.
---

# Variant Research

Searches 11 biomedical databases for a given rsID and generates an interactive HTML report.

## Databases Searched
- **Literature**: PubMed (NCBI E-utilities)
- **Patents**: PatentsView (requires PATENTSVIEW_API_KEY)
- **Clinical**: ClinVar, ClinicalTrials.gov, GWAS Catalog
- **Protein**: STRING-db, Human Protein Atlas, IntAct, BioPlex, BioGRID
- **Drug Targets**: Open Targets Platform

## Report Sections
1. Variant Summary
2. Clinical Significance
3. GWAS Associations
4. Literature Review
5. Patent Landscape
6. Protein Interactions
7. Drug Target Analysis
8. Competitive Intelligence
9. References

## Setup
The `/variant-research` command automatically runs setup on first use. The setup script creates a Python venv inside the plugin's own directory and installs dependencies (requests, jinja2). This only happens once.

## Optional API Keys
- `NCBI_API_KEY` — increases PubMed rate limit (3/s to 10/s)
- `PATENTSVIEW_API_KEY` — required for patent search (free at patentsview.org/apis/keyrequest)
- `BIOGRID_API_KEY` — required for BioGRID (free at thebiogrid.org)
