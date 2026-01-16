# DocETL Operation Reference

Detailed documentation for all DocETL operations.

## Table of Contents
- [Map Operation](#map-operation)
- [Filter Operation](#filter-operation)
- [Reduce Operation](#reduce-operation)
- [Split Operation](#split-operation)
- [Unnest Operation](#unnest-operation)
- [Resolve Operation](#resolve-operation)
- [Code Operations](#code-operations)
- [Retrievers (LanceDB)](#retrievers-lancedb)

## Map Operation

Applies an LLM transformation to each document independently.

```yaml
- name: extract_info
  type: map
  prompt: |
    Analyze this document:
    {{ input.text }}

    Extract the main topic and 3 key points.
  output:
    schema:
      topic: string
      key_points: list[string]
  model: anthropic/claude-haiku-4-5-20251001  # optional, uses default_model if not set
  skip_on_error: true  # recommended for large-scale runs
  validate:  # optional
    - len(output["key_points"]) == 3
  num_retries_on_validate_failure: 2  # optional
```

**Key parameters:**
- `prompt`: Jinja2 template, use `{{ input.field }}` to reference fields
- `output.schema`: Define output structure
- `skip_on_error`: Set `true` to continue on LLM errors (recommended at scale)
- `validate`: Python expressions to validate output
- `sample`: Process only N documents (for testing)
- `limit`: Stop after producing N outputs

## Filter Operation

Keeps or removes documents based on LLM criteria. Output schema must have exactly one boolean field.

```yaml
- name: filter_relevant
  type: filter
  skip_on_error: true
  prompt: |
    Document: {{ input.text }}

    Is this document relevant to climate change?
    Respond true or false.
  output:
    schema:
      is_relevant: boolean
```

## Reduce Operation

Aggregates documents by a key using an LLM.

**Always include `fold_prompt` and `fold_batch_size`** for reduce operations. This handles cases where the group is too large to fit in context.

```yaml
- name: summarize_by_category
  type: reduce
  reduce_key: category  # use "_all" to aggregate everything
  skip_on_error: true
  prompt: |
    Summarize these {{ inputs | length }} items for category "{{ inputs[0].category }}":

    {% for item in inputs %}
    - {{ item.title }}: {{ item.description }}
    {% endfor %}

    Provide a 2-3 sentence summary of the key themes.
  fold_prompt: |
    You have a summary based on previous items, and new items to incorporate.

    Previous summary (based on {{ output.item_count }} items):
    {{ output.summary }}

    New items ({{ inputs | length }} more):
    {% for item in inputs %}
    - {{ item.title }}: {{ item.description }}
    {% endfor %}

    Write a NEW summary that covers ALL items (previous + new).

    IMPORTANT: Output a clean, standalone summary as if describing the entire dataset.
    Do NOT mention "updated", "added", "new items", or reference the incremental process.
  fold_batch_size: 100
  output:
    schema:
      summary: string
      item_count: int
  validate:
    - len(output["summary"].strip()) > 0
  num_retries_on_validate_failure: 2
```

### Writing Good Fold Prompts

The `fold_prompt` is called repeatedly as batches are processed. Its output must:
1. **Reflect ALL data seen so far**, not just the latest batch
2. **Be a clean, standalone output** - no "updated X" or "added Y items" language
3. **Match the same schema** as the initial `prompt` output

Bad fold_prompt output: "Added 50 new projects. The updated summary now includes..."
Good fold_prompt output: "Developers are building privacy-focused tools and local-first apps..."

### Estimating fold_batch_size

- **Use 100+ for most cases** - larger batches = fewer LLM calls = lower cost
- For very long documents, reduce to 50-75
- For short documents (tweets, titles), can use 150-200
- Claude Haiku has 200k context, so batch size is rarely the bottleneck

**Key parameters:**
- `reduce_key`: Field to group by (or list of fields, or `_all`)
- `fold_prompt`: Template for incrementally adding items to existing output (required)
- `fold_batch_size`: Number of items per fold iteration (required, use 100+)
- `associative`: Set to `false` if order matters

## Split Operation

Divides long text into smaller chunks. No LLM call.

```yaml
- name: split_document
  type: split
  split_key: content
  method: token_count  # or "delimiter"
  method_kwargs:
    num_tokens: 500
    model: anthropic/claude-haiku-4-5-20251001
```

**Output adds:**
- `{split_key}_chunk`: The chunk content
- `{op_name}_id`: Original document ID
- `{op_name}_chunk_num`: Chunk number

## Unnest Operation

Flattens list fields into separate rows. No LLM call.

```yaml
- name: unnest_items
  type: unnest
  unnest_key: items  # field containing the list
  keep_empty: false  # optional
```

**Example:** If a document has `items: ["a", "b", "c"]`, unnest creates 3 documents, each with `items: "a"`, `items: "b"`, `items: "c"`.

## Resolve Operation

Deduplicates and canonicalizes entities. Uses pairwise comparison.

```yaml
- name: dedupe_names
  type: resolve
  optimize: true  # let optimizer find blocking rules
  skip_on_error: true
  comparison_prompt: |
    Are these the same person?

    Person 1: {{ input1.name }} ({{ input1.email }})
    Person 2: {{ input2.name }} ({{ input2.email }})

    Respond true or false.
  resolution_prompt: |
    Standardize this person's name:

    {% for entry in inputs %}
    - {{ entry.name }}
    {% endfor %}

    Return the canonical name.
  output:
    schema:
      name: string
```

**Important:** Set `optimize: true` and run `docetl build` to generate efficient blocking rules. Without blocking, this is O(n^2).

## Code Operations

Deterministic Python transformations without LLM calls.

### code_map

```yaml
- name: compute_stats
  type: code_map
  code: |
    def transform(doc) -> dict:
        return {
            "word_count": len(doc["text"].split()),
            "char_count": len(doc["text"])
        }
```

### code_reduce

```yaml
- name: aggregate
  type: code_reduce
  reduce_key: category
  code: |
    def transform(items) -> dict:
        total = sum(item["value"] for item in items)
        return {"total": total, "count": len(items)}
```

### code_filter

```yaml
- name: filter_long
  type: code_filter
  code: |
    def transform(doc) -> bool:
        return len(doc["text"]) > 100

```

## Retrievers (LanceDB)

> **Note:** Only use if user explicitly requests cross-document retrieval, RAG, or similarity search. Retrievers require embedding model API access which may not be available in all environments.

Augment LLM operations with retrieved context from a LanceDB index. Useful for:
- Finding related documents to compare against
- Providing additional context for extraction/classification
- Cross-referencing facts across a dataset

### Define a Retriever

```yaml
retrievers:
  facts_index:
    type: lancedb
    dataset: extracted_facts  # dataset to index
    index_dir: workloads/wiki/lance_index
    build_index: if_missing  # if_missing | always | never
    index_types: ["fts", "embedding"]  # or "hybrid"
    fts:
      index_phrase: "{{ input.fact }}: {{ input.source }}"
      query_phrase: "{{ input.fact }}"
    embedding:
      model: voyage-3  # or other embedding model
      index_phrase: "{{ input.fact }}"
      query_phrase: "{{ input.fact }}"
    query:
      mode: hybrid
      top_k: 5
```

### Use in Operations

```yaml
- name: find_conflicts
  type: map
  retriever: facts_index
  prompt: |
    Check if this fact conflicts with any retrieved facts:

    Current fact: {{ input.fact }} (from {{ input.source }})

    Related facts from other articles:
    {{ retrieval_context }}

    Return whether there's a genuine conflict.
  output:
    schema:
      has_conflict: boolean
```

### Key Points

- `{{ retrieval_context }}` is injected into prompts automatically
- Index is built on first use (when `build_index: if_missing`)
- Supports full-text (`fts`), vector (`embedding`), or `hybrid` search
- Use `save_retriever_output: true` to debug what was retrieved
- **Can index intermediate outputs**: Retriever can index the output of a previous pipeline step
