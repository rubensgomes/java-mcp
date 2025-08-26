# java-mcp

This is MCP server provides AI coding assistant access to Java APIs and
documentations fetched from its corresponding Git repository. It basically
fetches files from a given set of Git repositories and processes Java source
code, extract API information, and serve it to coding assistants.

## Supported Java version

- Java 21 or older

## Prerequisite Tools

- antlr4 4.13.2 or later
- pipx 1.7.1 or later
- poetry 2.1.3 or later
- pylint 3.3.7 or later
- python3 3.13.0 or later
- pytest 8.3.4 or later
- semantic-release 10.3.1 or later
- IDE (e.g., PyCharm)

## Key Libraries

- [FastMCP](https://gofastmcp.com/getting-started/welcome)
- [GitPython](https://gitpython.readthedocs.io/en/stable/)
- [ANTLR4](https://www.antlr.org/)

## Workflow of the MCP server

- Git Repos → Java Source Code -> MCP Server → Structured API Data → AI Assistant Context

### Main Objects

[GitRepoIndexer](java_mcp/git_repo_indexer.py)
- Validates the list of given Git repository URLs
- Ensures a local base folder exists to clone the Git repositories
- Clones or updates the Git repositories from the given URLs
- Provides a list of `Repo` objects representing the cloned repositories





5. : Indexes Java source code from a Git repository.

- `GitRepo`: Represents a Git repository containing Java source code.

## Development Setup

See the [DEVSETUP](DEVSETUP.md) for details on development environment setup.

## Changelog

See the [CHANGELOG](CHANGELOG.md) for details on version updates.

---
Author:  [Rubens Gomes](https://rubensgomes.com/)