#!/usr/bin/env python3
"""SubagentStop hook for community-time-finder.

Reads the most recently written `community/estimative-{n}.md` written by the
agent and fills in tier proportions (intermediate / advanced / top minutes)
into its YAML front-matter, based on `level` and `time-minutes`.

Multiplier interpretation:
  - INTER_MULT = 0.7 — advanced = intermediate * 0.7
                       (advanced is faster than intermediate; intermediate ≈ 1.43× advanced)
  - TOP_MULT   = 1/1.5 ≈ 0.667 — top = advanced * 0.667
                       (top is faster than advanced; advanced ≈ 1.5× top)

Safe to run for ALL SubagentStop events: exits 0 silently when the agent is
not a community-time-finder, or when anything goes wrong.
"""

import json
import os
import re
import sys

INTER_MULT = 0.7
TOP_MULT = 1.0 / 1.5


def log_err(msg):
    sys.stderr.write(f"[subagent_stop_community_finder] {msg}\n")


def _is_community_finder(payload):
    """Return True if this SubagentStop is for a community-time-finder agent."""
    for key in ("agent_type", "subagent_type", "name"):
        val = payload.get(key)
        if isinstance(val, str) and "community-time-finder" in val:
            return True
        # Some payloads use community-times-finder-pN naming; treat those as
        # legacy and ignore (they don't write the new front-matter format).
    return False


def _find_pdir_from_transcript(transcript_path):
    """Scan the agent transcript for the injected <pdir>...</pdir> tag."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return None
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                # Walk all string values looking for <pdir>X</pdir>.
                for s in _iter_strings(rec):
                    m = re.search(r"<pdir>([^<]+)</pdir>", s)
                    if m:
                        return m.group(1).strip()
    except Exception as e:
        log_err(f"failed to scan transcript {transcript_path}: {e}")
    return None


def _iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_strings(v)


def _find_pdir_from_message(msg):
    """Search the last_assistant_message for a path containing /community/estimative-*.md."""
    if not msg or not isinstance(msg, str):
        return None
    m = re.search(r"([^\s`'\"]+)/community/estimative-\d+\.md", msg)
    if m:
        return m.group(1)
    return None


def _most_recent_estimative(pdir):
    """Return path to the most recently mtime'd estimative-{n}.md in {pdir}/community/."""
    cdir = os.path.join(pdir, "community")
    if not os.path.isdir(cdir):
        return None
    candidates = []
    for name in os.listdir(cdir):
        if re.match(r"^estimative-\d+\.md$", name):
            full = os.path.join(cdir, name)
            try:
                candidates.append((os.path.getmtime(full), full))
            except OSError:
                continue
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def _parse_frontmatter(text):
    """Return (frontmatter_dict_or_None, body_text)."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    fm_text = m.group(1)
    body = text[m.end() :]
    try:
        import yaml
    except ImportError:
        log_err("PyYAML not installed; cannot parse front-matter")
        return None, text
    try:
        data = yaml.safe_load(fm_text) or {}
    except Exception as e:
        log_err(f"front-matter parse error: {e}")
        return None, text
    if not isinstance(data, dict):
        return None, text
    return data, body


def _serialize(fm, body):
    try:
        import yaml
    except ImportError:
        log_err("PyYAML not installed; cannot serialize front-matter")
        return None
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm_text}\n---\n{body if body.startswith(chr(10)) else (chr(10) + body if body else '')}"


def _compute_tiers(level, time_minutes):
    """Return dict with intermediate / advanced / top minutes (ints)."""
    t = float(time_minutes)
    lv = (level or "").strip().lower()
    if lv == "intermediate":
        intermediate = round(t)
        advanced = round(t * INTER_MULT)
        top = round(advanced * TOP_MULT)
    elif lv == "top":
        top = round(t)
        advanced = round(t / TOP_MULT)
        intermediate = round(advanced / INTER_MULT)
    else:
        # Default to Advanced for missing/unknown level.
        advanced = round(t)
        intermediate = round(advanced / INTER_MULT)
        top = round(advanced * TOP_MULT)
    return {"intermediate": int(intermediate), "advanced": int(advanced), "top": int(top)}


def main():
    try:
        raw = sys.stdin.read()
    except Exception as e:
        log_err(f"failed to read stdin: {e}")
        return 0

    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except Exception as e:
        log_err(f"payload not valid JSON: {e}")
        return 0

    if not isinstance(payload, dict):
        return 0

    if not _is_community_finder(payload):
        return 0

    transcript_path = payload.get("agent_transcript_path") or payload.get("transcript_path")
    last_msg = payload.get("last_assistant_message") or ""

    pdir = _find_pdir_from_transcript(transcript_path)
    if not pdir:
        pdir = _find_pdir_from_message(last_msg)
    if not pdir:
        log_err("could not determine pdir from transcript or last_assistant_message")
        return 0

    target = _most_recent_estimative(pdir)
    if not target:
        log_err(f"no estimative-N.md files found under {pdir}/community/")
        return 0

    try:
        with open(target, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        log_err(f"failed to read {target}: {e}")
        return 0

    fm, body = _parse_frontmatter(text)
    if fm is None:
        log_err(f"{target}: missing or unparseable YAML front-matter")
        return 0

    level = fm.get("level")
    time_minutes = fm.get("time-minutes")
    if time_minutes is None:
        log_err(f"{target}: front-matter missing 'time-minutes'")
        return 0

    try:
        tiers = _compute_tiers(level, time_minutes)
    except Exception as e:
        log_err(f"{target}: failed to compute tiers: {e}")
        return 0

    fm["intermediate"] = tiers["intermediate"]
    fm["advanced"] = tiers["advanced"]
    fm["top"] = tiers["top"]

    new_text = _serialize(fm, body)
    if new_text is None:
        return 0

    try:
        with open(target, "w", encoding="utf-8") as f:
            f.write(new_text)
    except Exception as e:
        log_err(f"failed to write {target}: {e}")
        return 0

    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as e:
        log_err(f"unexpected error: {e}")
        rc = 0
    sys.exit(rc or 0)
