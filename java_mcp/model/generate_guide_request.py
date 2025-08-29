from typing import Optional

from pydantic import BaseModel, Field


class GenerateGuideRequest(BaseModel):
    """
    Request model for the generate_api_guide tool.

    Defines parameters for generating contextual API usage guides based on
    specific use cases. Analyzes cached APIs to find relevant classes and methods.

    Attributes:
        use_case (str): Description of the specific use case or functionality needed
                       (e.g., "user authentication", "file upload", "database operations")
        repository (Optional[str]): Limit search to specific repository name

    Examples:
        General use case:
            GenerateGuideRequest(use_case="user authentication and security")

        Repository-specific:
            GenerateGuideRequest(
                use_case="data validation",
                repository="company-validation-framework"
            )
    """
    use_case: str = Field(description="Specific use case or functionality needed")
    repository: Optional[str] = Field(default=None, description="Specific repository to focus on")
