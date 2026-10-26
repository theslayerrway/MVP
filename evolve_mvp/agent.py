import datetime
import difflib
import json
import os
import re
import signal
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .core import save_lessons

HOME = Path(os.environ.get("MVP_HOME") or Path.home() / ".mvp")
STEPS = int(os.environ.get("MVP_MAX_STEPS", "30"))
BUDGET = int(os.environ.get("MVP_MAX_TOKENS", "0"))
CLIP = 8000
DENIED = "The user denied this action."
LOCAL = [f"http://127.0.0.1:{port}/v1" for port in (8080, 11434, 8000, 5001, 1234)]
SECRET = re.compile(r"^\.|\.(pem|key|p12|pfx)$|^id_|secret|credential", re.I)
CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
HIDDEN_ENV = re.compile(r"KEY|TOKEN|SECRET|PASSWORD", re.I)


def show(*parts):
    print(CTRL.sub("", " ".join(str(p) for p in parts)))


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
        self.kind = "openai"
        self.key = os.environ.get("MVP_API_KEY", "")
        self.model = os.environ.get("MVP_MODEL", "")
        self.base = os.environ.get("MVP_BASE_URL", "").rstrip("/") or next((u for u in LOCAL if self.models(u)), "")
        if not self.base:
            raise SystemExit("No model server found. Set MVP_BASE_URL.")
        host = urllib.parse.urlparse(self.base).hostname or ""
        if self.key and self.base.startswith("http://") and host not in ("127.0.0.1", "localhost", "::1"):
            raise SystemExit("MVP_API_KEY is only sent over https.")
        if host == "api.anthropic.com":
            self.kind = "anthropic"
        if not self.model and not self.key:
            self.model = (self.models(self.base) or [""])[0]
        if not self.model:
            raise SystemExit("Set MVP_MODEL.")

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
        options = "[y/N]" if kind == "run_shell" else "[y/N, a = always this session]"
        try:
            answer = input(f"  allow {what}? {options} ").strip().lower()
        except EOFError:
            return False
        if answer == "a" and kind != "run_shell":
            self.always.add(kind)
            return True
        return answer in ("y", "yes")

    def inside(self, path):
        p = (self.root / Path(path).expanduser()).resolve()
        if p == self.root or self.root in p.parents:
            if any(SECRET.search(part) for part in p.relative_to(self.root).parts):
                raise PermissionError(f"{path} is off limits")
            return p
        if any(d == p or d in p.parents for d in self.extra):
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
                show(f"[token budget of {BUDGET} reached]")
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
                show("\n" + content)
            if not calls:
                break
            for c in calls:
                args = parse(c["function"]["arguments"])
                result = self.run(c["function"]["name"], args, names)
                self.messages.append({"role": "tool", "tool_call_id": c["id"], "content": result})
                self.log("tool", name=c["function"]["name"], args=args, result=result)
        else:
            show(f"[stopped after {STEPS} steps]")
        show(f"[{self.tokens} tokens so far]")
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
                 if p.is_file() and not any(SECRET.search(s) for s in p.relative_to(self.root).parts)]
        return "\n".join(files[:400]) + (f"\n...{len(files) - 400} more" if len(files) > 400 else "")

    def tool_read_file(self, a):
        p = self.inside(a["path"])
        show("  read", a["path"])
        return p.read_text(encoding="utf-8", errors="replace")

    def tool_run_shell(self, a):
        show("  $", a["command"])
        if not self.ok("run_shell", "this command"):
            return DENIED
        env = {k: v for k, v in os.environ.items() if not HIDDEN_ENV.search(k)}
        p = subprocess.Popen(a["command"], shell=True, cwd=self.root, env=env, text=True, start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            out = p.communicate(timeout=300)[0]
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            out = p.communicate()[0] + "\n[killed after 300s]"
        return f"exit {p.returncode}\n{out}"

    def tool_write_file(self, a):
        p = self.inside(a["path"])
        old = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        diff = "".join(difflib.unified_diff(old.splitlines(True), a["content"].splitlines(True), a["path"], a["path"]))
        show(diff[:6000] or f"  {a['path']} unchanged")
        if not self.ok("write_file", f"writing {a['path']}"):
            return DENIED
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(a["content"], encoding="utf-8")
        return f"wrote {a['path']}"

    def tool_propose_lesson(self, a):
        show(f"  lesson {a['mode']}: {a['cause']} -> {a['fix']}")
        if not self.ok("propose_lesson", "this lesson"):
            return DENIED
        entry = {"date": datetime.date.today().isoformat(), "mode": a["mode"], "cause": a["cause"], "fix": a["fix"]}
        self.lessons[:] = [l for l in self.lessons if l["mode"] != a["mode"]] + [entry]
        save_lessons(self.root, self.lessons)
        return "saved to LESSONS.json"

    def tool_remember(self, a):
        show("  remember:", a["text"])
        if not self.ok("remember", "saving this"):
            return DENIED
        HOME.mkdir(parents=True, exist_ok=True)
        with open(HOME / "MEMORY.md", "a", encoding="utf-8") as f:
            f.write(f"- {a['text']}\n")
        return "saved to memory"
