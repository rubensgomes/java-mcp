"""
Request Models for Java Class Analysis Operations

This module defines Pydantic models that represent request parameters for Java class
analysis operations in the FastMCP 2.0 framework. These models provide type-safe,
validated input structures for MCP tools that analyze Java codebases, enabling
AI assistants to request specific Java class analysis operations with proper
parameter validation and documentation.

The models in this module serve as the interface between AI assistants and the
Java MCP server's class analysis capabilities, ensuring that requests are properly
structured and validated before processing.

Key Features:
============

Type Safety:
- Pydantic-based models with automatic validation
- Clear type annotations for all request parameters
- Runtime validation of input data

Documentation Integration:
- Field descriptions that appear in MCP tool schemas
- Self-documenting API through Pydantic field metadata
- Clear parameter expectations for AI assistants

FastMCP 2.0 Compatibility:
- Designed for use with FastMCP 2.0 tool parameter validation
- Automatic schema generation for MCP protocol
- Seamless integration with MCP server tool definitions

Usage in MCP Tools:
==================

The models in this module are typically used as parameter types for MCP tools:

```python
from fastmcp import FastMCP
from java_mcp.model.analyze_class_request import AnalyzeClassRequest

mcp = FastMCP("Java Analysis Server")

@mcp.tool()
def analyze_class(request: AnalyzeClassRequest) -> str:
    '''Analyze a Java class and return detailed information.'''
    # The request parameter is automatically validated by Pydantic
    class_name = request.class_name
    repository = request.repository

    # Perform analysis...
    return analysis_result
```

Validation and Error Handling:
=============================

Pydantic models provide automatic validation with descriptive error messages:

```python
# Valid request
request = AnalyzeClassRequest(
    class_name="com.example.service.UserService",
    repository="user-management"
)

# Invalid request - will raise ValidationError
try:
    invalid_request = AnalyzeClassRequest(
        class_name="",  # Empty string not allowed
        repository=None  # This is allowed (optional field)
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

Integration with Java Analysis Pipeline:
=======================================

These request models integrate with the broader Java analysis infrastructure:

1. **Input Validation**: Ensure proper parameter format and constraints
2. **Repository Resolution**: Handle optional repository specification
3. **Class Name Processing**: Support fully qualified class names
4. **Error Propagation**: Provide clear validation errors to AI assistants

See Also:
=========
- java_mcp.server: MCP server implementation using these models
- java_mcp.java_analyzer: Core analysis logic that processes these requests
- fastmcp: Framework for building MCP servers with type-safe tools
- pydantic: Data validation and parsing library
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class AnalyzeClassRequest(BaseModel):
    """
    Request model for analyzing Java classes within a repository or codebase.

    This model defines the parameters required to request analysis of a specific
    Java class. It supports both standalone class analysis and repository-specific
    analysis, providing flexibility for different analysis scenarios.

    The model is designed for use with FastMCP 2.0 tools, providing automatic
    parameter validation and schema generation for AI assistant interactions.

    Attributes:
        class_name (str): The fully qualified name of the Java class to analyze.
                         Must follow Java package naming conventions (e.g., "com.example.MyClass").
                         Required field that cannot be empty.

        repository (Optional[str]): The name or identifier of the repository containing the class.
                                   If provided, analysis will be scoped to that specific repository.
                                   If None, analysis will search across all available repositories.
                                   Optional field that defaults to None.

    Validation Rules:
        - class_name must be non-empty and contain valid Java class name characters
        - class_name should follow Java naming conventions (packages separated by dots)
        - repository, if provided, must be a non-empty string

    Usage Examples:
        Analyze a specific class in a known repository:
        ```python
        request = AnalyzeClassRequest(
            class_name="com.example.service.UserService",
            repository="user-management-api"
        )
        ```

        Analyze a class across all repositories:
        ```python
        request = AnalyzeClassRequest(
            class_name="java.util.ArrayList"
            # repository defaults to None
        )
        ```

        Standard library class analysis:
        ```python
        request = AnalyzeClassRequest(
            class_name="java.lang.String",
            repository=None  # Search all available sources
        )
        ```

    MCP Tool Integration:
        This model is typically used as a parameter type in MCP tool definitions:
        ```python
        @mcp.tool()
        def analyze_java_class(request: AnalyzeClassRequest) -> ClassAnalysisResult:
            '''Analyze a Java class and return detailed structural information.'''
            # Automatic validation ensures request.class_name is valid
            return perform_class_analysis(request.class_name, request.repository)
        ```

    Error Scenarios:
        - Empty class_name will raise ValidationError
        - Invalid characters in class_name will be flagged
        - Empty repository string (if provided) will raise ValidationError
    """

    class_name: str = Field(
        description="Fully qualified Java class name (e.g., 'com.example.service.UserService')",
        min_length=1,
        example="com.example.service.UserService"
    )

    repository: Optional[str] = Field(
        default=None,
        description="Repository name to scope the analysis (optional - if not provided, searches all repositories)",
        example="user-management-api"
    )

    @validator('class_name')
    def validate_class_name(cls, value: str) -> str:
        """
        Validate the Java class name format and content.

        Args:
            value: The class name to validate

        Returns:
            str: The validated class name

        Raises:
            ValueError: If the class name format is invalid
        """
        if not value or not value.strip():
            raise ValueError("Class name cannot be empty")

        # Remove leading/trailing whitespace
        value = value.strip()

        # Basic validation for Java class name format
        # Allow letters, digits, dots (for packages), dollar signs (for inner classes), and underscores
        import re
        if not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*(\.[a-zA-Z_$][a-zA-Z0-9_$]*)*$', value):
            raise ValueError(
                f"Invalid Java class name format: '{value}'. "
                "Must follow Java naming conventions (e.g., 'com.example.MyClass')"
            )

        return value

    @validator('repository')
    def validate_repository(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the repository name if provided.

        Args:
            value: The repository name to validate (may be None)

        Returns:
            Optional[str]: The validated repository name or None

        Raises:
            ValueError: If the repository name is an empty string
        """
        if value is not None:
            if not value or not value.strip():
                raise ValueError("Repository name cannot be empty string (use None instead)")
            return value.strip()
        return value

    class Config:
        """Pydantic model configuration."""
        # Generate example values in schema
        schema_extra = {
            "examples": [
                {
                    "class_name": "com.example.service.UserService",
                    "repository": "user-management-api"
                },
                {
                    "class_name": "java.util.ArrayList",
                    "repository": None
                },
                {
                    "class_name": "org.springframework.boot.SpringApplication"
                }
            ]
        }

        # Allow field population by name or alias
        allow_population_by_field_name = True

        # Validate assignment (re-validate when fields are modified)
        validate_assignment = True
