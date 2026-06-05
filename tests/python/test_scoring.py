"""Unit tests for the deterministic critique scoring helper.

Covers time_selection.score_critique — the function that ranks candidate
sources by counting weighted bullets under '### Flaws in Justificative'.
The scoring drives time_selection's direct-vs-tiebreak decision; a bug here
silently picks the wrong source. Earlier issues (#7) involved misranking when
severity keywords were missed.

Run: python -m pytest tests/python/test_scoring.py
"""

from time_selection import HIGH_SEVERITY_WEIGHT, OTHER_BULLET_WEIGHT, score_critique


def test_score_empty_text_returns_zero():
    assert score_critique("") == 0.0


def test_score_none_text_returns_zero():
    assert score_critique(None) == 0.0


def test_score_no_flaws_section_returns_zero():
    text = "## Selected Times\n\nSome other content."
    assert score_critique(text) == 0.0


def test_score_empty_flaws_section_returns_zero():
    text = "### Flaws in Justificative\n\n"
    assert score_critique(text) == 0.0


def test_score_single_other_bullet():
    text = "### Flaws in Justificative\n- The estimate seems okay.\n"
    assert score_critique(text) == OTHER_BULLET_WEIGHT


def test_score_single_high_severity_bullet():
    text = "### Flaws in Justificative\n- The estimate is unrealistic.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_high_severity_keyword_biased():
    text = "### Flaws in Justificative\n- The reasoning is biased.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_high_severity_keyword_incorrect():
    text = "### Flaws in Justificative\n- The complexity claim is incorrect.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_high_severity_keyword_overconfident_hyphen():
    text = "### Flaws in Justificative\n- The author is over-confident.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_high_severity_keyword_overconfident_no_hyphen():
    text = "### Flaws in Justificative\n- The author is overconfident in pacing.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_high_severity_underweights():
    text = "### Flaws in Justificative\n- This underweights testing time.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_high_severity_off_by():
    text = "### Flaws in Justificative\n- The boundary is off-by one.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_high_severity_ignores():
    text = "### Flaws in Justificative\n- The estimate ignores debugging time.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_severity_keywords_case_insensitive():
    text = "### Flaws in Justificative\n- The estimate is BIASED.\n"
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT


def test_score_mixed_bullets():
    text = (
        "### Flaws in Justificative\n"
        "- The estimate is unrealistic.\n"
        "- The complexity claim is incorrect.\n"
        "- Minor wording nit.\n"
    )
    assert score_critique(text) == HIGH_SEVERITY_WEIGHT * 2 + OTHER_BULLET_WEIGHT


def test_score_accepts_asterisk_bullets():
    text = "### Flaws in Justificative\n* Minor concern.\n* The estimate is biased.\n"
    assert score_critique(text) == OTHER_BULLET_WEIGHT + HIGH_SEVERITY_WEIGHT


def test_score_ignores_non_bullet_lines():
    text = (
        "### Flaws in Justificative\nSome intro paragraph.\n- A real bullet.\nAnother paragraph.\n"
    )
    assert score_critique(text) == OTHER_BULLET_WEIGHT


def test_score_stops_at_next_heading():
    text = (
        "### Flaws in Justificative\n"
        "- One flaw.\n"
        "- Another flaw.\n"
        "### Suggested Fixes\n"
        "- This bullet should not count.\n"
        "- Neither should this biased one.\n"
    )
    assert score_critique(text) == OTHER_BULLET_WEIGHT * 2


def test_score_handles_indented_bullets():
    text = "### Flaws in Justificative\n  - Indented flaw.\n"
    assert score_critique(text) == OTHER_BULLET_WEIGHT


def test_score_section_header_case_insensitive():
    text = "### flaws in justificative\n- A flaw.\n"
    assert score_critique(text) == OTHER_BULLET_WEIGHT


def test_score_higher_score_means_worse():
    weak = "### Flaws in Justificative\n- Minor wording.\n"
    strong = (
        "### Flaws in Justificative\n"
        "- The estimate is unrealistic.\n"
        "- The complexity claim is incorrect.\n"
        "- The reasoning is biased.\n"
    )
    assert score_critique(strong) > score_critique(weak)
