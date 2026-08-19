#!/usr/bin/env bash
# Collect the factual state a handoff document needs. Read-only — touches nothing.
# Usage: scripts/gather.sh
set -uo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT" || exit 1

section() { printf '\n===== %s =====\n' "$1"; }

section ROOT
echo "$ROOT"

section NOW
echo "slug:  $(date +'%Y-%m-%d-%H%M')"
echo "human: $(date +'%Y-%m-%d %H:%M %Z')"
echo "iso:   $(date +'%Y-%m-%dT%H:%M:%S%z')"

section SESSION
# Model, effort, and session identity, read from the harness rather than self-reported.
# Claude Code, Codex CLI, opencode, Amp, and Grok CLI all keep a local session record; this
# resolves whichever one is running, then falls back to inferring it from the most recent
# session that touched this repo.
if ! command -v python3 >/dev/null 2>&1; then
  echo "harness: unknown — python3 unavailable, cannot read session records"
  echo "(self-report model/effort, or write 'unknown')"
else
python3 - "$ROOT" <<'PYEOF'
import glob, json, os, sys, time
from urllib.parse import unquote

REPO = sys.argv[1]


def real(p):
    try:
        return os.path.realpath(p)
    except Exception:
        return p


def within(a, b):
    """True if directory a IS b or sits inside it. Strict on purpose: a session
    opened at $HOME is not a session that touched this repo."""
    if not a or not b:
        return False
    a, b = real(a), real(b)
    return a == b or a.startswith(b + os.sep)


def related(a, b):
    """Looser: either direction. A session launched at the repo's parent and then
    cd'd into it is still plausibly this repo's session."""
    return within(a, b) or within(b, a)


def mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return 0.0


def when(epoch):
    if not epoch:
        return "unknown"
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(epoch))


# ---------------------------------------------------------------- claude code
def claude_transcripts():
    d = os.path.expanduser("~/.claude/projects/" + REPO.replace("/", "-"))
    return sorted(glob.glob(os.path.join(d, "*.jsonl")), key=mtime, reverse=True)


def claude_read(path):
    model = effort = version = None
    try:
        for line in open(path, errors="replace"):
            if '"assistant"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") != "assistant":
                continue
            model = (d.get("message") or {}).get("model") or model
            effort = d.get("effort") or effort
            version = d.get("version") or version
    except OSError:
        return None
    return {
        "harness": "claude-code",
        "version": version,
        "session_id": os.path.basename(path)[: -len(".jsonl")],
        "model": model,
        "effort": effort or os.environ.get("CLAUDE_EFFORT"),
        "cwd": REPO,
        "transcript": path,
        "when": mtime(path),
    }


def pick_claude():
    want = os.environ.get("CLAUDE_CODE_SESSION_ID")
    files = claude_transcripts()
    if want:
        exact = os.path.expanduser(
            "~/.claude/projects/" + REPO.replace("/", "-") + "/" + want + ".jsonl"
        )
        if os.path.isfile(exact):
            return claude_read(exact), "$CLAUDE_CODE_SESSION_ID"
        return None, None
    return (claude_read(files[0]), "newest transcript for this directory") if files else (None, None)


# --------------------------------------------------------------------- codex
def codex_home():
    return os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")


def codex_rollouts(cap=600):
    # ~/.codex/sessions/YYYY/MM/DD/rollout-<iso>-<uuid>.jsonl — not keyed by cwd,
    # so the cwd has to come out of each file's session_meta line.
    files = glob.glob(os.path.join(codex_home(), "sessions", "*", "*", "*", "rollout-*.jsonl"))
    files.sort(key=mtime, reverse=True)
    return files[:cap]


def codex_meta(path):
    try:
        with open(path, errors="replace") as fh:
            first = fh.readline()
    except OSError:
        return None
    try:
        d = json.loads(first)
    except Exception:
        return None
    if d.get("type") != "session_meta":
        return None
    p = d.get("payload") or {}
    bi = p.get("base_instructions")
    prov = (bi.get("provenance") or {}) if isinstance(bi, dict) else {}
    return {
        "session_id": p.get("session_id") or p.get("id"),
        "cwd": p.get("cwd"),
        "version": p.get("cli_version"),
        "originator": p.get("originator"),
        "provider": p.get("model_provider"),
        "model": prov.get("model"),
    }


