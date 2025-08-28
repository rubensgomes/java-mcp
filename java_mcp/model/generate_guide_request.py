"""
Request Models for Java API Usage Guide Generation

This module defines Pydantic models that represent request parameters for generating
comprehensive API usage guides in the FastMCP 2.0 framework. These models provide
type-safe, validated input structures for MCP tools that create detailed documentation
and usage examples for Java APIs, enabling AI assistants to request customized
guides tailored to specific use cases and requirements.

The models facilitate intelligent guide generation by allowing specification of
particular use cases, functionality needs, and repository scope, enabling the
creation of targeted documentation that addresses specific developer scenarios
and implementation patterns.

Key Features:
============

Use Case-Driven Generation:
- Specify particular functionality or implementation scenarios
- Generate guides tailored to specific developer needs
- Support for both generic and specialized use cases

Repository Scoping:
- Optional repository filtering for focused documentation
- Cross-repository analysis when no specific repository is provided
- Support for multi-repository Java projects and microservices

Type Safety and Validation:
- Pydantic-based models with automatic validation
- Use case validation and formatting
- Repository name validation and normalization

FastMCP 2.0 Compatibility:
- Designed for use with FastMCP 2.0 tool parameter validation
- Automatic schema generation for MCP protocol
- Self-documenting API through Pydantic field metadata

Usage in MCP Tools:
==================

The models in this module are typically used as parameter types for MCP tools:

```python
from fastmcp import FastMCP
from java_mcp.model.generate_guide_request import GenerateGuideRequest

mcp = FastMCP("Java Analysis Server")

@mcp.tool()
def generate_api_usage_guide(request: GenerateGuideRequest) -> str:
    '''Generate comprehensive API usage guides for specific use cases.'''
    # Generate guide based on use case and repository scope
    guide_content = guide_generator.create_usage_guide(
        use_case=request.use_case,
        repository_filter=request.repository
    )

    return format_guide_documentation(guide_content)
```

Common Usage Patterns:
=====================

Generate general authentication guide:
```python
request = GenerateGuideRequest(
    use_case="user authentication and authorization",
    repository=None  # Search all repositories
)
```

Create Spring Boot specific guide:
```python
request = GenerateGuideRequest(
    use_case="REST API development with validation",
    repository="spring-boot-backend"
)
```

Database integration patterns:
```python
request = GenerateGuideRequest(
    use_case="JPA entity relationships and querying",
    repository="data-access-layer"
)
```

Microservices communication:
```python
request = GenerateGuideRequest(
    use_case="inter-service communication with Feign clients",
    repository="microservices-commons"
)
```

Testing strategies:
```python
request = GenerateGuideRequest(
    use_case="unit testing with mocks and integration tests",
    repository="test-framework"
)
```

Integration with Documentation Pipeline:
=======================================

These request models integrate with the broader documentation generation infrastructure:

1. **Use Case Analysis**: Parse and understand specific requirements and scenarios
2. **Repository Filtering**: Scope analysis to relevant codebases and projects
3. **API Discovery**: Find relevant classes, methods, and patterns for the use case
4. **Example Generation**: Create practical code examples and implementation patterns
5. **Documentation Formatting**: Structure guides with clear sections and examples

Error Handling and Validation:
=============================

The models provide comprehensive validation with descriptive error messages:

```python
# Valid request
request = GenerateGuideRequest(
    use_case="implementing caching strategies with Redis",
    repository="caching-service"
)

# Invalid requests - will raise ValidationError
try:
    # Empty use case
    invalid_request = GenerateGuideRequest(
        use_case="",  # Empty string not allowed
        repository="valid-repo"
    )
except ValidationError as e:
    print(f"Use case validation error: {e}")

try:
    # Empty repository string
    invalid_request = GenerateGuideRequest(
        use_case="valid use case",
        repository=""  # Empty string should be None
    )
except ValidationError as e:
    print(f"Repository validation error: {e}")
```

Guide Generation Strategies:
===========================

The system supports various guide generation approaches:

**Pattern-Based Guides**: Focus on common implementation patterns
- Factory patterns for object creation
- Builder patterns for complex configurations
- Strategy patterns for algorithm selection

**Framework-Specific Guides**: Tailored to specific Java frameworks
- Spring Boot application development
- Hibernate ORM usage patterns
- JUnit testing strategies

**Architecture Guides**: Focus on system design and structure
- Microservices communication patterns
- Event-driven architecture implementation
- Clean architecture principles

**Integration Guides**: Cover external system integration
- Database connectivity and ORM usage
- Message queue integration
- REST API consumption and production

See Also:
=========
- java_mcp.java_analyzer: Core analysis logic for guide generation
- java_mcp.parser: Java source code parsing for example extraction
- java_mcp.java: Java file discovery and project structure analysis
- java_mcp.server: MCP server implementation using these models
- fastmcp: Framework for building MCP servers with type-safe tools
- pydantic: Data validation and parsing library
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class GenerateGuideRequest(BaseModel):
    """
    Request model for generating comprehensive API usage guides for Java projects.

    This model defines the parameters required to generate detailed, use case-specific
    API usage guides. It supports both general-purpose guides that span multiple
    repositories and focused guides that target specific repositories or projects.

    The model is designed for use with FastMCP 2.0 tools, providing automatic
    parameter validation and schema generation for AI assistant interactions.
    It enables intelligent documentation generation that addresses specific
    developer scenarios and implementation patterns.

    Attributes:
        use_case (str): The specific use case, functionality, or scenario for which
                       to generate the API usage guide. This should be a clear,
                       descriptive statement of what the developer wants to achieve.
                       Examples: "user authentication with JWT", "database operations
                       with JPA", "REST API with validation", "microservices communication".
                       Required field that cannot be empty.

        repository (Optional[str]): The name or identifier of a specific repository
                                   to focus the guide generation on. If provided,
                                   the guide will primarily use APIs and patterns
                                   from that repository. If None, the guide will
                                   analyze and include relevant APIs from all
                                   available repositories. Optional field that
                                   defaults to None.

    Validation Rules:
        - use_case must be non-empty and contain meaningful description
        - use_case should be descriptive enough to guide API selection
        - repository, if provided, must be a non-empty string

    Usage Examples:
        Authentication and security guide:
        ```python
        request = GenerateGuideRequest(
            use_case="implementing JWT-based authentication with role-based authorization",
            repository="security-service"
        )
        ```

        Data persistence guide:
        ```python
        request = GenerateGuideRequest(
            use_case="JPA entity relationships and complex querying with Criteria API",
            repository="data-access-layer"
        )
        ```

        Cross-repository microservices guide:
        ```python
        request = GenerateGuideRequest(
            use_case="inter-service communication with circuit breakers and retries",
            repository=None  # Analyze all repositories
        )
        ```

        Testing strategies guide:
        ```python
        request = GenerateGuideRequest(
            use_case="comprehensive testing with unit tests, integration tests, and mocking",
            repository="test-framework"
        )
        ```

        API development guide:
        ```python
        request = GenerateGuideRequest(
            use_case="building RESTful APIs with Spring Boot, validation, and error handling"
        )
        ```

    MCP Tool Integration:
        This model is typically used as a parameter type in MCP tool definitions:
        ```python
        @mcp.tool()
        def generate_java_usage_guide(request: GenerateGuideRequest) -> APIUsageGuide:
            '''Generate detailed API usage guides for specific Java development scenarios.'''
            return guide_generator.create_comprehensive_guide(
                use_case=request.use_case,
                repository_scope=request.repository
            )
        ```

    Guide Generation Process:
        1. **Use Case Analysis**: Parse the use case to identify key concepts and requirements
        2. **API Discovery**: Find relevant classes, methods, and patterns in the specified scope
        3. **Pattern Matching**: Identify common implementation patterns for the use case
        4. **Example Generation**: Create practical, runnable code examples
        5. **Documentation Structure**: Organize content with clear sections and explanations
        6. **Best Practices**: Include recommendations and common pitfalls to avoid

    Generated Guide Structure:
        - **Overview**: Introduction to the use case and approach
        - **Prerequisites**: Required dependencies and setup
        - **Core Concepts**: Key APIs and classes involved
        - **Implementation Steps**: Step-by-step guide with code examples
        - **Complete Example**: Full working example
        - **Best Practices**: Recommendations and tips
        - **Common Issues**: Troubleshooting and pitfalls
        - **Further Reading**: Additional resources and references

    Performance Considerations:
        - Repository scoping significantly reduces analysis time for large codebases
        - Use case specificity helps focus on relevant APIs and reduces noise
        - Guide generation may take longer for complex use cases requiring
          analysis of multiple interconnected APIs

    Error Scenarios:
        - Empty or vague use cases will result in ValidationError
        - Non-existent repositories will cause runtime errors during processing
        - Use cases requiring APIs not present in the specified repository
          may result in incomplete guides
    """

    use_case: str = Field(
        description="Specific use case or functionality needed (e.g., 'JWT authentication with role-based access')",
        min_length=5,
        example="implementing REST API with Spring Boot and validation"
    )

    repository: Optional[str] = Field(
        default=None,
        description="Specific repository to focus on (optional - if not provided, analyzes all repositories)",
        example="user-management-service"
    )

    @validator('use_case')
    def validate_use_case(cls, value: str) -> str:
        """
        Validate the use case description for guide generation.

        Args:
            value: The use case description to validate

        Returns:
            str: The validated and normalized use case description

        Raises:
            ValueError: If the use case is too short, empty, or not descriptive
        """
        if not value or not value.strip():
            raise ValueError("Use case description cannot be empty")

        value = value.strip()

        # Check minimum length for meaningful use case
        if len(value) < 5:
            raise ValueError(
                f"Use case description too short: '{value}'. "
                "Please provide a more descriptive use case (at least 5 characters)"
            )

        # Check for overly generic use cases that won't be helpful
        generic_terms = ["help", "guide", "how to", "tutorial", "example"]
        if value.lower() in generic_terms:
            raise ValueError(
                f"Use case too generic: '{value}'. "
                "Please specify what you want to accomplish (e.g., 'JWT authentication', "
                "'REST API development', 'database integration')"
            )

        # Normalize whitespace
        value = ' '.join(value.split())

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
                    "use_case": "implementing JWT authentication with role-based authorization",
                    "repository": "auth-service"
                },
                {
                    "use_case": "JPA entity relationships and complex querying",
                    "repository": "data-layer"
                },
                {
                    "use_case": "building RESTful APIs with Spring Boot and validation",
                    "repository": None
                },
                {
                    "use_case": "microservices communication with Feign clients and circuit breakers",
                    "repository": "service-commons"
                },
                {
                    "use_case": "implementing caching strategies with Redis and Spring Cache",
                    "repository": "caching-service"
                },
                {
                    "use_case": "unit and integration testing with JUnit and Mockito",
                    "repository": "test-framework"
                }
            ]
        }

        # Allow field population by name or alias
        allow_population_by_field_name = True

        # Validate assignment (re-validate when fields are modified)
        validate_assignment = True
