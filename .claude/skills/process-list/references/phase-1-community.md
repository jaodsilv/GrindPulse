# Phase 1: Produce - COMMUNITY PATH Appendix

This document describes the use of the extra agent for phase 1 when `--community-path` is present in ARGUMENTS

- **Worker agent type name:** Add `community-time-finder` as an enabled worker type alongside the others.
- **Counter Names to Track:**
  - **successfully completed Agents:** `community_count`
  - **in-flight Agents:** `community_ongoing_count`
- **Agent tool usage to spawn worker:**

  ```
  Agent(subagent_type: community-time-finder, description: "Find community estimates", prompt: "follow your process instructions strictly")
  ```

- **String to print once all queues are empty:** Append `", community={community_count}"` to the string to print.
