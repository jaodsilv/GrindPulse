"""Unit tests for the in-flight counter helpers in lib/dispatch_state.

Covers read_counter and write_counter from lib.dispatch_state — recently
hardened in A7 to clamp malformed/missing files to 0 with a stderr log.
A bug here causes the dispatcher to wedge on ValueError or under-count
slots, which is exactly what motivated A7.

Run: python -m pytest tests/python/test_dispatch_state.py
"""

from lib.dispatch_state import counter_path, read_counter, write_counter


def test_read_counter_missing_file_returns_zero(tmp_path):
    assert read_counter(str(tmp_path)) == 0


def test_read_counter_empty_file_returns_zero_and_logs(tmp_path, capsys):
    counter_path(str(tmp_path)).write_text("")
    val = read_counter(str(tmp_path))
    captured = capsys.readouterr()
    assert val == 0
    assert "empty" in captured.err.lower()
    assert "[dispatch_state]" in captured.err


def test_read_counter_whitespace_only_returns_zero_and_logs(tmp_path, capsys):
    counter_path(str(tmp_path)).write_text("   \n\t  ")
    val = read_counter(str(tmp_path))
    captured = capsys.readouterr()
    assert val == 0
    assert "empty" in captured.err.lower()


def test_read_counter_non_int_returns_zero_and_logs(tmp_path, capsys):
    counter_path(str(tmp_path)).write_text("not-a-number")
    val = read_counter(str(tmp_path))
    captured = capsys.readouterr()
    assert val == 0
    assert "non-integer" in captured.err.lower()
    assert "not-a-number" in captured.err


def test_read_counter_partial_write_corruption(tmp_path, capsys):
    """Simulate a partial write from a crashed process (digits + garbage)."""
    counter_path(str(tmp_path)).write_text("3abc")
    val = read_counter(str(tmp_path))
    captured = capsys.readouterr()
    assert val == 0
    assert "non-integer" in captured.err.lower()


def test_read_counter_valid_int_round_trip(tmp_path):
    write_counter(str(tmp_path), 5)
    assert read_counter(str(tmp_path)) == 5


def test_read_counter_zero_round_trip(tmp_path):
    write_counter(str(tmp_path), 0)
    assert read_counter(str(tmp_path)) == 0


def test_read_counter_handles_surrounding_whitespace(tmp_path):
    counter_path(str(tmp_path)).write_text("  7\n")
    assert read_counter(str(tmp_path)) == 7


def test_write_counter_clamps_negative_to_zero(tmp_path):
    write_counter(str(tmp_path), -1)
    assert read_counter(str(tmp_path)) == 0
    assert counter_path(str(tmp_path)).read_text() == "0"


def test_write_counter_clamps_large_negative_to_zero(tmp_path):
    write_counter(str(tmp_path), -42)
    assert read_counter(str(tmp_path)) == 0


def test_write_counter_overwrites_existing_value(tmp_path):
    write_counter(str(tmp_path), 3)
    write_counter(str(tmp_path), 8)
    assert read_counter(str(tmp_path)) == 8


def test_write_counter_creates_file_if_missing(tmp_path):
    p = counter_path(str(tmp_path))
    assert not p.exists()
    write_counter(str(tmp_path), 2)
    assert p.exists()
    assert p.read_text() == "2"


def test_counter_path_returns_in_flight_txt(tmp_path):
    p = counter_path(str(tmp_path))
    assert p.name == "in-flight.txt"
    assert p.parent == tmp_path
