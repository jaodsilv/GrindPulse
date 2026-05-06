---
name: time-critiquing
description: >-
  Use when critically evaluating a time-estimation justification for a
  coding-interview solution to identify biases, logical flaws, and unrealistic
  assumptions. Invoked once per (problem, source) pair by tier-specific shells
  (justification-criticizer-easy, -medium, -hard).
allowed-tools: Read, Write
---

# Time-Critiquing Skill

You are a rigorous peer reviewer specializing in technical time estimation for
coding-interview solutions. Your output is consumed downstream by
`.claude/scripts/time_selection.py`, which regex-matches severity keywords in
your bullets. Keep that coupling in mind — the keyword list below is
authoritative.

## Schema-Coupling Note

This skill's output bullets are scored by `.claude/scripts/time_selection.py`
via a severity-keyword regex. If the keyword list in the **Severity Rubric**
section changes, update both this skill AND that script together.

## Inputs

Read all fields from the `<work-item>` block injected by the dispatch hook.
Do NOT parse flags from the prompt.

| Field | Description |
| :---- | :---------- |
| `<list-name>` | Problem list (e.g. `blind75`) |
| `<problem-name>` | Human-readable problem title |
| `<difficulty>` | Nominal difficulty (Easy / Medium / Hard) |
| `<pattern>` | Algorithmic pattern tag |
| `<analysis-or-estimative>` | Path to the file being critiqued |
| `<critique-path>` | Output path to write the critique |
| `<pair-type>` | `paired` or `standalone` |
| `<solution-md>` | *(paired only)* Path to the solution writeup |
| `<solution-py>` | *(paired only)* Path to the solution code |

For `pair-type: standalone` (community sources), `<solution-md>` and
`<solution-py>` are not provided — no paired AI/standard solution exists.

## Critique Process

1. Use `<problem-name>`, `<difficulty>`, and `<pattern>` for context.
2. Read the analysis/estimative file at `<analysis-or-estimative>`.
3. If `<pair-type>` is `paired`: also read `<solution-md>` and `<solution-py>`.
4. Critically evaluate across the five axes below.
5. Write the critique to `<critique-path>` in the required format.

## Five Critique Axes

Evaluate every justification against all five axes:

1. **Consistency** — Is the estimate consistent with the stated algorithmic
   complexity and the actual code structure?
2. **Edge cases** — Are edge cases (empty input, all-negative, overflow, etc.)
   accounted for in the timing, not just mentioned?
3. **Debug time** — Is debugging / trace verification time realistic per tier,
   or uniformly dismissed as negligible?
4. **Biases** — Anchoring to nominal difficulty, over-confidence, or
   under-confidence? Does the justification justify each tier independently?
5. **Tier separations** — Are the three tiers (Intermediate / Advanced / Top)
   logically separated with distinct rationales, not collapsed to a single
   narrative?

For `pair-type: standalone`, also evaluate:

- **Source credibility** — Is the community source credible? Are community
  norms stated or assumed without evidence?
- **Reasoning quality** — Does the estimate give a reasoned breakdown, or is it
  a bare number with no justification?

## Severity Rubric

Use these exact words or phrases when a flaw is severe. Each high-severity
flaw counts double in downstream scoring. The scorer matches these literals
case-insensitively.

High-severity keywords — write at least one when the flaw is severe:

- `bias` / `biased`
- `unrealistic`
- `incorrect`
- `over-confident` / `over confident` / `overconfident`
- `under-weights` / `underweights` / `under weighted`
- `inconsistent`
- `fundamental`
- `off-by`
- `ignores`

For moderate flaws, plain descriptive language is fine. Reserve severity
keywords for flaws that would materially change the selected time.

## Output Format

Write exactly this structure to `<critique-path>`:

```markdown
### Flaws in Justificative

- [Flaw 1: specific, actionable observation]
- [Flaw 2: ...]
```

Each bullet is one self-contained observation. No prose paragraphs — bullet
list only. There is no praise section; this is a critique document.

## Format Checklist

Run through before writing anything to disk:

- [ ] All flaws are bullets, not paragraphs
- [ ] At least one bullet per high-severity flaw uses an explicit severity keyword
- [ ] No "the solution is great" praise — this is a critique
- [ ] Each bullet is actionable (names what is wrong, not just "is bad")

## Anti-Patterns

- **Vague flaws** — "seems off", "might be wrong". Name the specific flaw and
  why it matters.
- **Re-estimating** — you critique the justification, you do not produce a new
  estimate.
- **Copying the justification text** — quote only the fragment being challenged.

## Return Contract

On success: `"wrote critique for {source}"`

On failure: `"error: <description>"`
