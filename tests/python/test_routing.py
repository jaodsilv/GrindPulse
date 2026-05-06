"""Unit tests for pipeline routing/phase-parsing helpers.

Covers:
  - subagent_stop_state_advance._route: maps (worker, source) to (from_phase, to_phase).
  - process_list_hook._parse_phases: parses --phases CLI flag into (start, end) ints.

Both helpers were implicated in earlier bugs (#1, #7, #12) where misrouted
work-items leaked counter slots or got dispatched to the wrong queue.

Run: python -m pytest tests/python/test_routing.py
"""

from process_list_hook import _parse_phases
from subagent_stop_state_advance import _route


class TestRoute:
    """Tests for subagent_stop_state_advance._route."""

    def test_route_solutions_parser(self):
        from_phase, to_phase = _route("solutions-parser", None)
        assert from_phase == "standard-solutions-path/phase1-producer"
        assert to_phase == "standard-solutions-path/phase2-explanator"

    def test_route_coding_challenge_solver(self):
        from_phase, to_phase = _route("coding-challenge-solver", None)
        assert from_phase == "ai-solutions-path/phase1-producer"
        assert to_phase == "ai-solutions-path/phase3-time-estimator"

    def test_route_community_time_finder_skips_phases_2_and_3(self):
        from_phase, to_phase = _route("community-time-finder", None)
        assert from_phase == "community-times-path/phase1-producer"
        assert to_phase == "community-times-path/phase4-criticizer"

    def test_route_code_explanator(self):
        from_phase, to_phase = _route("code-explanator", None)
        assert from_phase == "standard-solutions-path/phase2-explanator"
        assert to_phase == "standard-solutions-path/phase3-time-estimator"

    def test_route_solution_analyzer_ai_source(self):
        from_phase, to_phase = _route("solution-analyzer", "ai")
        assert from_phase == "ai-solutions-path/phase3-time-estimator"
        assert to_phase == "ai-solutions-path/phase4-criticizer"

    def test_route_solution_analyzer_std_source(self):
        from_phase, to_phase = _route("solution-analyzer", "std")
        assert from_phase == "standard-solutions-path/phase3-time-estimator"
        assert to_phase == "standard-solutions-path/phase4-criticizer"

    def test_route_solution_analyzer_std_n_source(self):
        from_phase, to_phase = _route("solution-analyzer", "std-3")
        assert from_phase == "standard-solutions-path/phase3-time-estimator"
        assert to_phase == "standard-solutions-path/phase4-criticizer"

    def test_route_solution_analyzer_none_source_treated_as_std(self):
        from_phase, to_phase = _route("solution-analyzer", None)
        assert from_phase == "standard-solutions-path/phase3-time-estimator"
        assert to_phase == "standard-solutions-path/phase4-criticizer"

    def test_route_justification_criticizer_ai(self):
        from_phase, to_phase = _route("justification-criticizer", "ai")
        assert from_phase == "ai-solutions-path/phase4-criticizer"
        assert to_phase == "phase5-time-selection"

    def test_route_justification_criticizer_community_prefix(self):
        from_phase, to_phase = _route("justification-criticizer", "community-2")
        assert from_phase == "community-times-path/phase4-criticizer"
        assert to_phase == "phase5-time-selection"

    def test_route_justification_criticizer_std(self):
        from_phase, to_phase = _route("justification-criticizer", "std")
        assert from_phase == "standard-solutions-path/phase4-criticizer"
        assert to_phase == "phase5-time-selection"

    def test_route_justification_criticizer_std_n(self):
        from_phase, to_phase = _route("justification-criticizer", "std-1")
        assert from_phase == "standard-solutions-path/phase4-criticizer"
        assert to_phase == "phase5-time-selection"

    def test_route_justification_criticizer_unknown_source_defaults_std(self):
        from_phase, to_phase = _route("justification-criticizer", "garbage")
        assert from_phase == "standard-solutions-path/phase4-criticizer"
        assert to_phase == "phase5-time-selection"

    def test_route_time_selection_terminal(self):
        from_phase, to_phase = _route("time-selection", None)
        assert from_phase == "phase5-time-selection"
        assert to_phase is None

    def test_route_unknown_worker_returns_none_pair(self):
        assert _route("nonsense-worker", None) == (None, None)

    def test_route_handles_uppercase_source(self):
        from_phase, _ = _route("solution-analyzer", "AI")
        assert from_phase == "ai-solutions-path/phase3-time-estimator"

    def test_route_handles_whitespace_source(self):
        from_phase, _ = _route("justification-criticizer", "  ai  ")
        assert from_phase == "ai-solutions-path/phase4-criticizer"


class TestParsePhases:
    """Tests for process_list_hook._parse_phases."""

    def test_parse_phases_default_when_flag_absent(self):
        start, end, err = _parse_phases(["/process-list", "some.tsv"])
        assert (start, end, err) == (0, 7, None)

    def test_parse_phases_single_int_value(self):
        start, end, err = _parse_phases(["--phases", "3"])
        assert start == 3
        assert end == 4
        assert err is None

    def test_parse_phases_range_full(self):
        start, end, err = _parse_phases(["--phases", "1:5"])
        assert start == 1
        assert end == 5
        assert err is None

    def test_parse_phases_range_left_open(self):
        start, end, err = _parse_phases(["--phases", ":4"])
        assert start == 0
        assert end == 4
        assert err is None

    def test_parse_phases_range_right_open(self):
        start, end, err = _parse_phases(["--phases", "2:"])
        assert start == 2
        assert end == 7
        assert err is None

    def test_parse_phases_missing_value(self):
        _, _, err = _parse_phases(["--phases"])
        assert err is not None
        assert "requires a value" in err

    def test_parse_phases_bare_colon_rejected(self):
        _, _, err = _parse_phases(["--phases", ":"])
        assert err is not None
        assert "bare ':'" in err

    def test_parse_phases_non_integer_left(self):
        _, _, err = _parse_phases(["--phases", "abc:3"])
        assert err is not None
        assert "must be an integer" in err

    def test_parse_phases_non_integer_right(self):
        _, _, err = _parse_phases(["--phases", "1:xyz"])
        assert err is not None
        assert "must be an integer" in err

    def test_parse_phases_non_integer_single(self):
        _, _, err = _parse_phases(["--phases", "five"])
        assert err is not None
        assert "must be an integer" in err

    def test_parse_phases_out_of_bounds_negative_start(self):
        _, _, err = _parse_phases(["--phases", "-1:3"])
        assert err is not None
        assert "out of bounds" in err

    def test_parse_phases_out_of_bounds_end_too_high(self):
        _, _, err = _parse_phases(["--phases", "0:8"])
        assert err is not None
        assert "out of bounds" in err

    def test_parse_phases_start_equals_end_invalid(self):
        _, _, err = _parse_phases(["--phases", "3:3"])
        assert err is not None
        assert "out of bounds" in err

    def test_parse_phases_start_greater_than_end_invalid(self):
        _, _, err = _parse_phases(["--phases", "5:2"])
        assert err is not None
        assert "out of bounds" in err

    def test_parse_phases_min_valid_range(self):
        start, end, err = _parse_phases(["--phases", "0:1"])
        assert (start, end, err) == (0, 1, None)

    def test_parse_phases_max_valid_range(self):
        start, end, err = _parse_phases(["--phases", "0:7"])
        assert (start, end, err) == (0, 7, None)
