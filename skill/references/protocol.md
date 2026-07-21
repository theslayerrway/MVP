# MVP Protocol — Reference

This is the canonical 4-phase protocol. Agents execute this in order, every time. No skipping.

---

## Phase 1 — ANALYZE (Exhaustive, Minimal User Input)

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

## Phase 2 — PREMORTEM (Kill Failures Before Build)

**Frame:** "It's 6 months from now. This project has failed. It's dead. We're looking back to understand why."

**Run deep-dive agents in PARALLEL** — one agent per failure reason. Each agent gets the full context (what/who/success/maturity/stack + gap table) and produces:

1. **THE FAILURE STORY** — 2-3 paragraph narrative of how this specific failure played out. Use project details. Name specific moments where things went wrong. Make it feel real.
2. **THE UNDERLYING ASSUMPTION** — The one thing the user took for granted that made this failure possible. One sentence.
3. **EARLY WARNING SIGNS** — 1-2 concrete, observable signals the user could watch for (measurable, not vague feelings).
4. **SEVERITY** — Probability (High/Med/Low) × Impact (Fatal/High/Med/Low) → Ship-blocker if Fatal × High/Med.

**Number of agents = number of genuine failure reasons.** Don't stop at 3 if there are 7. Don't force 7 if there are 3. Be comprehensive but not padded.

**Minimum output:** 4 failure reasons. If fewer emerge, the context was too thin — go back to Phase 1.

---

## Phase 3 — REGRESSION (Prove the Method, Not Just the Project)

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

**For each failure mode:** Does the current plan repeat it? If yes → apply the fix. Flag every repeat. The output is a list of "REPEAT DETECTED" with the fix applied.

---

## Phase 4 — ACT (Tandem Build to Ship)

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

## Self-Evolution: LESSONS.json

Every project gets a `LESSONS.json` in its root. First run creates it with hard-coded modes. Subsequent runs:
- Read existing lessons
- If new failure modes discovered, append them (deduped by `mode`)
- The log compounds — the tool gets smarter from usage, not manual edits.

Format:
```json
[
  {"date": "2026-07-19", "mode": "no-single-audience", "cause": "Building for everyone at once", "fix": "Force ONE clear user before building"},
  {"date": "2026-07-19", "mode": "custom-mode", "cause": "Specific to this project", "fix": "Specific fix"}
]
```

---

## Output Files

Every run produces in project root (or cwd):
1. **`mvp-report-[timestamp].html`** — Visual report (dark theme, scannable, inline CSS, opens in browser)
2. **`mvp-transcript-[timestamp].md`** — Full transcript for reference
3. **`LESSONS.json`** — Updated regression log

---

## Model-Agnostic HTML Fallback

If the agent cannot run tools or the user wants a browser UI, open `web/index.html`:
- Drop project files or .zip
- Select model backend (Claude, Gemini, Grok, OpenAI, or "local/paste-anywhere")
- Click RUN PROTOCOL
- Copy the generated protocol + files into your AI of choice
- Client-side only, nothing uploaded