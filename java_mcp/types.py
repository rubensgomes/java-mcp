"""
Java code analysis types for MCP (Model Context Protocol) server.

This module defines data structures that represent Java code elements
(classes, methods, fields) that will be exposed to AI coding assistants
through the MCP server. These types enable structured communication
about Java codebases between the MCP server and AI assistants.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# pylint: disable=R0902
@dataclass
class JavaMethod:
    """
    Represents a Java method with its documentation and metadata.

    This structure is used by the MCP server to provide AI assistants
    with detailed information about Java methods, including their
    signatures, documentation, and source location.

    Attributes:
        name: The method name
        return_type: The method's return type (e.g., "String", "void")
        parameters: List of parameter dictionaries with 'name' and 'type' keys
        modifiers: Method modifiers (e.g., ["public", "static"])
        javadoc: Extracted Javadoc documentation text
        annotations: Java annotations applied to the method
        exceptions: Declared thrown exceptions
        line_number: Source file line number where method is defined
    """
    name: str
    return_type: str
    parameters: List[Dict[str, str]]
    modifiers: List[str]
    javadoc: Optional[str] = None
    annotations: List[str] = None
    exceptions: List[str] = None
    line_number: int = 0

# pylint: disable=R0902
@dataclass
class JavaClass:
    """
    Represents a Java class with its methods, fields, and documentation.

    This is the primary data structure exposed by the MCP server to AI
    assistants for understanding Java class structure, inheritance
    relationships, and contained methods/fields.

    Attributes:
        name: The class name (simple name, not fully qualified)
        package: The package declaration (e.g., "com.example.utils")
        modifiers: Class modifiers (e.g., ["public", "final"])
        extends: Parent class name if this class extends another
        implements: List of interface names this class implements
        javadoc: Extracted class-level Javadoc documentation
        methods: List of JavaMethod objects representing class methods
        fields: List of field dictionaries with metadata
        annotations: Java annotations applied to the class
        file_path: Absolute path to the source file
        line_number: Source file line number where class is defined
    """
    name: str
    package: str
    modifiers: List[str]
    extends: Optional[str] = None
    implements: List[str] = None
    javadoc: Optional[str] = None
    methods: List[JavaMethod] = None
    fields: List[Dict[str, Any]] = None
    annotations: List[str] = None
    file_path: str = ""
    line_number: int = 0

    def __post_init__(self):
        """Initialize empty lists for optional list attributes."""
        if self.methods is None:
            self.methods = []
        if self.fields is None:
            self.fields = []
        if self.annotations is None:
            self.annotations = []
        if self.implements is None:
            self.implements = []
