# Phase 5: Select & Write TSV

Phase 5 picks the best-justified time estimate for each problem and writes it back to the TSV. The pipeline uses a hybrid approach: a deterministic Python script handles unambiguous cases, and an LLM tiebreaker handles only the close calls.

## Step 1: Run the deterministic selector

Before any worker dispatch, run the selection script:

```bash
python .claude/scripts/time_selection.py --list-name <list-name> [--ai-path] [--community-path]
```

The script:
- Writes `selected-times.md` directly under `p<N>/` for problems with one source or a clear winner.
- Appends `{problem-id, candidate-sources}` entries to `<work-folder>/queues/tiebreak.yaml` for problems where the top two sources have similar critique scores (gap below the tiebreak threshold).
- Prints a 5-line summary (`processed`, `direct-emissions`, `tiebreaks-queued`, `skipped (already-selected)`, `skipped (no-sources)`).

If the script exits non-zero, forward its stderr to the user and stop. Do NOT proceed to step 2.

## Step 2: Conditionally dispatch the tiebreak agent

If `<work-folder>/queues/tiebreak.yaml` does not exist or is empty (zero `tiebreaks-queued`), phase 5 is complete after step 1. Skip step 2.

Otherwise, run the standard `## Dispatch Protocol` from the parent SKILL.md with this single worker type:

- **Worker agent type name:** `time-selection-tiebreak`
- **Counter Names to Track:**
  - **Completed worker agents counter name:** `tiebreak_count`
  - **Ongoing worker agents counter name:** `tiebreak_ongoing_count`
- **Agent tool usage to spawn worker:**

  ```
  Agent(subagent_type: time-selection-tiebreak, description: "Tiebreak time estimate", prompt: "follow your process instructions strictly")
  ```

## Phase 5 completion string

Combine both steps:
- If step 2 ran: `"selected via direct={direct_count} + tiebreak={tiebreak_count} problems"`
- If step 2 was skipped: `"selected via direct={direct_count} problems"`

`{direct_count}` is the `direct-emissions` value printed by the script in step 1.

CRITICAL: Do not attempt to write the times to the tsv file yourself. The script handles direct cases via its own write path, and the tiebreak agent emits the standard contract line that the SubagentStop hook consumes.
