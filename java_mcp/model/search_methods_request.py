from typing import Optional
from pydantic import BaseModel, Field

# Pydantic models for FastMCP 2.0 tool parameters
class SearchMethodsRequest(BaseModel):
    """Request model for searching Java methods."""
    method_name: str = Field(description="Method name to search for")
    class_name: Optional[str] = Field(default=None, description="Class name filter")
