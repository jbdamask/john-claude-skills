---
name: docetl-claude
description: Build and run LLM-powered data processing pipelines with DocETL using Claude models. Use when users say "docetl", want to analyze unstructured data, process documents, extract information, or run ETL tasks on text. Helps with data collection, pipeline creation, execution, and optimization. This version uses Anthropic Claude Haiku for all LLM operations.
---

# DocETL Pipeline Development (Claude Edition)

DocETL is a system for creating LLM-powered data processing pipelines. This skill helps you build end-to-end pipelines: from data preparation to execution and optimization. **This version uses Anthropic Claude Haiku models.**

## Workflow Overview: Iterative Data Analysis

Work like a data analyst: **write → run → inspect → iterate**. Never write all scripts at once and run them all at once. Each phase should be completed and validated before moving to the next.

### Phase 1: Data Collection
1. Write data collection script
2. **Run it immediately** (with user permission)
3. **Inspect the dataset** - show total count, keys, sample documents, length distribution
4. Iterate if needed

### Phase 2: Pipeline Development
1. Read sample documents to understand format
2. Write pipeline YAML with `sample: 10-20` for testing
3. **Run the test pipeline**
4. **Inspect intermediate results** - extraction quality, distributions, validation failures
5. Iterate on prompts/schema based on results
6. Remove `sample` and run full pipeline
7. **Show final results**

### Phase 3: Visualization & Presentation
1. Write visualization script based on actual output structure
2. **Run and show the report** to the user
3. Iterate on charts/tables if needed

See [references/visualization.md](references/visualization.md) for detailed styling guidelines.

**Key principle:** The user should see results at every step.

## Required Package

This skill requires the `docetl` Python package.

### Check if DocETL is Available

```bash
which docetl || echo "NOT_FOUND"
```

Also check common venv locations:
```bash
ls ~/.venvs/docetl/bin/docetl 2>/dev/null && echo "EXISTS" || echo "NOT_IN_VENVS"
```

### If Not Installed, Ask User

**Ask:** "The `docetl` package is required but not installed. How would you like to install it?"

**Options:**
- **Specify path** - User provides path to existing venv or installation
- **Create a venv for me** - Look up the venv-manager skill and follow its conventions

If user chooses the convenience option and venv-manager isn't available, offer to create at `~/.venvs/docetl/`.

### Running DocETL Commands

Examples use `<docetl>` as placeholder for the actual path:

```bash
<docetl> run pipeline.yaml
<docetl> build pipeline.yaml --optimizer moar
```

## Step 1: Data Preparation

DocETL datasets must be **JSON arrays** or **CSV files**.

### JSON Format
```json
[
  {"id": 1, "text": "First document content...", "metadata": "value"},
  {"id": 2, "text": "Second document content...", "metadata": "value"}
]
```

### Data Collection Scripts

```python
import json

documents = []
for source in sources:
    documents.append({
        "id": source.id,
        "text": source.content,  # DO NOT truncate text
    })

with open("dataset.json", "w") as f:
    json.dump(documents, f, indent=2)
```

**Important:** Never truncate document text. DocETL operations like `split` handle long documents properly.

### After Running Data Collection

**Always inspect results before proceeding:**

```python
import json
data = json.load(open("dataset.json"))

print(f"Total documents: {len(data)}")
print(f"Keys: {list(data[0].keys())}")
print(f"Avg length: {sum(len(str(d)) for d in data) // len(data)} chars")
print(json.dumps(data[0], indent=2)[:500])
```

## Step 2: Read and Understand the Data

**CRITICAL**: Before writing any prompts, READ the actual input data to understand structure, vocabulary, and edge cases.

```python
import json
with open("dataset.json") as f:
    data = json.load(f)
for doc in data[:5]:
    print(doc)
```

## Step 3: Pipeline Structure

```yaml
default_model: anthropic/claude-haiku-4-5-20251001

system_prompt:
  dataset_description: <describe the data based on what you observed>
  persona: <role for the LLM to adopt>

datasets:
  input_data:
    type: file
    path: "dataset.json"

operations:
  - name: <operation_name>
    type: <operation_type>
    prompt: |
      <Detailed, specific prompt based on the actual data>
    output:
      schema:
        <field_name>: <type>

pipeline:
  steps:
    - name: process
      input: input_data
      operations:
        - <operation_name>
  output:
    type: file
    path: "output.json"
    intermediate_dir: "intermediates"  # ALWAYS set this for debugging
```

### Key Configuration

- **default_model**: Use `anthropic/claude-haiku-4-5-20251001` (fast and cost-effective)
- **intermediate_dir**: Always set to log intermediate results

## Step 4: Writing Effective Prompts

**Prompts must be specific to the data, not generic.**

### Bad (Generic)
```yaml
prompt: |
  Extract key information from this document.
  {{ input.text }}
```

### Good (Specific)
```yaml
prompt: |
  You are analyzing a medical transcript from a doctor-patient visit.

  The transcript follows this format:
  - Doctor statements are prefixed with "DR:"
  - Patient statements are prefixed with "PT:"

  From the following transcript, extract:
  1. All medications mentioned
  2. Dosages if specified
  3. Patient-reported side effects

  Transcript:
  {{ input.transcript }}
```

### Prompt Guidelines

1. **Describe the data format** you observed
2. **Be specific about what to extract**
3. **Mention edge cases** you noticed
4. **Provide examples** if ambiguous
5. **Set expectations** for missing/unclear information

## Step 5: Choosing Operations

