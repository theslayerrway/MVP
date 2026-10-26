import argparse
import html
import sys
import time
import zipfile
from pathlib import Path

from .agent import ALL, HOME, READ, Agent, Model
from .core import BEHAVIORAL_GUARDS, VERSION, act_phase, analyze_phase, load_lessons, premortem_phase, regression_phase

BRIEF = ("You are MVP, an agent that takes a project from where it is to a shipped minimum viable product. "
         "Work only on the phase you are given. Look with tools before you conclude, name the files you used, "
         "and never report something as done or working unless you checked it.")


def skills(root):
    found = {}
    for f in sorted((HOME / "skills").glob("*/SKILL.md")) + sorted((root / ".mvp" / "skills").glob("*/SKILL.md")):
        parts = f.read_text(encoding="utf-8", errors="replace").split("---")
        meta = dict(line.split(":", 1) for line in parts[1].splitlines() if ":" in line) if len(parts) > 2 else {}
        found[f.parent.resolve()] = f"- {meta.get('name', f.parent.name).strip()}: {meta.get('description', '').strip()} ({f})"
    return found


def system(found):
    parts = [BRIEF, "Guards:\n" + "\n".join("- " + g for g in BEHAVIORAL_GUARDS)]
    if found:
        parts.append("Skills. Read a skill's file before using it:\n" + "\n".join(found.values()))
    if (HOME / "MEMORY.md").exists():
        parts.append("What you know about the user:\n" + (HOME / "MEMORY.md").read_text(encoding="utf-8")[-4000:])
    return "\n\n".join(parts)


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return "q"


def finish(agent):
    stamp = time.strftime("%Y%m%d-%H%M%S")
    text = "\n\n".join(
        f"## {m['role']}\n\n{m.get('content') or ''}"
        + "".join(f"\n\n`{c['function']['name']} {c['function']['arguments'][:300]}`" for c in m.get("tool_calls", []))
        for m in agent.messages[1:])
    (agent.dir / f"mvp-transcript-{stamp}.md").write_text(text, encoding="utf-8")
    page = ("<!doctype html><meta charset=utf-8><title>MVP report</title><pre style='white-space:pre-wrap;"
            f"max-width:60rem;margin:2rem auto;font:14px/1.6 ui-monospace,monospace'>{html.escape(text)}</pre>")
    (agent.dir / f"mvp-report-{stamp}.html").write_text(page, encoding="utf-8")
    print(f"\n{agent.tokens} tokens | report and transcript in {agent.dir}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="mvp", description="Analyze, premortem, regression check, then build, "
                                                        "with your sign-off between every phase.")
    p.add_argument("project", nargs="?", default=".")
    p.add_argument("--describe", default="", help="one line about the project")
    p.add_argument("--resume", action="store_true", help="continue the last session in this project")
    a = p.parse_args(argv)
    root = Path(a.project).expanduser().resolve()
    if root.suffix == ".zip":
        zipfile.ZipFile(root).extractall(root.with_suffix(""))
        root = root.with_suffix("")
    if not root.is_dir():
        sys.exit(f"not a folder: {root}")
    model, lessons, found = Model(), load_lessons(root), skills(root)
    agent = Agent(root, model, lessons, found)
    phases = [("analyze", analyze_phase(str(root)), READ),
              ("premortem", premortem_phase(a.describe or root.name), READ),
              ("regression", regression_phase(lessons), READ),
              ("act", act_phase(), ALL)]
    if not (a.resume and agent.load()):
        agent.messages = [{"role": "system", "content": system(found)}]
    print(f"mvp {VERSION} | {model.model or 'default model'} at {model.base} | {root}")
    try:
        for i in range(agent.phase, len(phases)):
            name, prompt, tools = phases[i]
            print(f"\n== {name} ==")
            agent.say(prompt, tools)
            while True:
                reply = ask("\nyou (enter to finish, q to quit): " if name == "act" else
                            "\n[enter] approve and continue, type feedback to redo, q to quit: ")
                if reply.lower() == "q":
                    return finish(agent)
                if not reply:
                    break
                agent.say(reply, tools)
            agent.phase = i + 1
            agent.save()
    except (KeyboardInterrupt, RuntimeError, OSError) as e:
        agent.save()
        print(f"\n[stopped: {e or 'interrupted'}] pick up where you left off with --resume")
    return finish(agent)
