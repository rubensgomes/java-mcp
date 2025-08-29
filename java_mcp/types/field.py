from dataclasses import dataclass
from typing import List, Optional

from .annotation import Annotation


@dataclass
class Field:
    """
    Represents a Java field (instance variable, static variable, or constant).

    Captures complete field information including type, modifiers, annotations,
    initial values, and documentation. Handles regular fields, static variables,
    constants, and enum constants.

    Attributes:
        name (str): Field name as declared
        type (str): Field type including generics (e.g., "List<String>")
        modifiers (List[str]): Field modifiers (public, private, static, final, etc.)
        javadoc (Optional[str]): Extracted and cleaned Javadoc documentation
        annotations (List[Annotation]): Field-level annotations
        initial_value (Optional[str]): Initial value assignment if present
        line_number (int): Line number where field is declared in source file

    Examples:
        Instance field:
            Field(name="name", type="String", modifiers=["private"])

        Static constant:
            Field(name="MAX_SIZE", type="int",
                 modifiers=["public", "static", "final"],
                 initial_value="100")

        Annotated field:
            Field(name="id", type="Long",
                 modifiers=["private"],
                 annotations=[Annotation("Id"), Annotation("GeneratedValue")])
    """
    name: str
    type: str
    modifiers: List[str]
    javadoc: Optional[str] = None
    annotations: List[Annotation] = None
    initial_value: Optional[str] = None
    line_number: int = 0

    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []
