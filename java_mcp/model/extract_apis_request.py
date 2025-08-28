"""
Request Models for Java API Extraction Operations

This module defines Pydantic models that represent request parameters for Java API
extraction operations in the FastMCP 2.0 framework. These models provide type-safe,
validated input structures for MCP tools that extract and analyze Java APIs from
Git repositories, enabling AI assistants to request comprehensive API documentation
and analysis with proper parameter validation.

The models facilitate automated extraction of Java API information from Git repositories,
supporting filtering by packages and classes to focus on specific parts of large codebases.
This enables efficient API discovery and documentation generation for Java projects.

Key Features:
============

Git Repository Integration:
- Direct extraction from Git repository URLs
- Branch specification for targeting specific code versions
- Seamless integration with Git cloning and checkout operations

Flexible Filtering:
- Package-based filtering for focusing on specific namespaces
- Class name pattern matching using regular expressions
- Optional filters that default to extracting all APIs when not specified

Type Safety and Validation:
- Pydantic-based models with automatic validation
- Git URL validation and format checking
- Pattern validation for regex-based class filtering

FastMCP 2.0 Compatibility:
- Designed for use with FastMCP 2.0 tool parameter validation
- Automatic schema generation for MCP protocol
- Self-documenting API through Pydantic field metadata

Usage in MCP Tools:
==================

The models in this module are typically used as parameter types for MCP tools:

```python
from fastmcp import FastMCP
from java_mcp.model.extract_apis_request import ExtractAPIsRequest

mcp = FastMCP("Java Analysis Server")

@mcp.tool()
def extract_java_apis(request: ExtractAPIsRequest) -> str:
    '''Extract Java APIs from a Git repository with optional filtering.'''
    # Clone repository and checkout specified branch
    repo_path = clone_repository(request.repo_url, request.branch)

    # Apply filters and extract APIs
    apis = extract_apis_with_filters(
        repo_path,
        request.package_filter,
        request.class_filter
    )

    return format_api_documentation(apis)
```

Common Usage Patterns:
=====================

Extract all APIs from a repository:
```python
request = ExtractAPIsRequest(
    repo_url="https://github.com/example/java-project.git",
    branch="main"
    # No filters - extracts all APIs
)
```

Focus on specific package:
```python
request = ExtractAPIsRequest(
    repo_url="https://github.com/spring-projects/spring-boot.git",
    branch="main",
    package_filter="org.springframework.boot.autoconfigure"
)
```

Filter by class name patterns:
```python
request = ExtractAPIsRequest(
    repo_url="https://github.com/example/microservices.git",
    branch="develop",
    class_filter=".*Service$"  # All classes ending with "Service"
)
```

Combined filtering:
```python
request = ExtractAPIsRequest(
    repo_url="https://github.com/apache/kafka.git",
    branch="trunk",
    package_filter="org.apache.kafka.clients",
    class_filter=".*Client$"
)
```

Integration with Java Analysis Pipeline:
=======================================

These request models integrate with the broader Java analysis infrastructure:

1. **Git Repository Management**: Coordinates with git module for cloning and checkout
2. **Java File Discovery**: Works with java_path_indexer for finding Java source files
3. **Source Code Parsing**: Integrates with parser module for code analysis
4. **API Documentation**: Supports documentation extraction and formatting

Error Handling and Validation:
=============================

The models provide comprehensive validation with descriptive error messages:

```python
# Valid request
request = ExtractAPIsRequest(
    repo_url="https://github.com/user/repo.git",
    branch="feature/api-v2",
    package_filter="com.example.api"
)

# Invalid requests - will raise ValidationError
try:
    # Invalid Git URL
    invalid_request = ExtractAPIsRequest(
        repo_url="not-a-valid-url",
        branch="main"
    )
except ValidationError as e:
    print(f"URL validation error: {e}")

try:
    # Invalid regex pattern
    invalid_request = ExtractAPIsRequest(
        repo_url="https://github.com/user/repo.git",
        class_filter="[invalid-regex"
    )
except ValidationError as e:
    print(f"Regex validation error: {e}")
```

See Also:
=========
- java_mcp.git: Git repository management and cloning utilities
- java_mcp.java: Java file discovery and path management
- java_mcp.parser: Java source code parsing and analysis
- java_mcp.server: MCP server implementation using these models
- fastmcp: Framework for building MCP servers with type-safe tools
- pydantic: Data validation and parsing library
"""

