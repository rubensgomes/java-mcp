from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Annotation:
    """
    Represents a Java annotation with its name and parameters.

    Java annotations can be simple (@Override) or complex with parameters
    (@RequestMapping(value="/api", method=GET)). This class captures both
    the annotation name and any associated parameter values.

    Attributes:
        name (str): The fully qualified or simple name of the annotation
                   (e.g., "Override", "org.springframework.web.bind.annotation.RequestMapping")
        parameters (Dict[str, Any]): Dictionary of parameter names to values.
                                   For single-value annotations, uses key "value".
                                   For parameterless annotations, this is empty.

    Examples:
        Simple annotation:
            Annotation(name="Override", parameters={})

        Single value annotation:
            Annotation(name="SuppressWarnings", parameters={"value": "unchecked"})

        Multi-parameter annotation:
            Annotation(name="RequestMapping",
                      parameters={"value": "/api", "method": "GET"})
    """
    name: str
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
