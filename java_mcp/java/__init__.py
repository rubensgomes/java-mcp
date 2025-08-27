"""
Java Processing Package for Java MCP Server

This package provides comprehensive Java source code processing capabilities for the Java MCP Server.
It serves as the core Java analysis layer, handling Java file discovery, path management, type
definitions, and source code parsing for Java projects within Git repositories.

The package bridges Git repository management with Java source code analysis by providing utilities
to locate, index, parse, and analyze Java files within standard Maven/Gradle project structures,
enabling AI assistants to understand and work with Java codebases effectively.

Package Structure:
=================

Core Modules:
- java_path_indexer.py: Java source file discovery and path management utilities
- types/: Comprehensive type system for representing Java code elements

Subpackages:
- types/: Complete type definitions for Java language constructs
  - annotation.py: Java annotation representations with parameters
  - parameter.py: Method parameter definitions with type information
  - method.py: Method and constructor representations with signatures
  - field.py: Field and variable definitions with modifiers
  - java_class.py: Complete class, interface, enum, and record representations
  - aliases.py: Type aliases and union types for collections and flexibility

Key Features:
============

Java File Discovery:
- Automatic detection of Java source files in Git repositories
- Support for standard Maven/Gradle project structures (src/main/java, src/test/java)
- Cross-platform path management and normalization
- Recursive directory traversal with filtering capabilities

Project Structure Support:
- Maven standard directory layout recognition
- Gradle project structure compatibility
- Multi-module project support
- Test source separation and handling

Type System:
- Complete representation of Java language constructs
- Rich metadata capture (annotations, documentation, source locations)
- Support for modern Java features (records, sealed classes, pattern matching)
- Type-safe collections and utility functions

Integration Points:
==================

Git Repository Integration:
- Works seamlessly with java_mcp.git for repository management
- Handles repository cloning, updating, and file system access
- Supports multiple repository analysis workflows

Parser Integration:
- Provides input to java_mcp.parser for detailed source code analysis
- Supplies file paths and structure information for parsing workflows
- Enables batch processing of Java source files

MCP Server Integration:
- Exposes Java analysis capabilities through the MCP protocol
- Provides structured data for AI assistant consumption
- Supports code discovery, documentation extraction, and structural analysis

Usage Patterns:
==============

Basic Java File Discovery:
```python
from java_mcp.java import JavaPathIndexer

# Discover Java files in a repository
indexer = JavaPathIndexer("/path/to/java/project")
java_files = indexer.get_java_files()
main_sources = indexer.get_main_java_files()
test_sources = indexer.get_test_java_files()
```

Working with Java Types:
```python
from java_mcp.java.types import Class, Method, Field, JavaClasses

# Create and work with Java type representations
user_class = Class(
    name="User",
    package="com.example.model",
    class_type="class"
)

# Process collections of Java elements
def analyze_classes(classes: JavaClasses) -> dict:
    return {
        "total_classes": len(classes),
        "public_classes": len([c for c in classes if "public" in c.modifiers]),
        "interfaces": len([c for c in classes if c.class_type == "interface"])
    }
```

Project Analysis Workflow:
```python
from java_mcp.java import JavaPathIndexer
from java_mcp.java.types import JavaClasses

# Complete project analysis
def analyze_java_project(project_path: str) -> dict:
    # Discover Java files
    indexer = JavaPathIndexer(project_path)
    java_files = indexer.get_java_files()

    # Analyze project structure
    packages = indexer.get_packages()
    main_sources = indexer.get_main_java_files()
    test_sources = indexer.get_test_java_files()

    return {
        "total_files": len(java_files),
        "packages": len(packages),
        "main_sources": len(main_sources),
        "test_sources": len(test_sources)
    }
```

Error Handling:
==============

The package provides robust error handling for common scenarios:
- Invalid or non-existent project paths
- Malformed Java project structures
- File system access permissions
- Git repository state issues

Performance Considerations:
==========================

- Lazy loading of Java file discovery for large projects
- Efficient path normalization and caching
- Memory-conscious handling of large codebases
- Parallel processing support for batch operations

Standards Compliance:
====================

- Follows Java package naming conventions
- Supports standard Maven/Gradle directory layouts
- Compatible with modern Java language features (Java 8-24+)
- Adheres to cross-platform file system standards

Extension Points:
================

The package is designed for extensibility:
- Custom project structure detection
- Additional file type support
- Enhanced metadata extraction
- Integration with build tools and IDEs

Dependencies:
============

- pathlib: Cross-platform path handling
- os: Operating system interface
- typing: Type hints and annotations
- dataclasses: Type definitions (in types subpackage)

See Also:
=========
- java_mcp.git: Git repository management and cloning
- java_mcp.parser: Java source code parsing and analysis
- java_mcp.server: MCP server implementation for Java analysis
- grammars/: ANTLR4 grammar definitions for Java parsing

Examples:
=========

For complete examples of using this package, see:
- tests/test_java_path_indexer.py: Unit tests and usage examples
- tests/test_types.py: Type system usage examples
- java_mcp.java_analyzer: High-level analysis workflows
"""

# Import main functionality for convenient access
from .java_path_indexer import JavaPathIndexer

# Import type system for external use
from .types import (
    # Core types
    Class, Method, Field, Parameter, Annotation,

    # Collection aliases
    JavaClasses, JavaMethods, JavaFields, JavaParameters, JavaAnnotations,

    # Union types
    JavaElement, JavaType, JavaCodeElement
)

# Define public API
__all__ = [
    # Main functionality
    'JavaPathIndexer',

    # Core type system
    'Class',
    'Method',
    'Field',
    'Parameter',
    'Annotation',

    # Collection types
    'JavaClasses',
    'JavaMethods',
    'JavaFields',
    'JavaParameters',
    'JavaAnnotations',

    # Union types
    'JavaElement',
    'JavaType',
    'JavaCodeElement',
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Java MCP Server Team"
__description__ = "Java source code processing and analysis for MCP servers"

# Module-level logging configuration
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Initialized {__package_name__} package version {__version__}")
