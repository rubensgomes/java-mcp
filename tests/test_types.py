"""
Unit tests for the types.py module.

This test suite provides comprehensive coverage for Java code analysis types
including Parameter, Method, Field, and Class dataclasses, testing their initialization,
default values, post-initialization behavior, and integration scenarios.
"""

import pytest
from dataclasses import FrozenInstanceError
from typing import List, Dict, Any

from java_mcp.types import Parameter, Method, Field, Class


class TestParameter:
    """Test cases for the Parameter dataclass."""

    def test_basic_initialization(self):
        """Test basic Parameter initialization with all required fields."""
        param = Parameter(
            name="userId",
            type="Long",
            annotations=["@NotNull"]
        )

        assert param.name == "userId"
        assert param.type == "Long"
        assert param.annotations == ["@NotNull"]

    def test_initialization_with_empty_annotations(self):
        """Test Parameter initialization with empty annotations list."""
        param = Parameter(
            name="count",
            type="int",
            annotations=[]
        )

        assert param.name == "count"
        assert param.type == "int"
        assert param.annotations == []

    def test_initialization_with_multiple_annotations(self):
        """Test Parameter with multiple annotations."""
        param = Parameter(
            name="user",
            type="User",
            annotations=["@NotNull", "@Valid", "@RequestBody"]
        )

        assert len(param.annotations) == 3
        assert "@NotNull" in param.annotations
        assert "@Valid" in param.annotations
        assert "@RequestBody" in param.annotations

    def test_complex_generic_type(self):
        """Test Parameter with complex generic types."""
        param = Parameter(
            name="userMap",
            type="Map<String, List<User>>",
            annotations=["@NotEmpty"]
        )

        assert param.type == "Map<String, List<User>>"

    def test_parameter_equality(self):
        """Test equality comparison between Parameter instances."""
        param1 = Parameter("name", "String", ["@NotNull"])
        param2 = Parameter("name", "String", ["@NotNull"])
        param3 = Parameter("name", "String", [])

        assert param1 == param2
        assert param1 != param3


class TestMethod:
    """Test cases for the Method dataclass."""

    def test_basic_initialization(self):
        """Test basic Method initialization with required fields."""
        method = Method(
            name="getName",
            return_type="String",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=10
        )

        assert method.name == "getName"
        assert method.return_type == "String"
        assert method.parameters == []
        assert method.modifiers == ["public"]
        assert method.annotations == []
        assert method.javadoc is None
        assert method.line_number == 10
        assert method.is_constructor is False
        assert method.throws_exceptions == []  # Should be initialized by __post_init__

    def test_initialization_with_parameters(self):
        """Test Method initialization with parameters."""
        param1 = Parameter("id", "Long", ["@NotNull"])
        param2 = Parameter("name", "String", [])

        method = Method(
            name="findUser",
            return_type="Optional<User>",
            parameters=[param1, param2],
            modifiers=["public"],
            annotations=["@Transactional"],
            javadoc="Finds a user by ID and name.",
            line_number=25
        )

        assert method.name == "findUser"
        assert method.return_type == "Optional<User>"
        assert len(method.parameters) == 2
        assert method.parameters[0].name == "id"
        assert method.parameters[1].name == "name"
        assert method.annotations == ["@Transactional"]
        assert method.javadoc == "Finds a user by ID and name."

    def test_constructor_method(self):
        """Test Method representing a constructor."""
        param = Parameter("name", "String", [])

        constructor = Method(
            name="User",
            return_type="void",
            parameters=[param],
            modifiers=["public"],
            annotations=[],
            javadoc="Creates a new User instance.",
            line_number=15,
            is_constructor=True
        )

        assert constructor.is_constructor is True
        assert constructor.name == "User"
        assert constructor.return_type == "void"

    def test_method_with_exceptions(self):
        """Test Method with throws_exceptions."""
        method = Method(
            name="saveUser",
            return_type="void",
            parameters=[Parameter("user", "User", [])],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=30,
            throws_exceptions=["IOException", "ValidationException"]
        )

        assert method.throws_exceptions == ["IOException", "ValidationException"]

    def test_post_init_initializes_exceptions(self):
        """Test that __post_init__ initializes throws_exceptions to empty list."""
        method = Method(
            name="test",
            return_type="void",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=1
        )

        # Should be initialized to empty list by __post_init__
        assert method.throws_exceptions == []
        assert isinstance(method.throws_exceptions, list)

    def test_static_method(self):
        """Test Method representing a static method."""
        method = Method(
            name="getInstance",
            return_type="Singleton",
            parameters=[],
            modifiers=["public", "static"],
            annotations=[],
            javadoc="Returns the singleton instance.",
            line_number=45
        )

        assert "static" in method.modifiers
        assert "public" in method.modifiers


