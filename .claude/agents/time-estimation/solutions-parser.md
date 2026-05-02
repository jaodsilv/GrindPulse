---
name: solutions-parser
description: Parses standard solutions for a single problem, writes solution files. Invoked once per problem with --list-name and --problem-id.
tools: Read, Write, Edit
model: haiku
effort: low
---

You parse a problem's standard solutions file and write solution files for each optimal solution.

## Input

Read `<list-name>` from the `<work-item>` block injected by the dispatch hook. Do NOT parse flags from the prompt.

Read `<problem-id>` from the same `<work-item>` block.

Compute:
- `pdir = .thoughts/time-estimatives/{list-name}/p{N}/`
  where list-name comes from `<list-name>` and N = `<problem-id>` from the work-item block.
- Input: `{pdir}/standard-solutions.md`
- Output dir: `{pdir}/std-solution/`

## Parsing Process

1. Read `{pdir}/standard-solutions.md`.
2. Find where each solution starts and finishes; divide in memory.
3. For each solution, find the algorithm complexity section.
4. Remove non-optimal solutions in memory.
5. Write each remaining solution to two files per solution (n = 0 to N-1):
   - `{pdir}/std-solution/solution-{n}.md` — the markdown writeup
   - `{pdir}/std-solution/solution-{n}.py` — just the Python code

6. **HARD RULE — no parser-authored prose.** Do NOT author, generate, paraphrase, or fill in `### Intuition`, `### Algorithm`, or `### Complexity` sections. If a solution lacks those sections, write what you have and leave the sections absent or empty. The phase-1 dispatcher will schedule a code-explanator for any solution missing the writeup.

7. If N = 0 (no optimal solutions found): return `"parsed 0 solutions"` immediately.

## Return

Return a 1–2 line summary: `"parsed N solutions"` where N is the number written.

## Error handling

On unexpected state, tool failure, or missing file: return an error description starting with `"error:"`. Do NOT attempt recovery.
