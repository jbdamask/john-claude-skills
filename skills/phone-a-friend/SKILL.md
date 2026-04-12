---
name: phone-a-friend
description: Spawn an Opus sub-agent in extended-thinking max-effort mode to debate, critique, and pressure-test the primary agent's current thinking through an unbounded multi-turn dialogue, terminating when the agents either reach genuine consensus or cleanly agree to disagree. Supports escalating clarifying questions to the human user mid-debate, and supports the user sending the debate back for another round (jury-room rule). Use when the user invokes "phone a friend", asks for a "second opinion", "sanity check", "debate this with another model", or otherwise signals they want rigorous adversarial review of an approach, plan, design, diagnosis, or decision before proceeding.
---

# Phone a Friend

## Overview

A consultation workflow where the primary Claude Code agent pauses its work, assembles a synopsis of the current situation, and engages an Opus sub-agent ("the friend") in a back-and-forth debate. The two agents argue, critique, research, and refine until they reach one of two valid terminal states: **genuine consensus** or **a clean agree-to-disagree**. At that point the primary reports back to the user.

There is **no hard iteration cap**. The goal is a real outcome, not a turn counter. If the user is not satisfied with the report, they can send the debate back for another round — the jury-room rule (Phase 7).

This is NOT a one-shot review. It is a multi-turn dialogue where both sides push back, ask questions, update their views, and — when they need information only the user has — pause to ask the user directly (Phase 4b).

## When the user invokes this skill

The user will typically say something like "phone a friend", "get a second opinion on this", "sanity check this", or "debate this with another model". Do not invoke this skill proactively — wait for the explicit ask.

## Workflow

Follow these phases in order.

### Phase 1: Confirm scope with the user (brief)

Before spinning up the friend, confirm in one sentence what the friend should debate. Offer a default based on current session context, e.g. "Phoning a friend to pressure-test the migration plan in `db/schema.ts` — want to narrow the question, or go broad?" Wait for the user's OK or redirection. Keep this exchange to one round; do not interrogate.

### Phase 2: Build the synopsis

Assemble a structured synopsis. The synopsis is a self-contained briefing — the friend has **zero** prior context from the session. Include:

1. **The question** — a single sentence stating what is being debated. Be specific. "Is this migration safe?" not "review this."
2. **Background** — what the user is trying to accomplish, why it matters, any deadlines or constraints.
3. **Current approach / proposal** — what the primary agent is about to do or has done, with concrete details (file paths, code snippets, command sequences, architectural choices).
4. **What has been tried / ruled out** — prior attempts, dead ends, options already rejected and why.
5. **Uncertainties** — where the primary is unsure or has low confidence.
6. **Relevant artifacts** — file paths (with line numbers), error messages, test output, logs. Quote small snippets inline; reference larger ones by path so the friend can read them.
7. **The ask** — what kind of feedback is wanted: adversarial critique, alternative approaches, risk assessment, missing considerations, etc.
8. **Research hints (optional)** — specific things the friend should consider investigating: "check whether library X supports this", "look at how `src/auth/*` handles the same case", "web-search current best practices for Y as of 2026". The friend decides for itself whether to act on these.

Keep the synopsis tight but complete. Aim for enough signal that the friend can form a real opinion without needing to ask clarifying questions on turn 1.

### Phase 3: Spawn the friend (turn 1)

Use the **Agent** tool with these exact settings:

- `subagent_type`: `"general-purpose"` (gives the friend access to all tools: Read, Grep, Glob, WebSearch, WebFetch, Bash, Edit, Write, etc.)
- `model`: `"opus"`
- `description`: `"Phone a friend: <short topic>"`
- `prompt`: the synopsis, framed as below.

The prompt MUST:

- Open with the word **`ultrathink`** on its own line to trigger maximum extended thinking budget.
- State the friend's role explicitly: "You are being consulted as a second opinion. Your job is to push back, not rubber-stamp. Disagree where you see flaws. Propose alternatives."
- Include the full synopsis.
- State the terminal goal: "Our job together is to reach genuine consensus, *or* to cleanly agree to disagree with both positions clearly stated. There is no turn limit. Do not force agreement to end the debate, and do not drag the debate out past its useful life. Stop when real progress stops."
- Explain the human-escalation channel: "If at any point you have a question only the human user can answer — missing business context, ambiguous requirements, a values/preference call, information not in the codebase or on the web — say so explicitly and I will pause our debate and surface the question to the user. Do NOT escalate questions you could answer yourself by reading files, searching the web, or running commands."
- State the read-only constraint in plain terms: **"You are a thought partner, not an actor. You must NOT create, modify, or delete any files or data under any circumstances. You must NOT run commands that mutate state (no `git commit`, no `git push`, no `rm`, no `mv`, no `touch`, no package installs, no migrations, no API calls that write, no config changes). Your tool use is strictly read-only: reading files, grepping, globbing, web search, web fetch, and read-only shell commands (`ls`, `cat`, `git log`, `git diff`, `git status`, etc.) are fine. If you believe an action should be taken, describe it in your response and let the primary agent carry it out after the user approves. Your job is to think, debate, and advise — never to act."**
- Tell the friend it has read/search tools (Read, Grep, Glob, WebSearch, WebFetch, read-only Bash) and should use them when grounding its opinion would benefit from real evidence — but that Edit, Write, NotebookEdit, and mutating Bash commands are off-limits.
- End with: "Respond with (a) your independent assessment, (b) specific critiques or concerns, (c) questions for me or for the human (label which), and (d) a current position (agree / disagree / need-more-info) on the primary ask. If you need to read files, search the web, or run commands to form your view, do so before responding."

