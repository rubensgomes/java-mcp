from typing import Optional

from pydantic import BaseModel, Field


class SearchMethodsRequest(BaseModel):
    """
    Request model for the search_java_methods tool.

    Defines parameters for searching methods across all cached repositories.
    Supports both exact and partial name matching with optional class filtering.

    Attributes:
        method_name (str): Method name to search for (partial matching supported)
        class_name (Optional[str]): Optional filter by class name (partial matching)

    Examples:
        Search all methods:
            SearchMethodsRequest(method_name="findById")

        Search in specific class:
            SearchMethodsRequest(method_name="save", class_name="Repository")
    """
    method_name: str = Field(description="Method name to search for")
    class_name: Optional[str] = Field(default=None, description="Class name filter")
