# Multi-Agent App Builder

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-green) ![Runs 100% Local](https://img.shields.io/badge/runs-100%25%20local-orange)

**Five AI agents — Planner → Developer → Tester → Reviewer → Orchestrator — turn one plain-English app idea into working code.**

## Overview

Multi-agent systems are the defining shift of 2026. We spent 2024 and 2025 wiring single prompts into chat windows; the interesting work now is getting several specialized agents to hand off to each other and ship something a human can actually run. This project is a small, honest version of that idea: you type one sentence, five roles collaborate, and you get a working Python file plus a build log that shows their reasoning.

The whole thing is built framework-free — plain Python functions, one per role, talking to a local Ollama model. That's a deliberate choice. CrewAI and LangGraph are great, but they abstract away the exact mechanics you most need to understand: how a handoff is structured, where a fix loop should terminate, and what "testing" an agent's output actually means. Build it by hand once and the frameworks stop being magic.

The point of difference here is the Tester. Most tutorial agents "test" code by asking the model whether the code looks good — which is theater. This one runs the generated code in a real subprocess, captures the real traceback, and feeds that traceback back to the Developer for exactly one bounded fix round before the Reviewer weighs in. Real signal, no infinite loops.

## Features

- **Five distinct roles** — Planner, Developer, Tester, Reviewer, and an Orchestrator that sequences them.
- **Real subprocess testing** — the Tester executes the generated code with a timeout and captures the actual stdout/stderr and traceback.
- **One bounded fix round** — a failing test feeds the real error back to the Developer once, then moves on. No runaway loops, no burned tokens.
- **Full build log** — every agent's output is written to `build_log.md` for auditability.
- **100% local** — runs entirely on Ollama with `qwen3-coder`. No API keys, no data leaving your machine.
- **No framework** — plain Python functions, so you can read and modify every step.

## How it works

```
        idea ("a CLI todo app with a json store")
                        |
                        v
                   [ Planner ]  --> spec
                        |
                        v
                  [ Developer ] --> code
                        |
                        v
                   [ Tester ]  --> run in subprocess (timeout)
                        |
                  pass? | fail? --> traceback
                        |              |
                        |              v
                        |        [ Developer ]  (one bounded fix round)
                        |              |
                        |<-------------+
                        v
                  [ Reviewer ]  --> final notes
                        |
                        v
        output/app.py  +  build_log.md
```

## Tech stack

| Layer | Choice |
|-------|--------|
| Runtime | Ollama (local LLM serving) |
| Model | `qwen3-coder` |
| Language | Python 3.10+ |
| Architecture | Plain Python functions, one per role |
| Testing | `subprocess` smoke test with timeout |

## Project structure

```
multi-agent-app-builder/
├── agent.py         # the five roles + orchestrator (MODEL/OUT/TEST_TIMEOUT config)
├── test_agent.py    # tests for the pure helpers + subprocess tester
├── output/          # generated artifacts (created at runtime)
│   ├── app.py       # the generated application
│   └── build_log.md # full audit trail of every agent's output
├── ARTICLE.md
├── requirements.txt
├── LICENSE
└── README.md
```

## Installation

1. Install [Ollama](https://ollama.com) and start it.
2. Pull the model and install deps:

```bash
ollama pull qwen3-coder
pip install -r requirements.txt
```

## Usage

```bash
python agent.py "a CLI todo app with a json store"
```

When it finishes you'll have `output/app.py` (the generated, test-passed app) and `output/build_log.md` (the full record of each agent). Run the result with `python output/app.py`.

## Configuration

Edit the constants at the top of `agent.py`:

| Constant | Default | What it controls |
|----------|---------|------------------|
| `MODEL` | `qwen3-coder` | The Ollama model used by every role |
| `OUT` | `output` | Directory for `app.py` and `build_log.md` |
| `TEST_TIMEOUT` | `20` | Seconds the Tester waits before killing the subprocess |

## Testing

```bash
pip install pytest
pytest
```

`test_agent.py` tests *this tool*; the Tester role inside `agent.py` tests the *generated code* by running it.

## Limitations

- **A smoke test isn't a test suite.** The Tester confirms the code runs without crashing, not that it's correct for every input.
- **Handoff quality compounds.** A vague plan produces vague code — the clearer your one-sentence idea, the better every downstream role performs.
- **No external tool use yet.** Agents can't browse, call APIs, or read files beyond what they generate — a natural v2 via MCP.
- **One fix round only.** By design (no infinite loops), but a genuinely hard bug may survive the single retry.

## Roadmap

- [ ] Acceptance tests — let the Planner emit example inputs/outputs the Tester asserts against
- [ ] Tool use via MCP — give agents file, search, and API access
- [ ] Multi-file project output instead of a single `app.py`
- [ ] Pluggable models per role (cheap Planner, strong Developer)

## Credits

📖 Full write-up: [ARTICLE.md](ARTICLE.md).

Based on Aman Kharwal's tutorial, ["Build an AI Agent for End-to-End App Development"](https://amanxai.com/2026/04/29/build-an-ai-agent-for-end-to-end-app-development/).

**What I changed vs the source tutorial:**

- **Real subprocess testing** — the Tester runs the generated code and captures the actual traceback, instead of asking the model whether the code looks fine.
- **One bounded fix round** — the real error feeds back to the Developer exactly once, eliminating infinite loops.
- **Full build log** — every agent's output is written to `build_log.md` for auditability.

## Author

Built by **Randhir Manekar** — [randhirmanekar.com](https://randhirmanekar.com) · [github.com/randhirmanekar15](https://github.com/randhirmanekar15)

## License

MIT — see [LICENSE](LICENSE).
