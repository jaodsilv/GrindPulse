"""Unit tests for the tier-filter helper in list_work.

Covers list_work._filter_items_by_tier — the helper that drops queue entries
whose problem-id metadata.yaml difficulty does not match the requested tier.
Earlier bugs (#2, #12) involved Easy/Medium/Hard items leaking into the wrong
worker queue, so this filter is on the hot path of correctness.

Run: python -m pytest tests/python/test_tier_filter.py
"""

import os

from list_work import _filter_items_by_tier


def _write_pdir(root, pid, difficulty):
    """Create root/p<pid>/metadata.yaml with the given nominal-difficulty value.

    Pass difficulty=None to create the directory but no metadata.yaml file
    (simulates a problem dir that hasn't been parsed yet).
    Pass difficulty="<garbage>" to write a malformed metadata file.
    """
    pdir = os.path.join(root, f"p{pid}")
    os.makedirs(pdir, exist_ok=True)
    if difficulty is None:
        return
    meta_path = os.path.join(pdir, "metadata.yaml")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"nominal-difficulty: {difficulty}\n")


def test_filter_items_keeps_matching_tier(tmp_path):
    root = str(tmp_path)
    _write_pdir(root, 1, "Easy")
    _write_pdir(root, 2, "Easy")
    items = [{"problem-id": 1}, {"problem-id": 2}]
    out = _filter_items_by_tier(root, items, "Easy")
    assert out == items


def test_filter_items_drops_non_matching_tier(tmp_path):
    root = str(tmp_path)
    _write_pdir(root, 1, "Easy")
    _write_pdir(root, 2, "Hard")
    items = [{"problem-id": 1}, {"problem-id": 2}]
    out = _filter_items_by_tier(root, items, "Easy")
    assert out == [{"problem-id": 1}]


def test_filter_items_drops_when_metadata_missing(tmp_path):
    root = str(tmp_path)
    _write_pdir(root, 1, None)
    items = [{"problem-id": 1}]
    out = _filter_items_by_tier(root, items, "Easy")
    assert out == []


def test_filter_items_drops_unknown_difficulty(tmp_path):
    root = str(tmp_path)
    _write_pdir(root, 1, "Trivial")
    items = [{"problem-id": 1}]
    out = _filter_items_by_tier(root, items, "Easy")
    assert out == []


def test_filter_items_skips_items_missing_problem_id(tmp_path):
    root = str(tmp_path)
    items = [{"source": "ai"}, {"problem-id": "not-an-int"}]
    out = _filter_items_by_tier(root, items, "Easy")
    assert out == []


def test_filter_items_caches_difficulty_per_pid(tmp_path):
    """Items with the same problem-id should reuse the cached difficulty."""
    root = str(tmp_path)
    _write_pdir(root, 5, "Medium")
    items = [
        {"problem-id": 5, "source": "std-0"},
        {"problem-id": 5, "source": "std-1"},
        {"problem-id": 5, "source": "ai"},
    ]
    out = _filter_items_by_tier(root, items, "Medium")
    assert len(out) == 3
    assert all(it["problem-id"] == 5 for it in out)


def test_filter_items_preserves_order(tmp_path):
    root = str(tmp_path)
    _write_pdir(root, 1, "Hard")
    _write_pdir(root, 2, "Easy")
    _write_pdir(root, 3, "Hard")
    _write_pdir(root, 4, "Hard")
    items = [{"problem-id": pid} for pid in (1, 2, 3, 4)]
    out = _filter_items_by_tier(root, items, "Hard")
    assert [it["problem-id"] for it in out] == [1, 3, 4]


def test_filter_items_empty_input_returns_empty(tmp_path):
    out = _filter_items_by_tier(str(tmp_path), [], "Easy")
    assert out == []


def test_filter_items_preserves_extra_fields(tmp_path):
    root = str(tmp_path)
    _write_pdir(root, 7, "Medium")
    items = [{"problem-id": 7, "source": "ai", "pair-type": "paired"}]
    out = _filter_items_by_tier(root, items, "Medium")
    assert out == [{"problem-id": 7, "source": "ai", "pair-type": "paired"}]
