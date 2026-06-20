"""Tests for pure helpers and the subprocess tester (no Ollama model required)."""

from agent import strip_fences, tester


def test_strip_fences():
    assert strip_fences("```python\nprint(1)\n```") == "print(1)"


def test_tester_passes_clean_code():
    passed, _ = tester("print('ok')")
    assert passed is True


def test_tester_fails_broken_code():
    passed, output = tester("import nonexistent_module_xyz")
    assert passed is False
    assert "ModuleNotFoundError" in output or "Error" in output
