from dataclasses import dataclass, field
from typing import List, Optional

from .method import Method
from .field import Field
from .parameter import Parameter
from .annotation import Annotation


@dataclass
class Class:
    """
    Represents a complete Java class, interface, enum, or record with all metadata.

    This is the top-level container for Java type definitions. It captures the complete
    structure of Java types including their inheritance relationships, implemented
    interfaces, contained methods and fields, nested types, and documentation.
    This comprehensive representation enables AI assistants to understand complex
    Java type hierarchies and relationships.

    Attributes:
        name: The class/interface/enum/record name without package qualification
        package: Full package name (e.g., "com.example.service")
        modifiers: Class-level modifiers (e.g., ["public", "abstract", "final"])
        class_type: Type of declaration ("class", "interface", "enum", "record", "annotation")
        extends: Full name of the superclass if any (e.g., "java.util.ArrayList")
        implements: List of implemented interface names
        javadoc: Extracted class-level Javadoc documentation
        methods: List of all methods (including constructors) defined in this class
        fields: List of all fields defined in this class
        annotations: List of class-level annotations
        type_parameters: Generic type parameters (e.g., ["T", "K extends Comparable<K>"])
        file_path: Absolute path to the source file containing this class
        line_number: Line number where class declaration starts
        inner_classes: List of nested/inner classes defined within this class
        enum_constants: List of enum constant names (only for enum types)
        record_components: List of record component definitions (only for record types)
        is_abstract: True if class is declared abstract
        is_final: True if class is declared final
        is_static: True if this is a static nested class

    Examples:
        Simple class:
            Class(
                name="User",
                package="com.example.model",
                class_type="class",
                modifiers=["public"]
            )

        Generic interface with documentation:
            Class(
                name="Repository",
                package="com.example.repository",
                class_type="interface",
                modifiers=["public"],
                type_parameters=["T", "ID extends Serializable"],
                methods=[
                    Method("findById", "Optional<T>", [Parameter("id", "ID")]),
                    Method("save", "T", [Parameter("entity", "T")])
                ],
                javadoc="Generic repository interface for CRUD operations."
            )

        Enum with constants:
            Class(
                name="Status",
                package="com.example.enums",
                class_type="enum",
                enum_constants=["ACTIVE", "INACTIVE", "PENDING"],
                javadoc="Represents the status of an entity."
            )
    """
    name: str
    package: str
    modifiers: List[str] = field(default_factory=list)
    class_type: str = "class"  # "class", "interface", "enum", "record", "annotation"
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    javadoc: Optional[str] = None
    methods: List[Method] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)
    annotations: List[Annotation] = field(default_factory=list)
    type_parameters: List[str] = field(default_factory=list)
    file_path: str = ""
    line_number: int = 0
    inner_classes: List['Class'] = field(default_factory=list)
    enum_constants: List[str] = field(default_factory=list)
    record_components: List[Parameter] = field(default_factory=list)
    is_abstract: bool = False
    is_final: bool = False
    is_static: bool = False

    def __post_init__(self):
        """Post-initialization processing to derive additional properties."""
        # Derive boolean flags from modifiers
        if "abstract" in self.modifiers:
            self.is_abstract = True
        if "final" in self.modifiers:
            self.is_final = True
        if "static" in self.modifiers:
            self.is_static = True

    def get_full_name(self) -> str:
        """
        Get the fully qualified class name.

        Returns:
            Full class name including package (e.g., "com.example.model.User")
        """
        if self.package:
            return f"{self.package}.{self.name}"
        return self.name

    def get_constructors(self) -> List[Method]:
        """
        Get all constructor methods for this class.

        Returns:
            List of Method objects where is_constructor is True
        """
        return [method for method in self.methods if method.is_constructor]

    def get_static_methods(self) -> List[Method]:
        """
        Get all static methods for this class.

        Returns:
            List of Method objects that have "static" in their modifiers
        """
        return [method for method in self.methods if "static" in method.modifiers]

    def get_public_methods(self) -> List[Method]:
        """
        Get all public methods for this class.

        Returns:
            List of Method objects that have "public" in their modifiers
        """
        return [method for method in self.methods if "public" in method.modifiers]

    def get_fields_by_type(self, field_type: str) -> List[Field]:
        """
        Get all fields of a specific type.

        Args:
            field_type: The type to filter by (e.g., "String", "List<User>")

        Returns:
            List of Field objects matching the specified type
        """
        return [field for field in self.fields if field.type == field_type]
