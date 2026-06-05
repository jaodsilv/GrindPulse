"""Deterministic time selection for the subagent-mode process-list pipeline.

Usage:
  python time_selection.py --list-name X [--ai-path] [--community-path] [--tiebreak-threshold N]

Replaces the LLM-driven `time-selection` agent with a scoring-based selector. For
each `p<N>/` subdir under `.thoughts/time-estimatives/<list-name>/`:
  1. Discover paired (eval, critique) sources (mirrors list_work.cmd_select_discover).
  2. Read each eval to extract (intermediate, advanced, top) integer minutes.
  3. Score each critique by counting bullets in `### Flaws in Justificative`,
     weighted by severity keywords.
  4. Lower score = stronger justification. Pick the winner.
  5. If only one source, or the gap to the runner-up is >= threshold, write
     `selected-times.md` directly. Otherwise enqueue a tiebreak entry for the
     LLM tiebreak agent at `<work-folder>/queues/tiebreak.yaml`.
"""

import os
import re
import subprocess
import sys
import traceback

import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from lib.discover_problems import (  # type: ignore[import-not-found]  # noqa: E402
    discover_problem_sources,
    iter_problem_dirs,
)

HIGH_SEVERITY_RE = re.compile(
    # Severity flags surfaced by the criticizer agent template.
    r"\b(bias(?:ed)?|unrealistic|incorrect|over[-\s]?confident|"
    r"under[-\s]?weight(?:s|ed)?|inconsistent|fundamental|off[-\s]?by|ignores)\b",
    re.IGNORECASE,
)
HIGH_SEVERITY_WEIGHT = 2.0
OTHER_BULLET_WEIGHT = 1.0
DEFAULT_TIEBREAK_THRESHOLD = 1.5

# Fallback used when the time-estimating skill source cannot be located/parsed.
# Kept in sync historically with the skill; only used after a stderr warning.
_TIER_LABELS_FALLBACK = {
    "intermediate": "Intermediate Max Time",
    "advanced": "Advanced Max Time",
    "top": "Top of the Crop Max Time",
}

# Path to the skill file that is the source of truth for the tier label strings.
# Resolved relative to this script: .claude/scripts/time_selection.py ->
# .claude/skills/time-estimating/SKILL.md
_SKILL_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "skills",
        "time-estimating",
        "SKILL.md",
    )
)

# Matches a single tier line in the skill's Output Format block, e.g.:
#   - Estimated Time for "Intermediate Max Time": [N] minutes
_SKILL_TIER_LINE_RE = re.compile(
    r'Estimated\s+Time\s+for\s+"([^"]+)"\s*:\s*\[N\]\s*minutes',
    re.IGNORECASE,
)


def _tier_key_for_label(label):
    """Map a parsed label string to its canonical tier key.

    The skill labels use the prefixes "Intermediate", "Advanced", and
    "Top of the Crop". The mapping is anchored on those prefixes (case-
    insensitive) so reordering or whitespace tweaks in the skill don't
    break parsing. Returns None if the label doesn't match any tier.
    """
    norm = label.strip().lower()
    if norm.startswith("intermediate"):
        return "intermediate"
    if norm.startswith("advanced"):
        return "advanced"
    if norm.startswith("top"):
        return "top"
    return None


