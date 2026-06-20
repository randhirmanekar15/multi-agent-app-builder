"""Multi-agent app builder.

Five roles turn one app idea into working code: Planner -> Developer -> Tester ->
Reviewer -> Orchestrator. The Tester actually executes the code in a subprocess
and feeds the real traceback back for one bounded fix round before review.

Inspired by Aman Kharwal's tutorial:
https://amanxai.com/2026/04/29/build-an-ai-agent-for-end-to-end-app-development/
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import ollama

MODEL = "qwen3-coder:latest"
OUT = Path("output")
TEST_TIMEOUT = 20  # seconds for the smoke test


def ask(role_system: str, user: str) -> str:
    """Single-turn chat with a role system prompt."""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": role_system},
            {"role": "user", "content": user},
        ],
    )
    return response["message"]["content"].strip()


def strip_fences(text: str) -> str:
    """Remove ```python ... ``` wrappers the model sometimes adds."""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return (match.group(1) if match else text).strip()


def planner(idea: str) -> str:
    return ask(
        "You are a software architect. Break the idea into a short, numbered build "
        "plan: core features, data structures, and the single Python file layout. "
        "Be concise.",
        idea,
    )


def developer(idea: str, plan: str, fix_error: str | None = None) -> str:
    user = f"Idea:\n{idea}\n\nPlan:\n{plan}\n"
    if fix_error:
        user += f"\nThe previous version failed tests with:\n{fix_error}\nFix it."
    user += "\nWrite the COMPLETE single-file Python program. Code only, no fences."
    return strip_fences(
        ask(
            "You are a senior Python developer. Write clean, runnable, "
            "self-contained code.",
            user,
        )
    )


def tester(code: str) -> tuple[bool, str]:
    """Smoke test: does the code import and run without crashing?"""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(code)
        path = handle.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            check=False,
        )
        passed = proc.returncode == 0
        return passed, (proc.stdout if passed else (proc.stderr or proc.stdout))
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {TEST_TIMEOUT}s."
    finally:
        Path(path).unlink(missing_ok=True)


def reviewer(code: str) -> str:
    return ask(
        "You are a staff engineer doing code review. List concrete improvements "
        "(bugs, edge cases, readability) as short bullets. Do not rewrite the code.",
        code,
    )


def build(idea: str) -> bool:
    """Run the five-stage pipeline. Returns whether the final code passed tests."""
    OUT.mkdir(exist_ok=True)
    log: list[str] = ["# Build Log", f"**Idea:** {idea}\n"]

    print("1/5 Planner...")
    plan = planner(idea)
    log += ["## Plan", plan, ""]

    print("2/5 Developer...")
    code = developer(idea, plan)

    print("3/5 Tester...")
    passed, result = tester(code)
    log += ["## First test", f"passed={passed}", "```", result[:1500], "```", ""]

    if not passed:
        print("   failed -> 4/5 Developer fix round...")
        code = developer(idea, plan, fix_error=result)
        passed, result = tester(code)
        log += ["## After fix", f"passed={passed}", "```", result[:1500], "```", ""]

    print("5/5 Reviewer...")
    review = reviewer(code)
    log += ["## Review notes", review, ""]

    (OUT / "app.py").write_text(code, encoding="utf-8")
    Path("build_log.md").write_text("\n".join(log), encoding="utf-8")
    print(f"\nDone. App: {OUT / 'app.py'}  (tests passed={passed})  Log: build_log.md")
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-agent app builder")
    parser.add_argument("idea", nargs="*", help="App idea in plain English")
    args = parser.parse_args()
    idea = " ".join(args.idea) or input("App idea: ")
    build(idea)


if __name__ == "__main__":
    main()
