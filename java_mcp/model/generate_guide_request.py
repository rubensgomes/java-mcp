from typing import Optional
from pydantic import BaseModel, Field

# Pydantic models for FastMCP 2.0 tool parameters
class GenerateGuideRequest(BaseModel):
    """Request model for generating API usage guides."""
    use_case: str = Field(description="Specific use case or functionality needed")
    repository: Optional[str] = Field(default=None, description="Specific repository to focus on")

