# notes-2026

Personal tech notes — debugging journals, post-mortems,
random investigations. Mostly self-reference, occasionally useful.

## Tooling

**REA (Reverse Engineer Anything)** — [morluto/rea](https://github.com/morluto/rea),
MIT. Registered as a project-scope MCP server in `.mcp.json` (pinned to
`rea-agents@6.7.0`, started via `npx`), with the bundled
`reverse-engineer-anything` skill vendored under `.claude/skills/`.
Claude Code picks both up automatically when opened in this repo.
Static JavaScript / .NET inspection works out of the box; native binary
analysis additionally needs Ghidra, Hopper or IDA on the machine.
Update: bump the version in `.mcp.json` and re-copy `skills/` from the
`rea-agents` npm package.
