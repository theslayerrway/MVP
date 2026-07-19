"""
evolve_mvp/cli.py
CLI entry point. `evolve-mvp /path/to/project`
Runs analyze -> premortem -> regression -> act against any project.
Model-agnostic: picks an adapter (claude/gemini/grok/openai/local).
"""
from __future__ import annotations
import os, sys, argparse, subprocess, datetime
from pathlib import Path
from .core import load_lessons, build_protocol, add_lesson, save_lessons, BEHAVIORAL_GUARDS, VERSION


ADAPTERS = {
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "grok": "XAI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "local": None,  # no key; expects a local OpenAI-compatible endpoint
}


def detect_adapter(arg: str | None) -> str:
    if arg:
        return arg
    for name, env in ADAPTERS.items():
        if env and os.environ.get(env):
            return name
    return "local"


def run_model(adapter: str, prompt: str) -> str:
    """Dispatch to the chosen model. Stubbed call sites; wire real SDKs here.
    For local/headless, falls back to printing the protocol so the user can
    paste it into any AI (Claude/Gemini/Grok/chat) — model-agnostic by design."""
    if adapter == "local":
        # No API key path: emit the full protocol for the user to run anywhere.
        return ("[LOCAL MODE] No API key. Copy the protocol below into any AI "
                "(Claude/Gemini/Grok/ChatGPT) or set an API key to auto-run.\n\n"
                + prompt)
    # Real adapters: each would call its SDK with `prompt`. Placeholder returned
    # so the CLI is runnable today without secrets.
    env = ADAPTERS.get(adapter)
    key = os.environ.get(env) if env else None
    if not key and env:
        return (f"[{adapter}] no {env} set. Set it to auto-run, or use "
                f"--adapter local to print the protocol.\n\n" + prompt)
    # TODO: real SDK call. For now mirror local behavior.
    return ("[STUB] would call " + adapter + " with the protocol.\n\n" + prompt)


def main(argv=None):
    p = argparse.ArgumentParser(prog="evolve-mvp",
        description="Turn any project into a shipped MVP. Self-evolving, regression-gated.")
    p.add_argument("project", help="Path to the project (dir, file, or .zip)")
    p.add_argument("--adapter", choices=list(ADAPTERS), default=None,
                   help="Model backend (claude/gemini/grok/openai/local)")
    p.add_argument("--describe", default="", help="One-line description if known")
    p.add_argument("--version", action="version", version=f"evolve-mvp {VERSION}")
    args = p.parse_args(argv)

    proj = Path(args.project).resolve()
    workdir = Path.cwd()
    lessons = load_lessons(workdir)

    adapter = detect_adapter(args.adapter)
    print(f"evolve-mvp {VERSION}  |  adapter: {adapter}  |  lessons: {len(lessons)}")
    print(f"project: {proj}\n")

    desc = args.describe or str(proj.name)
    protocol = build_protocol(str(proj), desc, lessons)

    print("=" * 60)
    print(protocol)
    print("=" * 60)
    print("\nBEHAVIORAL GUARDS (honor these):")
    for g in BEHAVIORAL_GUARDS:
        print("  -", g)

    out = run_model(adapter, protocol)
    print("\n" + out)

    # Self-evolution hook: if user reports a new failure, append it.
    # (In interactive mode this would capture the model's failure modes.)
    return 0


if __name__ == "__main__":
    sys.exit(main())