def codex_read(path):
    m = codex_meta(path)
    if not m:
        return None
    model, effort = m.get("model"), None
    try:
        for line in open(path, errors="replace"):
            if "turn_context" not in line and "collaboration_mode" not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            p = d.get("payload") or {}
            if d.get("type") == "turn_context":
                # last turn wins — the user may have switched model mid-session
                model = p.get("model") or model
                effort = (
                    p.get("reasoning_effort")
                    or p.get("model_reasoning_effort")
                    or p.get("effort")
                    or effort
                )
                cm = p.get("collaboration_mode") or {}
                st = cm.get("settings") or {}
                model = st.get("model") or cm.get("model") or model
                effort = st.get("reasoning_effort") or effort
            elif d.get("type") == "world_state":
                cm = ((p.get("state") or {}).get("collaboration_mode")) or {}
                model = cm.get("model") or model
    except OSError:
        pass
    return {
        "harness": "codex",
        "version": m.get("version"),
        "session_id": m.get("session_id"),
        "model": model,
        "provider": m.get("provider"),
        "effort": effort,
        "cwd": m.get("cwd"),
        "transcript": path,
        "when": mtime(path),
    }


def pick_codex():
    want = os.environ.get("CODEX_SESSION_ID") or os.environ.get("CODEX_THREAD_ID")
    files = codex_rollouts()
    if want:
        for f in files:
            if want in os.path.basename(f):
                return codex_read(f), "$CODEX_SESSION_ID/$CODEX_THREAD_ID"
    for f in files:
        m = codex_meta(f)
        if m and within(m.get("cwd"), REPO):
            return codex_read(f), "newest codex rollout whose cwd matches this repo"
    return None, None


# ------------------------------------------------------------------ opencode
# opencode >= ~1.18 keeps sessions in SQLite (opencode.db); the storage/*.json tree below is
# the legacy layout and is still read as a fallback for older installs.
def opencode_dbs():
    xdg = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    out = []
    for b in (os.path.join(xdg, "opencode"), os.path.expanduser("~/.local/share/opencode"),
              os.path.expanduser("~/.opencode")):
        f = os.path.join(b, "opencode.db")
        if os.path.isfile(f) and f not in out:
            out.append(f)
    return out


def opencode_db_connect(path):
    """Read-only. immutable=1 is the fallback: it ignores the -wal, so it can miss the
    newest rows, but it opens when a plain ro attach cannot build the -shm."""
    try:
        import sqlite3
    except Exception:
        return None
    for uri in ("file:%s?mode=ro" % path, "file:%s?mode=ro&immutable=1" % path):
        try:
            c = sqlite3.connect(uri, uri=True, timeout=2)
            c.execute("select 1 from session limit 1")
            return c
        except Exception:
            continue
    return None


def opencode_db_sessions():
    rows = []
    for db in opencode_dbs():
        c = opencode_db_connect(db)
        if c is None:
            continue
        try:
            for sid, d, title, ver, tu in c.execute(
                "select id, directory, title, version, time_updated from session"
            ):
                rows.append({"db": db, "session_id": sid, "cwd": d, "title": title,
                             "version": ver, "when": (tu or 0) / 1000.0})
        except Exception:
            pass
        finally:
            c.close()
    rows.sort(key=lambda r: r["when"], reverse=True)
    return rows


def opencode_db_read(row):
    r = dict(row)
    r["harness"] = "opencode"
    c = opencode_db_connect(row["db"])
    if c is not None:
        try:
            for (data,) in c.execute(
                "select data from message where session_id=? order by time_created desc limit 60",
                (row["session_id"],),
            ):
                try:
                    d = json.loads(data)
                except Exception:
                    continue
                if d.get("role") != "assistant" or not d.get("modelID"):
                    continue
                r["model"] = d.get("modelID")
                r["provider"] = d.get("providerID")
                r["mode"] = d.get("agent") or d.get("mode")
                r["mode_kind"] = "opencode agent mode"
                break
        except Exception:
            pass
        finally:
            c.close()
    r["transcript"] = "%s  (sqlite; session %s)" % (row["db"], row["session_id"])
    r.setdefault("effort", None)  # opencode records agent mode, not reasoning effort
    return r


def opencode_storages():
    xdg = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    bases, out = [], []
    for b in (os.path.join(xdg, "opencode"), os.path.expanduser("~/.local/share/opencode"),
              os.path.expanduser("~/.opencode")):
        if b not in bases:
            bases.append(b)
    for b in bases:
        cand = os.path.join(b, "storage")
        if os.path.isdir(cand):
            out.append(cand)
        # newer layouts shard storage per project
        out.extend(p for p in sorted(glob.glob(os.path.join(b, "project", "*", "storage")))
                   if os.path.isdir(p))
    return out


