from typing import Optional
from pydantic import BaseModel, Field

# Pydantic models for FastMCP 2.0 tool parameters
class AnalyzeClassRequest(BaseModel):
    """Request model for analyzing Java classes."""
    class_name: str = Field(description="Fully qualified class name")
    repository: Optional[str] = Field(default=None, description="Repository name")
