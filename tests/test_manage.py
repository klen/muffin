"""Shell completion for `muffin <app> ...` (argcomplete)."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("argcomplete")

ROOT = Path(__file__).parent.parent


def complete(line: str) -> set[str]:
    """Run the CLI the way the shell does and return the completion candidates."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "completions"
        subprocess.run(
            [sys.executable, "-c", "from muffin.manage import cli; cli()"],
            cwd=ROOT,
            env={
                **os.environ,
                "_ARGCOMPLETE": "1",
                "_ARGCOMPLETE_SHELL": "bash",
                "_ARGCOMPLETE_STDOUT_FILENAME": out.as_posix(),
                "COMP_LINE": line,
                "COMP_POINT": str(len(line)),
            },
            check=True,
        )
        return {c.strip() for c in out.read_text().split("\v") if c.strip()}


def test_commands():
    assert {"shell", "run"} <= complete("muffin tests ")
    assert complete("muffin tests sh") == {"shell"}


def test_options():
    assert "--host" in complete("muffin tests run --ho")
    # The app path is not the first word
    assert "--host" in complete("muffin --config tests.config_fixture tests run --ho")
