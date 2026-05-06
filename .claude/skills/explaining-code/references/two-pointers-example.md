# Reference: Two Pointers with Nested Steps

This is a reference for the exact format to produce when the Algorithm is a
conditional loop with several sub-actions per iteration.

Input code:

```python
class Solution:
    def intervalIntersection(self, firstList: List[List[int]], secondList: List[List[int]]) -> List[List[int]]:
        res = []
        i = j = 0
        while i < len(firstList) and j < len(secondList):
            startA, endA = firstList[i]
            startB, endB = secondList[j]

            start = max(startA, startB)
            end = min(endA, endB)

            if start <= end:
                res.append([start, end])

            if endA < endB:
                i += 1
            else:
                j += 1

        return res
```

Expected output:

```markdown
## 3. Two Pointers

### Intuition

Since both interval lists are sorted and disjoint within themselves, we can use two pointers to efficiently find intersections. At each step, we compare the current interval from each list. If they overlap, we record the intersection. Then we advance the pointer for whichever interval ends first, since that interval cannot intersect with any future intervals from the other list. This eliminates unnecessary comparisons and processes each interval exactly once.

### Algorithm

1. Initialize two pointers `i` and `j` to `0`, and an empty result list.
2. While both pointers are within bounds:
   - Get the current intervals: `[startA, endA]` from `firstList[i]` and `[startB, endB]` from `secondList[j]`.
   - Compute the potential intersection: `start = max(startA, startB)` and `end = min(endA, endB)`.
   - If `start <= end`, add `[start, end]` to the result.
   - Advance the pointer for the interval that ends first (if `endA < endB`, increment `i`; otherwise, increment `j`).
3. Return the result list.

### Code (Python)

```python
class Solution:
    def intervalIntersection(self, firstList: List[List[int]], secondList: List[List[int]]) -> List[List[int]]:
        res = []
        i = j = 0
        while i < len(firstList) and j < len(secondList):
            startA, endA = firstList[i]
            startB, endB = secondList[j]

            start = max(startA, startB)
            end = min(endA, endB)

            if start <= end:
                res.append([start, end])

            if endA < endB:
                i += 1
            else:
                j += 1

        return res
```

### Complexity

- Time complexity: $O(m + n)$
- Space complexity:
   - $O(1)$ extra space.
   - $O(m + n)$ for the output list.

> Where $m$ and $n$ are the sizes of the arrays `firstList` and `secondList`, respectively.
```

## Why this is good

- Intuition connects the approach to the problem's invariants (sorted,
  disjoint). It does NOT describe line-by-line behavior.
- Algorithm is a numbered list; step 2 has nested sub-steps because the loop
  body has multiple distinct actions. Nesting is 3-space indented with `- `.
- Every variable name (`i`, `j`, `startA`, etc.) is in backticks.
- Complexity uses `$O(...)$` LaTeX delimiters.
- The blockquote defines `m` and `n` because they are not obvious from the
  problem statement.
