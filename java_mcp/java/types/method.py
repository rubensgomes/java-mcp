from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Method:
    """
    Represents a Java method with complete signature and metadata information.

    Methods are fundamental building blocks of Java classes. This class captures
    all aspects of a method including its signature, modifiers, documentation,
    exceptions, and source location. This comprehensive representation enables
    AI assistants to understand method behavior, usage patterns, and integration points.

    Attributes:
        name: The method name as declared
        return_type: Complete return type including generics (e.g., "Optional<User>")
        parameters: List of Parameter objects representing method parameters
        modifiers: Access and behavioral modifiers (e.g., ["public", "static", "final"])
        javadoc: Extracted Javadoc documentation text with formatting preserved
        annotations: List of annotations applied to the method
        exceptions: List of exception types declared in throws clause
        line_number: Source file line number where method declaration starts
        is_constructor: True if this method is a constructor
        type_parameters: Generic type parameters (e.g., ["T", "K extends Comparable<K>"])
        is_abstract: True if method is declared abstract
        is_native: True if method is declared native
        is_synchronized: True if method is declared synchronized

    Examples:
        Simple method:
            Method(
                name="getName",
                return_type="String",
                parameters=[],
                modifiers=["public"]
            )

        Complex generic method:
            Method(
                name="findByQuery",
                return_type="List<T>",
                parameters=[
                    Parameter("query", "String", [Annotation("NotBlank")]),
                    Parameter("pageSize", "int", [], is_final=True)
                ],
                modifiers=["public"],
                type_parameters=["T extends Entity"],
                exceptions=["DatabaseException", "ValidationException"],
                javadoc="Finds entities matching the given query with pagination.",
                annotations=[
                    Annotation("Transactional", {"readOnly": "true"}),
                    Annotation("Cacheable")
                ]
            )
    """
    name: str
    return_type: str
    parameters: List[Parameter] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    javadoc: Optional[str] = None
    annotations: List[Annotation] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    line_number: int = 0
    is_constructor: bool = False
    type_parameters: List[str] = field(default_factory=list)
    is_abstract: bool = False
    is_native: bool = False
    is_synchronized: bool = False

    def __post_init__(self):
        """Post-initialization processing to derive additional properties."""
        # Derive boolean flags from modifiers
        if "abstract" in self.modifiers:
            self.is_abstract = True
        if "native" in self.modifiers:
            self.is_native = True
        if "synchronized" in self.modifiers:
            self.is_synchronized = True

    def get_signature(self) -> str:
        """
        Generate a human-readable method signature.

        Returns:
            Complete method signature including modifiers, return type, name, and parameters
        """
        parts = []

        # Add annotations
        if self.annotations:
            parts.extend(str(ann) for ann in self.annotations)

        # Add modifiers
        if self.modifiers:
            parts.append(" ".join(self.modifiers))

        # Add type parameters
        if self.type_parameters:
            parts.append(f"<{', '.join(self.type_parameters)}>")

        # Add return type and name
        if not self.is_constructor:
            parts.append(f"{self.return_type} {self.name}")
        else:
            parts.append(self.name)

        # Add parameters
        param_strs = [str(param) for param in self.parameters]
        parts.append(f"({', '.join(param_strs)})")

        # Add exceptions
        if self.exceptions:
            parts.append(f"throws {', '.join(self.exceptions)}")

        return " ".join(parts)
