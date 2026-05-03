# Phase 2: Explain

- **Worker agent type name:** `code-explanator`.
- **Counter Names to Track:**
  - **Completed worker agents counter name:** `explain_count`
  - **Ongoing worker agents counter name:** `explain_ongoing_count`
- **Agent tool usage to spawn worker:**

  ```
  Agent(subagent_type: code-explanator, description: "Explain code solution", prompt: "follow your process instructions strictly")
  ```

- **String to print once queue is empty:** `"explained {explain_count} solutions"`.
