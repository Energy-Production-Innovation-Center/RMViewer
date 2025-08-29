# RMViewer

## Index ##
- [Examples](#examples)
- [Local development](#local-development-environment)
   - [Requirements](#requirements)
   - [Checking code](#checking-code)


RMViewer is a graphing tool that allows you to view representative models in different projections.
It allows you to analyze risk curves, cross plots, histograms, and monitor the convergence of solutions.

## Examples ##

An example configuration file is available at `/examples/config_viewer.json`.

## Local development

The [Task](https://taskfile.dev/) tool provides an easy way to automatize the whole development process.

### Requirements
Make sure you have the following tools installed:

- [Conda](https://docs.conda.io/projects/conda/en/latest/index.html)
- [Docker](https://www.docker.com/)
- [pre-commit](https://pre-commit.com/)
- [Task](https://taskfile.dev/) (v3.0+)

### Checking code

- `task check` to run all tasks, or:
- `task lint:check` ([Ruff](https://docs.astral.sh/ruff/) linter)
- `task format:check` ([Ruff](https://docs.astral.sh/ruff/) formatter)
- `task type:check` ([ty](https://github.com/astral-sh/ty) type checker)

Some tools also support automatic fixing for some known problems:

- `task fix` to run all tasks, or:
- `task lint:fix` ([Ruff](https://docs.astral.sh/ruff/) linter)
- `task format:fix` ([Ruff](https://docs.astral.sh/ruff/) formatter)

The `pre-commit` tool is also configured to run some checks automatically before new commits.