def _load_tier_labels():
    """Parse tier label strings from the time-estimating skill file.

    Returns a dict {tier_key: label_string} matching the structure of
    `_TIER_LABELS_FALLBACK`. On any failure (file missing, all three tiers
    not found, IO error) emits a clear stderr warning naming the expected
    skill path and returns the fallback dict.
    """
    try:
        with open(_SKILL_PATH, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(
            f"warning: could not read time-estimating skill at {_SKILL_PATH}: {e}; "
            f"falling back to hardcoded TIER_LABELS",
            file=sys.stderr,
        )
        return dict(_TIER_LABELS_FALLBACK)

    parsed: dict[str, str] = {}
    for m in _SKILL_TIER_LINE_RE.finditer(text):
        label = m.group(1).strip()
        key = _tier_key_for_label(label)
        if key and key not in parsed:
            parsed[key] = label

    if set(parsed.keys()) != set(_TIER_LABELS_FALLBACK.keys()):
        print(
            f"warning: time-estimating skill at {_SKILL_PATH} did not yield all "
            f"three tier labels (got {sorted(parsed.keys())}); "
            f"falling back to hardcoded TIER_LABELS",
            file=sys.stderr,
        )
        return dict(_TIER_LABELS_FALLBACK)

    return parsed


# Module-level constant: parsed once at import. Downstream code reads from this.
TIER_LABELS = _load_tier_labels()


def _source_sort_key(name):
    """Lexicographic sort key for tie-breaking among sources with equal scores."""
    return name


def discover_sources(pdir):
    """Walk pdir to discover paired (eval + critique) source files.

    Thin wrapper around lib.discover_problems.discover_problem_sources that
    keeps the legacy dict shape used by the rest of this module.
    """
    return [
        {
            "name": s.name,
            "kind": s.kind,
            "eval": s.eval_abs,
            "critique": s.critique_abs,
        }
        for s in discover_problem_sources(pdir)
    ]


def read_estimative(path):
    """Parse a time-evaluation or estimative file.

    Returns {"intermediate": int|None, "advanced": int|None, "top": int|None}
    or None if the file cannot be read. Any tier missing in the file maps to None.
    """
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None
    except OSError as e:
        # Permission/IO error other than missing-file: caller treats None as
        # "no source data" and skips the source. Log so a misconfigured perm
        # isn't silently dropping a source.
        print(
            f"warning: could not read estimative {path}: {e}; skipping source",
            file=sys.stderr,
        )
        return None

    out: dict[str, int | None] = {"intermediate": None, "advanced": None, "top": None}
    for tier, label in TIER_LABELS.items():
        # Match e.g.: Estimated Time for "Intermediate Max Time": 20 minutes
        pattern = re.compile(
            r'Estimated\s+Time\s+for\s+"' + re.escape(label) + r'"\s*:\s*(\d+)\s*min',
            re.IGNORECASE,
        )
        m = pattern.search(text)
        if m:
            out[tier] = int(m.group(1))
    return out


def expand_community(times):
    """Fill missing tiers in a partial community estimative using the canonical ratios.

    Ratios: intermediate = round(advanced * 1.5), top = round(advanced * 0.6).
    Returns a dict with all three tiers populated, or None if no anchor available.
    """
    if times is None:
        return None
    inter = times.get("intermediate")
    adv = times.get("advanced")
    top = times.get("top")

    if inter is None and adv is None and top is None:
        return None

    if adv is None:
        if top is not None:
            adv = round(top / 0.6)
        elif inter is not None:
            adv = round(inter / 1.5)

    if adv is None:
        return None

    if inter is None:
        inter = round(adv * 1.5)
    if top is None:
        top = round(adv * 0.6)

    return {"intermediate": int(inter), "advanced": int(adv), "top": int(top)}


def read_critique(path):
    """Read the critique file content. Returns text or None if missing/unreadable."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None
    except OSError as e:
        print(
            f"warning: could not read critique {path}: {e}; treating as missing",
            file=sys.stderr,
        )
        return None


def score_critique(text):
    """Sum weighted bullet count under '### Flaws in Justificative'.

    Returns a float. Missing/empty section returns 0 (= strongest possible).
    """
    if not text:
        return 0.0

    # Find the Flaws section; it may be the only section in the file.
    flaws_match = re.search(
        r"###\s+Flaws\s+in\s+Justificative\s*\n",
        text,
        re.IGNORECASE,
    )
    if not flaws_match:
        return 0.0

    section_start = flaws_match.end()
    # Section ends at next heading or EOF.
    next_heading = re.search(r"\n#{1,6}\s+", text[section_start:])
    if next_heading:
        section_text = text[section_start : section_start + next_heading.start()]
    else:
        section_text = text[section_start:]

    score = 0.0
    for line in section_text.splitlines():
        stripped = line.lstrip()
        if not (stripped.startswith("- ") or stripped.startswith("* ")):
            continue
        bullet_body = stripped[2:]
        if HIGH_SEVERITY_RE.search(bullet_body):
            score += HIGH_SEVERITY_WEIGHT
        else:
            score += OTHER_BULLET_WEIGHT
    return score


def evaluate_source(src):
    """Read eval + critique for a source and return enriched dict.

    Returns {"name", "times", "score", "parse_error": bool} or None if eval
    cannot be parsed at all (no source data). Parse failures on std/ai still
    return a record with score penalty so the source ranks lower.
    """
    raw_times = read_estimative(src["eval"])
    times = None
    parse_error = False

    if src["kind"] == "community":
        times = expand_community(raw_times)
        if times is None:
            return None
    else:
        if raw_times is None:
            return None
        if (
            raw_times.get("intermediate") is None
            or raw_times.get("advanced") is None
            or raw_times.get("top") is None
        ):
            parse_error = True
            # Fill missing tiers with placeholders so downstream rationale text
            # still has values; this source ranks worse via the penalty below.
            times = {
                "intermediate": raw_times.get("intermediate") or 0,
                "advanced": raw_times.get("advanced") or 0,
                "top": raw_times.get("top") or 0,
            }
        else:
            inter_v = raw_times["intermediate"]
            adv_v = raw_times["advanced"]
            top_v = raw_times["top"]
            assert inter_v is not None and adv_v is not None and top_v is not None
            times = {
                "intermediate": int(inter_v),
                "advanced": int(adv_v),
                "top": int(top_v),
            }

    critique_text = read_critique(src["critique"])
    score = score_critique(critique_text)
    if parse_error:
        # Treat eval-parse failure as one extra synthetic "other" flaw.
        score += OTHER_BULLET_WEIGHT

    return {
        "name": src["name"],
        "times": times,
        "score": score,
        "parse_error": parse_error,
    }


def select_winner(sources_with_scores, threshold):
    """Choose the best source (lowest score) and decide direct vs tiebreak.

    Returns (decision, winner_dict_or_None, rationale_text).
    decision is "direct" or "tiebreak".
    """
    if not sources_with_scores:
        return ("none", None, "no scorable sources")

    ranked = sorted(
        sources_with_scores,
        key=lambda s: (s["score"], _source_sort_key(s["name"])),
    )

    best = ranked[0]
    if len(ranked) == 1:
        rationale = f"single source: {best['name']} (critique score {best['score']:g})."
        return ("direct", best, rationale)

    runner = ranked[1]
    gap = runner["score"] - best["score"]
    if gap >= threshold:
        rationale = (
            f"lowest critique score: {best['name']} at {best['score']:g} "
            f"vs runner-up {runner['name']} at {runner['score']:g} "
            f"(gap {gap:g} >= threshold {threshold:g})."
        )
        return ("direct", best, rationale)

    rationale = (
        f"ambiguous: {best['name']} {best['score']:g} vs "
        f"{runner['name']} {runner['score']:g} (gap {gap:g} < {threshold:g})"
    )
    return ("tiebreak", best, rationale)


def emit_selected_times(pdir, source_name, times, rationale):
    """Write selected-times.md to pdir using the canonical schema."""
    content = (
        "## Selected Times\n"
        "\n"
        f"<intermediate>{int(times['intermediate'])}</intermediate>\n"
        f"<advanced>{int(times['advanced'])}</advanced>\n"
        f"<top>{int(times['top'])}</top>\n"
        f"<best-justification-source>{source_name}</best-justification-source>\n"
        "\n"
        "### Rationale\n"
        "\n"
        f"{rationale}\n"
    )
    out_path = os.path.join(pdir, "selected-times.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


def invoke_write_tsv(work_folder, problem_id, source, times):
    """Run write_tsv.py for a direct emission. Mirrors the SubagentStop hook's invocation.

    work_folder: e.g. ".thoughts/time-estimatives/uber" — list name is its basename.
    Raises RuntimeError if the subprocess fails.
    """
    list_name = os.path.basename(os.path.normpath(work_folder))
    here = os.path.dirname(os.path.abspath(__file__))
    write_tsv = os.path.join(here, "write_tsv.py")
    cmd = [
        sys.executable,
        write_tsv,
        "--list-name",
        list_name,
        "--problem-id",
        str(problem_id),
        "--intermediate",
        str(times["intermediate"]),
        "--advanced",
        str(times["advanced"]),
        "--top",
        str(times["top"]),
        "--source",
        source,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        raise RuntimeError(f"write_tsv subprocess failed: {e}") from e
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip().replace("\n", " ")
        raise RuntimeError(f"write_tsv exited {proc.returncode}: {stderr}")


def append_tiebreak(work_folder, problem_id, candidate_sources):
    """Append (idempotently) a tiebreak entry to <work-folder>/queues/tiebreak.yaml.

    candidate_sources: list of source names (e.g. ["std-0", "std-1", "ai"]) that
    the deterministic scorer could not separate. The LLM tiebreak agent reads
    these from the work-item to know which (eval, critique) pairs to compare.
    """
    queues_dir = os.path.join(work_folder, "queues")
    os.makedirs(queues_dir, exist_ok=True)
    path = os.path.join(queues_dir, "tiebreak.yaml")

    existing = []
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or []
            if isinstance(loaded, list):
                existing = [item for item in loaded if isinstance(item, dict)]
        except (OSError, yaml.YAMLError) as e:
            print(
                f"warning: could not read existing tiebreak queue {path}: {e}; "
                f"replacing with fresh list",
                file=sys.stderr,
            )
            existing = []

    for item in existing:
        if item.get("problem-id") == problem_id:
            return

    existing.append(
        {
            "problem-id": int(problem_id),
            "candidate-sources": list(candidate_sources),
        }
    )
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(existing, f, sort_keys=False)


def process_problem(pid, pdir, work_folder, threshold):
    """Process one problem dir. Returns one of:
    {"direct", "tiebreak", "skip-already", "skip-no-sources", "error"}.
    """
    if os.path.isfile(os.path.join(pdir, "selected-times.md")):
        return "skip-already"

    sources = discover_sources(pdir)
    if not sources:
        return "skip-no-sources"

    scored = []
    for src in sources:
        try:
            rec = evaluate_source(src)
        except Exception as e:
            print(
                f"warning: p{pid} source {src.get('name', '?')} evaluation failed: {e}",
                file=sys.stderr,
            )
            continue
        if rec is not None:
            scored.append(rec)

    if not scored:
        print(
            f"warning: p{pid} has sources but none could be scored",
            file=sys.stderr,
        )
        return "skip-no-sources"

    decision, winner, rationale = select_winner(scored, threshold)

    if decision == "direct":
        assert winner is not None
        try:
            emit_selected_times(pdir, winner["name"], winner["times"], rationale)
        except OSError as e:
            print(f"warning: p{pid} failed to write selected-times.md: {e}", file=sys.stderr)
            return "error"
        try:
            invoke_write_tsv(work_folder, pid, winner["name"], winner["times"])
        except RuntimeError as e:
            print(f"warning: p{pid} write_tsv failed: {e}", file=sys.stderr)
            return "error"
        return "direct"

    if decision == "tiebreak":
        try:
            candidate_names = [rec["name"] for rec in scored]
            append_tiebreak(work_folder, pid, candidate_names)
        except OSError as e:
            print(f"warning: p{pid} failed to append tiebreak: {e}", file=sys.stderr)
            return "error"
        return "tiebreak"

    return "error"


def _parse_args(argv):
    """sys.argv-style parsing matching list_work.py conventions.

    --ai-path and --community-path are accepted for CLI compatibility with
    list_work.py callers but are not consumed: discovery walks every problem
    dir and infers source kinds from filesystem contents.
    """
    list_name = None
    threshold = DEFAULT_TIEBREAK_THRESHOLD

    for i, a in enumerate(argv):
        if a == "--list-name" and i + 1 < len(argv):
            list_name = argv[i + 1]
        elif a == "--tiebreak-threshold" and i + 1 < len(argv):
            try:
                threshold = float(argv[i + 1])
            except ValueError:
                print(
                    f"--tiebreak-threshold must be a number, got {argv[i + 1]!r}",
                    file=sys.stderr,
                )
                sys.exit(2)

    if not list_name:
        print(
            "Usage: time_selection.py --list-name X "
            "[--ai-path] [--community-path] [--tiebreak-threshold N]",
            file=sys.stderr,
        )
        sys.exit(1)

    return list_name, threshold


def main():
    list_name, threshold = _parse_args(sys.argv[1:])

    work_folder = f".thoughts/time-estimatives/{list_name}"
    if not os.path.isdir(work_folder):
        print(f"work folder not found: {work_folder}", file=sys.stderr)
        sys.exit(1)

    counters = {
        "processed": 0,
        "direct": 0,
        "tiebreak": 0,
        "skip-already": 0,
        "skip-no-sources": 0,
        "error": 0,
    }

    for pid, pdir in iter_problem_dirs(work_folder):
        counters["processed"] += 1
        try:
            result = process_problem(pid, pdir, work_folder, threshold)
        except Exception as e:
            print(
                f"warning: p{pid} crashed: {e}\n{traceback.format_exc()}",
                file=sys.stderr,
            )
            counters["error"] += 1
            continue
        counters[result] = counters.get(result, 0) + 1

    print(f"processed: {counters['processed']}")
    print(f"direct-emissions: {counters['direct']}")
    print(f"tiebreaks-queued: {counters['tiebreak']}")
    print(f"skipped (already-selected): {counters['skip-already']}")
    print(f"skipped (no-sources): {counters['skip-no-sources']}")
    if counters["error"]:
        print(f"errors: {counters['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
