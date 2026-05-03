# Phase 3: Analyze

This phase uses three tier-specific analyzer workers so each problem's time analysis runs on a model sized to its difficulty (haiku for Easy, sonnet for Medium, opus for Hard). Each tier draws from its own queue file produced by Queue Rebuild (`analyze-easy.yaml`, `analyze-medium.yaml`, `analyze-hard.yaml`). The dispatcher's "drop this type from rotation when its queue is empty" behavior applies to each tier independently — phase 3 is complete only after all three queues are drained.

- **Worker agent types (all three are always enabled):** `solution-analyzer-easy`, `solution-analyzer-medium`, `solution-analyzer-hard`.
- **Counter Names to Track (one set per tier):**
  - **Completed worker agents counters:** `analyze_easy_count`, `analyze_medium_count`, `analyze_hard_count`
  - **Ongoing worker agents counters:** `analyze_easy_ongoing_count`, `analyze_medium_ongoing_count`, `analyze_hard_ongoing_count`
- **Agent tool usage to spawn workers:**

  ```
  Agent(subagent_type: solution-analyzer-easy, description: "Analyze Easy solution time", prompt: "follow your process instructions strictly")
  Agent(subagent_type: solution-analyzer-medium, description: "Analyze Medium solution time", prompt: "follow your process instructions strictly")
  Agent(subagent_type: solution-analyzer-hard, description: "Analyze Hard solution time", prompt: "follow your process instructions strictly")
  ```

- **String to print once all three queues are empty:** `"analyzed easy={analyze_easy_count}, medium={analyze_medium_count}, hard={analyze_hard_count} solutions"`.
