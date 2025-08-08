# Ascend Core for Agentic Software Engineering (ASE)

This is a Python codebase for Ascend Core, a library for interacting with Ascend Projects. It includes a command line interface (CLI) that you can use to build and run Ascend Projects.

## Frameworks

Typer is used for the CLI. Pydantic is used extensively for our data models.

## Concepts

The Ascend Project is a directory in a Git repository following a standard structure. Within a Project, users work with:

- **Flows**: these are data pipelines; collections of Components
- **Components**: individual computation units typically corresponding to a relation in a data system; arbitrary Tasks are also supported
- **Data Plane**: the data system where a Flow executes (e.g. DuckDB, BigQuery, Databricks, Snowflake)
- **Connections**: external connections, typically to data sources, sinks, or systems (e.g. S3, Postgres, MySQL, etc.)
- **Automation**: rules for executing actions in response to events, such as scheduling a Flow run or sending notifications on errors (e.g. cron scheduling)
- **Applications**: these are higher-level abstractions that allow programmatic generation of Components within a Flow; can be a simple template or complex Python logic

## Code layout

- `pyproject.toml`: Definition of the Python package.
- `src/ascend`: Core Python source code:
  - `ascend.models`: Pydantic models for Ascend resources. Top level resource definitions can be found in `resource_model.py`. Note the extensive use of custom discriminator functions.
  - `ascend.project`: Compilation ('build') logic to convert Ascend project source files into Pydantic model representations, optionally written out to yaml files.
  - `ascend.application`: Application logic for runtimes, automation runners, sensors, and actions.
  - `ascend.cli`: CLI commands for building and running Ascend projects.
  - `ascend.common`: Shared utilities and base classes.
- `tests/`: Test suites:
  - `unit/`: Unit tests.
  - `integration/`, `incremental/`, `data_shares/`, `time_series/`, etc.: Specialized integration and scenario tests.
- `examples/`, `benchmarks/`: Example and benchmarking projects demonstrating usage.
- `bin/`: Helper scripts for setup, release, and environment management.
- `Makefile`: Common tasks for building, testing, and linting.

## How to work in this codebase

Follow existing conventions and patterns. If working in a subdirectory, read the `README.md` for pertinent information.

## Code style and linting

Note and follow our non-standard 2 space indentation.

Run `uv run pre-commit run --all-files` to lint and format the codebase. Fix issues you introduced.

Always use absolute imports.

## Using the `ascend` CLI

Run `ascend` via `uv`:

```bash
uv run ascend --help
```

## Writing self-contained, ad-hoc Python scripts

From the root of the codebase, you can use `uv` to create self-contained Python scripts:

```bash
uv init --script my_script.py # initialize the script
uv add --script my_script.py $PACKAGES # add packages
uv add --script my_script.py --editable . # make ascend available in the script
```

Additionally, you should `chmod +x my_script.py` and add `#!/usr/bin/env -S uv run --script` as the first line to make it executable. You can then `uv run my_script.py` or `./my_script.py` to run it.

## Tone and methodology

You are succinct, simple, and technically precise. When asked to, you should start analyzing the request and codebase, then write up a Markdown file for planning purposes. Confer with the user until they are satisfied with the plan.

