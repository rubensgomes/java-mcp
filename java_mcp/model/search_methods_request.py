"""
Request Models for Java Method Search Operations

This module defines Pydantic models that represent request parameters for searching
Java methods in the FastMCP 2.0 framework. These models provide type-safe,
validated input structures for MCP tools that perform method discovery and analysis
across Java codebases, enabling AI assistants to find specific methods with
flexible filtering criteria.

The models support both broad method searches across entire codebases and targeted
searches within specific classes, providing powerful capabilities for code
exploration, API discovery, and implementation pattern analysis.

Key Features:
============

Flexible Method Discovery:
- Search by method name with pattern matching support
- Optional class-based filtering for targeted searches
- Cross-repository method discovery capabilities

Pattern Matching Support:
- Exact method name matching for precise searches
- Wildcard and regex pattern support for broader discovery
- Case-sensitive and case-insensitive search options

Type Safety and Validation:
- Pydantic-based models with automatic validation
- Method name validation and normalization
- Class name validation with Java naming convention checks

FastMCP 2.0 Compatibility:
- Designed for use with FastMCP 2.0 tool parameter validation
- Automatic schema generation for MCP protocol
- Self-documenting API through Pydantic field metadata

Usage in MCP Tools:
==================

The models in this module are typically used as parameter types for MCP tools:

```python
from fastmcp import FastMCP
from java_mcp.model.search_methods_request import SearchMethodsRequest

mcp = FastMCP("Java Analysis Server")

@mcp.tool()
def search_java_methods(request: SearchMethodsRequest) -> str:
    '''Search for Java methods with optional class filtering.'''
    # Perform method search with filters
    methods = method_searcher.find_methods(
        method_name=request.method_name,
        class_filter=request.class_name
    )

    return format_method_results(methods)
```

Common Search Patterns:
======================

Find all methods with specific name:
```python
request = SearchMethodsRequest(
    method_name="findById",
    class_name=None  # Search all classes
)
```

Search within specific class:
```python
request = SearchMethodsRequest(
    method_name="save",
    class_name="com.example.repository.UserRepository"
)
```

Pattern-based method discovery:
```python
request = SearchMethodsRequest(
    method_name="get*",  # All methods starting with "get"
    class_name="com.example.service.*Service"  # All service classes
)
```

Constructor searches:
```python
request = SearchMethodsRequest(
    method_name="<init>",  # Constructor methods
    class_name="com.example.model.User"
)
```

Overloaded method analysis:
```python
request = SearchMethodsRequest(
    method_name="create",
    class_name="com.example.factory.ObjectFactory"
)
```

Integration with Java Analysis Pipeline:
=======================================

These request models integrate with the broader Java analysis infrastructure:

1. **Method Discovery**: Find methods across parsed Java source files
2. **Pattern Matching**: Support various search patterns and wildcards
3. **Class Filtering**: Scope searches to specific classes or packages
4. **Signature Analysis**: Extract complete method signatures and metadata
5. **Cross-Reference Resolution**: Link method calls and implementations

Search Result Types:
===================

The search system can return various types of method information:

**Basic Method Information**:
- Method name and signature
- Declaring class and package
- Access modifiers and keywords
- Return type and parameter types

**Advanced Metadata**:
- Javadoc documentation
- Annotations and their parameters
- Source location (file and line number)
- Override relationships

**Implementation Details**:
- Method body analysis (if available)
- Exception handling patterns
- Local variable declarations
- Method call patterns

Error Handling and Validation:
=============================

The models provide comprehensive validation with descriptive error messages:

```python
# Valid request
request = SearchMethodsRequest(
    method_name="calculateTotal",
    class_name="com.example.service.OrderService"
)

# Invalid requests - will raise ValidationError
try:
    # Empty method name
    invalid_request = SearchMethodsRequest(
        method_name="",  # Empty string not allowed
        class_name="ValidClass"
    )
except ValidationError as e:
    print(f"Method name validation error: {e}")

try:
    # Invalid class name format
    invalid_request = SearchMethodsRequest(
        method_name="validMethod",
        class_name="invalid..class..name"
    )
except ValidationError as e:
    print(f"Class name validation error: {e}")
```

Search Performance Optimization:
===============================

The search system includes several optimization strategies:

**Indexing**: Pre-built indexes for fast method name lookup
**Caching**: Cached search results for frequently accessed methods
**Filtering**: Early filtering to reduce search scope
**Parallel Processing**: Concurrent searches across multiple repositories

Search Scope and Context:
=========================

Method searches can operate in different scopes:

**Repository-Scoped**: Search within specific Git repositories
**Package-Scoped**: Limit searches to specific Java packages
**Class-Scoped**: Focus on individual classes or class hierarchies
**Global**: Search across all available Java source code

See Also:
=========
- java_mcp.java_analyzer: Core method analysis and search logic
- java_mcp.parser: Java source code parsing for method extraction
- java_mcp.java: Java file discovery and project structure analysis
- java_mcp.server: MCP server implementation using these models
- fastmcp: Framework for building MCP servers with type-safe tools
- pydantic: Data validation and parsing library
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
import re


class SearchMethodsRequest(BaseModel):
    """
    Request model for searching Java methods with optional class filtering.

    This model defines the parameters required to search for Java methods across
    a codebase. It supports both exact method name matching and pattern-based
    searches, with optional filtering by class names to narrow the search scope.

    The model is designed for use with FastMCP 2.0 tools, providing automatic
    parameter validation and schema generation for AI assistant interactions.
    It enables comprehensive method discovery for code exploration, API analysis,
    and implementation pattern identification.

    Attributes:
        method_name (str): The name or pattern of the method(s) to search for.
                          Supports exact names (e.g., "findById") and patterns
                          (e.g., "get*", ".*Repository"). Required field that
                          cannot be empty. Special method names like "<init>"
                          for constructors are supported.

        class_name (Optional[str]): The fully qualified class name or pattern
                                   to filter the search scope. If provided, only
                                   methods from matching classes will be returned.
                                   Supports patterns like "com.example.*Service"
                                   or exact names like "com.example.UserService".
                                   Optional field that defaults to None (search all classes).

    Validation Rules:
        - method_name must be non-empty and contain valid method name characters
        - method_name supports wildcards (*) and regex patterns
        - class_name, if provided, must follow Java class naming conventions
        - class_name supports package patterns and wildcards

    Usage Examples:
        Search for specific method across all classes:
        ```python
        request = SearchMethodsRequest(
            method_name="findById",
            class_name=None
        )
        ```

        Search within specific class:
        ```python
        request = SearchMethodsRequest(
            method_name="save",
            class_name="com.example.repository.UserRepository"
        )
        ```

        Pattern-based method search:
        ```python
        request = SearchMethodsRequest(
            method_name="get*",  # All getter methods
            class_name="com.example.model.*"  # All model classes
        )
        ```

        Constructor search:
        ```python
        request = SearchMethodsRequest(
            method_name="<init>",
            class_name="com.example.entity.User"
        )
        ```

        Service method discovery:
        ```python
        request = SearchMethodsRequest(
            method_name=".*Service$",  # Methods ending with "Service"
            class_name="com.example.service.*"
        )
        ```

        Overloaded method analysis:
        ```python
        request = SearchMethodsRequest(
            method_name="create",
            class_name="com.example.factory.ObjectFactory"
        )
        ```

    MCP Tool Integration:
        This model is typically used as a parameter type in MCP tool definitions:
        ```python
        @mcp.tool()
        def find_java_methods(request: SearchMethodsRequest) -> MethodSearchResults:
            '''Search for Java methods with flexible filtering options.'''
            return method_finder.search_methods(
                method_pattern=request.method_name,
                class_pattern=request.class_name
            )
        ```

    Search Patterns and Wildcards:
        The search system supports various pattern types:

        **Exact Matching**: "findById" matches only methods named "findById"
        **Wildcard Patterns**: "get*" matches "getName", "getAge", "getUser", etc.
        **Regex Patterns**: ".*Repository$" matches methods ending with "Repository"
        **Constructor Pattern**: "<init>" specifically searches for constructors
        **Case Sensitivity**: Searches are case-sensitive by default

    Performance Considerations:
        - Exact method names provide fastest search performance
        - Wildcard patterns are optimized for prefix matching
        - Complex regex patterns may require more processing time
        - Class filtering significantly reduces search scope and improves performance
        - Indexing enables fast lookups for common method names

    Search Result Information:
        Successful searches return comprehensive method information:
        - Complete method signature with parameter types
        - Declaring class and package information
        - Access modifiers and method characteristics
        - Javadoc documentation (if available)
        - Source file location and line numbers
        - Annotation metadata
        - Override and implementation relationships

    Error Scenarios:
        - Empty method name will raise ValidationError
        - Invalid method name patterns will be flagged
        - Malformed class name patterns will raise ValidationError
        - Non-existent classes will result in empty search results
        - Invalid regex patterns will cause search failures
    """

    method_name: str = Field(
        description="Method name or pattern to search for (supports wildcards and regex)",
        min_length=1,
        example="findById"
    )

    class_name: Optional[str] = Field(
        default=None,
        description="Fully qualified class name or pattern to filter results (optional)",
        example="com.example.repository.UserRepository"
    )

    @validator('method_name')
    def validate_method_name(cls, value: str) -> str:
        """
        Validate the method name or pattern for searching.

        Args:
            value: The method name or pattern to validate

        Returns:
            str: The validated method name or pattern

        Raises:
            ValueError: If the method name format is invalid
        """
        if not value or not value.strip():
            raise ValueError("Method name cannot be empty")

        value = value.strip()

        # Allow special constructor method name
        if value == "<init>":
            return value

        # For regex patterns, validate by attempting to compile
        if any(char in value for char in ['[', ']', '(', ')', '{', '}', '^', '$', '+', '?']):
            try:
                re.compile(value)
            except re.error as e:
                raise ValueError(
                    f"Invalid regex pattern in method name: '{value}'. "
                    f"Regex error: {e}"
                )
            return value

        # For simple patterns with wildcards, basic validation
        if '*' in value:
            # Wildcard patterns are allowed
            simple_pattern = value.replace('*', 'X')  # Replace wildcards for validation
            if not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', simple_pattern):
                raise ValueError(
                    f"Invalid method name pattern: '{value}'. "
                    "Must be a valid Java method name with optional wildcards (*)"
                )
            return value

        # For exact method names, validate Java naming conventions
        if not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', value):
            raise ValueError(
                f"Invalid method name: '{value}'. "
                "Must follow Java method naming conventions (letters, digits, underscore, dollar sign)"
            )

        return value

    @validator('class_name')
    def validate_class_name(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the class name or pattern for filtering.

        Args:
            value: The class name or pattern to validate (may be None)

        Returns:
            Optional[str]: The validated class name or pattern, or None

        Raises:
            ValueError: If the class name format is invalid
        """
        if value is not None:
            if not value.strip():
                return None  # Empty string treated as no filter

            value = value.strip()

            # For patterns with wildcards, validate the non-wildcard parts
            if '*' in value:
                # Split by wildcards and validate each part
                parts = value.split('*')
                for part in parts:
                    if part and not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*(\.[a-zA-Z_$][a-zA-Z0-9_$]*)*$', part):
                        raise ValueError(
                            f"Invalid class name pattern: '{value}'. "
                            "Parts between wildcards must follow Java naming conventions"
                        )
                return value

            # For exact class names, validate Java naming conventions
            if not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*(\.[a-zA-Z_$][a-zA-Z0-9_$]*)*$', value):
                raise ValueError(
                    f"Invalid class name: '{value}'. "
                    "Must follow Java class naming conventions (e.g., 'com.example.MyClass')"
                )

        return value

    class Config:
        """Pydantic model configuration."""
        # Generate example values in schema
        schema_extra = {
            "examples": [
                {
                    "method_name": "findById",
                    "class_name": None
                },
                {
                    "method_name": "save",
                    "class_name": "com.example.repository.UserRepository"
                },
                {
                    "method_name": "get*",
                    "class_name": "com.example.model.*"
                },
                {
                    "method_name": "<init>",
                    "class_name": "com.example.entity.User"
                },
                {
                    "method_name": ".*Service$",
                    "class_name": "com.example.service.*"
                },
                {
                    "method_name": "create",
                    "class_name": "com.example.factory.ObjectFactory"
                }
            ]
        }

        # Allow field population by name or alias
        allow_population_by_field_name = True

        # Validate assignment (re-validate when fields are modified)
        validate_assignment = True