def opencode_sessions():
    rows = []
    for st in opencode_storages():
        for f in glob.glob(os.path.join(st, "session", "*", "ses_*.json")):
            try:
                d = json.load(open(f, errors="replace"))
            except Exception:
                continue
            t = d.get("time") or {}
            rows.append({
                "storage": st,
                "session_file": f,
                "session_id": d.get("id"),
                "cwd": d.get("directory"),
                "version": d.get("version"),
                "title": d.get("title"),
                "slug": d.get("slug"),
                "project_id": d.get("projectID"),
                "when": (t.get("updated") or t.get("created") or 0) / 1000.0,
            })
    rows.sort(key=lambda r: r["when"], reverse=True)
    return rows


def opencode_read(row):
    r = dict(row)
    r["harness"] = "opencode"
    msgs = sorted(
        glob.glob(os.path.join(r["storage"], "message", r["session_id"] or "", "msg_*.json")),
        key=mtime, reverse=True,
    )
    for f in msgs:
        try:
            d = json.load(open(f, errors="replace"))
        except Exception:
            continue
        if d.get("role") != "assistant":
            continue
        r["model"] = r.get("model") or d.get("modelID")
        r["provider"] = r.get("provider") or d.get("providerID")
        r["mode"] = r.get("mode") or d.get("agent") or d.get("mode")
        r["mode_kind"] = "opencode agent mode"
        p = d.get("path") or {}
        r["cwd"] = r.get("cwd") or p.get("root") or p.get("cwd")
        if r.get("model"):
            break
    r["transcript"] = os.path.join(r["storage"], "message", r["session_id"] or "")
    r.setdefault("effort", None)  # opencode records agent mode, not reasoning effort
    return r


def opencode_project_cwd(row):
    """Older sessions can carry directory '/' — fall back to the project's worktree."""
    if row.get("cwd") and row["cwd"] != "/":
        return row["cwd"]
    pf = os.path.join(row["storage"], "project", (row.get("project_id") or "") + ".json")
    try:
        return (json.load(open(pf, errors="replace")) or {}).get("worktree") or row.get("cwd")
    except Exception:
        return row.get("cwd")


def pick_opencode():
    for row in opencode_db_sessions():
        if within(row.get("cwd"), REPO):
            return (opencode_db_read(row),
                    "newest opencode session in opencode.db whose directory matches this repo")
    for row in opencode_sessions():
        row["cwd"] = opencode_project_cwd(row)
        if within(row.get("cwd"), REPO):
            return (opencode_read(row),
                    "newest opencode session (legacy json storage) whose directory matches this repo")
    return None, None


# ----------------------------------------------------------------------- amp
def amp_dirs():
    xdg = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    cache = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    data = []
    for b in (os.path.join(xdg, "amp"), os.path.expanduser("~/.local/share/amp"),
              os.environ.get("AMP_HOME") or ""):
        if b and os.path.isdir(b) and b not in data:
            data.append(b)
    return data, os.path.join(cache, "amp")


def amp_trees(d):
    """Workspace roots, recorded as file:// URIs on the thread's initial env."""
    trees = ((d.get("env") or {}).get("initial") or {}).get("trees") or []
    out = []
    for t in trees:
        uri = (t or {}).get("uri") or ""
        if uri.startswith("file://"):
            out.append(uri[len("file://"):])
    return out


def amp_read(path):
    try:
        d = json.load(open(path, errors="replace"))
    except Exception:
        return None
    initial = ((d.get("env") or {}).get("initial")) or {}
    plat = initial.get("platform") or {}
    model = None
    for m in reversed(d.get("messages") or []):
        u = (m or {}).get("usage") or {}
        if u.get("model"):
            model = u["model"]
            break
    if not model:
        for t in initial.get("tags") or []:
            if isinstance(t, str) and t.startswith("model:"):
                model = t.split(":", 1)[1]
                break
    cwds = amp_trees(d)
    return {
        "harness": "amp",
        "version": plat.get("clientVersion"),
        "session_id": d.get("id"),
        "model": model,
        "effort": d.get("agentMode"),
        "effort_kind": "amp agent mode",
        "cwd": cwds[0] if cwds else None,
        "cwds": cwds,
        "title": d.get("title"),
        "transcript": path,
        "when": mtime(path),
    }


