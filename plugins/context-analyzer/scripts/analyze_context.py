#!/usr/bin/env python3
"""
Claude Code Context Analyzer

Analyzes Claude Code chat history JSONL files to identify what's consuming
context window space, finds optimization opportunities, and produces
actionable recommendations.

Usage:
    python3 analyze_context.py [project_dir_path]

If no path is provided, auto-detects from the current working directory
by converting it to the ~/.claude/projects/ folder naming convention.
"""

import json
import os
import sys
import glob
import collections
from pathlib import Path


def find_project_history_dir(cwd=None):
    """Find the Claude Code project history directory for the given working directory."""
    if cwd is None:
        cwd = os.getcwd()

    claude_projects = os.path.expanduser("~/.claude/projects")
    if not os.path.isdir(claude_projects):
        return None

    # Claude Code encodes the project path by replacing / with -
    # e.g., /Users/johndamask/code/rockysurf -> -Users-johndamask-code-rockysurf
    encoded = cwd.replace("/", "-")

    candidate = os.path.join(claude_projects, encoded)
    if os.path.isdir(candidate):
        return candidate

    # Try partial matching (in case cwd has trailing slash variations)
    for entry in os.listdir(claude_projects):
        entry_path = os.path.join(claude_projects, entry)
        if os.path.isdir(entry_path) and encoded in entry:
            return entry_path

    return None