class TestField:
    """Test cases for the Field dataclass."""

    def test_basic_initialization(self):
        """Test basic Field initialization with required fields."""
        field = Field(
            name="userName",
            type="String",
            modifiers=["private"],
            annotations=["@Column"],
            javadoc="The user's name",
            line_number=20
        )

        assert field.name == "userName"
        assert field.type == "String"
        assert field.modifiers == ["private"]
        assert field.annotations == ["@Column"]
        assert field.javadoc == "The user's name"
        assert field.line_number == 20
        assert field.initial_value is None

    def test_field_with_initial_value(self):
        """Test Field with initial value."""
        field = Field(
            name="count",
            type="int",
            modifiers=["private"],
            annotations=[],
            javadoc=None,
            line_number=25,
            initial_value="0"
        )

        assert field.initial_value == "0"

    def test_static_final_field(self):
        """Test Field representing a static final constant."""
        field = Field(
            name="MAX_SIZE",
            type="int",
            modifiers=["public", "static", "final"],
            annotations=[],
            javadoc="Maximum allowed size",
            line_number=10,
            initial_value="100"
        )

        assert "static" in field.modifiers
        assert "final" in field.modifiers
        assert "public" in field.modifiers
        assert field.initial_value == "100"

    def test_field_with_complex_type(self):
        """Test Field with complex generic type."""
        field = Field(
            name="userCache",
            type="Map<String, List<User>>",
            modifiers=["private"],
            annotations=["@Autowired"],
            javadoc=None,
            line_number=30,
            initial_value="new HashMap<>()"
        )

        assert field.type == "Map<String, List<User>>"
        assert field.initial_value == "new HashMap<>()"

    def test_field_with_multiple_annotations(self):
        """Test Field with multiple annotations."""
        field = Field(
            name="users",
            type="List<User>",
            modifiers=["private"],
            annotations=["@OneToMany", "@JoinColumn(name=\"user_id\")", "@Cascade(CascadeType.ALL)"],
            javadoc="Associated users",
            line_number=35
        )

        assert len(field.annotations) == 3
        assert "@OneToMany" in field.annotations
        assert "@JoinColumn(name=\"user_id\")" in field.annotations


