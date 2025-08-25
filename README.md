# java-mcp

This is MCP server provides AI coding assistant access to Java APIs and
documentations fetched from its corresponding Git repository. It basically
fetches files from a given set of Git repositories and processes Java source
code, extract API information, and serve it to coding assistants.

## Supported Java version

- Java 21 or older

## Prerequisite Tools

- pipx 1.7.1 or later
- poetry 2.1.3 or later
- pylint 3.3.7 or later
- python3 3.13.0 or later
- pytest 8.3.4 or later
- IDE (e.g., PyCharm)

## Key Libraries

- [FastMCP](https://gofastmcp.com/getting-started/welcome)
- [GitPython](https://gitpython.readthedocs.io/en/stable/)
- [ANTLR4](https://www.antlr.org/)

## Workflow of the MCP server

- Git Repos → MCP Server → Structured API Data → AI Assistant Context

## Development Setup

See the [DEVSETUP](DEVSETUP.md) for details on development environment setup.

## Changelog

See the [CHANGELOG](CHANGELOG.md) for details on version updates.

---
Author:  [Rubens Gomes](https://rubensgomes.com/)