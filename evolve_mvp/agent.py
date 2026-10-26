import datetime
import difflib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from .core import save_lessons

HOME = Path(os.environ.get("MVP_HOME") or Path.home() / ".mvp")
STEPS = int(os.environ.get("MVP_MAX_STEPS", "30"))
BUDGET = int(os.environ.get("MVP_MAX_TOKENS", "0"))
CLIP = 8000
DENIED = "The user denied this action."
LOCAL = ["http://127.0.0.1:8080/v1", "http://127.0.0.1:11434/v1"]
PROVIDERS = {
    "claude": ("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1", "claude-sonnet-5-5"),
    "grok": ("XAI_API_KEY", "https://api.x.ai/v1", ""),
    "openai": ("OPENAI_API_KEY", "https://api.openai.com/v1", ""),
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai", ""),
}


def spec(name, desc, **params):
    props = {k: {"type": "string", "description": v} for k, v in params.items()}
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": list(params)}}}


TOOLS = {
    "list_files": spec("list_files", "List files in a project folder.", path="folder relative to the project root, or ."),
    "read_file": spec("read_file", "Read a text file from the project or a listed skill.", path="file path"),
    "propose_lesson": spec("propose_lesson", "Add a failure mode to the regression log. Needs user approval.",
                           mode="short kebab-case id", cause="what caused the failure", fix="structural fix"),
    "remember": spec("remember", "Save a lasting fact about the user or how they like to work. Needs user approval.",
                     text="the fact"),
    "run_shell": spec("run_shell", "Run a shell command in the project root. Needs user approval.", command="the command"),
    "write_file": spec("write_file", "Create or replace a project file. Needs user approval.",
                       path="file path", content="the complete new file content"),
}
READ = ["list_files", "read_file", "propose_lesson", "remember"]
ALL = READ + ["run_shell", "write_file"]


