"""
Unit tests for the types.py module.

This test suite provides comprehensive coverage for Java code analysis types
including JavaMethod and JavaClass dataclasses, testing their initialization,
default values, and post-initialization behavior.
"""

import pytest
from dataclasses import FrozenInstanceError
from typing import List, Dict, Any

from java_mcp.types import JavaMethod, JavaClass


class TestJavaMethod:
    """Test cases for the JavaMethod dataclass."""

    def test_basic_initialization(self):
        """Test basic JavaMethod initialization with required fields."""
        method = JavaMethod(
            name="getValue",
            return_type="String",
            parameters=[{"name": "index", "type": "int"}],
            modifiers=["public"]
        )

        assert method.name == "getValue"
        assert method.return_type == "String"
        assert method.parameters == [{"name": "index", "type": "int"}]
        assert method.modifiers == ["public"]

        # Check default values
        assert method.javadoc is None
        assert method.annotations is None
        assert method.exceptions is None
        assert method.line_number == 0

    def test_initialization_with_all_fields(self):
        """Test JavaMethod initialization with all optional fields."""
        method = JavaMethod(
            name="processData",
            return_type="void",
            parameters=[
                {"name": "data", "type": "List<String>"},
                {"name": "options", "type": "Map<String, Object>"}
            ],
            modifiers=["public", "static"],
            javadoc="Processes the given data with specified options.",
            annotations=["@Override", "@Deprecated"],
            exceptions=["IOException", "IllegalArgumentException"],
            line_number=42
        )

        assert method.name == "processData"
        assert method.return_type == "void"
        assert len(method.parameters) == 2
        assert method.parameters[0] == {"name": "data", "type": "List<String>"}
        assert method.parameters[1] == {"name": "options", "type": "Map<String, Object>"}
        assert method.modifiers == ["public", "static"]
        assert method.javadoc == "Processes the given data with specified options."
        assert method.annotations == ["@Override", "@Deprecated"]
        assert method.exceptions == ["IOException", "IllegalArgumentException"]
        assert method.line_number == 42

    def test_empty_parameters_list(self):
        """Test JavaMethod with empty parameters list."""
        method = JavaMethod(
            name="initialize",
            return_type="void",
            parameters=[],
            modifiers=["private"]
        )

        assert method.parameters == []
        assert len(method.parameters) == 0

    def test_complex_return_types(self):
        """Test JavaMethod with complex generic return types."""
        method = JavaMethod(
            name="getMap",
            return_type="Map<String, List<Integer>>",
            parameters=[],
            modifiers=["public"]
        )

        assert method.return_type == "Map<String, List<Integer>>"

    def test_constructor_method(self):
        """Test representing a constructor as JavaMethod."""
        constructor = JavaMethod(
            name="<init>",
            return_type="void",
            parameters=[{"name": "name", "type": "String"}],
            modifiers=["public"],
            javadoc="Creates a new instance with the given name."
        )

        assert constructor.name == "<init>"
        assert constructor.return_type == "void"
        assert constructor.javadoc == "Creates a new instance with the given name."

    def test_method_equality(self):
        """Test equality comparison between JavaMethod instances."""
        method1 = JavaMethod(
            name="test",
            return_type="String",
            parameters=[],
            modifiers=["public"]
        )

        method2 = JavaMethod(
            name="test",
            return_type="String",
            parameters=[],
            modifiers=["public"]
        )

        method3 = JavaMethod(
            name="different",
            return_type="String",
            parameters=[],
            modifiers=["public"]
        )

        assert method1 == method2
        assert method1 != method3

    def test_method_with_varargs(self):
        """Test JavaMethod with varargs parameters."""
        method = JavaMethod(
            name="format",
            return_type="String",
            parameters=[
                {"name": "template", "type": "String"},
                {"name": "args", "type": "Object..."}
            ],
            modifiers=["public", "static"]
        )

        assert method.parameters[1]["type"] == "Object..."


