# Five AI Agents, One Engineering Team: Turning an Idea Into Working Code

*Planner → Developer → Tester → Reviewer → Orchestrator. I built a multi-agent system where each role does one job, the Tester actually runs the code, and a bounded fix-loop patches failures before review. Here's how — and how it maps to where agentic AI is heading in 2026.*

---

## Why a "team" beats a genius

Ask one model to "build me an app" and it does everything at once, badly. The 2026 consensus is the opposite: **specialized agents, each with a defined role and tools, coordinated into a crew.** That's not a hot take — it's the architecture CrewAI is built around (role-based agents, working prototypes in hours) and the workflow LangGraph hardened for production with state persistence and human-in-the-loop checkpoints.

The framework field exploded to back this up: OpenAI shipped its Agents SDK, Google introduced ADK, and Anthropic published its Agent SDK alongside Claude 4.6 — all in the last year. I deliberately built this **without** a framework, in plain Python, because the best way to understand what LangGraph and CrewAI are doing for you is to wire the agent handoffs by hand once.

## The team

Five roles, each a function with its own system persona:

| Agent | Job |
|-------|-----|
| **Planner** | Breaks the idea into a numbered build plan and file layout |
| **Developer** | Writes the complete single-file program |
| **Tester** | Actually executes the code and reports real pass/fail |
| **Reviewer** | Lists concrete improvements (bugs, edge cases, readability) |
| **Orchestrator** | The script itself — routes the handoffs and the fix-loop |

## What it does

Give it an app idea in plain English. It plans, builds, **runs** the result, and if it crashes, sends the real error back to the Developer for one fix round before the Reviewer weighs in. Final code lands in `output/app.py`, and every stage is written to `build_log.md`.

## The stack

| Piece | Choice |
|-------|--------|
| Runtime | Ollama (local, no keys) |
| Model | `qwen3-coder` |
| Agents | Plain Python functions, one system role each |
| Test | `subprocess` smoke-test with a 20s timeout |

## The part most "multi-agent" demos fake: the Tester

A lot of multi-agent showcases have a "Tester agent" that just *asks the model* whether the code is good. That's theater. Mine runs the code:

```python
def tester(code: str) -> tuple[bool, str]:
    """Smoke test: does it actually run without crashing?"""
    proc = subprocess.run(
        [sys.executable, path], capture_output=True, text=True, timeout=20
    )
    ok = proc.returncode == 0
    return ok, (proc.stdout if ok else (proc.stderr or proc.stdout))
```

Same principle as my self-correcting assistant: the verifier has to be **external**. A model grading its own code is not a test. The interpreter is.

## The orchestration

The Orchestrator is just the control flow — and that's the insight. "Agent orchestration" sounds heavy; at its core it's a sequence of calls with one conditional:

```python
def build(idea: str) -> None:
    plan = planner(idea)                          # 1. plan
    code = developer(idea, plan)                  # 2. build
    ok, result = tester(code)                     # 3. test (runs it)

    if not ok:                                    # 4. one bounded fix round
        code = developer(idea, plan, fix_error=result)
        ok, result = tester(code)

    review = reviewer(code)                       # 5. review
    # write output/app.py + build_log.md
```

The fix round is **bounded on purpose** — one retry, not an open loop. Unbounded agent loops are how you burn tokens and hang processes. The 2026 Hype Cycle explicitly flags cost and governance as first-class concerns alongside capability, and a single capped retry is the cheapest possible nod to both.

## What I changed from the original tutorial

Inspired by Aman Kharwal's **["Build an AI Agent for End-to-End App Development"](https://amanxai.com/2026/04/29/build-an-ai-agent-for-end-to-end-app-development/)**. My version:

- **Single-file orchestrator** where each agent is a typed function with its own role prompt — easy to read, easy to extend.
- **The Tester executes code in a subprocess** and feeds the *real* traceback back, instead of a model "reviewing" the output.
- **One automatic, bounded fix round** before review — no infinite loops.
- **Full artifacts**: `output/app.py` plus a `build_log.md` capturing every stage's output, so the whole build is auditable. (Auditability is exactly why LangGraph won enterprise mindshare — worth understanding before you adopt the framework version.)

## Where it breaks

- **A smoke test isn't a test suite.** "It ran" ≠ "it's correct." The honest upgrade is having the Planner specify acceptance tests and the Tester run *those*.
- **Handoff quality compounds.** A vague plan produces vague code. Garbage in early multiplies downstream — the classic multi-agent failure mode.
- **No real tool use yet.** These agents reason and write; they don't call external tools. Which leads to the obvious next step…

## What I'd build next: give the agents real tools via MCP

The single biggest 2026 development I haven't used here yet is the **Model Context Protocol (MCP)** — the now-standard way to connect agents to real tools and data. It hit **~97 million monthly SDK downloads and 5,800+ servers**, every major lab adopted it natively, and Anthropic donated it to the Linux Foundation's Agentic AI Foundation in late 2025. Frameworks like LangChain, CrewAI, and LangGraph now treat MCP as the default tool-calling layer.

The natural v2 of this project: let the Developer agent actually read the filesystem, run a linter, and check docs through MCP servers — instead of writing code blind. That's the jump from "LLM that writes code" to "agent that builds software."

## Takeaway

Building this by hand taught me what the frameworks abstract: a multi-agent system is **roles + handoffs + an external verifier + bounded loops.** Everything LangGraph and CrewAI sell you is a nicer way to manage those four things at scale. Understand them in plain Python first; reach for the framework when you actually need the persistence, observability, and orchestration they provide.

**Code:** [link your GitHub repo here]

---

*Inspired by Aman Kharwal's tutorial, ["Build an AI Agent for End-to-End App Development"](https://amanxai.com/2026/04/29/build-an-ai-agent-for-end-to-end-app-development/). Rebuilt and extended as described.*

### Sources
- [The best AI agent frameworks in 2026 — LangChain](https://www.langchain.com/resources/ai-agent-frameworks)
- [CrewAI vs LangChain 2026 — NxCode](https://www.nxcode.io/resources/news/crewai-vs-langchain-ai-agent-framework-comparison-2026)
- [The 2026 MCP Roadmap — Model Context Protocol Blog](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [MCP Adoption Statistics 2026 — Digital Applied](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol)
- [2026 Hype Cycle for Agentic AI — Gartner](https://www.gartner.com/en/articles/hype-cycle-for-agentic-ai)
