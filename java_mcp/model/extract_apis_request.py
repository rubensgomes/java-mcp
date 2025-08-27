from typing import Optional
from pydantic import BaseModel, Field

# Pydantic models for FastMCP 2.0 tool parameters
class ExtractAPIsRequest(BaseModel):
    """Request model for extracting Java APIs."""
    repo_url: str = Field(description="Git repository URL")
    branch: str = Field(default="main", description="Git branch")
    package_filter: Optional[str] = Field(default=None, description="Filter classes by package prefix")
    class_filter: Optional[str] = Field(default=None, description="Filter classes by name pattern (regex)")
