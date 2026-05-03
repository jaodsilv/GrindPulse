# Phase 1: Produce

This phase manages up to **three** worker types, each with its own queue.

Possible worker agent types:
- `solutions-parser` - This agent is ALWAYS enabled.
- `coding-challenge-solver-{easy,medium,hard}` - The 3 tier-specific solver workers are enabled when `--ai-path` is present in the input Arguments. If enabled read the file `${CLAUDE_SKILL_DIR}/references/phase-1-ai.md` for the per-tier counter and spawn details.
- `community-time-finder` - This agent is enabled when `--community-path` is present in the input Arguments. If enabled read the file `${CLAUDE_SKILL_DIR}/references/phase-1-community.md`.

## Worker Spawning Order

On each loop iteration, spawn agents alternating between the enabled worker types (rotate; a type goes disabled when the hook denies with `"queue empty"`). When `--ai-path` is enabled, treat each of the three solver tiers as its own independent worker type in the rotation.

This means at some point we may have more agents of one type (for taking longer) than the others, and that is ok and expected.

Keep the order:
1. `solutions-parser`
2. `coding-challenge-solver-easy` if `--ai-path` is enabled
3. `coding-challenge-solver-medium` if `--ai-path` is enabled
4. `coding-challenge-solver-hard` if `--ai-path` is enabled
5. `community-time-finder` if `--community-path` is enabled
6. Go back to `solutions-parser`

## Standard Solutions Path

- **Worker agent type name:** `solutions-parser`
- **Counter Names to Track:**
  - **Completed worker agents counter name:** `std_count`
  - **Ongoing worker agents counter name:** `std_ongoing_count`
- **Agent tool usage to spawn worker:**

  ```
  Agent(subagent_type: solutions-parser, description: "Parse problem solutions", prompt: "follow your process instructions strictly")
  ```

- **String to print once all queues are empty:** `"produced std={std_count}"`.