Many tasks only need a **single map operation**:

| Task | Recommended Approach |
|------|---------------------|
| Extract info from each doc | Single `map` |
| Multiple extractions | Multiple `map` operations chained |
| Extract then summarize | `map` → `reduce` |
| Filter then process | `filter` → `map` |
| Split long docs | `split` → `map` → `reduce` |
| Deduplicate entities | `map` → `unnest` → `resolve` |

## Operation Types

DocETL provides these operation types:

| Type | Purpose | LLM? |
|------|---------|------|
| `map` | Transform each document | Yes |
| `filter` | Keep/remove documents | Yes |
| `reduce` | Aggregate by key | Yes |
| `resolve` | Deduplicate entities | Yes |
| `split` | Chunk long text | No |
| `unnest` | Flatten lists to rows | No |
| `code_map` | Python transform per doc | No |
| `code_reduce` | Python aggregation | No |
| `code_filter` | Python filtering | No |

**For detailed operation documentation with examples, see [references/operations.md](references/operations.md).**

### Key Points for Common Operations

**Map**: Use `skip_on_error: true` for large-scale runs. Add `validate` rules with `num_retries_on_validate_failure`.

**Reduce**: Always include `fold_prompt` and `fold_batch_size` (use 100+). The fold_prompt must produce clean, standalone output - no "updated" or "added items" language.

**Resolve**: Set `optimize: true` and run `docetl build` to generate blocking rules. Without blocking, this is O(n^2).

## Step 6: Environment Setup

Verify API key exists:

```bash
cat .env
```

Required: `ANTHROPIC_API_KEY=sk-ant-...`

## Step 7: Execution

**Always test on a sample first.**

### Test Run
Add `sample: 10-20` to your first operation:
```bash
<docetl> run pipeline.yaml
```

**Inspect test results:**
```python
import json
from collections import Counter

data = json.load(open("intermediates/step_name/operation_name.json"))
print(f"Processed: {len(data)} docs")

if "domain" in data[0]:
    print("Domain distribution:")
    for k, v in Counter(d["domain"] for d in data).most_common():
        print(f"  {k}: {v}")
```

### Full Run
1. Remove `sample` parameter
2. Ask user for permission (estimate cost)
3. Run: `<docetl> run pipeline.yaml`
4. **Show final results**

## Step 8: Optimization (Optional)

Use MOAR optimizer for cost vs. accuracy tradeoffs:

```yaml
optimizer_config:
  type: moar
  save_dir: ./optimization_results
  available_models:
    - anthropic/claude-haiku-4-5-20251001
    - anthropic/claude-sonnet-4-20250514
  evaluation_file: evaluate.py
  metric_key: score
  max_iterations: 20
  model: anthropic/claude-haiku-4-5-20251001
```

Create `evaluate.py`:
```python
def evaluate(outputs: list[dict]) -> dict:
    correct = sum(1 for o in outputs if is_correct(o))
    return {"score": correct / len(outputs)}
```

Run: `<docetl> build pipeline.yaml --optimizer moar`

## Output Schemas

**Keep schemas minimal** - default to 1-3 fields unless user requests more.

**Nesting limit:** Maximum 2 levels deep.

```yaml
# Good - minimal
output:
  schema:
    summary: string

# Good - 2 levels (list of objects)
output:
  schema:
    items: "list[{name: str, value: int}]"

# Bad - too deep (not supported)
output:
  schema:
    data: "list[{nested: {too: {deep: str}}}]"
```

Supported types: `string`, `int`, `float`, `bool`, `list[type]`, `enum`

## Validation

**Always add validation to LLM operations:**

```yaml
- name: extract_keywords
  type: map
  prompt: |
    Extract 3-5 keywords from: {{ input.text }}
  output:
    schema:
      keywords: list[string]
  validate:
    - len(output["keywords"]) >= 3
    - len(output["keywords"]) <= 5
  num_retries_on_validate_failure: 2
```

Common patterns:
```yaml
- len(output["items"]) >= 1              # List not empty
- output["sentiment"] in ["positive", "negative", "neutral"]  # Enum
- len(output["summary"].strip()) > 0     # String not empty
- output["score"] >= 0 and output["score"] <= 100  # Range
```

## Jinja2 Templating

**Map operations** - use `input`:
```yaml
prompt: |
  Document: {{ input.text }}
  {% if input.metadata %}
  Context: {{ input.metadata }}
  {% endif %}
```

**Reduce operations** - use `inputs` (list):
```yaml
prompt: |
  Summarize these {{ inputs | length }} items:
  {% for item in inputs %}
  - {{ item.summary }}
  {% endfor %}
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Pipeline won't run | Check `.env` has `ANTHROPIC_API_KEY`, verify dataset exists |
| Bad outputs | Read more input data, add `validate` rules, simplify schema |
| High costs | Use `sample: 10` first, run MOAR optimizer |
| Debug issues | Check `intermediate_dir` folder |

## Quick Reference

```bash
<docetl> run pipeline.yaml              # Run pipeline
<docetl> run pipeline.yaml --max_threads 16  # More parallelism
<docetl> build pipeline.yaml --optimizer moar  # Optimize
<docetl> clear-cache                    # Clear LLM cache
<docetl> version                        # Check version
```

**Note:** Replace `<docetl>` with actual path (e.g., `~/.venvs/docetl/bin/docetl`).

## References

- [references/operations.md](references/operations.md) - Detailed operation documentation
- [references/visualization.md](references/visualization.md) - Report styling guidelines