def analyze_sessions(project_dir):
    """Analyze all JSONL session files in the project directory."""
    jsonl_files = sorted(glob.glob(os.path.join(project_dir, "*.jsonl")))
    if not jsonl_files:
        return None

    # ── Aggregate counters ──────────────────────────────────────────────
    grand_totals = {
        "user_pasted_images": 0,
        "browser_screenshots": 0,
        "progress_messages": 0,
        "metadata_overhead": 0,
        "file_reads": 0,
        "bash_output": 0,
        "assistant_text": 0,
        "edit_write_input": 0,
        "grep_glob_output": 0,
        "task_subagent": 0,
        "web_content": 0,
        "browser_other": 0,
        "plan_mode": 0,
        "other": 0,
    }

    file_read_bytes = collections.Counter()
    file_read_counts = collections.Counter()
    tool_call_counts = collections.Counter()
    tool_call_sizes = collections.Counter()
    total_user_images = 0
    total_browser_screenshots = 0
    sessions_with_images = 0
    file_read_count_all = 0
    session_stats = []

    for fpath in jsonl_files:
        sid = os.path.basename(fpath).replace(".jsonl", "")[:8]
        fsize = os.path.getsize(fpath)
        msg_count = 0
        has_user_images = False
        session_images = 0
        session_image_bytes = 0
        pending_tools = {}

        with open(fpath) as f:
            for line in f:
                msg_count += 1
                line_size = len(line)
                try:
                    msg = json.loads(line)
                    msg_type = msg.get("type", "")

                    if msg_type == "progress":
                        grand_totals["progress_messages"] += line_size
                        continue
                    if msg_type in ("file-history-snapshot", "queue-operation", "system"):
                        grand_totals["other"] += line_size
                        continue

                    message = msg.get("message", {})
                    role = message.get("role", "")
                    content = message.get("content", "")

                    # Metadata overhead
                    content_json = json.dumps(content) if content else ""
                    grand_totals["metadata_overhead"] += line_size - len(content_json)

                    if not isinstance(content, list):
                        if role == "assistant":
                            grand_totals["assistant_text"] += len(content_json)
                        continue

                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        btype = block.get("type", "")
                        bsize = len(json.dumps(block))

                        # User-pasted images
                        if btype == "image" and role == "user":
                            grand_totals["user_pasted_images"] += bsize
                            total_user_images += 1
                            has_user_images = True
                            session_images += 1
                            session_image_bytes += bsize
                            continue

                        # Assistant text
                        if btype == "text" and role == "assistant":
                            grand_totals["assistant_text"] += bsize
                            continue

                        # User text
                        if btype == "text" and role == "user":
                            grand_totals["other"] += bsize
                            continue

                        # Tool calls
                        if btype == "tool_use":
                            name = block.get("name", "unknown")
                            tid = block.get("id", "")
                            pending_tools[tid] = name
                            tool_call_counts[name] += 1
                            tool_call_sizes[name] += bsize

                            inp = block.get("input", {})
                            if name == "Read" and "file_path" in inp:
                                file_read_counts[inp["file_path"]] += 1

                            if name in ("Edit", "Write"):
                                grand_totals["edit_write_input"] += bsize
                            elif name == "ExitPlanMode":
                                grand_totals["plan_mode"] += bsize
                            else:
                                grand_totals["other"] += bsize
                            continue

                        # Tool results
                        if btype == "tool_result":
                            tid = block.get("tool_use_id", "")
                            tool_name = pending_tools.get(tid, "unknown")
                            inner = block.get("content", "")

                            # Calculate result size
                            result_text_size = 0
                            has_image = False
                            if isinstance(inner, list):
                                for item in inner:
                                    if isinstance(item, dict):
                                        if item.get("type") == "image":
                                            has_image = True
                                            result_text_size += len(json.dumps(item))
                                        elif item.get("type") == "text":
                                            result_text_size += len(item.get("text", ""))
                            elif isinstance(inner, str):
                                result_text_size = len(inner)

                            if tool_name == "Read":
                                grand_totals["file_reads"] += bsize
                                file_read_count_all += 1
                                # Track bytes per file
                                for ftid, fname in pending_tools.items():
                                    if ftid == tid and fname == "Read":
                                        pass  # already counted above
                                file_read_bytes[
                                    next(
                                        (
                                            k
                                            for k in file_read_counts
                                            if file_read_counts[k] > 0
                                        ),
                                        "unknown",
                                    )
                                ] += result_text_size
                            elif tool_name == "Bash":
                                grand_totals["bash_output"] += bsize
                            elif tool_name in ("Grep", "Glob"):
                                grand_totals["grep_glob_output"] += bsize
                            elif tool_name in ("Edit", "Write"):
                                grand_totals["edit_write_input"] += bsize
                            elif tool_name == "Task":
                                grand_totals["task_subagent"] += bsize
                            elif tool_name in ("WebSearch", "WebFetch"):
                                grand_totals["web_content"] += bsize
                            elif tool_name == "mcp__claude-in-chrome__computer":
                                if has_image:
                                    grand_totals["browser_screenshots"] += bsize
                                    total_browser_screenshots += 1
                                    session_images += 1
                                    session_image_bytes += bsize
                                else:
                                    grand_totals["browser_other"] += bsize
                            elif "mcp__claude-in-chrome" in tool_name:
                                grand_totals["browser_other"] += bsize
                            elif tool_name in ("EnterPlanMode", "ExitPlanMode"):
                                grand_totals["plan_mode"] += bsize
                            else:
                                grand_totals["other"] += bsize
                            continue

                        grand_totals["other"] += bsize

                except (json.JSONDecodeError, KeyError, TypeError):
                    grand_totals["other"] += line_size

        if has_user_images:
            sessions_with_images += 1

        session_stats.append(
            {
                "id": sid,
                "size": fsize,
                "msgs": msg_count,
                "images": session_images,
                "image_bytes": session_image_bytes,
            }
        )

    # ── Track file read bytes more accurately ───────────────────────────
    # Re-scan for precise per-file byte tracking
    file_read_bytes_precise = collections.Counter()
    for fpath in jsonl_files:
        pending = {}
        with open(fpath) as f:
            for line in f:
                try:
                    msg = json.loads(line)
                    message = msg.get("message", {})
                    content = message.get("content", "")
                    if not isinstance(content, list):
                        continue
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        btype = block.get("type", "")
                        if btype == "tool_use":
                            name = block.get("name", "")
                            tid = block.get("id", "")
                            inp = block.get("input", {})
                            if name == "Read" and "file_path" in inp:
                                pending[tid] = inp["file_path"]
                        elif btype == "tool_result":
                            tid = block.get("tool_use_id", "")
                            if tid in pending:
                                fp = pending[tid]
                                inner = block.get("content", "")
                                sz = 0
                                if isinstance(inner, list):
                                    for item in inner:
                                        if isinstance(item, dict) and item.get("type") == "text":
                                            sz += len(item.get("text", ""))
                                elif isinstance(inner, str):
                                    sz = len(inner)
                                file_read_bytes_precise[fp] += sz
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass

    return {
        "project_dir": project_dir,
        "session_count": len(jsonl_files),
        "total_size": sum(s["size"] for s in session_stats),
        "grand_totals": grand_totals,
        "file_read_counts": file_read_counts,
        "file_read_bytes": file_read_bytes_precise,
        "tool_call_counts": tool_call_counts,
        "tool_call_sizes": tool_call_sizes,
        "total_user_images": total_user_images,
        "total_browser_screenshots": total_browser_screenshots,
        "sessions_with_images": sessions_with_images,
        "file_read_count_all": file_read_count_all,
        "session_stats": session_stats,
    }


def format_size(bytes_val):
    """Format bytes into human-readable size."""
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / 1024 / 1024:.1f} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val / 1024:.0f} KB"
    return f"{bytes_val} B"


