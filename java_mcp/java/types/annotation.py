from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Annotation:
    """
    Represents a Java annotation with its name and parameters.

    Java annotations provide metadata about code elements and can have parameters
    that configure their behavior. This class captures both simple marker annotations
    and complex annotations with multiple parameters.

    Attributes:
        name: The annotation name without the @ symbol (e.g., "Override", "NotNull")
        parameters: Dictionary of parameter names to values for parameterized annotations

    Examples:
        Simple annotation:
            Annotation(name="Override")

        Parameterized annotation:
            Annotation(
                name="RequestMapping",
                parameters={"value": "/api/users", "method": "GET"}
            )

        Complex annotation with arrays:
            Annotation(
                name="JsonTypeInfo",
                parameters={
                    "use": "JsonTypeInfo.Id.NAME",
                    "include": "JsonTypeInfo.As.PROPERTY",
                    "property": "type"
                }
            )
    """
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return string representation of the annotation."""
        if not self.parameters:
            return f"@{self.name}"

        param_strs = []
        for key, value in self.parameters.items():
            if isinstance(value, str):
                param_strs.append(f'{key}="{value}"')
            else:
                param_strs.append(f'{key}={value}')

        return f"@{self.name}({', '.join(param_strs)})"

