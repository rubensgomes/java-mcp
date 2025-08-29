from dataclasses import dataclass
from typing import List

from .annotation import Annotation


@dataclass
class Parameter:
    """
    Represents a Java method parameter with type information and annotations.

    Captures complete parameter information including type (with generics),
    name, annotations, and whether it's a varargs parameter (...).

    Attributes:
        name (str): Parameter name as declared in the method signature
        type (str): Full parameter type including generics
                   (e.g., "String", "List<String>", "Map<String, Integer>")
        annotations (List[Annotation]): List of annotations applied to this parameter
                                       (e.g., @NotNull, @Valid, @PathVariable)
        is_varargs (bool): True if this is a varargs parameter (type...)

    Examples:
        Simple parameter:
            Parameter(name="userId", type="Long", annotations=[], is_varargs=False)

        Annotated parameter:
            Parameter(name="user", type="UserDto",
                     annotations=[Annotation("Valid"), Annotation("NotNull")],
                     is_varargs=False)

        Varargs parameter:
            Parameter(name="values", type="String", annotations=[], is_varargs=True)
    """
    name: str
    type: str
    annotations: List[Annotation] = None
    is_varargs: bool = False

    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []
