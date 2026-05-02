"""Shared in-flight counter helpers for agent_dispatch and subagent_stop_state_advance."""

from pathlib import Path


def counter_path(work_folder):
    return Path(work_folder) / "in-flight.txt"


def read_counter(work_folder):
    p = counter_path(work_folder)
    return int(p.read_text().strip()) if p.exists() else 0


def write_counter(work_folder, n):
    counter_path(work_folder).write_text(str(max(0, n)))