class TestJavaClass:
    """Test cases for the JavaClass dataclass."""

    def test_basic_initialization(self):
        """Test basic JavaClass initialization with required fields."""
        java_class = JavaClass(
            name="StringBuilder",
            package="java.lang",
            modifiers=["public", "final"]
        )

        assert java_class.name == "StringBuilder"
        assert java_class.package == "java.lang"
        assert java_class.modifiers == ["public", "final"]

        # Check default values
        assert java_class.extends is None
        assert java_class.javadoc is None
        assert java_class.file_path == ""
        assert java_class.line_number == 0

    def test_post_init_empty_lists(self):
        """Test that __post_init__ initializes None list attributes to empty lists."""
        java_class = JavaClass(
            name="TestClass",
            package="com.test",
            modifiers=["public"]
        )

        # These should be initialized to empty lists by __post_init__
        assert java_class.methods == []
        assert java_class.fields == []
        assert java_class.annotations == []
        assert java_class.implements == []
        assert isinstance(java_class.methods, list)
        assert isinstance(java_class.fields, list)
        assert isinstance(java_class.annotations, list)
        assert isinstance(java_class.implements, list)

    def test_post_init_preserves_existing_lists(self):
        """Test that __post_init__ preserves existing list values."""
        methods = [JavaMethod("test", "void", [], ["public"])]
        fields = [{"name": "value", "type": "String", "modifiers": ["private"]}]
        annotations = ["@Component"]
        implements = ["Serializable"]

        java_class = JavaClass(
            name="TestClass",
            package="com.test",
            modifiers=["public"],
            methods=methods,
            fields=fields,
            annotations=annotations,
            implements=implements
        )

        # Should preserve the provided values
        assert java_class.methods is methods
        assert java_class.fields is fields
        assert java_class.annotations is annotations
        assert java_class.implements is implements

    def test_initialization_with_all_fields(self):
        """Test JavaClass initialization with all fields."""
        method1 = JavaMethod("getName", "String", [], ["public"])
        method2 = JavaMethod("setName", "void", [{"name": "name", "type": "String"}], ["public"])

        java_class = JavaClass(
            name="Person",
            package="com.example.model",
            modifiers=["public"],
            extends="Object",
            implements=["Serializable", "Comparable<Person>"],
            javadoc="Represents a person with basic information.",
            methods=[method1, method2],
            fields=[
                {"name": "name", "type": "String", "modifiers": ["private"]},
                {"name": "age", "type": "int", "modifiers": ["private"]}
            ],
            annotations=["@Entity", "@Table(name=\"persons\")"],
            file_path="/src/main/java/com/example/model/Person.java",
            line_number=15
        )

        assert java_class.name == "Person"
        assert java_class.package == "com.example.model"
        assert java_class.modifiers == ["public"]
        assert java_class.extends == "Object"
        assert java_class.implements == ["Serializable", "Comparable<Person>"]
        assert java_class.javadoc == "Represents a person with basic information."
        assert len(java_class.methods) == 2
        assert java_class.methods[0].name == "getName"
        assert java_class.methods[1].name == "setName"
        assert len(java_class.fields) == 2
        assert java_class.fields[0]["name"] == "name"
        assert java_class.fields[1]["name"] == "age"
        assert java_class.annotations == ["@Entity", "@Table(name=\"persons\")"]
        assert java_class.file_path == "/src/main/java/com/example/model/Person.java"
        assert java_class.line_number == 15

    def test_interface_class(self):
        """Test JavaClass representing an interface."""
        interface = JavaClass(
            name="Drawable",
            package="com.example.graphics",
            modifiers=["public", "interface"],
            methods=[
                JavaMethod("draw", "void", [], ["public", "abstract"]),
                JavaMethod("getArea", "double", [], ["public", "abstract"])
            ]
        )

        assert "interface" in interface.modifiers
        assert len(interface.methods) == 2
        assert all("abstract" in method.modifiers for method in interface.methods)

    def test_abstract_class(self):
        """Test JavaClass representing an abstract class."""
        abstract_class = JavaClass(
            name="Shape",
            package="com.example.shapes",
            modifiers=["public", "abstract"],
            extends="Object",
            methods=[
                JavaMethod("getArea", "double", [], ["public", "abstract"]),
                JavaMethod("getPerimeter", "double", [], ["public"])
            ]
        )

        assert "abstract" in abstract_class.modifiers
        assert abstract_class.extends == "Object"

    def test_enum_class(self):
        """Test JavaClass representing an enum."""
        enum_class = JavaClass(
            name="Color",
            package="com.example.types",
            modifiers=["public", "enum"],
            extends="Enum<Color>",
            fields=[
                {"name": "RED", "type": "Color", "modifiers": ["public", "static", "final"]},
                {"name": "GREEN", "type": "Color", "modifiers": ["public", "static", "final"]},
                {"name": "BLUE", "type": "Color", "modifiers": ["public", "static", "final"]}
            ]
        )

        assert "enum" in enum_class.modifiers
        assert enum_class.extends == "Enum<Color>"
        assert len(enum_class.fields) == 3

    def test_nested_class(self):
        """Test JavaClass representing a nested/inner class."""
        nested_class = JavaClass(
            name="Builder",
            package="com.example.util",
            modifiers=["public", "static"],
            methods=[
                JavaMethod("build", "Object", [], ["public"]),
                JavaMethod("withValue", "Builder", [{"name": "value", "type": "String"}], ["public"])
            ]
        )

        assert "static" in nested_class.modifiers
        assert nested_class.name == "Builder"

    def test_class_equality(self):
        """Test equality comparison between JavaClass instances."""
        class1 = JavaClass(
            name="Test",
            package="com.example",
            modifiers=["public"]
        )

        class2 = JavaClass(
            name="Test",
            package="com.example",
            modifiers=["public"]
        )

        class3 = JavaClass(
            name="Different",
            package="com.example",
            modifiers=["public"]
        )

        assert class1 == class2
        assert class1 != class3

    def test_complex_generic_class(self):
        """Test JavaClass with complex generic types."""
        generic_class = JavaClass(
            name="Repository",
            package="com.example.data",
            modifiers=["public"],
            implements=["CrudRepository<Entity, Long>"],
            methods=[
                JavaMethod(
                    "findById",
                    "Optional<Entity>",
                    [{"name": "id", "type": "Long"}],
                    ["public"]
                )
            ]
        )

        assert "CrudRepository<Entity, Long>" in generic_class.implements
        assert generic_class.methods[0].return_type == "Optional<Entity>"


