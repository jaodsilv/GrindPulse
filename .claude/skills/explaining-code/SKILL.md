---
name: explaining-code
description: Use when generating the Intuition, Algorithm, and Complexity writeup for a coding-interview Python solution that arrived as code-only (no neetcode.io writeup was available).
allowed-tools: Read, Edit
---

# Explaining Code Skill

You are reconstructing the writeup fields (Intuition, Algorithm, Complexity) for a
single coding-interview solution whose source page had only code available. Your
output will be embedded in a `standard-solutions.md` file alongside other
approaches and consumed by a downstream time-estimator.

## Inputs

You receive the location of a single problem folder. Inside you must read:

- `problem.md` — the problem statement.
- `standard-solutions.md` — the current solutions file where your writeup will
  be inserted. It contains one section per approach, already ordered. You are
  asked to fill in the empty `### Intuition`, `### Algorithm`, `### Complexity`
  under a specific `## N. Solution N` heading.
- `metadata.yaml` — the nominal difficulty and pattern (hint only).

Do NOT assume you know the problem; read the files every time.

## What "good" looks like

Match the house style exactly. Read both reference files before writing, even
if you think you remember the format:

- `references/two-pointers-example.md` — two-pointer sweep, nested algorithm list
- `references/dp-example.md` — memoized search / DP, single-level list

Your writeup must be consistent with these files down to punctuation, heading
depth, list markers, and math formatting.

## Required output format

The final assembled section, for a given approach numbered `N` with name
`TITLE`, must look exactly like:

```markdown
## N. TITLE

### Intuition

<1 paragraph, 3–6 sentences. Why this approach works. Connect the problem
structure to the technique. No code, no step-by-step — that goes in Algorithm.
Avoid the words "simply", "just", "easy".>

### Algorithm

<Ordered list. Each top-level step ends with a period. If a step has sub-steps,
nest a bulleted list (with `- `) indented by 3 spaces. Wrap every identifier
from the code in backticks: variables, function names, literals. Reference
actual names from the provided code, not paraphrases.>

### Code (Python)

```python
<LEAVE THIS BLOCK ALONE — it is already filled with the source code.>
```

### Complexity

- Time complexity: $O(...)$
- Space complexity: $O(...)$
  <optional sub-bullets only when the space breakdown is non-trivial>

> Where <variable-meanings> ...
```

The trailing blockquote is optional — include it only if one or more symbols
in the complexity line need defining (`n`, `m`, `k`, etc.). Match how the
reference files do it.

## Process

1. Read `problem.md`, `metadata.yaml`, and the existing `standard-solutions.md`.
2. Read BOTH reference files (`references/two-pointers-example.md` and
   `references/dp-example.md`). Do not skip this step.
3. Identify the `## N. ` heading you were asked to fill. Read the code in its
   `### Code (Python)` block carefully.
4. Derive an approach name (replace the placeholder "Solution N" if it is
   generic — pick the technique, e.g. "Backtracking with Bitmask", "Deque",
   "DFS with Memoization"). Update the `## N. ` line if the current one is a
   placeholder.
5. Write the three sections. Enforce the format checklist (below) before
   writing anything to disk.
6. Edit `standard-solutions.md` in place: replace the empty section body with
   your content. Do not touch other approaches.
7. Reply `code_explained` to the sender with the problem name, the approach
   index, and the path to the updated file.

## Format checklist (run through before editing)

- [ ] Intuition is one paragraph, no list, no headings.
- [ ] Algorithm is a numbered list using `1.` / `2.` / ...
- [ ] Sub-steps use `- ` with 3-space indent.
- [ ] Every identifier from the code is wrapped in backticks the first time it
      appears in each section.
- [ ] Complexity uses `$O(...)$` LaTeX math delimiters, not Unicode math.
- [ ] The `### Code (Python)` block is unchanged.
- [ ] The approach's `## N. TITLE` heading reflects the technique, not
      "Solution 1".
- [ ] No emoji, no "I/we", no filler ("basically", "simply", "just").

## Anti-patterns

- Paraphrasing the code line-by-line ("We set i to 0. Then we check if ...").
  The Algorithm section is a high-level recipe, not a transcription.
- Overclaiming correctness or performance ("optimal", "cannot be improved").
  Stick to what the code does.
- Using a trailing blockquote when the symbols are obvious from the problem
  statement (e.g. `n = len(nums)`).
- Merging Intuition and Algorithm — keep them separate and each earning its
  own section.
