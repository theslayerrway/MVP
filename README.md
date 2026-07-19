# evolve-mvp

> I just want to help people realize their dreams. However I see a lot get lost in the pursuit of trying to create. I believe this tool will help you no matter where you are, to finally get from chat to product. Analyze any project. Utilize M.V.P — analyze → premortem → regression → actionable M.V.P steps.

**evolve-mvp turns any project into a shipped MVP — and gets smarter from every run.**

Most AI tools are frozen prompts. evolve-mvp is different: it runs a four-phase protocol
(analyze → premortem → regression → act) and **evolves from its own failures** via a
regression log. It doesn't wait for you to edit it. It compounds.

## The gap this fills

People don't fail at MVP because of tech. They fail because of:
- **No single audience** — building for everyone
- **Scope creep** — "just one more feature"
- **Perfectionism paralysis** — never launching
- **Sunk-cost fallacy** — continuing a dead project because of hours spent
- **Overengineering** — wrong stack for a validation bet
- **Minimum over viable** — shipping a useless stub

evolve-mvp enforces guards against all six. It reads your project's artifacts, infers
what it is (you barely type), premorts the failure modes, regresses against known
failures, then works in tandem with you to ship.

## Three ways to use it

### 1. CLI
```bash
pip install evolve-mvp
evolve-mvp /path/to/your/project
```
Outputs the full protocol + behavioral guards. Set any API key to auto-run, or use
`--adapter local` to paste the protocol into any AI.

### 2. Web (drag-drop)
Open `index.html`. Drop a file or `.zip`. Get the protocol in a terminal-style
interface. Client-side only — nothing leaves your machine.

### 3. GitHub
Clone, extend, PR. The `LESSONS` regression log is the heart of the tool — add to it
and the engine improves for everyone.

## Model-agnostic
The protocol is plain instructions. Adapters for **Claude, Gemini, Grok, OpenAI,
and local** models. Not locked to any vendor.

## How it evolves
Each run checks the plan against `LESSONS.json` (the regression log). If it would
repeat a past failure, it's flagged and the logged fix applies. New failure modes
append to the log. The tool maintains itself.

## Architecture (Tier0 security standard)
- Read-only artifact inspection by default — never executes untrusted code.
- API keys only from environment — never logged or stored.
- Web UI is fully client-side — no server, no uploads.
- Least privilege throughout.

## License
MIT. Contributions welcome via PR.
