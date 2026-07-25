# M.V.P.

**Author:** [@theslayerrway](https://github.com/theslayerrway) · **License:** MIT

> I just want to help people realize their dreams. However I see a lot 
> get lost in the pursuit of trying to create. I believe this tool will 
> help you no matter where you are, to finally get from chat to product.

M.V.P. turns any project into a shipped product — and gets smarter 
from every run.

Analyze. Premortem. Regression. Act. Tandem to ship.

## What it does

Fixed four-phase protocol:

1. **Analyze** — map current state vs. MVP
2. **Premortem** — generate failure modes, verify with maker-checker
3. **Regression** — check plan against past failures
4. **Act** — tandem build, smallest shippable version

Every phase has a mandatory human checkpoint.

## Use it

**CLI**
```bash
pip install mvp-cli
mvp-cli /path/to/your/project
```

**Web**
Open `index.html`. Drop a file or `.zip`. Client-side only.

## Model support

Works with Claude, Gemini, Grok, OpenAI, and local models.

## Outputs

- `mvp-report-[timestamp].html` — visual report
- `mvp-transcript-[timestamp].md` — full transcript
- `LESSONS.json` — self-evolving regression log
