# Reference: Backtracking / Bitmask DP with Memoization

This reference covers the flat, non-nested case: a function with a clear
recursive body and a memo table. The Algorithm section is a single-level
numbered list (no sub-bullets).

Input code:

```python
class Solution:
    def minTransfers(self, transactions: List[List[int]]) -> int:
        balance_map = collections.defaultdict(int)
        for a, b, amount in transactions:
            balance_map[a] += amount
            balance_map[b] -= amount

        balance_list = [amount for amount in balance_map.values() if amount]
        n = len(balance_list)

        memo = [-1] * (1 << n)
        memo[0] = 0

        def dfs(total_mask):
            if memo[total_mask] != -1:
                return memo[total_mask]
            balance_sum, answer = 0, 0

            for i in range(n):
                cur_bit = 1 << i
                if total_mask & cur_bit:
                    balance_sum += balance_list[i]
                    answer = max(answer, dfs(total_mask ^ cur_bit))

            memo[total_mask] = answer + (balance_sum == 0)
            return memo[total_mask]

        return n - dfs((1 << n) - 1)
```

Expected output:

```markdown
## 1. Backtracking with Bitmask Memoization

### Intuition

Every transaction only matters through each person's net balance; people with a zero balance can be dropped immediately. The goal becomes: partition the remaining nonzero balances into as many subsets with sum zero as possible, since each such subset can settle internally with one fewer transfer than it has members. A bitmask over the filtered balances enumerates subsets compactly, and memoization reuses the best partitioning for each submask so the exponential search collapses to a polynomial number of distinct states.

### Algorithm

1. Build `balance_map` by adding each transaction's amount to the sender and subtracting it from the receiver.
2. Collect nonzero balances into `balance_list`, with `n` its length.
3. Initialize `memo` of size `1 << n` to `-1`, and set `memo[0] = 0` as the base case.
4. Define `dfs(total_mask)`: if `memo[total_mask]` is cached, return it; otherwise compute the best count of zero-sum subsets obtainable by removing one active person at a time.
5. Inside `dfs`, iterate each active bit `cur_bit` in `total_mask`: accumulate the subset sum into `balance_sum`, and recurse on `total_mask ^ cur_bit` to get the best answer for the smaller mask.
6. Store `answer + (balance_sum == 0)` in `memo[total_mask]` so the current mask counts as an extra zero-sum subset exactly when its active balances sum to zero.
7. Return `n - dfs((1 << n) - 1)`: the minimum number of transfers equals the count of people minus the maximum number of zero-sum subsets.

### Code (Python)

```python
class Solution:
    def minTransfers(self, transactions: List[List[int]]) -> int:
        balance_map = collections.defaultdict(int)
        for a, b, amount in transactions:
            balance_map[a] += amount
            balance_map[b] -= amount

        balance_list = [amount for amount in balance_map.values() if amount]
        n = len(balance_list)

        memo = [-1] * (1 << n)
        memo[0] = 0

        def dfs(total_mask):
            if memo[total_mask] != -1:
                return memo[total_mask]
            balance_sum, answer = 0, 0

            for i in range(n):
                cur_bit = 1 << i
                if total_mask & cur_bit:
                    balance_sum += balance_list[i]
                    answer = max(answer, dfs(total_mask ^ cur_bit))

            memo[total_mask] = answer + (balance_sum == 0)
            return memo[total_mask]

        return n - dfs((1 << n) - 1)
```

### Complexity

- Time complexity: $O(n \cdot 2^n)$
- Space complexity: $O(2^n)$

> Where $n$ is the number of people with a nonzero net balance after aggregating the transactions.
```

## Why this is good

- Intuition explains the transformation from "minimum transfers" to a subset
  cover problem; this is the essential idea that motivates the code.
- Algorithm is a flat numbered list because the inner loop doesn't have
  independent sub-actions — just one body.
- Each step names the actual identifier (`balance_map`, `memo`, `dfs`,
  `total_mask`, `cur_bit`) verbatim, in backticks.
- Complexity uses `$O(...)$` and the blockquote defines `n` because the
  problem inputs are `transactions`, not `n`.
