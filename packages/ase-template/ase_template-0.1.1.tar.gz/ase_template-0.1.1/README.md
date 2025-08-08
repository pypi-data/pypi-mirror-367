# Agentic software engineering (ASE) template repository

The purpose of this repository is to serve as a public template for agentic software engineering (ASE) developed at [Ascend.io](https://ascend.io). We use a variety of tools like Claude Code, Cursor, Codex CLI, and GitHub Copilot to assist in the software development process. This repository is designed to be a starting point for teams looking to implement ASE practices in their own projects.

## What?

Common context to be included in all agentic sessions are centralized in the [`AGENTS.md`](AGENTS.md) file. Tool-specific files are then symlinked or copied from this `AGENTS.md` file.

### Structure

| ***What*** | ***How*** | ***Why*** |
|------|-----|-----|
| `AGENTS.md` | Central context file | Single source of truth for agent instructions |
| `CLAUDE.md` | Symlinked from AGENTS.md | Claude Code specific context |
| `GEMINI.md` | Symlinked from AGENTS.md | Gemini CLI specific context |
| `.github/copilot-instructions.md` | Symlinked from AGENTS.md | GitHub Copilot specific context |
| `bin/` | Executable utility scripts | Direct execution of bash/Python utilities |
| `prompts/` | Durable context files as Markdown | Reusable prompt templates and context |
| `tasks/` | Ephemeral development task files | Temporary task documentation |
| `src/` | Source code directory | Main application code |

## Why?

Standards are hard [obligatory xkcd here]. Nobody agrees on the files -- nor even the extension -- to use for their ASE tooling. So, over time we settled on the root agent context file with some additional structure.

