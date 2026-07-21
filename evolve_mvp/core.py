"""
evolve_mvp/core.py
The methodology engine. Model-agnostic: produces the protocol prompts/structure
that ANY AI model executes. Does not call a model itself — adapters do that.

Novel core:
  - REGRESSION-GATED: every analysis is checked against a failure log (LESSONS)
    before acting. Repeats of past mistakes are caught.
  - SELF-EVOLVING: each run appends new failure modes to LESSONS. The tool
    compounds from usage, not from manual edits.
"""
from __future__ import annotations
import os, json, datetime
from pathlib import Path

VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Failure log (the regression memory). This is what makes the tool evolve.
# Starts with domain-general MVP-killers from research; grows from every run.
# ---------------------------------------------------------------------------
DEFAULT_LESSONS = [
    {"date": "2026-07-19", "mode": "no-single-audience",
     "cause": "Building for everyone at once", "fix": "Force ONE clear user before building"},
    {"date": "2026-07-19", "mode": "scope-creep",
     "cause": "Kitchen-sink syndrome / 'just one more feature'", "fix": "Hard scope line; below = post-MVP"},
    {"date": "2026-07-19", "mode": "perfectionism-paralysis",
     "cause": "Over-analysis, never launches", "fix": "Ship viable; polish after signal"},
    {"date": "2026-07-19", "mode": "sunk-cost",
     "cause": "Continuing dead project because of hours already spent",
     "fix": "Stop/pivot on dead premortem signal regardless of invested hours"},
    {"date": "2026-07-19", "mode": "overengineering",
     "cause": "Wrong/complex stack for a validation bet", "fix": "Simplest stack that proves the bet"},
    {"date": "2026-07-19", "mode": "minimum-over-viable",
     "cause": "Shipping a useless stub", "fix": "MVP must prove something real"},
]


def load_lessons(path: Path) -> list:
    p = path / "LESSONS.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return list(DEFAULT_LESSONS)


def save_lessons(path: Path, lessons: list):
    (path / "LESSONS.json").write_text(json.dumps(lessons, indent=2))


def add_lesson(lessons: list, mode: str, cause: str, fix: str) -> list:
    """Self-evolution hook: append a new failure mode discovered this run."""
    lessons.append({
        "date": datetime.date.today().isoformat(),
        "mode": mode, "cause": cause, "fix": fix,
    })
    # de-dupe by mode
    seen = set(); out = []
    for l in lessons:
        if l["mode"] in seen:
            continue
        seen.add(l["mode"]); out.append(l)
    return out


# ---------------------------------------------------------------------------
# The protocol builder. Returns the full prompt + structure for any model.
# ---------------------------------------------------------------------------
def analyze_phase(project_path: str) -> str:
    return f"""PHASE 1 — ANALYZE (exhaustive, minimal user input)
Project: {project_path}
Goal: build a complete, evidence-based picture of current state from ARTIFACTS alone.
1. Locate: use the path given. Do not ask the user to describe the project.
2. Map the tree (list all files, structure, count by type). Note present vs absent (no tests/README/entry).
3. Read signal files if present: README/CLAUDE.md/AGENTS.md/DESIGN*, manifest (package.json/pyproject.toml/Cargo.toml/go.mod/requirements.txt), entry (main/index/app/__main__.py), config (.env.example/*.config.*), `git log --oneline -20`, a couple core source files.
4. Infer (do NOT ask to confirm): WHAT IT IS, WHO IT'S FOR, SUCCESS, MATURITY, STACK — from artifacts.
5. Gap-to-MVP: from present vs absent, what's needed.
6. Sufficiency gate: only if truly empty ask ONE question. Else state inferred understanding in 2-3 lines.
Output a STATE TABLE: | Component | Exists? | State | Gap to MVP |"""


def premortem_phase(project_desc: str) -> str:
    return f"""PHASE 2 — PREMORTEM (kill failures before build)
Frame: "It's 6 months from now. {project_desc} failed. Why?"
Generate genuine failure reasons specific to this project. Each:
  - root cause (the assumption that enabled it)
  - early warning (observable, pre-fatal)
  - STRUCTURAL fix (changes the plan, not advisory)
Rank by probability x impact. Fatal x Med+ = ship-blocker.
For substantial projects: one deep-dive per reason, then synthesize
(most likely failure, most dangerous, hidden assumption, revised plan, checklist)."""


def regression_phase(lessons: list) -> str:
    log = "\n".join(f"  - {l['mode']}: {l['cause']} -> {l['fix']}" for l in lessons)
    return f"""PHASE 3 — REGRESSION (prove the method, not just the project)
Known failure modes from the regression log (do not repeat these):
{log}

Check the proposed plan against each. If it would repeat a logged failure,
flag it and apply the logged fix. This is the gate that keeps the method honest."""


def act_phase() -> str:
    return """PHASE 4 — ACT (tandem build)
1. MVP LINE: minimum that delivers real value; below = post-MVP.
2. Next steps as SMALLEST SHIPPABLE CHUNKS; offer to build the first NOW.
3. THE EDGE: what makes this MVP cutting-edge vs standard.
4. MVP VERIFICATION: exact checks proving done.
5. Name the BEHAVIORAL GUARD most likely to kill THIS project and how the
   tandem build holds the line (scope creep / perfectionism / sunk cost / no niche / overstack).

TANDEM MANDATE: do not stop at a plan. Work with the user chunk by chunk until
the MVP ships. Default to executing, not describing."""


def build_protocol(project_path: str, project_desc: str, lessons: list) -> str:
    return "\n\n".join([
        "SYSTEM: You are the evolve-mvp engine. Run the protocol in order. Evidence-based, specific, no fluff.",
        analyze_phase(project_path),
        premortem_phase(project_desc),
        regression_phase(lessons),
        act_phase(),
    ])


# Behavioral guards surface as a checklist the model must honor.
BEHAVIORAL_GUARDS = [
    "ONE audience — force a single clear user before building.",
    "SCOPE LINE hard — below = post-MVP; reject 'just one more feature'.",
    "DONE > PERFECT — ship viable; polish after signal.",
    "SUNK COST IS NOT A REASON — if dead, say so; stop or pivot regardless of hours.",
    "STACK SERVES VALIDATION — simplest stack that proves the bet.",
    "VIABLE > MINIMUM — must prove something real, not a useless stub.",
]


if __name__ == "__main__":
    lp = Path(os.getcwd())
    lessons = load_lessons(lp)
    proto = build_protocol("./my-project", "a SaaS for X", lessons)
    print(proto[:500])
    print(f"\n... [{len(lessons)} lessons loaded]")
