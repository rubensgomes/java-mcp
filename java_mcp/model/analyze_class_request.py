from typing import Optional

from pydantic import BaseModel, Field


class AnalyzeClassRequest(BaseModel):
    """
    Request model for the analyze_java_class tool.

    Defines parameters for detailed analysis of specific Java classes.
    Supports both simple and fully qualified class names with optional repository filtering.

    Attributes:
        class_name (str): Class name to analyze (simple or fully qualified)
        repository (Optional[str]): Limit search to specific repository name

    Examples:
        Simple class name:
            AnalyzeClassRequest(class_name="UserService")

        Fully qualified:
            AnalyzeClassRequest(class_name="com.example.service.UserService")

        Repository-specific:
            AnalyzeClassRequest(class_name="UserService", repository="user-management")
    """
    class_name: str = Field(description="Fully qualified class name")
    repository: Optional[str] = Field(default=None, description="Repository name")
