from typing import Optional

from pydantic import BaseModel, Field


# Pydantic models for FastMCP 2.0 tool parameters
class ExtractAPIsRequest(BaseModel):
    """
    Request model for the extract_java_apis tool.

    Defines the parameters needed to extract Java APIs from a Git repository.
    Uses Pydantic for automatic validation and schema generation in FastMCP 2.0.

    Attributes:
        repo_url (str): Git repository URL (HTTPS or SSH format)
        branch (str): Git branch to clone/checkout (defaults to "main")
        package_filter (Optional[str]): Filter classes by package prefix
                                       (e.g., "com.example" matches "com.example.*")
        class_filter (Optional[str]): Filter classes by name using regex pattern
                                     (e.g., ".*Service.*" matches classes with "Service" in name)

    Examples:
        Basic extraction:
            ExtractAPIsRequest(repo_url="https://github.com/user/repo.git")

        With filters:
            ExtractAPIsRequest(
                repo_url="https://github.com/spring-projects/spring-framework.git",
                branch="main",
                package_filter="org.springframework.web",
                class_filter=".*Controller.*"
            )
    """
    repo_url: str = Field(description="Git repository URL")
    branch: str = Field(default="main", description="Git branch")
    package_filter: Optional[str] = Field(default=None, description="Filter classes by package prefix")
    class_filter: Optional[str] = Field(default=None, description="Filter classes by name pattern (regex)")
