---
name: cost-tracking
description: Track API token costs for specific operations in Claude Code. Use when the user invokes /cost-tracking to start measuring costs, or says "stop tracking", "stop cost tracking", or "how much did that cost" to stop and calculate. Tracks input, output, and cache tokens per API call and calculates USD cost using current Anthropic pricing.
---

# Cost Tracking

Track the exact token cost of any Claude Code operation by marking a start and stop point in the session JSONL.

## Start Tracking

When the user invokes `/cost-tracking`:

1. Determine the current session JSONL path. It lives at:
   ```
   ~/.claude/projects/<project-hash>/<session-id>.jsonl
   ```
   Find the project directory by looking for the most recently modified `.jsonl` file under `~/.claude/projects/`. The project hash is a mangled version of the working directory path (slashes replaced with dashes, e.g., `-Users-johndamask-myproject`).

2. Determine the cost tracking output directory:
   ```
   ~/.claude/projects/<project-hash>/cost-tracking/
   ```

3. Run the start script:
   ```bash
   python3 <skill-dir>/scripts/start_tracking.py <session_jsonl_path> <cost_tracking_dir>
   ```

4. Store the returned `tracking_id` — mention it to the user and remember it for the stop step.

5. Confirm: "Cost tracking started. I'll calculate costs when you say 'stop tracking'."

## Stop Tracking

When the user says "stop tracking", "stop cost tracking", or asks about the cost:

1. Run the stop script with the tracking_id from the start step:
   ```bash
   python3 <skill-dir>/scripts/stop_tracking.py <tracking_id> <cost_tracking_dir>
   ```

2. The script outputs a formatted cost report and writes:
   - `tokens.jsonl` — per-entry token log with timestamp, model, input_tokens, output_tokens
   - `summary.json` — aggregated cost breakdown by model

3. Present the report to the user.

## Pricing

The stop script fetches pricing **live** from Anthropic's published page
(`https://platform.claude.com/docs/en/about-claude/pricing.md`) at run time — it parses the
"Model pricing" table, maps the session's model id (e.g. `claude-opus-4-8`) to the matching
row, and caches the result for 24h in `scripts/.pricing_cache.json`. It distinguishes
5-minute vs 1-hour cache writes via the `cache_creation.ephemeral_*` fields, and picks the
correct row when a model has date-scoped pricing (e.g. Sonnet 5's introductory rate).

`resources/pricing.json` is now only an **offline fallback**, used if both the live fetch
and the cache are unavailable. If neither the page, the cache, nor the fallback can price a
model, the script reports an **error** for it — it never silently substitutes another
model's rate (the failure mode that once 3×-overcharged an Opus 4.8 run at legacy Opus
rates). Keep `resources/pricing.json` reasonably current as a backstop, but the live page
is the source of truth.
