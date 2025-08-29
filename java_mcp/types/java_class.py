from dataclasses import dataclass
from typing import List, Optional

from .annotation import Annotation
from .field import Field
from .method import Method


@dataclass
class Class:
    """
    Represents a Java class, interface, enum, record, or annotation type.

    This is the main container for Java API information, capturing complete
    type definitions including all members, metadata, inheritance relationships,
    and nested types. Supports all Java type declarations from Java 8 through Java 24.

    Attributes:
        name (str): Simple class name (not fully qualified)
        package (str): Package name containing this class
        modifiers (List[str]): Class modifiers (public, abstract, final, sealed, etc.)
        class_type (str): Type of declaration ("class", "interface", "enum", "record", "annotation")
        extends (Optional[str]): Superclass name if this class extends another
        implements (List[str]): List of interface names this class implements
        javadoc (Optional[str]): Extracted and cleaned class-level Javadoc
        methods (List[Method]): All methods and constructors in this class
        fields (List[Field]): All fields, constants, and enum values in this class
        annotations (List[Annotation]): Class-level annotations
        type_parameters (List[str]): Generic type parameters (e.g., ["T", "U extends Serializable"])
        file_path (str): Path to source file containing this class
        line_number (int): Line number where class declaration starts
        inner_classes (List['Class']): Nested classes, interfaces, enums, etc.

    Examples:
        Regular class:
            Class(name="User", package="com.example.model", class_type="class",
                 extends="BaseEntity", implements=["Serializable"])

        Generic interface:
            Class(name="Repository", package="com.example.dao", class_type="interface",
                 type_parameters=["T", "ID extends Serializable"])

        Enum:
            Class(name="Status", package="com.example.enums", class_type="enum")

        Record (Java 14+):
            Class(name="Point", package="com.example.geometry", class_type="record")

        Sealed class (Java 17+):
            Class(name="Shape", package="com.example.shapes", class_type="class",
                 modifiers=["public", "sealed"])
    """
    name: str
    package: str
    modifiers: List[str]
    class_type: str  # "class", "interface", "enum", "record", "annotation"
    extends: Optional[str] = None
    implements: List[str] = None
    javadoc: Optional[str] = None
    methods: List[Method] = None
    fields: List[Field] = None
    annotations: List[Annotation] = None
    type_parameters: List[str] = None
    file_path: str = ""
    line_number: int = 0
    inner_classes: List['Class'] = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.fields is None:
            self.fields = []
        if self.annotations is None:
            self.annotations = []
        if self.implements is None:
            self.implements = []
        if self.type_parameters is None:
            self.type_parameters = []
        if self.inner_classes is None:
            self.inner_classes = []