def format_report(results):
    """Format analysis results as a markdown report."""
    gt = results["grand_totals"]
    total_analyzed = sum(gt.values())
    lines = []

    lines.append("# Context Window Analysis Report")
    lines.append("")
    lines.append(f"**Sessions analyzed:** {results['session_count']}")
    lines.append(f"**Total history size:** {format_size(results['total_size'])}")
    lines.append(
        f"**Average session size:** {format_size(results['total_size'] // max(results['session_count'], 1))}"
    )
    lines.append("")

    # ── Consumption breakdown ───────────────────────────────────────────
    lines.append("## Context Consumption Breakdown")
    lines.append("")
    lines.append("| Rank | Category | Size | % of Total |")
    lines.append("|------|----------|------|------------|")
    ranked = sorted(gt.items(), key=lambda x: x[1], reverse=True)
    for i, (category, size) in enumerate(ranked, 1):
        pct = size * 100 / total_analyzed if total_analyzed > 0 else 0
        label = category.replace("_", " ").title()
        lines.append(f"| {i} | {label} | {format_size(size)} | {pct:.1f}% |")
    lines.append("")

    # ── Key metrics ─────────────────────────────────────────────────────
    lines.append("## Key Metrics")
    lines.append("")
    lines.append(
        f"- **User-pasted images:** {results['total_user_images']} images across {results['sessions_with_images']} sessions ({format_size(gt['user_pasted_images'])})"
    )
    lines.append(
        f"- **Browser screenshots:** {results['total_browser_screenshots']} screenshots ({format_size(gt['browser_screenshots'])})"
    )
    lines.append(
        f"- **File read operations:** {results['file_read_count_all']} total reads ({format_size(gt['file_reads'])})"
    )
    lines.append("")

    # ── Most re-read files ──────────────────────────────────────────────
    lines.append("## Most Re-Read Files")
    lines.append("")
    lines.append("| File | Times Read | Total Bytes | Avg per Read |")
    lines.append("|------|-----------|-------------|-------------|")
    frc = results["file_read_counts"]
    frb = results["file_read_bytes"]
    # Sort by total bytes consumed
    top_files = sorted(frb.items(), key=lambda x: x[1], reverse=True)[:20]
    for fp, total_bytes in top_files:
        count = frc.get(fp, 1)
        avg = total_bytes // count if count > 0 else 0
        # Shorten path for display
        short = fp
        home = os.path.expanduser("~")
        if short.startswith(home):
            short = "~" + short[len(home):]
        lines.append(
            f"| `{short}` | {count} | {format_size(total_bytes)} | {format_size(avg)} |"
        )
    lines.append("")

    # ── Tool usage summary ──────────────────────────────────────────────
    lines.append("## Tool Usage Summary")
    lines.append("")
    lines.append("| Tool | Calls | Input Size |")
    lines.append("|------|-------|------------|")
    for tool, count in results["tool_call_counts"].most_common(15):
        size = results["tool_call_sizes"].get(tool, 0)
        lines.append(f"| {tool} | {count} | {format_size(size)} |")
    lines.append("")

    # ── Largest sessions ────────────────────────────────────────────────
    lines.append("## Largest Sessions")
    lines.append("")
    lines.append("| Session | Size | Messages | Images |")
    lines.append("|---------|------|----------|--------|")
    top_sessions = sorted(
        results["session_stats"], key=lambda x: x["size"], reverse=True
    )[:10]
    for s in top_sessions:
        lines.append(
            f"| {s['id']}... | {format_size(s['size'])} | {s['msgs']} | {s['images']} |"
        )
    lines.append("")

    # ── Recommendations ─────────────────────────────────────────────────
    lines.append("## Recommendations")
    lines.append("")
    recs = generate_recommendations(results)
    for i, rec in enumerate(recs, 1):
        lines.append(f"{i}. **{rec['title']}** — {rec['detail']}")
    lines.append("")

    return "\n".join(lines)