def http(url, body=None, headers=None, timeout=600, tries=4):
    data = None if body is None else json.dumps(body).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data, {"Content-Type": "application/json", **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if (e.code < 500 and e.code != 429) or i == tries - 1:
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")
        except OSError:
            if i == tries - 1:
                raise
        time.sleep(2 ** i)


def parse(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw or "{}")
    except ValueError:
        return {}


def text_calls(content, names):
    try:
        d = json.loads(content[content.index("{"):content.rindex("}") + 1])
    except ValueError:
        return []
    if not isinstance(d, dict) or d.get("name") not in names:
        return []
    args = d.get("arguments") or d.get("parameters") or {}
    return [{"type": "function", "function": {"name": d["name"], "arguments": json.dumps(args)}}]


def anthropic_messages(messages):
    out = []
    for m in messages[1:]:
        if m["role"] == "assistant":
            role, blocks = "assistant", m.get("_blocks") or (
                ([{"type": "text", "text": m["content"]}] if m["content"] else [])
                + [{"type": "tool_use", "id": c["id"], "name": c["function"]["name"],
                    "input": parse(c["function"]["arguments"])} for c in m.get("tool_calls", [])])
        elif m["role"] == "tool":
            role, blocks = "user", [{"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}]
        else:
            role, blocks = "user", [{"type": "text", "text": m["content"]}]
        if not blocks:
            continue
        if out and out[-1]["role"] == role:
            out[-1]["content"] += blocks
        else:
            out.append({"role": role, "content": list(blocks)})
    return out


class Model:
    def __init__(self):
        name = os.environ.get("MVP_PROVIDER", "").lower()
        self.kind = "anthropic" if name == "claude" else "openai"
        self.base = os.environ.get("MVP_BASE_URL", "").rstrip("/")
        self.model = os.environ.get("MVP_MODEL", "")
        self.key = os.environ.get("MVP_API_KEY", "")
        if name in PROVIDERS:
            env, base, model = PROVIDERS[name]
            self.key, self.base, self.model = self.key or os.environ.get(env, ""), self.base or base, self.model or model
            if not self.key:
                raise SystemExit(f"set {env} to use {name}")
            if not self.model:
                raise SystemExit(f"set MVP_MODEL to the {name} model you want")
        elif not self.base:
            self.base = next((u for u in LOCAL if self.models(u)), "")
            if not self.base:
                raise SystemExit("no local model server on :8080 or :11434. Start llama-server or ollama, "
                                 "or set MVP_PROVIDER to claude, grok, openai or gemini.")
        if not self.model:
            self.model = (self.models(self.base) or [""])[0]

    def headers(self):
        if self.kind == "anthropic":
            return {"x-api-key": self.key, "anthropic-version": "2023-06-01"}
        return {"Authorization": f"Bearer {self.key or 'none'}"}

    def models(self, base):
        try:
            return [m["id"] for m in http(base + "/models", headers=self.headers(), timeout=2, tries=1)["data"]]
        except Exception:
            return []

    def chat(self, messages, tools):
        if self.kind == "anthropic":
            r = http(self.base + "/messages", {
                "model": self.model, "max_tokens": 8192, "system": messages[0]["content"],
                "messages": anthropic_messages(messages),
                "tools": [{"name": t["function"]["name"], "description": t["function"]["description"],
                           "input_schema": t["function"]["parameters"]} for t in tools]}, self.headers())
            calls = [{"id": b["id"], "type": "function",
                      "function": {"name": b["name"], "arguments": json.dumps(b["input"])}}
                     for b in r["content"] if b["type"] == "tool_use"]
            text = "".join(b.get("text", "") for b in r["content"] if b["type"] == "text")
            u = r.get("usage", {})
            return ({"content": text, "tool_calls": calls, "_blocks": r["content"]},
                    u.get("input_tokens", 0) + u.get("output_tokens", 0))
        clean = [{k: v for k, v in m.items() if k != "_blocks"} for m in messages]
        r = http(self.base + "/chat/completions", {"model": self.model, "messages": clean, "tools": tools},
                 self.headers())
        return r["choices"][0]["message"], (r.get("usage") or {}).get("total_tokens", 0)


class Agent:
    def __init__(self, root, model, lessons, extra=()):
        self.root, self.model, self.lessons, self.extra = root, model, lessons, list(extra)
        self.messages, self.tokens, self.phase, self.always = [], 0, 0, set()
        self.dir = root / ".mvp"
        self.dir.mkdir(exist_ok=True)
        self.logfile = self.dir / f"log-{time.strftime('%Y%m%d-%H%M%S')}.jsonl"

    def log(self, kind, **data):
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": round(time.time(), 3), "kind": kind, **data}) + "\n")

    def save(self):
        state = {"phase": self.phase, "tokens": self.tokens, "messages": self.messages}
        (self.dir / "session.json").write_text(json.dumps(state), encoding="utf-8")

    def load(self):
        path = self.dir / "session.json"
        if not path.exists():
            return False
        state = json.loads(path.read_text(encoding="utf-8"))
        self.phase, self.tokens, self.messages = state["phase"], state["tokens"], state["messages"]
        return True

    def ok(self, kind, what):
        if kind in self.always:
            return True
        try:
            answer = input(f"  allow {what}? [y/N, a = always this session] ").strip().lower()
        except EOFError:
            return False
        if answer == "a":
            self.always.add(kind)
        return answer in ("y", "yes", "a")

    def inside(self, path):
        p = (self.root / Path(path).expanduser()).resolve()
        if any(d == p or d in p.parents for d in [self.root, *self.extra]):
            return p
        raise PermissionError(f"{path} is outside the project")

    def say(self, text, tools):
        self.messages.append({"role": "user", "content": text})
        self.log("user", text=text)
        self.turn(tools)

    def turn(self, names):
        tools = [TOOLS[n] for n in names]
        for _ in range(STEPS):
            if BUDGET and self.tokens >= BUDGET:
                print(f"[token budget of {BUDGET} reached]")
                break
            msg, used = self.model.chat(self.messages, tools)
            self.tokens += used
            content, calls = msg.get("content") or "", msg.get("tool_calls") or []
            if not calls and self.model.kind == "openai":
                calls = text_calls(content, names)
                content = "" if calls else content
            for i, c in enumerate(calls):
                c["id"] = c.get("id") or f"call{len(self.messages)}_{i}"
            entry = {"role": "assistant", "content": content}
            if calls:
                entry["tool_calls"] = calls
            if msg.get("_blocks"):
                entry["_blocks"] = msg["_blocks"]
            self.messages.append(entry)
            self.log("assistant", content=content, tool_calls=calls, tokens=used)
            if content:
                print("\n" + content)
            if not calls:
                break
            for c in calls:
                args = parse(c["function"]["arguments"])
                result = self.run(c["function"]["name"], args, names)
                self.messages.append({"role": "tool", "tool_call_id": c["id"], "content": result})
                self.log("tool", name=c["function"]["name"], args=args, result=result)
        else:
            print(f"[stopped after {STEPS} steps]")
        print(f"[{self.tokens} tokens so far]")
        self.save()

    def run(self, name, args, allowed):
        if name not in allowed:
            return f"{name} is not available in this phase."
        try:
            out = getattr(self, "tool_" + name)(args)
        except Exception as e:
            out = f"error: {e}"
        return out if len(out) <= CLIP else out[:CLIP] + f"\n...[{len(out) - CLIP} more characters]"

    def tool_list_files(self, a):
        base = self.inside(a.get("path") or ".")
        files = [str(p.relative_to(self.root)) for p in sorted(base.rglob("*"))
                 if p.is_file() and not any(s.startswith(".") for s in p.relative_to(self.root).parts)]
        return "\n".join(files[:400]) + (f"\n...{len(files) - 400} more" if len(files) > 400 else "")

    def tool_read_file(self, a):
        p = self.inside(a["path"])
        print(f"  read {a['path']}")
        return p.read_text(encoding="utf-8", errors="replace")

    def tool_run_shell(self, a):
        print(f"  $ {a['command']}")
        if not self.ok("run_shell", "this command"):
            return DENIED
        r = subprocess.run(a["command"], shell=True, cwd=self.root, capture_output=True, text=True, timeout=300)
        return f"exit {r.returncode}\n{r.stdout}{r.stderr}"

    def tool_write_file(self, a):
        p = self.inside(a["path"])
        old = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        diff = "".join(difflib.unified_diff(old.splitlines(True), a["content"].splitlines(True), a["path"], a["path"]))
        print(diff[:6000] or f"  {a['path']} unchanged")
        if not self.ok("write_file", f"writing {a['path']}"):
            return DENIED
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(a["content"], encoding="utf-8")
        return f"wrote {a['path']}"

    def tool_propose_lesson(self, a):
        print(f"  lesson {a['mode']}: {a['cause']} -> {a['fix']}")
        if not self.ok("propose_lesson", "this lesson"):
            return DENIED
        entry = {"date": datetime.date.today().isoformat(), "mode": a["mode"], "cause": a["cause"], "fix": a["fix"]}
        self.lessons[:] = [l for l in self.lessons if l["mode"] != a["mode"]] + [entry]
        save_lessons(self.root, self.lessons)
        return "saved to LESSONS.json"

    def tool_remember(self, a):
        print(f"  remember: {a['text']}")
        if not self.ok("remember", "saving this"):
            return DENIED
        HOME.mkdir(parents=True, exist_ok=True)
        with open(HOME / "MEMORY.md", "a", encoding="utf-8") as f:
            f.write(f"- {a['text']}\n")
        return "saved to memory"
