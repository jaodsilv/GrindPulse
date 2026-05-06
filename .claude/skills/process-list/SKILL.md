---
name: process-list
description: Use this command when you need to estimate time ranges for completing coding interview problems at different skill levels (top, advanced, intermediate). The pipeline analyzes standard solutions from neetcode.io by default; pass --ai-path and/or --community-path to opt into extra estimation sources.
model: sonnet
argument-hint: "raw/<list>.tsv [--fresh] [--ai-path] [--community-path] [--parallelism N] [--fetch-delay-seconds N] [--phases <spec>]"
allowed-tools: Read, Bash(python .claude/scripts/cleanup.py), Bash(python .claude/scripts/list_work.py *), Agent, TaskCreate, TaskEdit, TaskGet, TaskList, TaskUpdate
---

# Time Estimation Pipeline

## Error Escalation

If any dispatcher returns an error message, forward it to the user verbatim and stop. Do NOT retry, do NOT advance to the next phase.

## Input Parsing

You may ignore most argument flags passed and XML tags from the additional context. They are meant to be used by hook scripts, not by you.
Do NOT re-read the TSV or recreate folders.

From ARGUMENTS: <arguments>${ARGUMENTS}</arguments> extract these 3 flags:
- `--ai-path` (optional): enable the AI-solution estimation path (see `references/ai-path.md`)
- `--community-path` (optional): enable the community-estimate path (see `references/community-path.md`)

From Hook Additional Context (already computed):
- `start-phase`
- `end-phase`
- `work-folder`
- `list-name`

## Conditional Path Loading

If `--ai-path` in ARGUMENTS, read `references/ai-path.md` before proceeding.
If `--community-path` in ARGUMENTS, read `references/community-path.md` before proceeding.

## Dispatch Protocol

Phases 1–5 fan out workers via the `Agent` tool.

**Spawning a worker.** Each phase doc declares which subagent name(s) to spawn. To spawn one, make a real `Agent` tool call with these parameters:
- `subagent_type` — the worker name from the phase doc (e.g., `solution-analyzer`)
- `description` — a 3–5 word summary
- `prompt` — the literal string `Run the base instructions you have`

The phase reference doc shows this as `Agent(subagent_type: <name>, description: "...", prompt: "Run the base instructions you have")`. Use this notation as a directive to invoke the Agent tool with those exact parameters.

Only try to start a worker once the previous finished initializing.

Interpret each spawn result:
- **Allowed/Success** — This means the Agent started successfullly. Once it finishes increment the local success counter for that worker type. Loop and spawn another Agent in parallel. Increment the number of in-flight agents. Update Current task title from task list with the updated number and start the next subagent.
- **Denied with `"maximum in-flight subagents running; wait for any agent to finish before spawning more"`** — the cap is full. Stop spawning this turn. The next turn arrives when an in-flight worker completes its work, when that happens, loop and try again.
- **Denied with `"queue empty"`** — that worker type's queue is drained. If the phase declares multiple worker types, drop this one from the live set; do **not** consider this phase complete until all declared types are drained. If all are drained, move to the next phase or exit if it is the last phase.
- **Any other denial** — return `"error: <denial reason>"` and stop.
- **On Agent completion** - increment count of completed agents and decrement in-flight agents number. Update Current task title from task list with the updated numbers.

Keep track of the number of in-flight agents and the number of completed agents.

The phase-specific return template is in each phase doc. Use the local success counter(s) — never call out to read state files.

On each phase reference file you will find the following information to complete the protocol:
- Worker agent type name
- Counter Names to Track
  - Completed workers counter name
  - Ongoing workers counter name
- Agent tool usage to spawn worker
- String to print once phase is complete

## Queue Rebuild

Before dispatching workers for each phase (1–5), rebuild its queue file(s) from current disk state.

For each applicable row below, run via Bash with `>` redirection. Append `--ai-path` if active; append `--community-path` if active.

| Phase | Verb | Queue file | Condition |
|---|---|---|---|
| 1 | `parse-needed` | `parse.yaml` | always |
| 1 | `solve-easy-needed` | `solve-easy.yaml` | `--ai-path` only |
| 1 | `solve-medium-needed` | `solve-medium.yaml` | `--ai-path` only |
| 1 | `solve-hard-needed` | `solve-hard.yaml` | `--ai-path` only |
| 1 | `community-needed` | `community.yaml` | `--community-path` only |
| 2 | `explain-needed` | `explain.yaml` | always |
| 3 | `analyze-easy-needed` | `analyze-easy.yaml` | always |
| 3 | `analyze-medium-needed` | `analyze-medium.yaml` | always |
| 3 | `analyze-hard-needed` | `analyze-hard.yaml` | always |
| 4 | `critique-easy-needed` | `critique-easy.yaml` | always |
| 4 | `critique-medium-needed` | `critique-medium.yaml` | always |
| 4 | `critique-hard-needed` | `critique-hard.yaml` | always |
| 5 | `tiebreak-needed` | `tiebreak.yaml` | only if `tiebreak.yaml` already exists from `time_selection.py` step 1 |

Command template:
```bash
python .claude/scripts/list_work.py <verb> --list-name <list-name> [--ai-path] [--community-path] > <work-folder>/queues/<file>
```

## Process

1. Use the TaskCreate tool to add a task for each phase in the task list.
2. **Phase loop.** Read `<start-phase>`, `<end-phase>`, `<work-folder>`, and `<list-name>` from hook context. For each phase in `start-phase..(end-phase-1)`:
   - Read the CURRENT PHASE reference file only:
     - Phase 0: `${CLAUDE_SKILL_DIR}/references/phase-0-fetch.md`.
     - Phase 1: `${CLAUDE_SKILL_DIR}/references/phase-1-produce.md`.
     - Phase 2: `${CLAUDE_SKILL_DIR}/references/phase-2-explain.md`.
     - Phase 3: `${CLAUDE_SKILL_DIR}/references/phase-3-analyze.md`.
     - Phase 4: `${CLAUDE_SKILL_DIR}/references/phase-4-critique.md`.
     - Phase 5: `${CLAUDE_SKILL_DIR}/references/phase-5-select.md`.
     - Phase 6: `${CLAUDE_SKILL_DIR}/references/phase-6-cleanup.md`.
   - For phases 1–5, run `## Queue Rebuild` for the current phase before dispatching workers.
   - For phases 1–5, run the `## Dispatch Protocol` instructions with the extra information from the phase reference files.
   - Once all queues are empty for the current phase record the 1-line summary (the phase's result string).
   - Only read the next phase file once the current phase has finished.

### Constraints

1. **Skipped phases** (P outside start..end-1). Do not read the phase doc.
2. **Error escalation.** If any worker produces a return string starting with `"error:"`, forward it verbatim to the user and stop. Do not advance to the next phase.