def generate_recommendations(results):
    """Generate actionable recommendations based on analysis."""
    gt = results["grand_totals"]
    total = sum(gt.values())
    recs = []

    # Check user-pasted images
    img_pct = gt["user_pasted_images"] * 100 / total if total > 0 else 0
    if img_pct > 5:
        recs.append(
            {
                "title": "Compress screenshots before pasting",
                "detail": f"User-pasted images consume {format_size(gt['user_pasted_images'])} ({img_pct:.0f}%). "
                f"Resize to ~800px wide JPEG before pasting, or use Claude-in-Chrome's screenshot tool which produces smaller images.",
            }
        )

    # Check file re-reads
    frc = results["file_read_counts"]
    heavily_read = [(f, c) for f, c in frc.most_common(5) if c > 10]
    if heavily_read:
        files_str = ", ".join(f"`{os.path.basename(f)}`" for f, _ in heavily_read[:3])
        recs.append(
            {
                "title": "Add file summaries to CLAUDE.md",
                "detail": f"Files {files_str} are read {heavily_read[0][1]}+ times across sessions. "
                f"Adding structural summaries to CLAUDE.md reduces re-reads.",
            }
        )

    # Check browser screenshots
    ss_pct = gt["browser_screenshots"] * 100 / total if total > 0 else 0
    if results["total_browser_screenshots"] > 20:
        recs.append(
            {
                "title": "Use /compact after browser automation",
                "detail": f"{results['total_browser_screenshots']} browser screenshots consume {format_size(gt['browser_screenshots'])}. "
                f"Run /compact after screenshot-heavy sequences to reclaim context.",
            }
        )

    # Check bash output
    bash_pct = gt["bash_output"] * 100 / total if total > 0 else 0
    if bash_pct > 5:
        recs.append(
            {
                "title": "Reduce verbose Bash output",
                "detail": f"Bash output consumes {format_size(gt['bash_output'])} ({bash_pct:.0f}%). "
                f"Pipe verbose commands through tail/head or redirect to files.",
            }
        )

    # Check for large documentation files being re-read
    for fp, count in frc.most_common(10):
        basename = os.path.basename(fp).lower()
        if basename in ("devlog.md", "changelog.md", "readme.md") and count > 15:
            recs.append(
                {
                    "title": f"Trim or archive {os.path.basename(fp)}",
                    "detail": f"`{os.path.basename(fp)}` is read {count} times. Keep it concise or add to .claudeignore and reference explicitly.",
                }
            )
            break

    # Check subagent usage
    if results["tool_call_counts"].get("Task", 0) > 50:
        task_count = results["tool_call_counts"]["Task"]
        recs.append(
            {
                "title": "Review subagent usage",
                "detail": f"{task_count} subagent invocations detected. Each adds context. Consider consolidating tasks or using more targeted prompts.",
            }
        )

    # Check edit/write volume
    ew_pct = gt["edit_write_input"] * 100 / total if total > 0 else 0
    if ew_pct > 5:
        recs.append(
            {
                "title": "Use targeted edits over full file writes",
                "detail": f"Edit/Write payloads consume {format_size(gt['edit_write_input'])} ({ew_pct:.0f}%). "
                f"Prefer Edit (partial replacement) over Write (full file) when possible.",
            }
        )

    # General recommendation
    avg_session = results["total_size"] // max(results["session_count"], 1)
    if avg_session > 3 * 1024 * 1024:  # >3MB average
        recs.append(
            {
                "title": "Use /compact proactively",
                "detail": f"Average session size is {format_size(avg_session)}. "
                f"Run /compact periodically during long sessions to free context.",
            }
        )

    if not recs:
        recs.append(
            {
                "title": "Context usage looks healthy",
                "detail": "No major optimization opportunities identified. Keep sessions focused and use /compact when needed.",
            }
        )

    return recs


def main():
    """Main entry point."""
    # Determine project history directory
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        project_dir = find_project_history_dir()

    if not project_dir or not os.path.isdir(project_dir):
        print(json.dumps({"error": "Could not find project history directory. "
              "Pass the path explicitly or run from within a Claude Code project directory."}))
        sys.exit(1)

    results = analyze_sessions(project_dir)
    if results is None:
        print(json.dumps({"error": "No JSONL session files found in " + project_dir}))
        sys.exit(1)

    # Output mode: markdown report by default, JSON with --json flag
    if "--json" in sys.argv:
        # Serialize counters for JSON output
        output = {
            "project_dir": results["project_dir"],
            "session_count": results["session_count"],
            "total_size": results["total_size"],
            "grand_totals": results["grand_totals"],
            "file_read_counts": dict(results["file_read_counts"].most_common(25)),
            "file_read_bytes": dict(results["file_read_bytes"].most_common(25)),
            "tool_call_counts": dict(results["tool_call_counts"].most_common(20)),
            "total_user_images": results["total_user_images"],
            "total_browser_screenshots": results["total_browser_screenshots"],
            "sessions_with_images": results["sessions_with_images"],
            "file_read_count_all": results["file_read_count_all"],
            "recommendations": generate_recommendations(results),
            "largest_sessions": sorted(
                results["session_stats"], key=lambda x: x["size"], reverse=True
            )[:10],
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_report(results))


if __name__ == "__main__":
    main()
