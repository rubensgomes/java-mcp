"""
Java Code Analysis Types Module

This module provides a comprehensive type system for representing Java code elements
in the MCP (Model Context Protocol) server. It defines dataclass-based structures
that capture the complete semantics and metadata of Java source code, enabling
AI assistants to understand and reason about Java codebases effectively.

The module is organized into separate files for each major Java code element type,
promoting maintainability and clear separation of concerns. Each type captures
both structural information (names, signatures, relationships) and metadata
(annotations, documentation, source locations).

Module Structure:
================

Core Type Definitions:
- annotation.py: Java annotation representations with parameters
- parameter.py: Method parameter definitions with type information
- method.py: Method and constructor representations with full signatures
- field.py: Field and variable definitions with modifiers and initial values
- java_class.py: Complete class, interface, enum, and record representations
- aliases.py: Type aliases and union types for collections and flexibility

Design Philosophy:
=================

1. **Completeness**: Capture all relevant Java language constructs and metadata
2. **Accuracy**: Faithfully represent Java semantics and relationships
3. **Usability**: Provide convenient access patterns and utility methods
4. **Extensibility**: Support evolution of Java language features
5. **Type Safety**: Enable static type checking and IDE support

Key Features:
============

- **Rich Metadata**: Javadoc extraction, source locations, and annotation support
- **Modern Java Support**: Records, pattern matching, sealed classes, and more
- **Inheritance Tracking**: Complete class hierarchy and interface relationships
- **Generic Type Support**: Full generic type parameter and constraint handling
- **Modifier Analysis**: Comprehensive access modifier and keyword tracking

Usage Patterns:
==============

```python
from java_mcp.java.types import Class, Method, Field, Parameter, Annotation

# Create a complete class representation
user_class = Class(
    name="User",
    package="com.example.model",
    class_type="class",
    modifiers=["public"],
    fields=[
        Field(
            name="id",
            type="Long",
            modifiers=["private"],
            annotations=[Annotation("Id")]
        ),
        Field(
            name="username",
            type="String",
            modifiers=["private"],
            annotations=[
                Annotation("Column", {"name": "user_name"}),
                Annotation("NotBlank")
            ]
        )
    ],
    methods=[
        Method(
            name="getId",
            return_type="Long",
            modifiers=["public"],
            parameters=[]
        ),
        Method(
            name="setUsername",
            return_type="void",
            modifiers=["public"],
            parameters=[
                Parameter(
                    name="username",
                    type="String",
                    annotations=[Annotation("NotBlank")]
                )
            ]
        )
    ],
    annotations=[
        Annotation("Entity"),
        Annotation("Table", {"name": "users"})
    ]
)

# Use type aliases for collections
from java_mcp.java.types import JavaClasses, JavaMethods

def analyze_public_methods(classes: JavaClasses) -> JavaMethods:
    public_methods = []
    for cls in classes:
        public_methods.extend(cls.get_public_methods())
    return public_methods
```

Integration with MCP Server:
===========================

These types serve as the foundation for the Java code analysis capabilities
provided by the MCP server. They enable:

- **Code Discovery**: Finding and cataloging Java code elements
- **Documentation Extraction**: Preserving and presenting Javadoc content
- **Structural Analysis**: Understanding class hierarchies and relationships
- **Annotation Processing**: Interpreting framework-specific metadata
- **Cross-Reference Resolution**: Linking types, methods, and field references

The types are designed to be serializable for transmission over the MCP protocol,
allowing AI assistants to receive rich, structured information about Java codebases.

Type Hierarchy:
==============

The module follows a hierarchical structure reflecting Java's own organization:

```
Class (top-level container)
├── Methods (behavior)
│   └── Parameters (method inputs)
├── Fields (state)
└── Annotations (metadata)
    └── Parameters (annotation configuration)
```

Each level captures appropriate metadata and provides utility methods for
common operations and queries.

Extension Points:
================

The type system is designed for extensibility to support:
- New Java language features as they are introduced
- Framework-specific annotations and patterns
- Additional metadata extraction capabilities
- Enhanced analysis and cross-reference features

See Also:
=========
- java_mcp.parser: Modules that populate these types from source code
- java_mcp.java.java_path_indexer: Discovery of Java files and packages
- java_mcp.server: MCP server that exposes these types to AI assistants
"""

# Import all core type definitions
from .annotation import Annotation
from .parameter import Parameter
from .method import Method
from .field import Field
from .java_class import Class

# Import type aliases and union types
from .aliases import (
    # Collection type aliases
    JavaClasses,
    JavaMethods,
    JavaFields,
    JavaParameters,
    JavaAnnotations,

    # Union type aliases
    JavaElement,
    JavaType,
    JavaCodeElement,

    # Functional type aliases
    JavaElementPredicate,
    JavaElementTransformer,
    JavaElementVisitor,
)

# Define what gets exported when using "from java_mcp.java.types import *"
__all__ = [
    # Core type definitions
    'Annotation',
    'Parameter',
    'Method',
    'Field',
    'Class',

    # Collection type aliases
    'JavaClasses',
    'JavaMethods',
    'JavaFields',
    'JavaParameters',
    'JavaAnnotations',

    # Union type aliases
    'JavaElement',
    'JavaType',
    'JavaCodeElement',

    # Functional type aliases
    'JavaElementPredicate',
    'JavaElementTransformer',
    'JavaElementVisitor',
]

# Version information for the type system
__version__ = "1.0.0"
__author__ = "Java MCP Server Team"
__description__ = "Comprehensive type system for Java code analysis in MCP servers"
