"""
Java Processing Package for Java MCP Server

This package provides comprehensive Java source code processing capabilities for the Java MCP Server.
It serves as the core Java analysis layer, handling Java file discovery, path management, and type
definitions for Java source code processing workflows.

The package bridges Git repository management with Java source code analysis by providing utilities
to locate, index, and process Java files within standard Maven/Gradle project structures.

Key Features:
- Java source file discovery and indexing from Git repositories
- Support for standard Maven/Gradle project structures (src/main/java)
- Path management for Java source files with cross-platform compatibility
- Type definitions for Java language constructs and analysis
- Integration with Git repository management for multi-repository Java projects
- Recursive package structure traversal and Java file discovery

Modules:
    java_path_indexer: Discovers and indexes Java source files from Git repositories
    types: Defines type structures for Java language constructs and analysis

Classes:
    JavaPathIndexer: Main class for indexing Java file paths from Git repositories

Functions:
    (Exported from submodules for convenient access)

Usage:
    # Import the main Java path indexer
    from java_mcp.java import JavaPathIndexer

    # Use with Git repositories to discover Java files
    from java_mcp.git import GitRepoIndexer
    git_indexer = GitRepoIndexer(repo_urls, "/local/repos")
    local_repos = git_indexer.get_local_repos()
    java_indexer = JavaPathIndexer(local_repos)
    java_files = java_indexer.get_java_paths()

    # Import type definitions
    from java_mcp.java.types import JavaClass, JavaMethod, JavaField

Project Structure Support:
    The package expects and supports standard Java project structures:
    - Maven: src/main/java/
    - Gradle: src/main/java/
    - Multi-module projects with nested src/main/java directories
    - Nested package hierarchies (com.example.project.*)

Dependencies:
    - GitPython: For Git repository operations
    - pathlib: For cross-platform path handling
    - typing: For type annotations and definitions

Integration:
    This package integrates with:
    - java_mcp.git: For Git repository management and cloning
    - java_mcp.parser: For Java source code parsing and analysis
    - java_mcp.server: For MCP server functionality

Author: Rubens Gomes
License: Apache-2.0
Version: 1.0.0
Package: java_mcp.java
"""

# Import main classes and functions for easy access
from .java_path_indexer import JavaPathIndexer

# Import type definitions for convenient access
from .types import *

# Define what gets exported when using "from java_mcp.java import *"
__all__ = [
    # Main indexer class
    'JavaPathIndexer',

    # Export all type definitions from types module
    # (This will include JavaClass, JavaMethod, JavaField, etc. when defined)
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Rubens Gomes'
__license__ = 'Apache-2.0'
__package_name__ = 'java_mcp.java'

# Module-level logging configuration
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Initialized {__package_name__} package version {__version__}")