def amp_live(thread_id, cache_root):
    """A thread still in flight has no local JSON yet — only a per-thread log."""
    log = os.path.join(cache_root, "logs", "threads", thread_id + ".log")
    if not os.path.isfile(log):
        return None
    mode = title = None
    try:
        for line in open(log, errors="replace"):
            if "agentMode" not in line and "title" not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            mode = d.get("agentMode") or mode
            title = d.get("title") or title
    except OSError:
        pass
    return {
        "harness": "amp",
        "session_id": thread_id,
        "model": None,
        "effort": mode,
        "effort_kind": "amp agent mode",
        "title": title,
        "transcript": log,
        "when": mtime(log),
        "note": "thread JSON not written yet — model unresolved; this log is the only local record",
    }


def pick_amp():
    data_dirs, cache_root = amp_dirs()
    files = []
    for d in data_dirs:
        files.extend(glob.glob(os.path.join(d, "threads", "T-*.json")))
    files.sort(key=mtime, reverse=True)

    def by_id(tid):
        for f in files:
            if os.path.basename(f) == tid + ".json":
                return amp_read(f)
        return None

    env_id = os.environ.get("AMP_CURRENT_THREAD_ID") or os.environ.get("AMP_THREAD_ID")
    if env_id:
        rec = by_id(env_id) or amp_live(env_id, cache_root)
        if rec:
            return rec, "$AMP_CURRENT_THREAD_ID"
    for f in files:
        rec = amp_read(f)
        if rec and any(within(c, REPO) for c in (rec.get("cwds") or [])):
            return rec, "newest amp thread whose workspace matches this repo"
    # amp syncs threads to the server; a recent one may exist only as a log
    last = None
    for d in data_dirs:
        try:
            j = json.load(open(os.path.join(d, "session.json"), errors="replace")) or {}
        except Exception:
            continue
        last = j.get("lastThreadId") or last
    if last and not by_id(last):
        rec = amp_live(last, cache_root)
        if rec:
            rec["note"] = rec["note"] + "; workspace unverified — may not be this repo"
            rec["unverified"] = True
            return rec, "amp session.json lastThreadId (workspace unverified)"
    return None, None


# ---------------------------------------------------------------------- grok
def grok_home():
    return os.environ.get("GROK_HOME") or os.path.expanduser("~/.grok")


def grok_version():
    try:
        j = json.load(open(os.path.join(grok_home(), "version.json"), errors="replace")) or {}
        return j.get("version")
    except Exception:
        return None


def grok_active():
    """Sessions grok believes are open right now: session_id, pid, cwd, opened_at."""
    try:
        rows = json.load(open(os.path.join(grok_home(), "active_sessions.json"), errors="replace"))
    except Exception:
        return []
    return rows if isinstance(rows, list) else []


def grok_summaries():
    # ~/.grok/sessions/<percent-encoded cwd>/<session-id>/summary.json
    out = []
    for f in glob.glob(os.path.join(grok_home(), "sessions", "*", "*", "summary.json")):
        try:
            d = json.load(open(f, errors="replace")) or {}
        except Exception:
            continue
        out.append((f, d))
    out.sort(key=lambda t: mtime(t[0]), reverse=True)
    return out


def grok_read(path, d, running=False):
    info = d.get("info") or {}
    cwd = info.get("cwd") or unquote(os.path.basename(os.path.dirname(os.path.dirname(path))))
    model = d.get("current_model_id")
    # chat_history carries the exact variant (grok-4.6-build), summary the family
    hist = os.path.join(os.path.dirname(path), "chat_history.jsonl")
    try:
        for line in open(hist, errors="replace"):
            if '"model_id"' not in line:
                continue
            try:
                m = json.loads(line)
            except Exception:
                continue
            model = m.get("model_id") or model
    except OSError:
        pass
    return {
        "harness": "grok",
        "version": grok_version(),
        "session_id": info.get("id") or os.path.basename(os.path.dirname(path)),
        "model": model,
        "effort": d.get("reasoning_effort"),
        "mode": d.get("agent_name"),
        "mode_kind": "grok agent",
        "cwd": cwd,
        "title": d.get("generated_title") or d.get("session_summary"),
        "transcript": os.path.join(os.path.dirname(path), "chat_history.jsonl"),
        "session_file": path,
        "when": mtime(path),
        "note": "grok reports this session as still open" if running else None,
    }


