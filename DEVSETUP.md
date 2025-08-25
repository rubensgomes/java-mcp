# Development Environment Setup

This page contains information to setup your development environment.

## Install required tools

```shell
# macOS commands.
brew install python3
brew install pipx
pipx ensurepath
pipx install pylint
pipx install pytest
pipx install poetry
pipx install python-semantic-release
```

## Add `poetry` dependencies

```shell
# to add runtime dependencies to pyproject.toml (e.g., fastmcp):
# poetry add fastmcp
# to add development dependencies to pyproject.toml (e.g., coverage):
# poetry add --dev coverage
```

## Set up virtual environment

As per [PEP 668](https://peps.python.org/pep-0668/) starting with Python 3.12,
non-brew-packaged Python package should only be installed in virtual
environments.

```shell
# Create virtual environment under <project>/.venv
poetry config virtualenvs.in-project true
poetry update -vv
poetry lock --regenerate -vv
# poetry automatically uses the existing virtual environment to install packages
poetry install
# display information about virtual environment 
poetry env info
poetry show
```

## Open a shell within virtual environment using `poetry`:

```shell
# Ensure at the top of the project root folder
# NOTE: this assumes you have cloned this project from a Git repo
cd $(git rev-parse --show-toplevel) || exit
poetry shell
```

## Linting and Unit Testing

   ```shell
   PACKAGE="java_mcp"
   cd $(git rev-parse --show-toplevel) || exit
   poetry run pylint "${PACKAGE}" || {
     printf "failed pylint.\n" >&2
     sleep 120
     exit 1
   }

   # run pytest with coverage
   poetry run python -m coverage run -m pytest tests/ || {
     printf "failed unit testing.\n" >&2
     sleep 10
     exit 1
   }

   # generate coverage report
   poetry run python -m coverage report -m
   ```

## Clean shell environment

- To complete clean any files and folders from this project untracked by git,
  including venv (virtual enviroment) run:

    ```shell
    git clean -fXd
    ```

- To remove only the virtual environment delete the `.venv` folder:

    ```shell
    # Ensure at the top of the project root folder
    # NOTE: this assumes you have cloned this project from a Git repo
    cd $(git rev-parse --show-toplevel) || exit
    rm -fr .venv/
    ```

## Release process

### GH_TOKEN environment variable

A GH_TOKEN environment variable is required to create releases on GitHub.

### Git commit messages

Due to the project release process, the `git commit` messages should follow the
below conventional commits format for commit messages:

- chore: Update dependencies
- fix: commits → patch version bump (0.1.0 → 0.1.1)
- feat: commits → minor version bump (0.1.0 → 0.2.0)
- BREAKING CHANGE: → major version bump (0.1.0 → 1.0.0)

```shell
git commit -m "feat: add new feature" -a
git push
```

```shell
git commit -m "fix: fixed bug" -a
git push
```

```shell
git commit -m "chore: setting up release" -a
git push
```

```shell
git commit -m "docs: update documentation" -a
git push
```

### Running the release

- Create an initial git tag:

```shell
git tag v0.1.0
git push origin v0.1.0
# Create a release for the existing tag
gh release create v0.1.0 --title "v0.1.0" --notes "Initial release"
```

```shell
# Ensure at the top of the project root folder
# NOTE: this assumes you have cloned this project from a Git repo
cd $(git rev-parse --show-toplevel) || exit
poetry run python -m semantic_release publish
```

## Running the main program

- To display the program version:

    ```shell
    PACKAGE="java_mcp"
    PYTHONPATH="$(git rev-parse --show-toplevel)"
    export PYTHONPATH
    python3 "${PACKAGE}/main.py"
    ```

## PyCharm IDE Development Environment

- First, ensure to follow all the previous steps to "Setting Up Shell
  Development Environment"

1. Open the project `rescreener` folder using `PyCharm`
2. Follow instructions
   to [Create a Poetry environment](https://www.jetbrains.com/help/pycharm/poetry.html#poetry-env)
    - Click on the Python Interpreter Selector to "Add New Interpreter"
    - Select "Add Local Interpreter..."
    - Select "Poetry Environment"
    - Ensure "Base interpreter" is `/opt/homebrew/bin/python3` or
      `/usr/local/bin/python3` (macOS/Linux only)
    - Ensure "Poetry executable" (e.g., ${HOME}/.local/bin/poetry)
    - Click the OK button
3. Go to `PyCharm` > `Settings`
    - Enter `Python Integrated Tools`
    - Under `Testing` > `Default test runner` select `pytest`
4. Open `PyCharm` > `Terminal` to go to venv prompt
    - Ensure .venv correct settings:

    ```shell
    poetry env info
    ```

