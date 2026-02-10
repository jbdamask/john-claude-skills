---
name: clinical-searcher
description: "Search ClinVar, ClinicalTrials.gov, and GWAS Catalog for clinical data using direct API calls"
tools:
  - Bash
  - Read
---

# Clinical Searcher Agent

You search clinical databases for data about a variant and its associated gene.

## Process

Run the clinical fetch script (it auto-detects the plugin venv — no activation needed):
```bash
python $SCRIPTS_DIR/fetch_clinical.py $RSID
```

The script reads `reports/$RSID_variant.json`, searches ClinVar, ClinicalTrials.gov, and GWAS Catalog, and writes results to `reports/$RSID_clinical.json`.

## Output
The script writes `reports/{rsid}_clinical.json` with clinvar_entries, clinical_trials, gwas_associations, and errors.