class TestDataclassFeatures:
    """Test dataclass-specific features and edge cases."""

    def test_string_representation(self):
        """Test string representation of dataclass instances."""
        method = JavaMethod("test", "void", [], ["public"])
        method_str = str(method)

        assert "JavaMethod" in method_str
        assert "test" in method_str
        assert "void" in method_str
        assert "public" in method_str

    def test_field_modification(self):
        """Test that dataclass fields can be modified after creation."""
        java_class = JavaClass("Test", "com.example", ["public"])

        # Initially empty due to __post_init__
        assert len(java_class.methods) == 0

        # Add a method
        method = JavaMethod("newMethod", "String", [], ["public"])
        java_class.methods.append(method)

        assert len(java_class.methods) == 1
        assert java_class.methods[0].name == "newMethod"

    def test_type_annotations(self):
        """Test that type annotations are preserved."""
        # This tests that the dataclasses maintain their type hints
        method = JavaMethod("test", "void", [], ["public"])
        java_class = JavaClass("Test", "com.example", ["public"])

        # Check that we can access type annotations
        assert hasattr(JavaMethod, '__annotations__')
        assert hasattr(JavaClass, '__annotations__')

        # Verify some key type annotations
        assert JavaMethod.__annotations__['name'] == str
        assert JavaMethod.__annotations__['parameters'] == List[Dict[str, str]]
        assert JavaClass.__annotations__['methods'] == List[JavaMethod]


# Integration test helpers
class TestIntegrationScenarios:
    """Integration test scenarios combining multiple types."""

    def test_complete_class_with_methods(self):
        """Test a complete class structure with multiple methods."""
        # Create methods
        constructor = JavaMethod(
            name="<init>",
            return_type="void",
            parameters=[{"name": "name", "type": "String"}],
            modifiers=["public"],
            javadoc="Creates a new user with the given name."
        )

        getter = JavaMethod(
            name="getName",
            return_type="String",
            parameters=[],
            modifiers=["public"],
            javadoc="Returns the user's name."
        )

        setter = JavaMethod(
            name="setName",
            return_type="void",
            parameters=[{"name": "name", "type": "String"}],
            modifiers=["public"],
            javadoc="Sets the user's name."
        )

        # Create complete class
        user_class = JavaClass(
            name="User",
            package="com.example.model",
            modifiers=["public"],
            extends="Object",
            implements=["Serializable"],
            javadoc="Represents a user in the system.",
            methods=[constructor, getter, setter],
            fields=[{"name": "name", "type": "String", "modifiers": ["private"]}],
            annotations=["@Entity"],
            file_path="/src/main/java/com/example/model/User.java",
            line_number=10
        )

        # Verify the complete structure
        assert user_class.name == "User"
        assert len(user_class.methods) == 3
        assert len(user_class.fields) == 1
        assert len(user_class.implements) == 1
        assert len(user_class.annotations) == 1

        # Verify method details
        constructor_method = user_class.methods[0]
        assert constructor_method.name == "<init>"
        assert len(constructor_method.parameters) == 1

        getter_method = user_class.methods[1]
        assert getter_method.name == "getName"
        assert getter_method.return_type == "String"
        assert len(getter_method.parameters) == 0

    def test_inheritance_hierarchy(self):
        """Test representing an inheritance hierarchy."""
        # Base class
        base_class = JavaClass(
            name="Animal",
            package="com.example.zoo",
            modifiers=["public", "abstract"],
            methods=[
                JavaMethod("getName", "String", [], ["public"]),
                JavaMethod("makeSound", "void", [], ["public", "abstract"])
            ]
        )

        # Derived class
        derived_class = JavaClass(
            name="Dog",
            package="com.example.zoo",
            modifiers=["public"],
            extends="Animal",
            implements=["Domesticated"],
            methods=[
                JavaMethod("makeSound", "void", [], ["public"]),
                JavaMethod("fetch", "void", [{"name": "item", "type": "String"}], ["public"])
            ]
        )

        assert base_class.extends is None
        assert "abstract" in base_class.modifiers
        assert derived_class.extends == "Animal"
        assert "Domesticated" in derived_class.implements


if __name__ == "__main__":
    pytest.main([__file__])