def grok_running_here():
    return [r for r in grok_active() if within((r or {}).get("cwd"), REPO)]


def pick_grok():
    live = {(r.get("session_id") or "") for r in grok_running_here()}
    rows = grok_summaries()
    if live:
        for f, d in rows:
            if ((d.get("info") or {}).get("id") or "") in live:
                return grok_read(f, d, running=True), "grok active_sessions.json (open in this repo)"
    for f, d in rows:
        rec_cwd = (d.get("info") or {}).get("cwd")
        if within(rec_cwd, REPO):
            return grok_read(f, d), "newest grok session whose cwd matches this repo"
    return None, None


# ------------------------------------------------------------------- resolve
PICKERS = {"claude-code": pick_claude, "codex": pick_codex, "amp": pick_amp,
           "opencode": pick_opencode, "grok": pick_grok}

env_order = []
if os.environ.get("CLAUDE_CODE_SESSION_ID"):
    env_order.append("claude-code")
if os.environ.get("CODEX_SESSION_ID") or os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_SANDBOX"):
    env_order.append("codex")
if os.environ.get("AMP_CURRENT_THREAD_ID") or os.environ.get("AMP_THREAD_ID"):
    env_order.append("amp")
if any(k.startswith("OPENCODE_") for k in os.environ):
    env_order.append("opencode")
# grok exposes no session env var; an open session registered against this repo is
# the equivalent signal
if grok_running_here():
    env_order.append("grok")

found = {}
for name, fn in PICKERS.items():
    try:
        found[name] = fn()
    except Exception as e:
        found[name] = (None, "probe failed: %s" % e)

active = via = None
# An env var is the strongest signal for which harness is running, but agents nest —
# a codex run started from a Claude Code shell inherits $CLAUDE_CODE_SESSION_ID. So
# take the first env candidate that actually has a session record for this repo.
for name in env_order:
    rec, how = found.get(name, (None, None))
    if rec:
        active, via = rec, how
        break

if active is None:
    best = [(0 if r.get("unverified") else 1, r["when"], n, r, h)
            for n, (r, h) in found.items() if r and r.get("when")]
    if best:
        best.sort(reverse=True)
        _, _, _, active, via = best[0]
        via = "INFERRED — %s; verify this is your session" % via
    elif env_order:
        active = {"harness": env_order[0]}
        via = "environment variable (no session record found for this repo)"

if active is None:
    print("harness: unknown — no Claude Code / Codex / opencode session record for this repo")
    print("(self-report model/effort, or write 'unknown')")
else:
    label = active.get("harness", "unknown")
    if active.get("version"):
        label += " " + str(active["version"])
    print("harness: %s" % label)
    print("detected_via: %s" % (via or "unknown"))
    print("session_id: %s" % (active.get("session_id") or "unknown"))
    print("model: %s" % (active.get("model") or "unknown"))
    if active.get("provider"):
        print("provider: %s" % active["provider"])
    eff = active.get("effort")
    kind = active.get("effort_kind")
    print("effort: %s%s" % (eff or "unknown", "  (%s)" % kind if eff and kind else ""))
    if active.get("mode"):
        print("mode: %s%s" % (active["mode"],
                              "  (%s)" % active["mode_kind"] if active.get("mode_kind") else ""))
    roots = active.get("cwds") or ([active["cwd"]] if active.get("cwd") else [])
    if roots and not any(related(c, REPO) for c in roots):
        print("WARNING: session workspace %s is not this repo" % ", ".join(roots))
    if active.get("title"):
        print("title: %s" % active["title"])
    if active.get("note"):
        print("note: %s" % active["note"])
    if len(env_order) > 1:
        print("ambiguous: env vars for %s are all set (nested agents?)" % ", ".join(env_order))
    if active.get("transcript"):
        print("transcript: %s" % active["transcript"])
    if active.get("session_file"):
        print("session_file: %s" % active["session_file"])

print("\n===== OTHER_AGENT_SESSIONS =====")
print("(most recent session from each harness that touched this repo — a handoff should")
print(" mention work another agent may still have in flight here)")
for name in ("claude-code", "codex", "amp", "opencode", "grok"):
    rec, _ = found.get(name, (None, None))
    if active is not None and rec is not None and rec.get("transcript") == active.get("transcript"):
        print("%-12s this session" % (name + ":"))
    elif rec:
        print("%-12s %s  %s  %s%s" % (
            name + ":", when(rec.get("when")), rec.get("session_id") or "?",
            rec.get("model") or "model unknown",
            "  [workspace unverified — may be another repo]" if rec.get("unverified") else ""))
    else:
        print("%-12s none for this repo" % (name + ":"))
