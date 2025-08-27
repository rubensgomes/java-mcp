from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Field:
    """
    Represents a Java field (instance or class variable) with complete metadata.

    Fields represent the state of Java objects and classes. This class captures
    field declarations including their types, modifiers, initial values, and
    documentation. This information helps AI assistants understand data structures
    and state management in Java classes.

    Attributes:
        name: The field name as declared
        type: Complete field type including generics (e.g., "Map<String, List<User>>")
        modifiers: Field modifiers (e.g., ["private", "final", "static"])
        javadoc: Extracted Javadoc documentation for the field
        annotations: List of annotations applied to the field
        initial_value: String representation of the field's initial value if present
        line_number: Source file line number where field is declared
        is_static: True if field is declared static
        is_final: True if field is declared final
        is_volatile: True if field is declared volatile
        is_transient: True if field is declared transient

    Examples:
        Simple field:
            Field(
                name="name",
                type="String",
                modifiers=["private"]
            )

        Complex field with annotations:
            Field(
                name="users",
                type="Map<String, User>",
                modifiers=["private", "final"],
                initial_value="new HashMap<>()",
                annotations=[
                    Annotation("JsonProperty", {"value": "user_map"}),
                    Annotation("NotNull")
                ],
                javadoc="Map of user IDs to User objects for quick lookup."
            )

        Static constant:
            Field(
                name="DEFAULT_TIMEOUT",
                type="long",
                modifiers=["public", "static", "final"],
                initial_value="30000L",
                javadoc="Default timeout in milliseconds for network operations."
            )
    """
    name: str
    type: str
    modifiers: List[str] = field(default_factory=list)
    javadoc: Optional[str] = None
    annotations: List[Annotation] = field(default_factory=list)
    initial_value: Optional[str] = None
    line_number: int = 0
    is_static: bool = False
    is_final: bool = False
    is_volatile: bool = False
    is_transient: bool = False

    def __post_init__(self):
        """Post-initialization processing to derive additional properties."""
        # Derive boolean flags from modifiers
        if "static" in self.modifiers:
            self.is_static = True
        if "final" in self.modifiers:
            self.is_final = True
        if "volatile" in self.modifiers:
            self.is_volatile = True
        if "transient" in self.modifiers:
            self.is_transient = True
