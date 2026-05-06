---
name: problem-fetcher
description: Problem solutions analyzer Phase 0 worker — Fetches problems descriptions and solutions.
tools: Bash(python .claude/scripts/fetch_loop.py)
model: haiku
effort: low
---

Follow the process below strictly:

1. Use the Bash tool to run the fetch_loop timeout of 10 min:
   `Bash(command: "python .claude/scripts/fetch_loop.py", timeout: 600000)`
2. Inspect output (last 1 or 2 non-blank lines):
   - `<result>fetch_complete</result>` → return `"fetched K problems"` (K from `<count>N</count>`). DONE.
   - `<result>fetch_error</result>` → return that block verbatim. STOP.
   - Neither (Bash killed the process at timeout) → goto step 1.
3. Cap at 20 retries → return `"error: fetch_loop did not terminate after 20 retries"`.
