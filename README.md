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

## Prompt provided to Claude

I need to develop an MCP server in python3 that will fetch and extract APIs and
documentation from Java version 21 source code files stored in Git repositories.
The APIs and documentation should be served to AI coding assistants. The
following are some requirements for the MCP server:

- The MCP server should Use the "gitpython" python library to handle Git
  operations.
- The MCP server should use the "FastMCP" python library to handle MCP server
  operations.
- The MCP server should use the "antlr4-python3-runtime" python library to
  handle Java source code parsing.
- The MCP server should use the "pylint" python library to ensure code quality.
- The MCP server should use the "pytest" python library to handle unit tests.
- The MCP server should use the "semantic-release" python library to handle
  versioning and releases.
- The MCP server should use the "poetry" python library to handle dependency
  management.
- The MCP server should be able to run on macOS or Linux operating systems.
- The MCP server should be able to run on Python 3.13 or later.
- The MCP server should the standard Python logging library to handle logging.
- The MCP server should be able to handle Java source code files written in
  Java version 21 or older.
- The MCP server should be able to handle Git repositories hosted on GitHub,
  GitLab, Bitbucket, or any other Git hosting service.
- The MCP server should use the antlr4 generated JavaLexer, JavarParser, and
  JavaParserListener classes to parse Java source code files.
- The MCP server should be modular and well documented.
- The MCP server should be able to handle multiple Git repository URLs as
  input.
- The MCP server should accept the list of Git repository URLs as an input
  parameter, either via a configuration file or command line argument.
- The MCP server should accept the local base folder path as an input parameter,
  either via a configuration file or command line argument.
- The MCP server should be able to clone or update the local Git repositories
  based on the provided URLs. The local repositories should be shallow clones.
- The MCP server should use the input local folder as the base folder to clone
  or update the Git repositories.
- The MCP server should be able to extract API information, documentation and
  other relevant information from the Java source code files and serve it to AI
  coding assistants.
- The MCP server should only fetch Java source code files located under the
  `src/main/java` directory of each Git repository.
- The MCP server should be able to handle errors gracefully, such as invalid
  Git repository URLs or network issues during Git operations.
- The MCP server should be able to run as a standalone program, with clear
  instructions on how to set up the environment and run the program.
- The MCP server should be able to handle signal interruptions (e.g., SIGINT)
  and perform necessary cleanup operations before exiting.
- The MCP server should include unit tests to ensure the correctness of its
  functionality.
- The MCP server should expose Resources as well as Tool capabilities to AI
  coding assistants.
- The MCP server should be able to handle concurrent requests from multiple AI
  coding assistants.
- The MCP server should define Python @dataclass classes to implement data
  structures that represent the extracted Java API code elements (annotations,
  classes, methods, parameters, fields) information and documentation in a
  structured format.

## Workflow of the MCP server

Git Repos → Java Source Code -> MCP Server → Structured API Data → AI Assistant
Context

### The ANTLR4 Process Flow

Java Source Code → Lexer → Tokens → Parser → Parse Tree → Your Analysis

## Application Classes

### Data Structure Classes

[Annotation](java_mcp/types/annotation.py)

- Represents a Java annotation with its name and parameters.

[Parameter](java_mcp/types/parameter.py)

- Represents a Java method parameter with complete type and annotation
  information.

[Method](java_mcp/types/method.py)

- Represents a Java method with complete signature and metadata information.

[Field](java_mcp/types/field.py)

- Represents a Java field (instance or class variable) with complete metadata.

[Class](java_mcp/types/java_class.py)

- Represents a complete Java class, interface, enum, or record with all
  metadata.

### Base Model Classes

[AnalyzeClassRequest](java_mcp/model/analyze_class_request.py)

- Represents a request to analyze a Java class, requiring as input the
  fully-qualified class name, and optional the repository name.
  source file path.

[ExtractAPIsRequest](java_mcp/model/extract_apis_request.py)

- Represents a request to extract Java APIs, requiring as input the
  Git repository URL, and the corresponding branch. It takes as optional inputs
  a package name, and class name to filter the extraction.

[GenerateGuideRequest](java_mcp/model/generate_guide_request.py)

- Represents a request to generate API usage guides. It takes as input a
  specific use case or functionality needed. And for optional inputs it takes a
  specific repository to focus on.

[SearchMethodsRequest](java_mcp/model/search_methods_request.py)

- Represents a request to search for Java methods. It takes as input the method
  name to search for. As optional inputs it takes a class name to filter on.

### Behaviour Objects

#### [GitRepoIndexer](java_mcp/git/git_repo_indexer.py)

Purpose:

- Validates the list of given Git repository URLs.
- Ensures a local base folder exists to clone the Git repositories.
- Clones or updates the Git repositories from the given URLs.
- Provides a list of `Repo` objects representing the cloned repositories.

Inputs:

- list of Git repository URLs.
- local base folder path for cloning repositories.

Outputs:

- list of `Repo` instances representing "shallow" local cloned repositories.
  This means Git only fetches the latest commit from the default branch on the
  specified Git remote repository.

#### [PathIndexer](java_mcp/parser/path_indexer.py)

Purpose:

- Creates a list of paths to Java source files found under the `src/main/java`
  directory of each local cloned Git repository in the provided list of `Repo`.

Inputs:

- list of `Repo` objects representing shallow cloned Git repositories.

Outputs:

- list of paths to Java source files found under the `src/main/java` directory
  of each local cloned Git repository.

#### [ParseErrorListener](java_mcp/parser/parser_error_listener.py)

Purpose:

- Custom ANTLR4 error listener used to report syntax errors during lexical and
  parser analysis of for Java source code processing.

Inputs:

- ANTLR4 syntax errors during lexical and parser analysis of Java source code.

Outputs:

- Logs syntax errors during lexical and parser analysis of Java source code.

#### [SourceParser](java_mcp/parser/source_parser.py)

Purpose:

- The SourceParser starts the lexical analysis (or "scanning") of the Java
  source code followed by the syntax analysis (or "parsing"). Then, it generates
  a Parer Walker Tree which is processed by a listener to extract the API
  elements (e.g, annotations, methods, parameters, fields, classes).

Inputs:

- Source file path to a Java source code file, and the corresponding content of
  the file.

Outputs:

- A `Class` object representing the parsed Java class, interface, enum, or
  record with all its metadata.

#### [APIExtractorListener](java_mcp/parser/api_extractor_listener.py)

Purpose:

- Event-driven ANTLR4 Listener for extracting Java API information from parse
  trees.

Inputs:

- Parser Walker Tree generated from a Java source code file.

Outputs:

- Java API elements (e.g., import, method declaration, classes) populated from
  inside event-driven enter methods called by the ANTLR4 Parser Walker. .

## Development Setup

See the [DEVSETUP](DEVSETUP.md) for details on development environment setup.

## Changelog

See the [CHANGELOG](CHANGELOG.md) for details on version updates.

---
Author:  [Rubens Gomes](https://rubensgomes.com/)