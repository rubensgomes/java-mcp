from dataclasses import dataclass, field
from typing import List


@dataclass
class Parameter:
    """
    Represents a Java method parameter with complete type and annotation information.

    Method parameters in Java can have complex type signatures, annotations for
    validation or processing hints, and special characteristics like varargs.
    This class captures all these details to provide complete parameter information
    to AI assistants.

    Attributes:
        name: The parameter name as declared in the method signature
        type: The parameter's type including generics (e.g., "List<String>", "Map<K,V>")
        annotations: List of annotations applied to this parameter
        is_varargs: True if this parameter uses varargs syntax (...)
        is_final: True if the parameter is declared as final

    Examples:
        Simple parameter:
            Parameter(name="count", type="int")

        Generic parameter with annotations:
            Parameter(
                name="users",
                type="List<User>",
                annotations=[
                    Annotation("NotNull"),
                    Annotation("Valid")
                ]
            )

        Varargs parameter:
            Parameter(
                name="values",
                type="String",
                is_varargs=True
            )
    """
    name: str
    type: str
    annotations: List[Annotation] = field(default_factory=list)
    is_varargs: bool = False
    is_final: bool = False

    def __str__(self) -> str:
        """Return string representation of the parameter."""
        parts = []

        if self.annotations:
            parts.extend(str(ann) for ann in self.annotations)

        if self.is_final:
            parts.append("final")

        type_str = self.type
        if self.is_varargs:
            type_str += "..."

        parts.append(f"{type_str} {self.name}")

        return " ".join(parts)
