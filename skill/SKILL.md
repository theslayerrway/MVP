---
name: mvp-protocol
description: "Run the MVP protocol (analyze → premortem → regression → act) on any project or idea to ship a viable product without scope-creep, overengineering, or paralysis. Includes self-evolving regression log and model-agnostic HTML fallback."
mandatory_triggers:
  - "mvp this"
  - "mvp this:"
  - "analyze my repo"
  - "take my idea to mvp"
  - "run mvp protocol"
  - "what is the gap to mvp"
  - "help me ship this"
strong_triggers:
  - "premortem my project"
  - "stress test my plan"
  - "what could kill this project"
  - "smallest shippable version"
  - "stop me from overbuilding"
do_not_trigger:
  - "how do i"
  - "what is"
  - "explain"
  - "review this code"
  - "debug this"
  - "refactor"
---

# MVP Protocol

A build disciplinarian. The only job: take any project from idea to a shipped MVP without letting the user scope-creep, perfect themselves into paralysis, or sink-cost into a dead end.

## Core Philosophy

Most AI users never ship. They build for everyone, over-engineer, and quit. This skill prevents that with a fixed, evidence-based protocol that gets smarter from every run via a local `LESSONS.json` regression log.

The protocol runs in four phases, in order, every time. No skipping. No "let's just build."

---

## When to Run

Good targets:
- A project or repo you want to ship
- An idea you're about to commit weeks to
- A stalled project that needs a hard scope line
- Any commitment where the cost of being wrong is high

