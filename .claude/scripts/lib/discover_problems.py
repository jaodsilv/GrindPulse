"""Helpers for walking a per-list work folder under ``.thoughts/time-estimatives/<list>/``.

This module owns the on-disk layout knowledge shared between ``list_work.py``
(the CLI invoked by hooks to enumerate work items) and ``time_selection.py``
(the deterministic time-selection scorer). Both need to enumerate the
``p<N>/`` problem subdirectories of a work folder and, for the time-selection
phase, discover paired (eval, critique) source files inside each problem dir
across the ``std-solution/``, ``ai-solution/``, and ``community/`` subtrees.

``iter_problem_dirs(work_folder)`` returns a list of ``(problem_id, pdir)``
tuples sorted by integer id, filtered to entries matching ``p[0-9]+`` and
silently returning ``[]`` when the work folder does not exist.
``discover_problem_sources(pdir)`` returns a list of ``ProblemSource``
records (one per paired eval+critique found), each carrying the source
``name``, ``kind`` (``std``/``ai``/``community``), absolute paths to the
eval and critique files, and the relative paths used in the YAML output of
``list_work.py select-discover``.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

_PROBLEM_DIR_RE = re.compile(r"^p(\d+)$")
_NUMBERED_CRITIQUE_RE = re.compile(r"^critique-(\d+)\.md$")


@dataclass(frozen=True)
class ProblemSource:
    """One paired (eval, critique) source discovered inside a problem directory.

    Both absolute and relative paths are exposed because the two callers want
    different shapes:

    - ``time_selection.py`` reads the files directly, so it uses ``eval_abs``
      and ``critique_abs``.
    - ``list_work.py select-discover`` emits paths as YAML for downstream
      hooks that resolve them relative to ``--pdir``, so it uses
      ``eval_rel`` and ``critique_rel``.

    ``kind`` is one of ``"std"``, ``"ai"``, ``"community"``.
    """

    name: str
    kind: str
    eval_abs: str
    critique_abs: str
    eval_rel: str
    critique_rel: str


def iter_problem_dirs(work_folder: str) -> list[tuple[int, str]]:
    """Return ``(problem_id, abs_path)`` for every ``p<N>/`` subdir of ``work_folder``.

    Sorted ascending by integer id. Non-matching entries (hidden dirs, ``.bak``
    suffixes, files, anything that isn't ``p`` followed by digits) are skipped.
    Missing ``work_folder`` returns ``[]`` rather than raising — both callers
    treat absent folders as "no work".
    """
    try:
        entries = os.listdir(work_folder)
    except FileNotFoundError:
        return []
    result: list[tuple[int, str]] = []
    for entry in entries:
        m = _PROBLEM_DIR_RE.match(entry)
        if m:
            result.append((int(m.group(1)), os.path.join(work_folder, entry)))
    result.sort(key=lambda x: x[0])
    return result


def _std_sources(pdir: str) -> list[ProblemSource]:
    std_dir = os.path.join(pdir, "std-solution")
    if not os.path.isdir(std_dir):
        return []
    out: list[ProblemSource] = []
    for fname in sorted(os.listdir(std_dir)):
        m = _NUMBERED_CRITIQUE_RE.match(fname)
        if not m:
            continue
        n = m.group(1)
        eval_named = f"time-evaluation-{n}.md"
        eval_path = os.path.join(std_dir, eval_named)
        if os.path.isfile(eval_path):
            out.append(
                ProblemSource(
                    name=f"std-{n}",
                    kind="std",
                    eval_abs=eval_path,
                    critique_abs=os.path.join(std_dir, fname),
                    eval_rel=f"std-solution/{eval_named}",
                    critique_rel=f"std-solution/{fname}",
                )
            )
        elif n == "1":
            eval_fallback = os.path.join(std_dir, "time-evaluation.md")
            if os.path.isfile(eval_fallback):
                out.append(
                    ProblemSource(
                        name=f"std-{n}",
                        kind="std",
                        eval_abs=eval_fallback,
                        critique_abs=os.path.join(std_dir, fname),
                        eval_rel="std-solution/time-evaluation.md",
                        critique_rel=f"std-solution/{fname}",
                    )
                )
    return out


def _ai_sources(pdir: str) -> list[ProblemSource]:
    ai_dir = os.path.join(pdir, "ai-solution")
    if not os.path.isdir(ai_dir):
        return []
    ev = os.path.join(ai_dir, "time-evaluation.md")
    cr = os.path.join(ai_dir, "critique.md")
    if not (os.path.isfile(ev) and os.path.isfile(cr)):
        return []
    return [
        ProblemSource(
            name="ai",
            kind="ai",
            eval_abs=ev,
            critique_abs=cr,
            eval_rel="ai-solution/time-evaluation.md",
            critique_rel="ai-solution/critique.md",
        )
    ]


def _community_sources(pdir: str) -> list[ProblemSource]:
    comm_dir = os.path.join(pdir, "community")
    if not os.path.isdir(comm_dir):
        return []
    out: list[ProblemSource] = []
    for fname in sorted(os.listdir(comm_dir)):
        m = _NUMBERED_CRITIQUE_RE.match(fname)
        if not m:
            continue
        n = m.group(1)
        est_named = f"estimative-{n}.md"
        est_path = os.path.join(comm_dir, est_named)
        if os.path.isfile(est_path):
            out.append(
                ProblemSource(
                    name=f"community-{n}",
                    kind="community",
                    eval_abs=est_path,
                    critique_abs=os.path.join(comm_dir, fname),
                    eval_rel=f"community/{est_named}",
                    critique_rel=f"community/{fname}",
                )
            )
    return out


def discover_problem_sources(pdir: str) -> list[ProblemSource]:
    """Walk ``pdir`` and return every paired (eval, critique) source found.

    Order: all ``std-*`` sources (sorted by filename), then ``ai`` (if both
    eval and critique exist), then all ``community-*`` sources. Returns ``[]``
    if ``pdir`` does not exist or contains no paired sources.
    """
    return _std_sources(pdir) + _ai_sources(pdir) + _community_sources(pdir)