PYEOF
fi

section PREVIOUS_HANDOFF
PREV=$(ls .handoff/*-HANDOFF.md 2>/dev/null | sort | tail -1)
if [ -n "$PREV" ]; then
  echo "file: ${PREV#./}"
  PREV_SHA=$(grep -m1 -E '^HEAD_SHA:' "$PREV" | sed 's/^HEAD_SHA:[[:space:]]*//' | tr -d '"')
  echo "head_sha: ${PREV_SHA:-unknown}"
  echo "--- frontmatter ---"
  sed -n '2,/^---$/p' "$PREV" | sed '$d'
else
  echo "none — this is the first handoff for this project"
  PREV_SHA=""
fi

section GIT
# REPO is the remote's owner/name. A local directory is NOT a repo identity — when there is no
# origin, REPO stays blank and WORKING_DIR carries the path instead.
_origin=$(git remote get-url origin 2>/dev/null || true)
if [ -n "$_origin" ]; then
  echo "repo:    $(printf '%s' "$_origin" | sed -E 's#^git@[^:]+:##; s#^ssh://[^/]+/##; s#^https?://[^/]+/##; s#\.git$##')"
else
  echo "repo:    (none — no origin remote; leave REPO blank, do not put the path here)"
fi
echo "working_dir: $ROOT"
echo "remote:  ${_origin:-no origin}"
echo "branch:  $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'not a git repo')"
echo "head:    $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "upstream:$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null || echo 'no upstream')"
echo "ahead/behind: $(git rev-list --left-right --count '@{u}...HEAD' 2>/dev/null || echo 'n/a')"

section WORKING_TREE
git status --short 2>/dev/null | head -40
echo "--- diffstat (unstaged+staged vs HEAD) ---"
git diff HEAD --stat 2>/dev/null | tail -20

section COMMITS
if [ -n "${PREV_SHA:-}" ] && git cat-file -e "${PREV_SHA}^{commit}" 2>/dev/null; then
  echo "(since previous handoff $PREV_SHA)"
  git log --oneline --no-decorate "${PREV_SHA}..HEAD" 2>/dev/null | head -40
else
  echo "(no usable predecessor sha — last 15)"
  git log --oneline --no-decorate -15 2>/dev/null
fi

section STASHES
git stash list 2>/dev/null | head -10

section TRACKERS
[ -d .beads ] && echo "beads: .beads/ present"
[ -f beads.db ] && echo "beads: beads.db present"
[ -d .github ] && echo "github: .github/ present"
if [ -f .linear ] || [ -f linear.json ]; then echo "linear: config present"; fi
[ -d .jira ] && echo "jira: .jira present"
git remote get-url origin 2>/dev/null | grep -qi github && echo "origin is GitHub"

section BEADS
if [ -d .beads ] || [ -f beads.db ]; then
  bd stats 2>&1 | head -15
  echo "--- in flight ---"
  bd list 2>&1 | head -40
else
  echo "not a beads project"
fi

section OPEN_PRS
if command -v gh >/dev/null 2>&1 && git remote get-url origin 2>/dev/null | grep -qi github; then
  gh pr list --limit 10 2>&1 | head -15
else
  echo "gh unavailable or non-GitHub remote"
fi

section PROJECT_DOCS
for f in CLAUDE.md AGENTS.md README.md DEVLOG.md CHANGELOG.md PLAN.md TODO.md; do
  [ -f "$f" ] && echo "$f"
done
ls .claude/plans/*.md 2>/dev/null | tail -5

section AGENT_CONFIG
# Per-agent project config. Which of these exist tells you which harnesses this
# repo is set up for — worth a line in the handoff when they disagree.
for d in .claude .codex .agents .opencode .amp .grok .cursor .github/copilot-instructions.md; do
  [ -e "$d" ] && echo "$d"
done
for f in opencode.json opencode.jsonc AGENT.md .amp/settings.json; do
  [ -f "$f" ] && echo "$f"
done

section HANDOFF_DIR_TRACKED
if [ -d .handoff ]; then
  git check-ignore -q .handoff && echo "WARNING: .handoff is gitignored but handoffs are meant to be committed" || echo ".handoff is tracked (good)"
else
  echo ".handoff does not exist yet — will be created"
fi