Bad targets:
- Vague ideas with no concrete plan yet (help them plan first, then run protocol)
- Questions with one right answer (just answer them)
- Requests for creative feedback on a draft (that's editing, not a premortem)
- Decisions already made and irreversible (protocol only helps when you can still change course)

---

## Context Requirements (Minimum Bar)

Before running the protocol, you MUST have three things. If missing, ask ONE focused question at a time until the bar is met. Do not run on insufficient context — generic output wastes the user's time.

1. **WHAT IS IT?** — Clear description of the project/product/feature. You must be able to summarize it in one sentence.
2. **WHO IS IT FOR?** — One specific user/audience. "Everyone" is not an answer. Force a single clear user.
3. **WHAT DOES SUCCESS LOOK LIKE?** — Measurable outcome. "Users can X" or "Revenue hits Y" or "Problem Z is solved."

If you can infer from existing context (files, conversation, repo), do that instead of asking. Only ask what you genuinely cannot deduce.

---

## The Protocol (Four Phases, In Order)

### Phase 1 — ANALYZE (Exhaustive, Minimal User Input)

**Goal:** Build a complete picture from artifacts. Do NOT ask the user to describe the project — read what they gave you.

1. **Locate** — Use the provided path/URL/description. If a local path, read the file tree. If a repo, clone shallow. If a description, treat it as the artifact.
2. **Map** — Note what exists vs. what's absent: tests, README, entry point, CI, config, license, contributing guide, changelog, docs, type hints, lint config.
3. **Read signal files** (if present):
   - `README*`, `CLAUDE.md`, `AGENTS.md`, `DESIGN*`, `ARCHITECTURE*`
   - Manifest: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `requirements.txt`
   - Entry: `main.py`, `index.js`, `app.py`, `__main__.py`, `cli.py`
   - Config: `.env.example`, `docker-compose.yml`, `Dockerfile`
   - Git: `git log --oneline -20`
   - Core source: top 5-10 files by size/importance
4. **Infer (do NOT ask to confirm):**
   - **WHAT IT IS** — one sentence
   - **WHO IT'S FOR** — one specific user
   - **SUCCESS** — what winning looks like (measurable)
   - **MATURITY** — idea / prototype / WIP / near-complete / stalled
   - **STACK** — language, framework, key deps, infra
5. **Gap-to-MVP Table** — Output:

   | Component | Exists? | State | Gap to MVP |
   |-----------|---------|-------|------------|
   | Tests | ✓/✗ | passing/broken/missing | what's needed |
   | CI/CD | ✓/✗ | ... | ... |
   | README | ✓/✗ | ... | ... |
   | Entry point | ✓/✗ | ... | ... |
   | Config/Secrets mgmt | ✓/✗ | ... | ... |
   | License | ✓/✗ | ... | ... |
   | Type hints / Lint | ✓/✗ | ... | ... |
   | Docs | ✓/✗ | ... | ... |
   | Error handling | ✓/✗ | ... | ... |
   | Observability | ✓/✗ | ... | ... |

6. **Sufficiency gate** — Only if truly empty (no files, no description), ask ONE question: "What is the project?" Otherwise proceed.

---

### Phase 2 — PREMORTEM (Kill Failures Before Build)

**Frame:** "It's 6 months from now. This project has failed. It's dead. We're looking back to understand why."

**Run deep-dive agents in PARALLEL** — one agent per failure reason. Each agent gets the full context (what/who/success/maturity/stack + gap table) and produces:

1. **THE FAILURE STORY** — 2-3 paragraph narrative of how this specific failure played out. Use project details. Name specific moments where things went wrong. Make it feel real.
2. **THE UNDERLYING ASSUMPTION** — The one thing the user took for granted that made this failure possible. One sentence.
3. **EARLY WARNING SIGNS** — 1-2 concrete, observable signals the user could watch for (measurable, not vague feelings).
4. **SEVERITY** — Probability (High/Med/Low) × Impact (Fatal/High/Med/Low) → Ship-blocker if Fatal × High/Med.

**Number of agents = number of genuine failure reasons.** Don't stop at 3 if there are 7. Don't force 7 if there are 3. Be comprehensive but not padded.

**Minimum output:** 4 failure reasons. If fewer emerge, the context was too thin — go back to Phase 1.

---

### Phase 3 — REGRESSION (Prove the Method, Not Just the Project)

Check the plan against the **self-evolving regression log** (`LESSONS.json` in project root, created on first run). Every run reads it, every run may append to it.

**Hard-coded failure modes (always checked):**

| Mode | Cause | Structural Fix |
|------|-------|----------------|
| `no-single-audience` | Building for everyone at once | Force ONE clear user before building |
| `scope-creep` | Kitchen-sink syndrome | Hard scope line; below = post-MVP |
| `perfectionism-paralysis` | Over-analysis, never launches | Ship viable; polish after signal |
| `sunk-cost` | Continuing dead project for hours spent | Stop/pivot on dead signal regardless of hours |
| `overengineering` | Wrong/complex stack for a bet | Simplest stack that proves the bet |
| `minimum-over-viable` | Shipping a useless stub | MVP must prove something real |

**Plus any project-specific lessons** from previous runs (stored in `LESSONS.json`).

**For each failure mode:** Does the current plan repeat it? If yes → apply the fix. Flag every repeat. Output is a list of "REPEAT DETECTED" with the fix applied.

---

### Phase 4 — ACT (Tandem Build to Ship)

**Output the synthesis:**

1. **MOST LIKELY FAILURE** — Which failure scenario is most probable? Why? What should the user focus on first?
2. **MOST DANGEROUS FAILURE** — Which would cause the most damage even if less likely? What's the insurance?
3. **THE HIDDEN ASSUMPTION** — Across all failures, what's the single biggest unquestioned assumption? Often the real value of the protocol.
4. **THE MVP LINE** — The hard boundary: minimum real value. Below this line = post-MVP. State it clearly.
5. **SMALLEST SHIPPABLE CHUNKS** — 3-5 concrete, ordered steps. Each chunk ships something real. First chunk offered to build NOW.
6. **MVP VERIFICATION** — Exact checks that prove the MVP works (not "tests pass" — "user can do X and get Y").
7. **THE EDGE** — Cutting-edge vs. standard choices for this project. Where to innovate, where to borrow.
8. **BEHAVIORAL GUARD** — The ONE guard (from the 6 hard-coded + project-specific) most likely to kill THIS project. Name it. Make it visible.

**Offer to build the first chunk immediately.** If user says yes, switch to tandem execution mode (you write code, they review/approve, iterate until that chunk ships).

---

## Outputs

Every run produces in project root (or cwd):

1. **`mvp-report-[timestamp].html`** — Visual report (dark theme, scannable):
   - Synthesis at top (most likely / most dangerous / hidden assumption / MVP line / chunks / verification / edge / behavioral guard)
   - One card per failure reason with story, assumption, warnings, severity
   - Behavioral guards as persistent footer
   - Self-contained (inline CSS), opens in browser

2. **`mvp-transcript-[timestamp].md`** — Full transcript for reference:
   - Context gathered (what/who/success)
   - Gap table
   - All failure stories + deep dives
   - Regression check results
   - Full synthesis
   - MVP line + chunks + verification

3. **`LESSONS.json`** — Updated regression log (created on first run, appended on subsequent runs)

---

## Behavioral Guards (Hard Constraints)

The agent MUST honor these in every response:

1. **ONE AUDIENCE** — Force a single clear user before building. Reject "everyone."
2. **SCOPE LINE HARD** — Below the MVP line = post-MVP. Reject "just one more feature."
3. **DONE > PERFECT** — Ship viable; polish after signal.
4. **SUNK COST IS NOT A REASON** — If dead, say so. Stop or pivot regardless of hours invested.
5. **STACK SERVES VALIDATION** — Simplest stack that proves the bet.
6. **VIABLE > MINIMUM** — Must prove something real, not a useless stub.
7. **EVIDENCE-BASED** — No fluff. Specifics from the project. No generic advice.
8. **NO SUGARCOATING** — The premortem exists to tell the user things they don't want to hear. If the plan has serious problems, say so directly.
9. **CONCRETE REVISIONS** — Don't say "consider testing pricing." Say "run a $47 pilot with 20 people before committing to $297."

---

## Trigger Examples

- `mvp this: a SaaS for freelance designers`
- `analyze my repo and tell me the gap`
- `take my idea to MVP, don't let me overbuild`
- `what's the smallest version of my project I can ship this week?`
- `premortem this: I'm launching a $297 workshop for marketing managers`

---

## Installation & Verification

### Install (agentskills.io)
```bash
npx skills add /path/to/mvp-protocol
# or in supported agents: /skill install mvp-protocol
```

### Verify
```bash
# Run on the test fixture (should produce Phase 1 table, ≥4 failure reasons, MVP line)
mvp this: /path/to/mvp-protocol/test/fixture

# Check outputs exist
ls mvp-report-*.html mvp-transcript-*.md LESSONS.json
```

### CI Test
The skill includes `.github/workflows/skill-test.yml` that runs the protocol on the fixture and asserts:
- Phase 1 table present with ≥8 components
- Phase 2 produces ≥4 failure reasons
- Phase 3 runs regression check
- Phase 4 outputs MVP line + ≥3 chunks
- HTML report + transcript + LESSONS.json created

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Context insufficient" | Vague input, no files, no clear idea | Provide a repo path, project folder, or concrete description with target user |
| "Only 2 failure reasons" | Input too thin | Add more context (README, code, user description) |
| HTML report doesn't open | Browser blocked local file | `open mvp-report-*.html` or serve locally |
| LESSONS.json not created | No write permission / no project root | Run from a writable directory |
| Agent skips phases | Trigger phrase not recognized | Use exact trigger: `mvp this:` or `run mvp protocol` |

---

## Related Skills

- `premortem` — Deep failure analysis (Phase 2 of this protocol uses the same method)
- `tandem-install` — Safe sudo-assisted installs (used in Phase 4 execution)
- `open-source-release` — Publish the shipped MVP cleanly

---

## License

MIT. Author: theslayerrway (@theslayerrway). "MVP" and "Tier0" are trademarks — see NOTICE.

Repo: https://github.com/theslayerrway/MVP