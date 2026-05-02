# Phase 0: Fetch

This phase has no queue. Only 1 agent instance should be spawned.

- **Worker agent type name:** `problem-fetcher`
- **Counter Names to Track:** None
- **Agent tool usage to spawn worker:**

  ```
  Agent(problem-fetcher, description: "Fetch problems descriptions and solutions", prompt: "follow your process instructions strictly")
  ```

- **String to print once phase is complete:** None.

CRITICAL: This phase does not follow the dispatch protocol, only 1 agent of this type should be spawned; No more agents are needed.
