"""Standalone script: pop next problem from remaining.yaml, create folder, fetch content.

Reads .active-list.yaml to find work folder. Prints XML result to stdout.
Exit 0 on success or empty list, exit 1 on error.

CLI flags:
    --problem-id N  Problem counter emitted in the success XML as
                    <problem-id>. Defaults to 1.
"""
# ruff: noqa: E402

import argparse
import os
import re
import shutil
import sys
import traceback
from urllib.parse import urlparse

import yaml
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from lib import status_io  # type: ignore[import-not-found]
from lib.active_list import load as _load_active_list_raw  # type: ignore[import-not-found]
from lib.file_lock import file_lock  # type: ignore[import-not-found]

_ALLOWED_NAV_HOSTS = frozenset({"neetcode.io"})


def _validate_nav_url(url: str) -> None:
    """Validate that a URL is safe to feed into Playwright's page.goto.

    Rejects non-http(s) schemes (file://, chrome://, javascript:, ...) and
    empty hosts, and enforces the allowlist of expected hosts. Raises
    ValueError on any failure, before navigation.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"refusing to navigate to non-http(s) URL: {url}")
    if not parsed.netloc:
        raise ValueError(f"refusing to navigate to non-http(s) URL: {url}")
    host = parsed.hostname or ""
    if host not in _ALLOWED_NAV_HOSTS:
        raise ValueError(f"refusing to navigate to non-http(s) URL: {url}")


def _load_active_list() -> dict:
    cfg = _load_active_list_raw()
    if not cfg:
        raise OSError("could not load .active-list.yaml (see stderr)")
    return cfg


def _is_row_filled(list_path: str, problem_name: str) -> bool:
    try:
        with open(list_path, encoding="utf-8") as f:
            for line in f:
                cols = line.strip().split("\t")
                if len(cols) >= 5 and cols[0].strip() == problem_name:
                    try:
                        t2 = int(cols[2].strip() or "0")
                        t3 = int(cols[3].strip() or "0")
                        t4 = int(cols[4].strip() or "0")
                    except ValueError as e:
                        # Non-integer time column: treat row as not-yet-filled
                        # so the caller fetches and overwrites with valid data.
                        print(
                            f"warning: malformed time columns for {problem_name!r} "
                            f"in {list_path}: {e}; treating as not-filled",
                            file=sys.stderr,
                        )
                        return False
                    return t2 > 0 and t3 > 0 and t4 > 0
    except OSError as e:
        # Best-effort: if the source TSV is unreadable we treat the row as
        # not-yet-filled so the caller proceeds to fetch. Log so a misconfigured
        # path doesn't fail silently across the whole run.
        print(
            f"warning: could not read {list_path} to check row {problem_name!r}: {e}",
            file=sys.stderr,
        )
    return False


def _next_id(work_folder: str) -> str:
    id_file = os.path.join(work_folder, "next-id.txt")
    with file_lock(id_file):
        try:
            with open(id_file, encoding="utf-8") as f:
                current = int(f.read().strip())
        except (OSError, ValueError):
            current = 1
        with open(id_file, "w", encoding="utf-8") as f:
            f.write(str(current + 1))
        return str(current)


def _find_existing_pn(work_folder: str, problem_name: str):
    """Return lowest pN suffix string where metadata['problem-name'] == problem_name, or None."""
    import glob as _glob

    matches = []
    for meta_path in _glob.glob(os.path.join(work_folder, "p*", "metadata.yaml")):
        try:
            with open(meta_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and data.get("problem-name") == problem_name:
                pn_dir = os.path.basename(os.path.dirname(meta_path))  # e.g. "p3"
                matches.append(int(pn_dir[1:]))
        except (OSError, yaml.YAMLError, ValueError) as e:
            print(
                f"warning: could not parse {meta_path} while searching for {problem_name!r}: {e}",
                file=sys.stderr,
            )
            continue
    if not matches:
        return None
    return str(min(matches))


def _files_complete(problem_folder: str) -> bool:
    """True iff metadata.yaml, problem.md, standard-solutions.md all exist with size > 0."""
    for fname in ("metadata.yaml", "problem.md", "standard-solutions.md"):
        p = os.path.join(problem_folder, fname)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            return False
    return True


def _find_problem_in_tsv(list_path: str, problem_name: str) -> dict:
    try:
        with open(list_path, encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[1:]:
            cols = line.strip().split("\t")
            if len(cols) >= 7 and cols[0].strip() == problem_name:
                return {
                    "problem-name": cols[0].strip(),
                    "nominal-difficulty": cols[1].strip(),
                    "problem-pattern": cols[5].strip(),
                    "link": cols[6].strip(),
                }
    except OSError as e:
        # If the source TSV cannot be read, return {} so the caller surfaces
        # the missing-link as a fetch error; don't swallow the failure.
        print(
            f"warning: could not read {list_path} for problem lookup {problem_name!r}: {e}",
            file=sys.stderr,
        )
    return {}


def _compute_solutions_link(link: str) -> str:
    slug_match = re.search(r"/problems/([^?/]+)", link)
    if slug_match:
        slug = slug_match.group(1)
        return f"https://neetcode.io/problems/{slug}/solutions"
    return ""


def _extract_description(body_text: str, title: str) -> str:
    """Extract problem description from the Question tab body text.

    The body has a structure like:
      ... nav links ...
      (xxx)          # maybe discuss count
      {Title}
      {Difficulty}
      Topics
      Company Tags
      Hints

      {description with examples and constraints}

      Topics
      Recommended Time & Space Complexity
      ...
    """
    lines = body_text.split("\n")
    # Find the line that equals the title after nav
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == title:
            start_idx = i
            break
    if start_idx is None:
        return ""

    # After title: difficulty, Topics, Company Tags, Hints, [blank], then description
    # Skip forward to the first blank line after "Hints" or "Company Tags"
    desc_start = None
    for i in range(start_idx + 1, min(start_idx + 10, len(lines))):
        s = lines[i].strip()
        if s in ("Hints", "Company Tags") or (s == "" and i > start_idx + 2):
            # look for a blank then content
            for j in range(i, len(lines)):
                if lines[j].strip() == "" and j + 1 < len(lines) and lines[j + 1].strip():
                    desc_start = j + 1
                    break
            if desc_start is not None:
                break
    if desc_start is None:
        desc_start = start_idx + 1

    # Find end: the second occurrence of "Topics" (trailing section) OR
    # "Recommended Time & Space Complexity" OR "Acceptance Rate" OR "Solution 1"
    desc_end = len(lines)
    end_markers = (
        "Recommended Time & Space Complexity",
        "Acceptance Rate",
        "Seen this question in a real interview?",
    )
    topics_seen_before = False
    # "Topics" appears before the description too; we want the second one
    for i in range(start_idx + 1, desc_start):
        if lines[i].strip() == "Topics":
            topics_seen_before = True
            break
    for i in range(desc_start, len(lines)):
        s = lines[i].strip()
        if s in end_markers:
            desc_end = i
            break
        if topics_seen_before and s == "Topics":
            desc_end = i
            break

    desc_lines = lines[desc_start:desc_end]
    # Strip trailing blank lines
    while desc_lines and desc_lines[-1].strip() == "":
        desc_lines.pop()
    return "\n".join(desc_lines).strip()


_APPROACH_EXTRACTION_JS = r"""
() => {
    // Walk document in order; h2 with '^\d+\. ' starts a new approach; h3s within
    // set the active section; collect outerHTML of content nodes into that section.
    const out = [];
    let cur = null;
    let cursor = null;
    const section_tags = new Set([
        'P', 'OL', 'UL', 'BLOCKQUOTE', 'PRE', 'DIV'
    ]);
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let node = walker.nextNode();
    while (node) {
        const tag = node.tagName;
        const text = (node.innerText || '').trim();
        if (tag === 'H2' && /^\d+\.\s+\S/.test(text)) {
            if (cur) out.push(cur);
            cur = {
                title: text.replace(/^\d+\.\s*/, ''),
                intuition_html: '',
                algorithm_html: '',
                complexity_html: '',
            };
            cursor = null;
            node = walker.nextNode();
            continue;
        }
        if (tag === 'H3' && cur) {
            if (text === 'Intuition') cursor = 'intuition_html';
            else if (text === 'Algorithm') cursor = 'algorithm_html';
            else if (text === 'Time & Space Complexity') cursor = 'complexity_html';
            else cursor = null;
            node = walker.nextNode();
            continue;
        }
        // Exit section on widgets
        if (tag === 'APP-ALGO-VISUALIZER' || tag === 'APP-CODE-TABS') {
            cursor = null;
            // skip subtree
            let skip = node;
            do { skip = walker.nextNode(); } while (skip && node.contains(skip));
            node = skip;
            continue;
        }
        if (cur && cursor && section_tags.has(tag)) {
            // Only capture top-level content blocks: skip if parent is already captured
            // Heuristic: if parent of this node is inside the already-collected HTML
            // we skip. Simpler: only capture if parent is not one of the section tags.
            const parent = node.parentElement;
            const parentTag = parent ? parent.tagName : '';
            if (parentTag !== 'OL' && parentTag !== 'UL' && parentTag !== 'LI'
                && parentTag !== 'BLOCKQUOTE' && parentTag !== 'P') {
                cur[cursor] += node.outerHTML;
                // skip subtree to avoid double-capture
                let skip = node;
                do { skip = walker.nextNode(); } while (skip && node.contains(skip));
                node = skip;
                continue;
            }
        }
        node = walker.nextNode();
    }
    if (cur) out.push(cur);
    return out;
}
"""


def _html_to_md(html: str) -> str:
    """Render a small subset of HTML (p, ol, ul, li, code, blockquote, span.katex)
    into clean markdown."""
    if not html or not html.strip():
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for katex in soup.select("span.katex"):
        ann = katex.find("annotation")
        if ann:
            katex.replace_with(NavigableString(f"${ann.get_text(strip=True)}$"))
        else:
            katex.replace_with(NavigableString(katex.get_text(" ", strip=True)))
    parts = [_render_node(c, 0) for c in soup.children]
    body = "\n\n".join(p.rstrip() for p in parts if p and p.strip())
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def _render_node(node, indent: int) -> str:
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", str(node))
    if not isinstance(node, Tag):
        return ""
    name = (node.name or "").lower()
    if name in ("ol", "ul"):
        return _render_list(node, indent, ordered=(name == "ol"))
    if name == "p":
        return _render_inline(node)
    if name == "blockquote":
        inner_parts = [_render_node(c, indent) for c in node.children]
        inner = "\n".join(p.rstrip() for p in inner_parts if p and p.strip())
        return "\n".join("> " + ln if ln.strip() else ">" for ln in inner.splitlines())
    if name in ("div", "span"):
        return "".join(_render_node(c, indent) for c in node.children)
    if name == "code":
        return f"`{node.get_text()}`"
    if name in ("strong", "b"):
        return f"**{node.get_text(' ', strip=True)}**"
    if name in ("em", "i"):
        return f"*{node.get_text(' ', strip=True)}*"
    if name == "br":
        return "\n"
    return "".join(_render_node(c, indent) for c in node.children)


def _render_list(node: Tag, indent: int, ordered: bool) -> str:
    items = [c for c in node.children if isinstance(c, Tag) and c.name == "li"]
    out = []
    for i, li in enumerate(items):
        prefix = f"{i + 1}. " if ordered else "- "
        out.append(_render_li(li, prefix, indent))
    return "\n".join(out)


def _render_li(li: Tag, prefix: str, indent: int) -> str:
    text_parts = []
    nested = []
    for child in li.children:
        if isinstance(child, Tag) and child.name in ("ol", "ul"):
            nested.append(_render_list(child, indent + 1, ordered=(child.name == "ol")))
        else:
            text_parts.append(_render_node(child, indent))
    text = re.sub(r"\s+", " ", "".join(text_parts)).strip()
    pad = "   " * indent
    head = f"{pad}{prefix}{text}"
    if not nested:
        return head
    return head + "\n" + "\n".join(nested)


def _render_inline(node: Tag) -> str:
    out = []
    for child in node.children:
        out.append(_render_node(child, 0))
    return re.sub(r"\s+", " ", "".join(out)).strip()


def _parse_solutions(body_text: str, code_blocks: list) -> list:
    """Parse the Solution tab body into approach dicts.

    Returns list of dicts with keys: title, intuition, algorithm, code, time, space.
    """
    lines = body_text.split("\n")
    # Find approach headings: lines matching ^\d+\. \S
    approach_indices = []
    for i, line in enumerate(lines):
        if re.match(r"^\d+\.\s+\S", line.strip()):
            # sanity: must have a known following section ("Intuition") within ~10 lines
            for j in range(i + 1, min(i + 15, len(lines))):
                if lines[j].strip() == "Intuition":
                    approach_indices.append((i, line.strip()))
                    break

    approaches = []
    for idx, (line_idx, heading) in enumerate(approach_indices):
        end_idx = approach_indices[idx + 1][0] if idx + 1 < len(approach_indices) else len(lines)
        section = lines[line_idx:end_idx]

        # Parse title (strip leading number)
        m = re.match(r"^(\d+)\.\s+(.+)$", heading)
        title = m.group(2) if m else heading

        # Find Intuition block
        intuition = ""
        algorithm = ""
        time_c = ""
        space_c = ""

        # Find Intuition start/end and Algorithm start/end
        try:
            intu_i = next(i for i, ln in enumerate(section) if ln.strip() == "Intuition")
        except StopIteration:
            intu_i = None
        try:
            algo_i = next(i for i, ln in enumerate(section) if ln.strip() == "Algorithm")
        except StopIteration:
            algo_i = None
        try:
            tsc_i = next(
                i for i, ln in enumerate(section) if ln.strip() == "Time & Space Complexity"
            )
        except StopIteration:
            tsc_i = None

        if intu_i is not None:
            end = algo_i if algo_i is not None else tsc_i if tsc_i is not None else len(section)
            intuition = "\n".join(section[intu_i + 1 : end]).strip()

        if algo_i is not None:
            end = tsc_i if tsc_i is not None else len(section)
            algorithm = "\n".join(section[algo_i + 1 : end]).strip()
            # Stop algorithm at the first visualization-looking line or the code block
            # Algorithm section often ends when we hit a blank then visual widget labels
            # Heuristic: truncate at first occurrence of "Step " or a line with only caps/numbers pattern
            algo_lines = algorithm.split("\n")
            cut = len(algo_lines)
            for i, ln in enumerate(algo_lines):
                if re.match(r"^Step \d+\s*/\s*\d+", ln.strip()):
                    cut = i
                    break
            algorithm = "\n".join(algo_lines[:cut]).strip()
            # Also strip trailing blank
            while algorithm.endswith("\n"):
                algorithm = algorithm[:-1]

        if tsc_i is not None:
            # Look for "Time complexity:" and "Space complexity:"
            tsc_block = "\n".join(section[tsc_i + 1 :])
            tm = re.search(r"Time complexity:\s*(.+?)(?:Space complexity:|$)", tsc_block, re.DOTALL)
            sm = re.search(r"Space complexity:\s*(.+)$", tsc_block, re.DOTALL)
            if tm:
                time_c = re.sub(r"\s+", " ", tm.group(1)).strip()
            if sm:
                space_c = re.sub(r"\s+", " ", sm.group(1)).strip()
                # Trim at any trailing next-approach garbage
                space_c = space_c.split("Where")[0].strip()

        code = code_blocks[idx] if idx < len(code_blocks) else ""
        approaches.append(
            {
                "title": title,
                "intuition": intuition,
                "algorithm": algorithm,
                "code": code,
                "time": time_c,
                "space": space_c,
            }
        )

    if not approaches and code_blocks:
        for i, code in enumerate(code_blocks, 1):
            approaches.append(
                {
                    "title": f"Solution {i}",
                    "intuition": "",
                    "algorithm": "",
                    "code": code,
                    "time": "",
                    "space": "",
                }
            )

    return approaches


def _fetch_problem_content(link: str) -> tuple:
    """Fetch problem description and solutions via playwright.

    Returns (problem_md, solutions_md, status) where status is "ok" or "pro_gated".
    Raises on error (caller handles).
    """
    if not link:
        return ("", "", "ok")

    slug_match = re.search(r"/problems/([^?/]+)", link)
    if not slug_match:
        return ("", "", "ok")

    slug = slug_match.group(1)
    url = f"https://neetcode.io/problems/{slug}/solutions"

    from playwright.sync_api import sync_playwright

    profile_path = os.path.join(".claude", "scripts", ".neetcode-profile")
    has_auth = os.path.isdir(profile_path)

    with sync_playwright() as p:
        browser: object | None = None
        if has_auth:
            context = p.chromium.launch_persistent_context(profile_path, headless=True)
        else:
            browser = p.chromium.launch(headless=True, channel="msedge")
            context = browser.new_context()
        try:
            page = context.new_page()
            _validate_nav_url(url)
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1500)

            body_text = page.evaluate("() => document.body.innerText")

            # Session expired detection: we expected auth to work but the page
            # still shows the pro paywall.
            if has_auth and "Get Pro Access" in body_text:
                raise RuntimeError(
                    "neetcode.io session expired or invalid — re-run "
                    "python .claude/scripts/auth_neetcode.py"
                )

            # Pro-gated detection (unauthenticated case)
            if "Get Pro Access" in body_text and len(body_text.strip()) < 200:
                return ("", "", "pro_gated")

            # Extract title and difficulty from the question view
            # Title sits between nav items and the difficulty label
            title = slug.replace("-", " ").title()
            lines = body_text.split("\n")
            for i, line in enumerate(lines):
                s = line.strip()
                if s in ("Easy", "Medium", "Hard") and i > 0:
                    candidate = lines[i - 1].strip()
                    # Skip a discuss-count line like "(148)"
                    if re.match(r"^\(\d+\)$", candidate) and i >= 2:
                        candidate = lines[i - 2].strip()
                    if candidate:
                        title = candidate
                    break

            description = _extract_description(body_text, title)
            problem_md = f"# {title}\n\n{description}\n" if description else ""

            # Click Solution tab
            elements = page.query_selector_all("a, button, [role=tab]")
            for el in elements:
                try:
                    if (el.inner_text() or "").strip() == "Solution":
                        el.click()
                        break
                except Exception as e:
                    # Playwright may raise on detached/animating nodes during
                    # the linear scan; logging and continuing is correct here
                    # because we only need one element to match.
                    print(
                        f"warning: skipping element while searching for Solution tab: "
                        f"{type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                    continue
            page.wait_for_timeout(3500)

            sol_body = page.evaluate("() => document.body.innerText")

            # Gather non-empty <pre> code blocks — these are the language-tabbed
            # code snippets; only the Python one (default) is populated per approach.
            pres = page.query_selector_all("pre")
            code_blocks = []
            for pre in pres:
                try:
                    t = pre.inner_text()
                except Exception as e:
                    # Playwright may raise if a node detaches mid-iteration;
                    # skip it and rely on the remaining matches.
                    print(
                        f"warning: skipping <pre> element: {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                    continue
                if t.strip() and ("class Solution" in t or "def " in t or "public " in t):
                    code_blocks.append(t.rstrip())

            html_approaches = page.evaluate(_APPROACH_EXTRACTION_JS) or []
            approaches = []
            for idx, ha in enumerate(html_approaches):
                approaches.append(
                    {
                        "title": ha.get("title", f"Solution {idx + 1}"),
                        "intuition": _html_to_md(ha.get("intuition_html", "")),
                        "algorithm": _html_to_md(ha.get("algorithm_html", "")),
                        "code": code_blocks[idx] if idx < len(code_blocks) else "",
                        "complexity_md": _html_to_md(ha.get("complexity_html", "")),
                        "time": "",
                        "space": "",
                    }
                )
            if not approaches:
                approaches = _parse_solutions(sol_body, code_blocks)

            if not approaches:
                solutions_md = f"# {title} - Solutions\n\n(No standard solutions parsed.)\n"
            else:
                parts = [f"# {title} - Solutions\n"]
                for i, a in enumerate(approaches, 1):
                    parts.append(f"## {i}. {a['title']}\n")
                    if a["intuition"]:
                        parts.append(f"### Intuition\n\n{a['intuition']}\n")
                    if a["algorithm"]:
                        parts.append(f"### Algorithm\n\n{a['algorithm']}\n")
                    if a["code"]:
                        parts.append(f"### Code (Python)\n\n```python\n{a['code']}\n```\n")
                    complexity_md = a.get("complexity_md", "")
                    if complexity_md:
                        parts.append(f"### Complexity\n\n{complexity_md}\n")
                    elif a.get("time") or a.get("space"):
                        parts.append("### Complexity\n")
                        if a.get("time"):
                            parts.append(f"- Time: {a['time']}")
                        if a.get("space"):
                            parts.append(f"- Space: {a['space']}")
                        parts.append("")
                solutions_md = "\n".join(parts)

            return (problem_md, solutions_md, "ok")
        finally:
            context.close()
            if browser is not None:
                browser.close()  # type: ignore[attr-defined]


def _setup_problem_folder(
    work_folder: str,
    list_path: str,
    problem_folder: str,
    problem_name: str,
    problem_id: str,
    ai_path: bool = False,
    community_path: bool = False,
    is_last: bool = False,
    skip_fetch: bool = False,
) -> None:
    if not skip_fetch:
        problem_info = _find_problem_in_tsv(list_path, problem_name)
        if not problem_info:
            problem_info = {
                "problem-name": problem_name,
                "nominal-difficulty": "Unknown",
                "problem-pattern": "Unknown",
                "link": "",
            }

        link = problem_info.get("link", "")

        # Fetch content BEFORE creating folder so an error doesn't leave a partial folder.
        problem_md, solutions_md, status = _fetch_problem_content(link)

        os.makedirs(problem_folder, exist_ok=True)

        metadata = {
            "problem-name": problem_info.get("problem-name", problem_name),
            "nominal-difficulty": problem_info.get("nominal-difficulty", "Unknown"),
            "problem-pattern": problem_info.get("problem-pattern", "Unknown"),
            "link": link,
            "standard-solutions-link": _compute_solutions_link(link),
        }
        with open(os.path.join(problem_folder, "metadata.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        if status == "pro_gated":
            problem_md = (
                f"# {problem_name}\n\n"
                "This problem requires Pro access on neetcode.io. No public content available.\n"
            )
            solutions_md = (
                f"# {problem_name} - Solutions\n\n"
                "This problem requires Pro access on neetcode.io. No public content available.\n"
            )

        with open(os.path.join(problem_folder, "problem.md"), "w", encoding="utf-8") as f:
            f.write(
                problem_md
                if problem_md
                else f"# {problem_name}\n\nProblem description not yet fetched.\n"
            )

        with open(
            os.path.join(problem_folder, "standard-solutions.md"), "w", encoding="utf-8"
        ) as f:
            f.write(
                solutions_md
                if solutions_md
                else f"# {problem_name} - Solutions\n\nSolutions not yet fetched.\n"
            )

    # Update top-level status.yaml: remove the entry from phase0-fetcher and
    # seed it into the first-phase `waiting` list of every enabled path.
    status = status_io.read_status(work_folder)
    fetcher = status.get("phase0-fetcher", {}) if isinstance(status, dict) else {}
    new_state = "complete" if is_last else "ongoing"
    if isinstance(fetcher, dict) and fetcher.get("state") != new_state:
        # Use a tiny dedicated mutation for the state change so we keep
        # everything atomic via status_io.
        from lib.file_lock import file_lock as _file_lock

        status_path = os.path.join(work_folder, "status.yaml")
        with _file_lock(status_path):
            data = status_io.read_status(work_folder)
            if isinstance(data.get("phase0-fetcher"), dict):
                data["phase0-fetcher"]["state"] = new_state
            tmp = status_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            os.replace(tmp, status_path)

    # Move from phase0-fetcher into the first phase of every enabled path.
    target_phases = ["standard-solutions-path/phase1-producer"]
    if ai_path:
        target_phases.append("ai-solutions-path/phase1-producer")
    if community_path:
        target_phases.append("community-times-path/phase1-producer")

    # First call also clears the entry from phase0-fetcher; subsequent calls
    # seed remaining paths without touching phase0-fetcher again.
    for i, dest in enumerate(target_phases):
        from_phase = "phase0-fetcher" if i == 0 else None
        status_io.move_to_phase(
            work_folder,
            problem_name,
            problem_id,
            problem_folder,
            from_phase,
            dest,
        )


def _write_remaining(remaining_path: str, problems: list) -> None:
    with open(remaining_path, "w", encoding="utf-8") as f:
        yaml.dump(
            {"problems": problems},
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Pop next problem from remaining.yaml and fetch content.",
        add_help=True,
    )
    parser.add_argument(
        "--problem-id",
        type=int,
        default=1,
        help=(
            "Problem-id for the fetched problem. Emitted in the success "
            "XML as <problem-id>. Defaults to 1."
        ),
    )
    args = parser.parse_args()
    problem_id = args.problem_id

    try:
        active = _load_active_list()
    except (OSError, yaml.YAMLError) as e:
        print(f"Error loading active list: {e}", file=sys.stderr)
        sys.exit(1)

    work_folder = active["work-folder"]
    list_path = active["list-path"]
    remaining_path = os.path.join(work_folder, "remaining.yaml")

    try:
        with open(remaining_path, encoding="utf-8") as f:
            remaining = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        remaining = {"problems": []}

    problems = remaining.get("problems", [])

    chosen = None
    skipped = []
    while problems:
        candidate = problems.pop(0)
        name = candidate.get("problem-name", "")
        if not _is_row_filled(list_path, name):
            chosen = candidate
            break
        skipped.append(candidate)

    if chosen is None:
        # Persist the skipped-removals (all rows were filled, nothing to do)
        _write_remaining(remaining_path, problems)
        print("<result>empty_list</result>")
        sys.exit(0)

    problem_name = chosen["problem-name"]
    fresh = bool(active.get("fresh", False))

    existing_pn = None
    if not fresh:
        candidate = _find_existing_pn(work_folder, problem_name)
        if candidate and _files_complete(os.path.join(work_folder, f"p{candidate}")):
            existing_pn = candidate

    if existing_pn is not None:
        problem_id = existing_pn
        skip_fetch = True
    else:
        problem_id = _next_id(work_folder)
        skip_fetch = False

    problem_folder = os.path.join(work_folder, f"p{problem_id}")

    ai_path = bool(active.get("ai-path", False))
    community_path = bool(active.get("community-path", False))
    is_last = len(problems) == 0

    try:
        _setup_problem_folder(
            work_folder,
            list_path,
            problem_folder,
            problem_name,
            problem_id,
            ai_path=ai_path,
            community_path=community_path,
            is_last=is_last,
            skip_fetch=skip_fetch,
        )
    except Exception as e:
        # Cleanup: remove any partial folder (only if we created it this run).
        if not skip_fetch and os.path.isdir(problem_folder):
            try:
                shutil.rmtree(problem_folder)
            except OSError as cleanup_err:
                # Best-effort: the original fetch failure is what matters; surface
                # the cleanup glitch as a warning so it isn't invisible.
                print(
                    f"warning: could not remove partial folder {problem_folder}: {cleanup_err}",
                    file=sys.stderr,
                )
        # Restore chosen to the front of problems so next run retries it.
        problems.insert(0, chosen)
        try:
            _write_remaining(remaining_path, problems)
        except OSError as restore_err:
            # Best-effort: failing to persist the restore means the next run may
            # skip this problem. Log so the user sees the inconsistency.
            print(
                f"warning: could not restore {chosen!r} to {remaining_path}: {restore_err}",
                file=sys.stderr,
            )

        traceback.print_exc(file=sys.stderr)
        msg = str(e).split("\n", 1)[0].strip() or repr(e)
        print(
            f"<result>fetch_error</result>\n"
            f"<problem-name>{problem_name}</problem-name>\n"
            f"<error-type>{type(e).__name__}</error-type>\n"
            f"<error-message>{msg}</error-message>"
        )
        sys.exit(1)

    # Success: persist the popped remaining list now.
    _write_remaining(remaining_path, problems)

    if skip_fetch:
        print("<result>problem_skipped</result>")
        print(f"<problem-id>{problem_id}</problem-id>")
    else:
        print(
            f"<result>problem_fetched</result>\n"
            f"<problem-folder>{problem_folder}</problem-folder>\n"
            f"<problem-name>{problem_name}</problem-name>\n"
            f"<problem-id>p{problem_id}</problem-id>"
        )


if __name__ == "__main__":
    main()
