# Analysis Methodology

## How the Context Analyzer Works

The analysis script parses Claude Code JSONL chat history files stored in `~/.claude/projects/`. Each line in these files is a JSON message representing one event in the conversation.

## Message Types

### `user` messages
Messages from the user or tool results. The `message.content` field contains an array of content blocks:
- `text` blocks: User-typed text
- `image` blocks: User-pasted screenshots (base64 encoded)
- `tool_result` blocks: Results from tool executions

### `assistant` messages
Claude's responses. The `message.content` field contains:
- `text` blocks: Claude's text output
- `tool_use` blocks: Tool invocations with input parameters

### `progress` messages
Streaming progress events from hooks and tool execution. These contain a `data` field with progress information.

### `file-history-snapshot` messages
Periodic snapshots of file state. Contain a `snapshot` field.

### `system` messages
System-level messages (session start, configuration).

## Categorization Logic

Each JSONL line is categorized into one of these buckets:

| Category | What it captures |
|----------|-----------------|
| `metadata_overhead` | JSON envelope fields per message (sessionId, uuid, cwd, gitBranch, version, etc.) minus the content |
| `progress_messages` | All messages with `type: "progress"` |
| `user_pasted_images` | `image` blocks in user messages |
| `file_reads` | `tool_result` blocks where the corresponding `tool_use` was a `Read` call |
| `browser_screenshots` | `tool_result` blocks from `mcp__claude-in-chrome__computer` that contain image data |
| `bash_output` | `tool_result` blocks from `Bash` calls |
| `edit_write_input` | `tool_use` and `tool_result` blocks from `Edit` and `Write` calls |
| `grep_glob_output` | `tool_result` blocks from `Grep` and `Glob` calls |
| `task_subagent` | `tool_result` blocks from `Task` calls |
| `web_content` | `tool_result` blocks from `WebSearch` and `WebFetch` calls |
| `browser_other` | Non-screenshot results from Claude-in-Chrome tools |
| `plan_mode` | `EnterPlanMode` and `ExitPlanMode` tool blocks |
| `assistant_text` | `text` blocks in assistant messages |
| `other` | Everything else (system messages, snapshots, user text, unrecognized) |

## File Re-Read Tracking

The script matches `tool_use` blocks with `name: "Read"` to their corresponding `tool_result` blocks using the `tool_use_id` field. This allows tracking:
- Which files were read and how many times
- The total bytes returned per file across all sessions
- Average bytes per read

## Project Path Detection

Claude Code stores history in `~/.claude/projects/` using an encoded path format. The current working directory `/Users/name/code/project` becomes the folder name `-Users-name-code-project` (slashes replaced with dashes).

The `--json` output flag produces machine-readable output for integration with other tools.