Capture the Agent tool call's returned agent ID or name — it is needed for follow-up turns via SendMessage.

### Phase 4: The dialogue loop

After turn 1, enter a dialogue loop. Each iteration:

1. **Read the friend's response carefully.** Extract: its position, its critiques, its questions, any new evidence it surfaced.
2. **Form the primary's next turn.** This is the primary agent's job — do not just pass the friend's message back. The primary should:
   - Answer any questions the friend asked (with concrete info from the session or by reading files).
   - Push back on critiques the primary genuinely disagrees with, with reasoning.
   - Concede points the friend got right.
   - Surface new considerations the friend may have missed.
   - Ask the friend for clarification where its reasoning is unclear.
   - Re-state the primary's current position (agree / disagree / evolving).
3. **Continue the dialogue** by calling **SendMessage** with `to` set to the friend's agent ID from Phase 3. Do NOT call Agent again — that would start a fresh agent with no memory of the prior turns. Always SendMessage to continue.
4. **Check for termination** after each response (see Phase 5).

**No hard iteration cap.** The task is to reach a real outcome — either a genuine consensus or a clean agree-to-disagree — not to hit a turn counter. Both agents should be explicitly told: "Your job is to reach consensus *or* to cleanly agree to disagree. Do not stop debating just because you are tired of debating. Do not force agreement to end the dialogue. When you have genuinely exhausted the productive arguments, say so explicitly."

That said, the primary agent should use judgment about when enough is enough. Use these heuristics:

- **Productive turns**: the friend is still surfacing new angles, evidence, or arguments → keep going.
- **Diminishing returns**: two consecutive turns add nothing new → check if this is consensus, agree-to-disagree, or genuine stalemate; then stop.
- **Reasonable bound**: around turn 25, reassess whether continued debate is actually productive. This is not a cap, it is a checkpoint. If real progress is still happening, keep going. If not, wrap up and report.

### Phase 4b: Escalating questions to the human

If at any point **either agent** is blocked by a question only the human can answer — missing context, ambiguous requirements, a values/preference call, information that is not in the codebase or on the web — pause the dialogue and surface the question to the user.

**What qualifies as a human-only question:**
- "What are the actual performance requirements here?"
- "Is it OK to break backwards compatibility?"
- "Which of these two tradeoffs matters more to you?"
- "Was this constraint a hard requirement or just a preference?"
- Anything that requires business context, user intent, or a judgment call the user has not yet made.

**What does NOT qualify** (do not escalate these — the agents should handle them):
- Questions answerable by reading code, running commands, or searching the web.
- Questions one agent could ask the other.
- Questions the primary already has context on from the session.

**How to escalate:**

1. Stop the dialogue loop. Do not send another SendMessage to the friend yet.
2. Return control to the user with a clearly framed message:
   - State that the debate is currently paused.
   - List the specific question(s) — phrased tightly, not a wall of text. If there are multiple, number them.
   - Give the user enough context to answer (which turn raised it, why it matters to the debate, what the current split is).
   - State which agent raised the question (primary or friend) so the user can calibrate.
3. **Wait for the user's answer.** Do not guess, do not proceed.
4. Once the user responds, resume the debate by calling **SendMessage** to the friend with the user's answer incorporated into the next turn. Quote the user's answer verbatim so the friend sees it unfiltered, then continue the dialogue with the new information.

The primary may also escalate its own questions the same way. Do not force the friend to be the one who asks.

**Batch questions when possible.** If the friend raises three clarifying questions at once, surface all three in a single escalation rather than one at a time.

**Early stop conditions:**
- Genuine consensus reached → stop and report.
- Genuine agree-to-disagree reached (both agents confirm their remaining disagreement is rooted in a real difference of view, not missing info) → stop and report.
- The friend explicitly says it has nothing to add → stop.
- The debate converges with no new arguments for two consecutive turns → stop.
- The primary realizes mid-debate that the question itself is wrong → stop, report this to the user, and ask whether to reformulate.

### Phase 5: Termination detection (consensus or agree-to-disagree)

There are two valid terminal states. Both are acceptable outcomes to report.

**Consensus** requires all of these, explicitly:

- Both agents agree on **the problem statement** (they are debating the same thing).
- Both agents agree on **the recommended action** (or on the recommended decision, if the ask was a yes/no).
- Both agents agree on **the key risks and caveats** worth flagging.

Before declaring consensus, state internally: "The friend and I now agree on X, Y, Z. Disagreements remaining: none / [list]." If the list is non-empty, it is not consensus.

