# Phase 4: Critique

This phase uses three tier-specific criticizer workers so each justification critique runs on a model sized to the problem's difficulty (haiku for Easy, sonnet for Medium, opus for Hard). Each tier draws from its own queue file produced by Queue Rebuild (`critique-easy.yaml`, `critique-medium.yaml`, `critique-hard.yaml`). The dispatcher's "drop this type from rotation when its queue is empty" behavior applies to each tier independently — phase 4 is complete only after all three queues are drained.

- **Worker agent types (all three are always enabled):** `justification-criticizer-easy`, `justification-criticizer-medium`, `justification-criticizer-hard`.
- **Counter Names to Track (one set per tier):**
  - **Completed worker agents counters:** `criticizer_easy_count`, `criticizer_medium_count`, `criticizer_hard_count`
  - **Ongoing worker agents counters:** `criticizer_easy_ongoing_count`, `criticizer_medium_ongoing_count`, `criticizer_hard_ongoing_count`
- **Agent tool usage to spawn workers:**

  ```
  Agent(subagent_type: justification-criticizer-easy, description: "Critique Easy time estimate", prompt: "follow your process instructions strictly")
  Agent(subagent_type: justification-criticizer-medium, description: "Critique Medium time estimate", prompt: "follow your process instructions strictly")
  Agent(subagent_type: justification-criticizer-hard, description: "Critique Hard time estimate", prompt: "follow your process instructions strictly")
  ```

- **String to print once all three queues are empty:** `"critiqued easy={criticizer_easy_count}, medium={criticizer_medium_count}, hard={criticizer_hard_count} items"`.
