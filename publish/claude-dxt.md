# MVP — install in Claude Desktop (DXT, one-click)

How YOU get MVP in Claude Desktop:

## Install
1. Download `mvp.dxt` from the repo's releases page
2. Double-click it (or drag into Claude Desktop)
3. One-click install — the `mvp` prompt is now available
4. Trigger with: `mvp this: [your idea]`

## What's in the .dxt
- manifest.json (DXT manifest)
- the MVP protocol as a prompt

## Build the .dxt yourself (if no release yet)
Zip this folder's contents → rename to `mvp.dxt`:
- manifest.json
- SKILL.md (the protocol)

The manifest:
{
  "dxt_version": "0.1.0",
  "name": "mvp",
  "display_name": "MVP — From Chat to Product",
  "version": "0.1.0",
  "description": "Analyze -> premortem -> regression -> act. Self-evolving MVP methodology.",
  "author": { "name": "theslayerrway", "url": "https://github.com/theslayerrway/MVP" },
  "license": "Apache-2.0",
  "tools": [],
  "prompts": [
    { "name": "mvp", "description": "Run the MVP protocol on a project",
      "arguments": [{ "name": "input", "description": "project path or idea", "required": true }] }
  ]
}

Repo: https://github.com/theslayerrway/MVP
