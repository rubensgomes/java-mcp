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
class Parameter:
    """
    Represents a Java method parameter with its type and annotations.

    This structure captures the details of a method parameter including its name,
    type information, and any annotations applied to it. It's used within Method
    objects to provide complete parameter information to AI assistants.

    Attributes:
        name: The parameter name (e.g., "userName", "index")
        type: The parameter's type (e.g., "String", "int", "List<User>")
        annotations: List of annotations applied to the parameter (e.g., ["@NotNull", "@Valid"])

    Example:
        Parameter(
            name="users",
            type="List<User>",
            annotations=["@NotNull", "@Valid"]
        )
    """
    name: str
    type: str
    annotations: List[str]

# pylint: disable=R0902
@dataclass
class Method:
    """
    Represents a Java method with its documentation and metadata.

    This structure is used by the MCP server to provide AI assistants
    with detailed information about Java methods, including their
    signatures, documentation, source location, and behavioral characteristics.

    Attributes:
        name: The method name (e.g., "calculateTotal", "getUserById")
        return_type: The method's return type (e.g., "String", "void", "Optional<User>")
        parameters: List of Parameter objects representing method parameters
        modifiers: Method modifiers (e.g., ["public", "static"], ["private", "final"])
        annotations: Java annotations applied to the method (e.g., ["@Override", "@Deprecated"])
        javadoc: Extracted Javadoc documentation text, if available
        line_number: Source file line number where method is defined
        is_constructor: True if this method represents a constructor
        throws_exceptions: List of exception types this method declares to throw

    Example:
        Method(
            name="findUserById",
            return_type="Optional<User>",
            parameters=[Parameter("id", "Long", ["@NotNull"])],
            modifiers=["public"],
            annotations=["@Transactional"],
            javadoc="Finds a user by their unique identifier.",
            line_number=42,
            is_constructor=False,
            throws_exceptions=["UserNotFoundException"]
        )
    """
    name: str
    return_type: str
    parameters: List[Parameter]
    modifiers: List[str]
    annotations: List[str]
    javadoc: Optional[str]
    line_number: int
    is_constructor: bool = False
    throws_exceptions: List[str] = None

    def __post_init__(self):
        if self.throws_exceptions is None:
            self.throws_exceptions = []


# pylint: disable=R0902
@dataclass
class Field:
    """
    Represents a Java field (instance or class variable) with its metadata.

    This structure captures the details of a Java field including its name, type,
    access modifiers, annotations, documentation, and optional initial value.
    It's used within Class objects to provide complete field information to AI assistants.

    Attributes:
        name: The field name (e.g., "userName", "MAX_SIZE")
        type: The field's type (e.g., "String", "int", "List<User>", "Map<String, Object>")
        modifiers: Field modifiers (e.g., ["private"], ["public", "static", "final"])
        annotations: Java annotations applied to the field (e.g., ["@Column", "@NotNull"])
        javadoc: Extracted Javadoc documentation text for the field, if available
        line_number: Source file line number where field is declared
        initial_value: The initial value assigned to the field, if any (e.g., "null", "0", "new ArrayList<>()")

    Example:
        Field(
            name="users",
            type="List<User>",
            modifiers=["private"],
            annotations=["@OneToMany", "@JoinColumn(name=\"user_id\")"],
            javadoc="List of users associated with this entity.",
            line_number=25,
            initial_value="new ArrayList<>()"
        )
    """
    name: str
    type: str
    modifiers: List[str]
    annotations: List[str]
    javadoc: Optional[str]
    line_number: int
    initial_value: Optional[str] = None


# pylint: disable=R0902
@dataclass
class Class:
    """
    Represents a Java class with its methods, fields, and documentation.

    This is the primary data structure exposed by the MCP server to AI assistants
    for understanding Java class structure, inheritance relationships, and contained
    methods/fields. It supports various Java constructs including classes, interfaces,
    enums, and records.

    Attributes:
        name: The class name (simple name, not fully qualified, e.g., "User", "Repository")
        package: The package declaration (e.g., "com.example.model", "java.util")
        modifiers: Class modifiers (e.g., ["public", "final"], ["public", "abstract"])
        annotations: Java annotations applied to the class (e.g., ["@Entity", "@Component"])
        javadoc: Extracted class-level Javadoc documentation text, if available
        line_number: Source file line number where class is declared
        methods: List of Method objects representing all class methods
        fields: List of Field objects representing all class fields
        inner_classes: List of nested Class objects for inner/nested classes
        extends: Parent class name if this class extends another (e.g., "AbstractUser")
        implements: List of interface names this class implements (e.g., ["Serializable", "Comparable<User>"])
        class_type: Type of Java construct ("class", "interface", "enum", "record")

    Example:
        Class(
            name="User",
            package="com.example.model",
            modifiers=["public"],
            annotations=["@Entity", "@Table(name=\"users\")"],
            javadoc="Represents a user entity in the system.",
            line_number=15,
            methods=[Method(...)],
            fields=[Field(...)],
            inner_classes=[],
            extends="AbstractEntity",
            implements=["Serializable"],
            class_type="class"
        )
    """
    name: str
    package: str
    modifiers: List[str]
    annotations: List[str]
    javadoc: Optional[str]
    line_number: int
    methods: List[Method]
    fields: List[Field]
    inner_classes: List['Class']
    extends: Optional[str] = None
    implements: List[str] = None
    class_type: str = "class"  # class, interface, enum, record

    def __post_init__(self):
        if self.implements is None:
            self.implements = []
        if self.inner_classes is None:
            self.inner_classes = []
