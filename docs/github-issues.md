# GitHub Issues — Dependencies, Conflicts & Sprints

This file is the single source of truth for issue scheduling. Agents read this at runtime.
Update this file as issues are closed, sprints change, or new issues are created.

## Dependency Graph

```
#76 (no dependencies — P0 bug, prioritize immediately)
#42 -> #38 -> #36 -> #14
       |
       v
     #40, #46
#26 -> #25, #27 -> #29
#23 -> #22
#74 (no dependencies)
```

An issue is READY when all upstream dependencies are closed/merged.

## File Conflict Zones

Issues touching the same file CANNOT have concurrent plan-executors:

| File | Issues | Sequence |
|------|--------|----------|
| `js_core_generator.py` | #76, #42, #38, #13, #41, #44, #46, #74 | #76 first (P0); #42 -> #38 -> rest |
| `js_awareness_generator.py` | #38, #40, #46 | #38 -> #46/#40 |
| `js_sync_generator.py` | #74 | standalone |
| `js_firebase_generator.py` | #76, #36, #14, #74 | #76 first (P0); #36 -> #14; #74 standalone |
| `html_generator.py` | #74 | standalone |
| `.github/workflows/release.yml` | #26, #28, #25, #27 | #26/#28 -> #25/#27 |
| `exceptions.py` / tests | #23, #22 | #23 -> #22 |

## Sprint Assignments

**Sprint 1** (10 issues): #76 (P0 bug — fix first), #42, #38, #36, #28, #26, #44, #13, #41, #46
**Sprint 2** (5 issues): #37, #14, #43, #23, #22
**Sprint 3** (5 issues): #25, #27, #29, #40, #74

## Priority Order (RICE scores)

0. #76 (P0 — data corruption bug, no RICE score, immediate priority)
1. #42 (360.0), 2. #38 (300.0), 3. #36 (105.0), 4. #28 (80.0), 5. #26 (80.0)
6. #44 (70.0), 7. #13 (66.7), 8. #41 (63.0), 9. #46 (56.0)
10. #37 (40.0), 11. #29 (26.7), 12. #40 (26.7), 13. #74 (24.0), 14. #22 (21.3)
15. #14 (18.7), 16. #43 (17.5), 17. #27 (13.3), 18. #25 (12.8), 19. #23 (10.7)
