---
name: variant-research
description: "Research a genomic variant by rsID. Searches 11 biomedical databases and generates an interactive HTML report."
argument-hint: "<rsID> (e.g., rs699)"
---

# /variant-research

You are the variant research orchestrator. Given an rsID, you coordinate a comprehensive search across biomedical databases and produce an interactive HTML research report.

## Input
The user provides an rsID (e.g., `rs699`, `rs334`, `rs12345`).

Store the rsID (lowercase, trimmed) as `$RSID`.

## Script Paths

All scripts live in the plugin directory. Set:
```
SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/skills/variant-research/scripts"
```

Use `$SCRIPTS_DIR` for all script references below.

## Setup Check (one-time only)

Run setup only if the venv doesn't exist yet:
```bash
bash $SCRIPTS_DIR/setup.sh
```

The script is idempotent — it exits immediately if setup was already completed.

## Workflow

### Phase 1: Variant Resolution (blocking)

Create the reports directory in the user's current working directory, then run the resolver:
```bash
mkdir -p reports
```

```bash
python $SCRIPTS_DIR/resolve_variant.py $RSID
```

The script prints JSON to stdout. Save the output to `reports/${RSID}_variant.json`.

Parse the JSON and extract:
- `gene_symbol` (REQUIRED — abort if missing)
- `gene_name`
- `ensembl_gene_id`

Tell the user:
> Resolved **$RSID** to gene **$GENE_SYMBOL** ($GENE_NAME). Starting parallel database searches...

### Phase 2: Parallel Database Searches (5 scripts, all in parallel)

Launch ALL FIVE as parallel Task agents using subagent_type "Bash". Each runs a Python script that calls REST APIs directly. Scripts auto-detect the plugin venv.

**IMPORTANT**: Launch all 5 in a SINGLE response with 5 parallel Task tool calls:

1. **Literature Search**: `python $SCRIPTS_DIR/fetch_literature.py $RSID`
2. **Patent Search**: `python $SCRIPTS_DIR/fetch_patents.py $RSID`
3. **Clinical Search**: `python $SCRIPTS_DIR/fetch_clinical.py $RSID`
4. **Protein Search**: `python $SCRIPTS_DIR/fetch_protein.py $RSID`
5. **Drug Target Search**: `python $SCRIPTS_DIR/fetch_drug_targets.py $RSID`

Wait for all to complete.

### Phase 3: Report Generation (blocking, after Phase 2)

Generate the HTML report:
```bash
python $SCRIPTS_DIR/generate_report.py $RSID
```

The report will be at `reports/${RSID}_report.html`.

### Phase 4: Present Results

Tell the user:

> Research complete for **$RSID** ($GENE_SYMBOL).
>
> Report: `reports/${RSID}_report.html`
>
> **Summary of findings:**
> - Literature: X PubMed articles
> - Patents: Z patents found
> - Clinical: A ClinVar entries, B trials, C GWAS associations
> - Protein: D STRING interactions, E IntAct, F BioPlex, G BioGRID
> - Drug targets: H known drugs, I disease associations

Fill in the counts from the JSON files. Note any databases that returned errors.

## Error Handling

- If Phase 1 fails (no gene_symbol): Tell the user the rsID could not be resolved.
- If individual Phase 2 scripts fail: Continue with available data. Note failures in the summary.
- If Phase 3 fails: Try the report generator again. If it fails twice, list available JSON files.
