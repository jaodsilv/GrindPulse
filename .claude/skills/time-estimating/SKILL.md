---
name: time-estimating
description: >-
  Use when analyzing a single coding-interview solution to produce time estimates
  for the three skill tiers (Top of the Crop, Advanced, Intermediate). Invoked by
  the tier-specific shells solution-analyzer-easy, solution-analyzer-medium, and
  solution-analyzer-hard. Handles all tier-invariant analysis logic.
allowed-tools: Read, Write
---

# Time-Estimating Skill

## Schema Coupling

The output written to `<output-path>` is consumed by `.claude/scripts/time_selection.py`
(via the `subagent_stop_time_selection` hook). If any field name in the output format
changes, both this skill AND that script must be updated together.

## Inputs

The dispatch hook injects a `<work-item>` block into the prompt. Read all fields from
it — do NOT parse flags from the raw prompt text.

| Field | Description |
|---|---|
| `<list-name>` | Problem list identifier (e.g. blind75, neetcode150) |
| `<problem-name>` | Human-readable problem title |
| `<difficulty>` | Nominal difficulty: Easy, Medium, or Hard |
| `<pattern>` | Algorithmic pattern tag (e.g. Two Pointers, DP) |
| `<solution-md>` | Absolute path to the Markdown writeup |
| `<solution-py>` | Absolute path to the Python solution file |
| `<analysis-path>` | Absolute path where the output must be written |
| `<output-path>` | Same as `<analysis-path>` — write the time-evaluation here |

## Process

1. Extract all work-item fields.
2. Read `<solution-md>` and `<solution-py>`.
3. Apply the 5-dimension framework (below) to the solution.
4. Assign whole-minute estimates for each of the three tiers.
5. Cross-check estimates against the calibration table.
6. Run the format checklist before writing.
7. Write the output to `<output-path>`.

## 5-Dimension Analysis Framework

Analyze every solution across all five dimensions before producing any number:

1. **Algorithmic complexity** — time/space complexity of the approach; how non-obvious the
   optimal algorithm is relative to naive alternatives.
2. **Logical design steps** — number of non-trivial reasoning steps required to construct
   the solution from the problem statement.
3. **Implementation steps and LOC** — concrete coding effort: helper structures, loops,
   index arithmetic, recursion setup, etc.
4. **Edge case density and bug likelihood** — off-by-one errors, empty inputs, overflow,
   cycle detection, duplicate handling, and similar traps embedded in this problem.
5. **Debug and test time** — how long a candidate spends verifying correctness under
   interview conditions given the above factors.

## Tier Definitions

- **Top of the Crop**: instantly recognizes the optimal approach; implements cleanly with
  minimal fumbling; handles edge cases reflexively.
- **Advanced/Expert**: recognizes the core pattern; needs deliberate time to work through
  edge cases and implementation details.
- **Intermediate**: understands the problem; may explore a suboptimal approach before
  converging on the correct one; implementation is slower and more error-prone.

## Calibration Table

| Difficulty | Top of the Crop | Advanced/Expert | Intermediate |
|---|---|---|---|
| Easy   | ~5–10 min  | ~10–20 min | ~20–35 min |
| Medium | ~10–20 min | ~20–35 min | ~35–50 min |
| Hard   | ~15–30 min | ~30–45 min | ~45–60 min |

Use `<difficulty>` as the starting row, then adjust up or down based on the
5-dimension analysis. A Medium problem with very high edge-case density may push
estimates toward Hard ranges; a Hard problem with a single clean trick may stay
near the low end of Hard.

## Output Format

Write exactly the following structure to `<output-path>`:

```markdown
## Estimative

- Estimated Time for "Intermediate Max Time": [N] minutes
- Estimated Time for "Advanced Max Time": [N] minutes
- Estimated Time for "Top of the Crop Max Time": [N] minutes

### Justificative

[Detailed justification referencing complexity, steps, edge cases, debugging]
```

`[N]` must be a whole positive integer. Field names must match character-for-character
(the consuming script parses them by exact string match).

## Format Checklist

Run through before writing to disk:

- [ ] Times are whole positive integers (minutes), no fractions or ranges
- [ ] All three tier lines present in exact order: Intermediate, Advanced, Top of the Crop
- [ ] Field labels match the output format spec exactly (character-for-character)
- [ ] Justificative references at least 3 of the 5 analysis dimensions by name
- [ ] Numbers are calibrated to `<difficulty>` via the table, with documented reasons for
      any deviation
- [ ] No filler words ("simply", "just", "obviously", "easy", "straightforward")

## Anti-Patterns

- Anchoring purely to nominal difficulty without performing the 5-dimension analysis.
- Ignoring edge-case density — a "simple" algorithm with many traps costs real time.
- Compressing tiers without justification (e.g., Top = Advanced, or all three within
  5 minutes of each other for a Hard problem).
- Rounding all estimates to the nearest 5 when the analysis supports more precision.
- Writing prose in the Estimative block — it must be bullet lines only.

## Return Contract

On success: `"wrote time-evaluation for {source}"`
On failure: `"error: <description>"`