from typing import Optional
import re
from pydantic import BaseModel, Field, validator


class ExtractAPIsRequest(BaseModel):
    """
    Request model for extracting Java APIs from Git repositories.

    This model defines the parameters required to extract Java API information
    from a Git repository. It supports branch specification and optional filtering
    by package prefixes and class name patterns to focus on specific parts of
    large codebases.

    The model is designed for use with FastMCP 2.0 tools, providing automatic
    parameter validation and schema generation for AI assistant interactions.
    It enables efficient API discovery and documentation generation workflows.

    Attributes:
        repo_url (str): The Git repository URL to extract APIs from.
                       Must be a valid Git URL (HTTPS, SSH, or file protocol).
                       Required field that cannot be empty.

        branch (str): The Git branch to checkout for API extraction.
                     Defaults to "main" if not specified.
                     Must be a valid Git branch name.

        package_filter (Optional[str]): Package prefix filter for focusing extraction.
                                       If provided, only classes in packages starting
                                       with this prefix will be analyzed.
                                       Example: "com.example.api" will include
                                       "com.example.api.UserService" but exclude
                                       "com.example.data.UserRepository".
                                       Optional field that defaults to None (no filtering).

        class_filter (Optional[str]): Regular expression pattern for class name filtering.
                                     If provided, only classes whose names match this
                                     regex pattern will be included in the extraction.
                                     Example: ".*Service$" will match all classes
                                     ending with "Service".
                                     Optional field that defaults to None (no filtering).

    Validation Rules:
        - repo_url must be a valid Git repository URL
        - branch must be a non-empty string with valid Git branch name characters
        - package_filter, if provided, must follow Java package naming conventions
        - class_filter, if provided, must be a valid regular expression

    Usage Examples:
        Extract all APIs from main branch:
        ```python
        request = ExtractAPIsRequest(
            repo_url="https://github.com/spring-projects/spring-framework.git",
            branch="main"
        )
        ```

        Focus on specific package:
        ```python
        request = ExtractAPIsRequest(
            repo_url="https://github.com/apache/commons-lang.git",
            branch="master",
            package_filter="org.apache.commons.lang3.text"
        )
        ```

        Filter by class naming pattern:
        ```python
        request = ExtractAPIsRequest(
            repo_url="https://github.com/google/guava.git",
            branch="master",
            class_filter=".*Utils?$"  # Classes ending with "Util" or "Utils"
        )
        ```

        Combined filtering for microservices:
        ```python
        request = ExtractAPIsRequest(
            repo_url="https://github.com/company/microservices.git",
            branch="develop",
            package_filter="com.company.services",
            class_filter=".*(?:Service|Controller|Repository)$"
        )
        ```

    MCP Tool Integration:
        This model is typically used as a parameter type in MCP tool definitions:
        ```python
        @mcp.tool()
        def extract_repository_apis(request: ExtractAPIsRequest) -> APIDocumentation:
            '''Extract comprehensive API documentation from a Java repository.'''
            return api_extractor.extract_apis(
                request.repo_url,
                request.branch,
                request.package_filter,
                request.class_filter
            )
        ```

    Performance Considerations:
        - Package filtering significantly reduces processing time for large repositories
        - Class filtering is applied after Java parsing, so it's most efficient
          when combined with package filtering
        - Branch specification allows targeting specific versions without
          processing entire repository history

    Error Scenarios:
        - Invalid Git URL format will raise ValidationError
        - Non-existent repository or branch will cause runtime errors during processing
        - Invalid regex patterns in class_filter will raise ValidationError
        - Empty strings for filters will be treated as None (no filtering)
    """

    repo_url: str = Field(
        description="Git repository URL (HTTPS, SSH, or file protocol)",
        example="https://github.com/spring-projects/spring-boot.git"
    )

    branch: str = Field(
        default="main",
        description="Git branch to checkout for API extraction",
        example="main"
    )

    package_filter: Optional[str] = Field(
        default=None,
        description="Filter classes by package prefix (e.g., 'com.example.api')",
        example="org.springframework.boot.autoconfigure"
    )

    class_filter: Optional[str] = Field(
        default=None,
        description="Filter classes by name pattern using regex (e.g., '.*Service$')",
        example=".*(?:Controller|Service|Repository)$"
    )

    @validator('repo_url')
    def validate_repo_url(cls, value: str) -> str:
        """
        Validate the Git repository URL format.

        Args:
            value: The repository URL to validate

        Returns:
            str: The validated repository URL

        Raises:
            ValueError: If the URL format is invalid for Git operations
        """
        if not value or not value.strip():
            raise ValueError("Repository URL cannot be empty")

        value = value.strip()

        # Basic validation for common Git URL formats
        git_url_patterns = [
            r'^https?://.*\.git$',  # HTTPS URLs ending with .git
            r'^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?$',  # GitHub URLs (with or without .git)
            r'^https?://gitlab\.com/[\w\-\.]+/[\w\-\.]+/?$',  # GitLab URLs
            r'^git@[\w\.\-]+:[\w\-\.]+/[\w\-\.]+\.git$',  # SSH URLs
            r'^ssh://git@[\w\.\-]+/[\w\-\.]+/[\w\-\.]+\.git$',  # SSH URLs with ssh://
            r'^file://.*$',  # Local file URLs
            r'^/.*$',  # Local absolute paths
            r'^\.\.?/.*$',  # Local relative paths
        ]

        if not any(re.match(pattern, value, re.IGNORECASE) for pattern in git_url_patterns):
            raise ValueError(
                f"Invalid Git repository URL format: '{value}'. "
                "Expected formats: https://github.com/user/repo.git, "
                "git@github.com:user/repo.git, or file:// URLs"
            )

        return value

    @validator('branch')
    def validate_branch(cls, value: str) -> str:
        """
        Validate the Git branch name.

        Args:
            value: The branch name to validate

        Returns:
            str: The validated branch name

        Raises:
            ValueError: If the branch name format is invalid
        """
        if not value or not value.strip():
            raise ValueError("Branch name cannot be empty")

        value = value.strip()

        # Basic validation for Git branch names
        # Git branch names cannot contain certain characters
        invalid_chars = [' ', '~', '^', ':', '?', '*', '[', '\\']
        if any(char in value for char in invalid_chars):
            raise ValueError(
                f"Invalid Git branch name: '{value}'. "
                f"Branch names cannot contain: {', '.join(invalid_chars)}"
            )

        # Cannot start or end with certain characters
        if value.startswith('.') or value.endswith('.'):
            raise ValueError("Branch names cannot start or end with '.'")

        if value.startswith('/') or value.endswith('/'):
            raise ValueError("Branch names cannot start or end with '/'")

        return value

    @validator('package_filter')
    def validate_package_filter(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the Java package filter format.

        Args:
            value: The package filter to validate (may be None)

        Returns:
            Optional[str]: The validated package filter or None

        Raises:
            ValueError: If the package filter format is invalid
        """
        if value is not None:
            if not value.strip():
                return None  # Empty string treated as no filter

            value = value.strip()

            # Validate Java package naming conventions
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$', value):
                raise ValueError(
                    f"Invalid Java package filter: '{value}'. "
                    "Must follow Java package naming conventions (e.g., 'com.example.api')"
                )

        return value

    @validator('class_filter')
    def validate_class_filter(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the regex pattern for class filtering.

        Args:
            value: The regex pattern to validate (may be None)

        Returns:
            Optional[str]: The validated regex pattern or None

        Raises:
            ValueError: If the regex pattern is invalid
        """
        if value is not None:
            if not value.strip():
                return None  # Empty string treated as no filter

            value = value.strip()

            # Validate regex pattern by attempting to compile it
            try:
                re.compile(value)
            except re.error as e:
                raise ValueError(
                    f"Invalid regular expression pattern: '{value}'. "
                    f"Regex error: {e}"
                )

        return value

    class Config:
        """Pydantic model configuration."""
        # Generate example values in schema
        schema_extra = {
            "examples": [
                {
                    "repo_url": "https://github.com/spring-projects/spring-boot.git",
                    "branch": "main"
                },
                {
                    "repo_url": "https://github.com/apache/kafka.git",
                    "branch": "trunk",
                    "package_filter": "org.apache.kafka.clients"
                },
                {
                    "repo_url": "https://github.com/google/guava.git",
                    "branch": "master",
                    "class_filter": ".*Utils?$"
                },
                {
                    "repo_url": "https://github.com/company/microservices.git",
                    "branch": "develop",
                    "package_filter": "com.company.services",
                    "class_filter": ".*(?:Service|Controller|Repository)$"
                }
            ]
        }

        # Allow field population by name or alias
        allow_population_by_field_name = True

        # Validate assignment (re-validate when fields are modified)
        validate_assignment = True
