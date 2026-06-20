# Multi-Agent App Builder

Five roles turn one plain-English app idea into working code: **Planner → Developer → Tester → Reviewer → Orchestrator**. Runs fully locally on [Ollama](https://ollama.com).

The Tester isn't theater — it actually runs the generated code in a subprocess and feeds the real traceback back to the Developer for one bounded fix round before the Reviewer weighs in.

## Stack

| Piece | Choice |
|-------|--------|
| Runtime | Ollama (local) |
| Model | `qwen3-coder` |
| Agents | Plain Python functions, one role each |
| Test | `subprocess` smoke test with a timeout |

## Setup

```bash
ollama pull qwen3-coder
pip install -r requirements.txt
```

## Usage

```bash
python agent.py "a CLI todo app with a json store"
```

Outputs: `output/app.py` and `build_log.md` (every stage captured for auditability).

## Test

```bash
pip install pytest
pytest
```

## Limitations

- A smoke test isn't a test suite — "it ran" is not "it's correct".
- Handoff quality compounds: a vague plan produces vague code.
- No external tool use yet (a natural v2 via the Model Context Protocol).

---

Inspired by Aman Kharwal's tutorial, [Build an AI Agent for End-to-End App Development](https://amanxai.com/2026/04/29/build-an-ai-agent-for-end-to-end-app-development/). Rebuilt and extended (real subprocess testing, bounded fix round, full build log).

MIT licensed.
