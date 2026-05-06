# Phase 1: Produce - AI PATH Appendix

This document describes the use of the extra agents for phase 1 when `--ai-path` is present in ARGUMENTS.

The AI path uses three tier-specific worker types so each problem is solved by a model sized to its difficulty (haiku for Easy, sonnet for Medium, opus for Hard). All three are enabled together; each draws from its own queue file produced by Queue Rebuild (`solve-easy.yaml`, `solve-medium.yaml`, `solve-hard.yaml`). The dispatcher's standard "drop this type from rotation when its queue is empty" behavior applies to each tier independently.

- **Worker agent types (add all three):** `coding-challenge-solver-easy`, `coding-challenge-solver-medium`, `coding-challenge-solver-hard`.
- **Counter Names to Track (one set per tier):**
  - **Completed worker agents counters:** `ai_easy_count`, `ai_medium_count`, `ai_hard_count`
  - **Ongoing worker agents counters:** `ai_easy_ongoing_count`, `ai_medium_ongoing_count`, `ai_hard_ongoing_count`
- **Agent tool usage to spawn workers:**

  ```
  Agent(subagent_type: coding-challenge-solver-easy, description: "Solve Easy problem with AI", prompt: "follow your process instructions strictly")
  Agent(subagent_type: coding-challenge-solver-medium, description: "Solve Medium problem with AI", prompt: "follow your process instructions strictly")
  Agent(subagent_type: coding-challenge-solver-hard, description: "Solve Hard problem with AI", prompt: "follow your process instructions strictly")
  ```

- **String to print once all three queues are empty:** Append `", ai-easy={ai_easy_count}, ai-medium={ai_medium_count}, ai-hard={ai_hard_count}"` to the string to print.