Do not confuse "the friend stopped objecting" with consensus. Politeness is not agreement. Explicitly ask the friend "Do you agree with the following conclusion: [conclusion]? If not, what would you change?" before calling it done.

**Agree-to-disagree** is equally valid and requires:

- Both agents have heard each other's full argument and understand it.
- Both agents have pushed back on the cruxes and neither has moved.
- The remaining disagreement is traceable to a genuine difference of view (risk tolerance, design philosophy, judgment call) — NOT to missing information (if it's missing info, escalate to the human per Phase 4b instead).
- Both agents can state the other's position fairly.

Before declaring agree-to-disagree, ask the friend explicitly: "We seem to have reached a genuine disagreement. Can you state my position fairly? And do you agree that the remaining gap is a real difference of view rather than missing information?" Only accept agree-to-disagree if the friend confirms.

### Phase 6: Report back to the user

Return control to the user with a report containing:

1. **The question** that was debated (one line).
2. **The outcome** — one of:
   - **Consensus**: the agreed recommendation, with reasoning.
   - **Agree-to-disagree**: both positions, stated fairly, with the crux of the disagreement identified.
   - **Stalemate / wrap-up**: the debate was wound down at the primary's judgment without a clean terminal state. Explain why.
3. **Key points that shifted** during the debate — what the primary learned or changed its mind on, what the friend updated. This is often the most valuable part for the user.
4. **Risks and caveats** both agents flagged.
5. **Recommended next action** — what the primary will do next, pending user approval. If agree-to-disagree, offer both paths.
6. **Turn count** — how many turns the debate took, and the friend's agent ID (so the debate can be resumed per the jury-room rule below).

Keep the report scannable. Bullets over prose. The user should be able to read it in under a minute and decide whether to proceed, redirect, or dig in.

After delivering the report, **wait for the user** before acting on the conclusion. The consensus is a recommendation, not a mandate.

### Phase 7: The jury-room rule (resuming the debate)

A stopped debate is not necessarily a finished debate. If the user reads the report and wants more — "go debate this more", "that's not enough, dig deeper", "keep arguing", "I'm not satisfied, send them back" — treat this like a judge sending a deadlocked jury back to the jury room.

To resume:

1. Use **SendMessage** with `to` set to the friend's original agent ID (saved from Phase 3 and reported in Phase 6). Do **not** spawn a new Agent — a fresh agent has no memory of the prior debate.
2. Frame the resumption: "The user has reviewed our report and wants us to continue debating. Their specific guidance is: [quote the user's feedback verbatim]. Let's dig further on the unresolved points."
3. Re-enter the dialogue loop from Phase 4. The primary still drives, escalation to the user is still available (Phase 4b), and the termination criteria still apply (Phase 5).
4. When the next terminal state is reached, report back again (Phase 6). The user can send the jury back repeatedly — there is no limit.

If the agent ID from the prior run is no longer valid (the session has been compacted or the agent was cleaned up), the debate must be restarted fresh. In that case, include a summary of the prior debate's key points in the new synopsis so the new friend starts with context — but flag to the user that this is a fresh debate, not a continuation.

## Important constraints

- **Do not phone a friend recursively.** The friend must not itself invoke this skill.
- **The friend is a thought partner, not an actor. Hard read-only constraint.** The friend MUST NOT create, update, or delete any files or data, and MUST NOT run state-mutating commands (no writes, no commits, no pushes, no migrations, no installs, no destructive shell commands, no write APIs). Allowed: Read, Grep, Glob, WebSearch, WebFetch, and read-only Bash (`ls`, `cat`, `git log`, `git diff`, `git status`, etc.). Disallowed: Edit, Write, NotebookEdit, and any Bash command that changes state on disk, in version control, in a database, or over the network. State this constraint explicitly in the turn-1 prompt (Phase 3) and reinforce it if the friend ever proposes to take an action itself — tell it to describe the action and the primary will carry it out after the user approves. If the friend takes a mutating action despite this instruction, immediately report it to the user.
- **Do not leak credentials or secrets** into the synopsis. If the context contains API keys, tokens, or private data, redact them before sending to the sub-agent.
- **Do not use phone-a-friend for simple questions.** It is expensive (Opus + extended thinking + multi-turn + tool use). If the question can be answered in one turn by the primary alone, answer it directly and tell the user why phoning a friend was unnecessary.
- **Track turns explicitly.** Number each turn in your own notes (Turn 1, Turn 2, ...) so you can report the count and so the ~25-turn checkpoint is meaningful.
- **The friend has tools — let it use them.** Do not pre-chew research. If the friend wants to read files or search the web to form its view, that is the point. The primary's job is to make the debate productive, not to spoon-feed.
- **Consensus and agree-to-disagree are both valid outcomes.** A forced consensus is worse than a clean split. A premature agree-to-disagree is worse than one more productive turn. Use judgment.
- **Escalate to the user when you need the user** — not when you are tired of debating. The user is a resource for information only the user has, not a tiebreaker for disagreements the agents should work through themselves.
- **The user can send the jury back.** If the user reads your report and wants more debate, resume the same friend agent via SendMessage (Phase 7). Do not spawn a new friend unless the original agent ID is no longer valid.