class TestClass:
    """Test cases for the Class dataclass."""

    def test_basic_initialization(self):
        """Test basic Class initialization with required fields."""
        java_class = Class(
            name="User",
            package="com.example.model",
            modifiers=["public"],
            annotations=["@Entity"],
            javadoc="Represents a user",
            line_number=10,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        assert java_class.name == "User"
        assert java_class.package == "com.example.model"
        assert java_class.modifiers == ["public"]
        assert java_class.annotations == ["@Entity"]
        assert java_class.javadoc == "Represents a user"
        assert java_class.line_number == 10
        assert java_class.methods == []
        assert java_class.fields == []
        assert java_class.inner_classes == []
        assert java_class.extends is None
        assert java_class.implements == []  # Should be initialized by __post_init__
        assert java_class.class_type == "class"

    def test_post_init_initializes_lists(self):
        """Test that __post_init__ initializes None list attributes."""
        java_class = Class(
            name="Test",
            package="com.test",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=1,
            methods=[],
            fields=[],
            inner_classes=[]
            # implements and inner_classes not provided, should be initialized by __post_init__
        )

        assert java_class.implements == []
        assert java_class.inner_classes == []
        assert isinstance(java_class.implements, list)
        assert isinstance(java_class.inner_classes, list)

    def test_class_with_inheritance(self):
        """Test Class with inheritance and interfaces."""
        java_class = Class(
            name="Employee",
            package="com.example.model",
            modifiers=["public"],
            annotations=["@Entity"],
            javadoc="Employee entity",
            line_number=15,
            methods=[],
            fields=[],
            inner_classes=[],
            extends="Person",
            implements=["Serializable", "Comparable<Employee>"]
        )

        assert java_class.extends == "Person"
        assert java_class.implements == ["Serializable", "Comparable<Employee>"]

    def test_interface_class(self):
        """Test Class representing an interface."""
        interface = Class(
            name="Drawable",
            package="com.example.graphics",
            modifiers=["public"],
            annotations=[],
            javadoc="Drawable interface",
            line_number=5,
            methods=[],
            fields=[],
            inner_classes=[],
            class_type="interface"
        )

        assert interface.class_type == "interface"

    def test_enum_class(self):
        """Test Class representing an enum."""
        enum_class = Class(
            name="Status",
            package="com.example.types",
            modifiers=["public"],
            annotations=[],
            javadoc="Status enumeration",
            line_number=8,
            methods=[],
            fields=[],
            inner_classes=[],
            extends="Enum<Status>",
            class_type="enum"
        )

        assert enum_class.class_type == "enum"
        assert enum_class.extends == "Enum<Status>"

    def test_record_class(self):
        """Test Class representing a record."""
        record_class = Class(
            name="Point",
            package="com.example.geometry",
            modifiers=["public"],
            annotations=[],
            javadoc="Point record",
            line_number=3,
            methods=[],
            fields=[],
            inner_classes=[],
            class_type="record"
        )

        assert record_class.class_type == "record"


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple types."""

    def test_complete_class_structure(self):
        """Test a complete class with methods, fields, and inner classes."""
        # Create parameters
        id_param = Parameter("id", "Long", ["@NotNull"])
        name_param = Parameter("name", "String", ["@NotBlank"])

        # Create methods
        constructor = Method(
            name="User",
            return_type="void",
            parameters=[id_param, name_param],
            modifiers=["public"],
            annotations=[],
            javadoc="Creates a new User",
            line_number=20,
            is_constructor=True
        )

        getter = Method(
            name="getName",
            return_type="String",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc="Returns the name",
            line_number=30
        )

        setter = Method(
            name="setName",
            return_type="void",
            parameters=[name_param],
            modifiers=["public"],
            annotations=[],
            javadoc="Sets the name",
            line_number=35
        )

        # Create fields
        id_field = Field(
            name="id",
            type="Long",
            modifiers=["private"],
            annotations=["@Id", "@GeneratedValue"],
            javadoc="User ID",
            line_number=15
        )

        name_field = Field(
            name="name",
            type="String",
            modifiers=["private"],
            annotations=["@Column(nullable=false)"],
            javadoc="User name",
            line_number=18
        )

        # Create inner class
        inner_class = Class(
            name="Builder",
            package="com.example.model",
            modifiers=["public", "static"],
            annotations=[],
            javadoc="Builder for User",
            line_number=40,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        # Create complete class
        user_class = Class(
            name="User",
            package="com.example.model",
            modifiers=["public"],
            annotations=["@Entity", "@Table(name=\"users\")"],
            javadoc="User entity representing a system user",
            line_number=10,
            methods=[constructor, getter, setter],
            fields=[id_field, name_field],
            inner_classes=[inner_class],
            implements=["Serializable"]
        )

        # Verify the complete structure
        assert user_class.name == "User"
        assert len(user_class.methods) == 3
        assert len(user_class.fields) == 2
        assert len(user_class.inner_classes) == 1
        assert len(user_class.annotations) == 2
        assert len(user_class.implements) == 1

        # Verify method details
        assert user_class.methods[0].is_constructor is True
        assert user_class.methods[1].name == "getName"
        assert user_class.methods[2].name == "setName"

        # Verify field details
        assert user_class.fields[0].name == "id"
        assert user_class.fields[1].name == "name"

        # Verify inner class
        assert user_class.inner_classes[0].name == "Builder"
        assert "static" in user_class.inner_classes[0].modifiers

    def test_inheritance_hierarchy(self):
        """Test representing a class inheritance hierarchy."""
        # Base abstract class
        base_class = Class(
            name="Vehicle",
            package="com.example.transport",
            modifiers=["public", "abstract"],
            annotations=[],
            javadoc="Base vehicle class",
            line_number=5,
            methods=[
                Method(
                    name="start",
                    return_type="void",
                    parameters=[],
                    modifiers=["public", "abstract"],
                    annotations=[],
                    javadoc="Start the vehicle",
                    line_number=10
                )
            ],
            fields=[
                Field(
                    name="model",
                    type="String",
                    modifiers=["protected"],
                    annotations=[],
                    javadoc="Vehicle model",
                    line_number=8
                )
            ],
            inner_classes=[]
        )

        # Concrete implementation
        car_class = Class(
            name="Car",
            package="com.example.transport",
            modifiers=["public"],
            annotations=["@Component"],
            javadoc="Car implementation",
            line_number=15,
            methods=[
                Method(
                    name="start",
                    return_type="void",
                    parameters=[],
                    modifiers=["public"],
                    annotations=["@Override"],
                    javadoc="Start the car",
                    line_number=20
                )
            ],
            fields=[],
            inner_classes=[],
            extends="Vehicle",
            implements=["Drivable"]
        )

        assert base_class.extends is None
        assert "abstract" in base_class.modifiers
        assert car_class.extends == "Vehicle"
        assert "Drivable" in car_class.implements
        assert car_class.methods[0].annotations == ["@Override"]


class TestDataclassFeatures:
    """Test dataclass-specific features and edge cases."""

    def test_string_representation(self):
        """Test string representation of dataclass instances."""
        param = Parameter("test", "String", [])
        param_str = str(param)

        assert "Parameter" in param_str
        assert "test" in param_str
        assert "String" in param_str

    def test_field_modification(self):
        """Test that dataclass fields can be modified after creation."""
        method = Method(
            name="test",
            return_type="void",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=1
        )

        # Initially empty due to __post_init__
        assert len(method.throws_exceptions) == 0

        # Add an exception
        method.throws_exceptions.append("IOException")

        assert len(method.throws_exceptions) == 1
        assert method.throws_exceptions[0] == "IOException"

    def test_type_annotations(self):
        """Test that type annotations are preserved."""
        # Check that we can access type annotations
        assert hasattr(Parameter, '__annotations__')
        assert hasattr(Method, '__annotations__')
        assert hasattr(Field, '__annotations__')
        assert hasattr(Class, '__annotations__')

        # Verify some key type annotations
        assert Parameter.__annotations__['name'] == str
        assert Parameter.__annotations__['type'] == str
        assert Method.__annotations__['parameters'] == List[Parameter]
        assert Class.__annotations__['methods'] == List[Method]
        assert Class.__annotations__['fields'] == List[Field]


if __name__ == "__main__":
    pytest.main([__file__])
