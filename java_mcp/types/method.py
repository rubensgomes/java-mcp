from dataclasses import dataclass
from typing import List, Optional

from .annotation import Annotation
from .parameter import Parameter


@dataclass
class Method:
    """
    Represents a Java method or constructor with complete signature information.

    Captures all aspects of a Java method including signature, modifiers,
    annotations, documentation, and metadata. Handles both regular methods
    and constructors.

    Attributes:
        name (str): Method name or constructor name
        return_type (str): Return type (empty string for constructors)
        parameters (List[Parameter]): List of method parameters
        modifiers (List[str]): Method modifiers (public, private, static, etc.)
        javadoc (Optional[str]): Extracted and cleaned Javadoc documentation
        annotations (List[Annotation]): Method-level annotations
        exceptions (List[str]): List of declared exceptions in throws clause
        line_number (int): Line number where method is declared in source file
        is_constructor (bool): True if this represents a constructor
        type_parameters (List[str]): Generic type parameters (e.g., <T, U>)

    Examples:
        Regular method:
            Method(name="findById", return_type="Optional<User>",
                  parameters=[Parameter("id", "Long")],
                  modifiers=["public"], is_constructor=False)

        Constructor:
            Method(name="User", return_type="",
                  parameters=[Parameter("name", "String")],
                  modifiers=["public"], is_constructor=True)

        Generic method:
            Method(name="process", return_type="T",
                  type_parameters=["T extends Serializable"],
                  modifiers=["public", "static"])
    """
    name: str
    return_type: str
    parameters: List[Parameter]
    modifiers: List[str]
    javadoc: Optional[str] = None
    annotations: List[Annotation] = None
    exceptions: List[str] = None
    line_number: int = 0
    is_constructor: bool = False
    type_parameters: List[str] = None

    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []
        if self.type_parameters is None:
            self.type_parameters = []
