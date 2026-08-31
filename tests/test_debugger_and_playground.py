"""Test Suite for SMC Interactive Step Debugger and Web Playground Harness."""

from __future__ import annotations

import io
from pathlib import Path
import sys
import pytest

from smc.cli import debug_file
from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.visualizer import MultiPhaseVisualizer
from smc.vm import DexterVM


def test_debugger_step_execution(tmp_path: Path, monkeypatch):
    """Verify that debug_file steps through statements with inputs."""
    script = tmp_path / "debug_test.smc"
    script.write_text("""
    experiment 'dbg' {
        let x = 10
        let y = x + 5
        print y
    }
    """, encoding="utf-8")

    # Mock user input: step, step, step
    inputs = iter(["s", "s", "s", "q"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    # Capture stdout
    captured = io.StringIO()
    monkeypatch.setattr("sys.stdout", captured)

    debug_file(script)

    out = captured.getvalue()
    assert "SMC Interactive Step Debugger" in out
    assert "Debugger finished" in out
    assert "15" in out or "y" in out


def test_playground_files_exist_and_valid():
    """Verify that playground web assets exist and contain required DOM IDs."""
    playground_dir = Path(__file__).parent.parent / "docs" / "playground"
    index_html = playground_dir / "index.html"
    style_css = playground_dir / "style.css"
    app_js = playground_dir / "app.js"

    assert index_html.is_file()
    assert style_css.is_file()
    assert app_js.is_file()

    html_content = index_html.read_text(encoding="utf-8")
    assert 'id="track-0"' in html_content
    assert 'id="track-1"' in html_content
    assert 'id="track-2"' in html_content
    assert 'id="ttl-container"' in html_content
    assert 'id="code-editor"' in html_content

    js_content = app_js.read_text(encoding="utf-8")
    assert "SAMPLES" in js_content
    assert "simulateTraceFromCode" in js_content
