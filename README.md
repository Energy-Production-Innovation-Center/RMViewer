# RMViewer

## Index ##
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Local development](#local-development-environment)


RMViewer is a graphing tool that allows you to view representative models in different projections.
It allows you to analyze risk curves, cross plots, histograms, and monitor the convergence of solutions.

## Installation ##

There are three ways to set up RMViewer locally:

- ###  Download the executable
   Download the binary for your operating system from the [Releases page](https://github.com/Energy-Production-Innovation-Center/RMViewer/releases/latest) page.

- ### Install via pip
   Install the package and its dependencies listed in pyproject.toml:

   ```pip install .```

- ### Set up local develop environment with Task
   The standard development environment. It uses [Task](https://taskfile.dev/) to automatize development process. 

   Click [here](#local-development) for instructions.

## Usage ##
RMViewer can be used in two ways: via CLI or directly in Python.

- ### Command-Line Interface
   You must provide the path to a valid JSON configuration file using the required --config_view argument.

   Examples:

   - #### Pre-built executable
      ```<exec_path> --config_view <json_file_path>```

   - #### Development environment
      ```task run -- --config_view <json_file_path>```

   - #### Via main
      ```python rmviewer/__main__.py --config_view <json_file_path>```

   - ### Directly in Python
      You can use the software directly from Python through a simplified interface. 

      > [!note]
      > If you are running outside the project root directory, set the PYTHONPATH environment variable:
      >
      > Linux:
      > `export PYTHONPATH="/path/to/project:$PYTHONPATH"`
      >
      > Windows (cmd):
      > `set PYTHONPATH=C:\path\to\project;%PYTHONPATH%`

      For a complete example, please check: [examples/script_rmviewer.py](examples/script_rmviewer.py)

## Examples ##

An example configuration file is available at `/examples/config_viewer.json`.

## Local development ##

The [Task](https://taskfile.dev/) tool provides an easy way to automatize the whole development process.

### Requirements
Make sure you have the following tools installed:

- [Conda](https://docs.conda.io/projects/conda/en/latest/index.html)
- [Docker](https://www.docker.com/)
- [pre-commit](https://pre-commit.com/)
- [Task](https://taskfile.dev/) (v3.0+)

### Run the application

- `task run` (Command-line interface)
  - To pass arguments use `--`, e.g. `task run -- --help`

A `conda` environment is automatically created or updated.

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

### Generate executables and installers

Pre-built binaries are available at the [Releases](https://github.com/Energy-Production-Innovation-Center/RMViewer/releases/latest) page.

**Linux:**

- `task build:linux` (application binary)
- `task dist:linux` (`.deb` and `.rpm` installers)

**Windows:**

- `task build:windows` (application binary)
- `task dist:windows` ([NSIS](https://nsis.sourceforge.io/Main_Page) installer)

Files will be available at:
- `rmviewer/out/`

> [!tip]
> Build tasks are executed in an isolated Docker container, so you'll need to be sure that application requirements are correctly configured in the `Dockerfile` when making changes.

