"""
Unit tests for the types.py module.

This test suite provides comprehensive coverage for Java code analysis types
including Parameter, Method, Field, and Class dataclasses, testing their initialization,
default values, post-initialization behavior, and integration scenarios.
"""

from java_mcp.java.types import Parameter, Method, Field, Class


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

    def test_varargs_parameter(self):
        """Test Parameter representing varargs (variable arguments)."""
        param = Parameter(
            name="values",
            type="String...",
            annotations=[]
        )

        assert param.name == "values"
        assert param.type == "String..."
        assert param.annotations == []

    def test_primitive_types(self):
        """Test Parameter with various primitive types."""
        primitive_types = ["int", "long", "double", "float", "boolean", "char", "byte", "short"]

        for ptype in primitive_types:
            param = Parameter(
                name=f"test_{ptype}",
                type=ptype,
                annotations=[]
            )
            assert param.type == ptype


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
        param1 = Parameter("name", "String", ["@NotNull"])
        param2 = Parameter("age", "int", [])

        method = Method(
            name="createUser",
            return_type="User",
            parameters=[param1, param2],
            modifiers=["public", "static"],
            annotations=["@Override"],
            javadoc="Creates a new user instance.",
            line_number=25
        )

        assert method.name == "createUser"
        assert method.return_type == "User"
        assert len(method.parameters) == 2
        assert method.parameters[0] == param1
        assert method.parameters[1] == param2
        assert method.modifiers == ["public", "static"]
        assert method.annotations == ["@Override"]
        assert method.javadoc == "Creates a new user instance."
        assert method.line_number == 25

    def test_constructor_initialization(self):
        """Test Method representing a constructor."""
        param = Parameter("name", "String", [])

        constructor = Method(
            name="User",
            return_type="User",
            parameters=[param],
            modifiers=["public"],
            annotations=[],
            javadoc="Default constructor.",
            line_number=15,
            is_constructor=True
        )

        assert constructor.name == "User"
        assert constructor.return_type == "User"
        assert constructor.is_constructor is True
        assert len(constructor.parameters) == 1

    def test_post_init_throws_exceptions_none(self):
        """Test that __post_init__ initializes throws_exceptions when None."""
        method = Method(
            name="test",
            return_type="void",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=10,
            throws_exceptions=None
        )

        assert method.throws_exceptions == []

    def test_post_init_throws_exceptions_provided(self):
        """Test that __post_init__ preserves provided throws_exceptions."""
        exceptions = ["IOException", "SQLException"]
        method = Method(
            name="test",
            return_type="void",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=10,
            throws_exceptions=exceptions
        )

        assert method.throws_exceptions == exceptions

    def test_void_return_type(self):
        """Test Method with void return type."""
        method = Method(
            name="doSomething",
            return_type="void",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=30
        )

        assert method.return_type == "void"

    def test_generic_return_type(self):
        """Test Method with generic return type."""
        method = Method(
            name="getList",
            return_type="List<String>",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=40
        )

        assert method.return_type == "List<String>"

    def test_multiple_annotations(self):
        """Test Method with multiple annotations."""
        method = Method(
            name="processRequest",
            return_type="ResponseEntity<String>",
            parameters=[],
            modifiers=["public"],
            annotations=["@PostMapping", "@ResponseBody", "@Transactional"],
            javadoc=None,
            line_number=50
        )

        assert len(method.annotations) == 3
        assert "@PostMapping" in method.annotations
        assert "@ResponseBody" in method.annotations
        assert "@Transactional" in method.annotations

    def test_multiple_throws_exceptions(self):
        """Test Method with multiple throws exceptions."""
        method = Method(
            name="complexOperation",
            return_type="String",
            parameters=[],
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=60,
            throws_exceptions=["IOException", "SQLException", "CustomException"]
        )

        assert len(method.throws_exceptions) == 3
        assert "IOException" in method.throws_exceptions
        assert "SQLException" in method.throws_exceptions
        assert "CustomException" in method.throws_exceptions


class TestField:
    """Test cases for the Field dataclass."""

    def test_basic_initialization(self):
        """Test basic Field initialization with required fields."""
        field = Field(
            name="userName",
            type="String",
            modifiers=["private"],
            annotations=["@Column"],
            javadoc="The user's name.",
            line_number=15
        )

        assert field.name == "userName"
        assert field.type == "String"
        assert field.modifiers == ["private"]
        assert field.annotations == ["@Column"]
        assert field.javadoc == "The user's name."
        assert field.line_number == 15
        assert field.initial_value is None

    def test_initialization_with_initial_value(self):
        """Test Field initialization with initial value."""
        field = Field(
            name="count",
            type="int",
            modifiers=["private"],
            annotations=[],
            javadoc=None,
            line_number=20,
            initial_value="0"
        )

        assert field.name == "count"
        assert field.type == "int"
        assert field.initial_value == "0"

    def test_static_final_field(self):
        """Test Field representing a static final constant."""
        field = Field(
            name="MAX_SIZE",
            type="int",
            modifiers=["public", "static", "final"],
            annotations=[],
            javadoc="Maximum allowed size.",
            line_number=10,
            initial_value="100"
        )

        assert field.name == "MAX_SIZE"
        assert field.type == "int"
        assert "public" in field.modifiers
        assert "static" in field.modifiers
        assert "final" in field.modifiers
        assert field.initial_value == "100"

    def test_complex_type_field(self):
        """Test Field with complex generic type."""
        field = Field(
            name="userMap",
            type="Map<String, List<User>>",
            modifiers=["private"],
            annotations=["@JsonIgnore"],
            javadoc=None,
            line_number=25,
            initial_value="new HashMap<>()"
        )

        assert field.type == "Map<String, List<User>>"
        assert field.initial_value == "new HashMap<>()"

    def test_multiple_annotations(self):
        """Test Field with multiple annotations."""
        field = Field(
            name="id",
            type="Long",
            modifiers=["private"],
            annotations=["@Id", "@GeneratedValue", "@Column(name=\"user_id\")"],
            javadoc="Primary key.",
            line_number=12
        )

        assert len(field.annotations) == 3
        assert "@Id" in field.annotations
        assert "@GeneratedValue" in field.annotations
        assert "@Column(name=\"user_id\")" in field.annotations

    def test_array_type_field(self):
        """Test Field with array type."""
        field = Field(
            name="values",
            type="String[]",
            modifiers=["private"],
            annotations=[],
            javadoc=None,
            line_number=30,
            initial_value="new String[10]"
        )

        assert field.type == "String[]"
        assert field.initial_value == "new String[10]"

    def test_primitive_field(self):
        """Test Field with primitive type."""
        field = Field(
            name="active",
            type="boolean",
            modifiers=["private"],
            annotations=[],
            javadoc=None,
            line_number=35,
            initial_value="false"
        )

        assert field.type == "boolean"
        assert field.initial_value == "false"


class TestClass:
    """Test cases for the Class dataclass."""

    def test_basic_initialization(self):
        """Test basic Class initialization with required fields."""
        cls = Class(
            name="User",
            package="com.example.model",
            modifiers=["public"],
            annotations=["@Entity"],
            javadoc="Represents a user entity.",
            line_number=10,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        assert cls.name == "User"
        assert cls.package == "com.example.model"
        assert cls.modifiers == ["public"]
        assert cls.annotations == ["@Entity"]
        assert cls.javadoc == "Represents a user entity."
        assert cls.line_number == 10
        assert cls.methods == []
        assert cls.fields == []
        assert cls.inner_classes == []
        assert cls.extends is None
        assert cls.implements == []  # Should be initialized by __post_init__
        assert cls.class_type == "class"

    def test_initialization_with_inheritance(self):
        """Test Class initialization with inheritance."""
        cls = Class(
            name="AdminUser",
            package="com.example.model",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=20,
            methods=[],
            fields=[],
            inner_classes=[],
            extends="User",
            implements=["Serializable", "Comparable<AdminUser>"]
        )

        assert cls.extends == "User"
        assert len(cls.implements) == 2
        assert "Serializable" in cls.implements
        assert "Comparable<AdminUser>" in cls.implements

    def test_post_init_implements_none(self):
        """Test that __post_init__ initializes implements when None."""
        cls = Class(
            name="Test",
            package="com.example",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=10,
            methods=[],
            fields=[],
            inner_classes=[],
            implements=None
        )

        assert cls.implements == []

    def test_post_init_inner_classes_none(self):
        """Test that __post_init__ initializes inner_classes when None."""
        cls = Class(
            name="Test",
            package="com.example",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=10,
            methods=[],
            fields=[],
            inner_classes=None
        )

        assert cls.inner_classes == []

    def test_class_with_methods_and_fields(self):
        """Test Class with methods and fields."""
        field = Field("name", "String", ["private"], [], None, 15)
        method = Method("getName", "String", [], ["public"], [], None, 20)

        cls = Class(
            name="Person",
            package="com.example",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=10,
            methods=[method],
            fields=[field],
            inner_classes=[]
        )

        assert len(cls.methods) == 1
        assert len(cls.fields) == 1
        assert cls.methods[0] == method
        assert cls.fields[0] == field

    def test_interface_class_type(self):
        """Test Class representing an interface."""
        cls = Class(
            name="UserRepository",
            package="com.example.repository",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=5,
            methods=[],
            fields=[],
            inner_classes=[],
            class_type="interface"
        )

        assert cls.class_type == "interface"

    def test_enum_class_type(self):
        """Test Class representing an enum."""
        cls = Class(
            name="Status",
            package="com.example.enums",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=8,
            methods=[],
            fields=[],
            inner_classes=[],
            class_type="enum"
        )

        assert cls.class_type == "enum"

    def test_record_class_type(self):
        """Test Class representing a record."""
        cls = Class(
            name="UserDto",
            package="com.example.dto",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=12,
            methods=[],
            fields=[],
            inner_classes=[],
            class_type="record"
        )

        assert cls.class_type == "record"

    def test_nested_inner_classes(self):
        """Test Class with nested inner classes."""
        inner_class = Class(
            name="Builder",
            package="com.example",
            modifiers=["public", "static"],
            annotations=[],
            javadoc=None,
            line_number=30,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        outer_class = Class(
            name="User",
            package="com.example",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=10,
            methods=[],
            fields=[],
            inner_classes=[inner_class]
        )

        assert len(outer_class.inner_classes) == 1
        assert outer_class.inner_classes[0] == inner_class

    def test_multiple_annotations(self):
        """Test Class with multiple annotations."""
        cls = Class(
            name="User",
            package="com.example.model",
            modifiers=["public"],
            annotations=["@Entity", "@Table(name=\"users\")", "@JsonIgnoreProperties"],
            javadoc=None,
            line_number=15,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        assert len(cls.annotations) == 3
        assert "@Entity" in cls.annotations
        assert "@Table(name=\"users\")" in cls.annotations
        assert "@JsonIgnoreProperties" in cls.annotations

    def test_abstract_class(self):
        """Test Class representing an abstract class."""
        cls = Class(
            name="AbstractEntity",
            package="com.example.model",
            modifiers=["public", "abstract"],
            annotations=[],
            javadoc=None,
            line_number=5,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        assert "public" in cls.modifiers
        assert "abstract" in cls.modifiers

    def test_final_class(self):
        """Test Class representing a final class."""
        cls = Class(
            name="ImmutableUser",
            package="com.example.model",
            modifiers=["public", "final"],
            annotations=[],
            javadoc=None,
            line_number=5,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        assert "public" in cls.modifiers
        assert "final" in cls.modifiers

    def test_complex_inheritance_scenario(self):
        """Test Class with complex inheritance scenario."""
        cls = Class(
            name="UserService",
            package="com.example.service",
            modifiers=["public"],
            annotations=["@Service", "@Transactional"],
            javadoc="Service for user operations.",
            line_number=25,
            methods=[],
            fields=[],
            inner_classes=[],
            extends="AbstractService<User>",
            implements=["UserOperations", "Auditable", "Cacheable<String>"]
        )

        assert cls.extends == "AbstractService<User>"
        assert len(cls.implements) == 3
        assert "UserOperations" in cls.implements
        assert "Auditable" in cls.implements
        assert "Cacheable<String>" in cls.implements


class TestIntegrationScenarios:
    """Test cases for integration scenarios between types."""

    def test_complete_class_with_all_components(self):
        """Test a complete Class with methods, fields, and inner classes."""
        # Create field
        id_field = Field(
            name="id",
            type="Long",
            modifiers=["private"],
            annotations=["@Id", "@GeneratedValue"],
            javadoc="Primary key.",
            line_number=15
        )

        name_field = Field(
            name="name",
            type="String",
            modifiers=["private"],
            annotations=["@Column(nullable=false)"],
            javadoc="User name.",
            line_number=20
        )

        # Create methods
        constructor = Method(
            name="User",
            return_type="User",
            parameters=[Parameter("name", "String", ["@NotNull"])],
            modifiers=["public"],
            annotations=[],
            javadoc="Constructor with name.",
            line_number=25,
            is_constructor=True
        )

        getter = Method(
            name="getName",
            return_type="String",
            parameters=[],
            modifiers=["public"],
            annotations=["@Override"],
            javadoc="Gets the user name.",
            line_number=30
        )

        # Create inner class
        builder = Class(
            name="Builder",
            package="com.example.model",
            modifiers=["public", "static"],
            annotations=[],
            javadoc="Builder pattern implementation.",
            line_number=40,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        # Create main class
        user_class = Class(
            name="User",
            package="com.example.model",
            modifiers=["public"],
            annotations=["@Entity", "@Table(name=\"users\")"],
            javadoc="Represents a user entity in the system.",
            line_number=10,
            methods=[constructor, getter],
            fields=[id_field, name_field],
            inner_classes=[builder],
            extends="AbstractEntity",
            implements=["Serializable"]
        )

        # Verify complete structure
        assert user_class.name == "User"
        assert len(user_class.fields) == 2
        assert len(user_class.methods) == 2
        assert len(user_class.inner_classes) == 1
        assert user_class.extends == "AbstractEntity"
        assert "Serializable" in user_class.implements

        # Verify field details
        assert user_class.fields[0].name == "id"
        assert user_class.fields[1].name == "name"

        # Verify method details
        assert any(m.is_constructor for m in user_class.methods)
        assert any(m.name == "getName" for m in user_class.methods)

        # Verify inner class
        assert user_class.inner_classes[0].name == "Builder"

    def test_method_with_complex_parameters(self):
        """Test Method with complex parameter scenarios."""
        param1 = Parameter("users", "List<User>", ["@NotNull", "@Valid"])
        param2 = Parameter("options", "Map<String, Object>", ["@RequestParam"])
        param3 = Parameter("callback", "Function<User, String>", [])
        param4 = Parameter("values", "String...", [])  # Varargs

        method = Method(
            name="processUsers",
            return_type="CompletableFuture<List<String>>",
            parameters=[param1, param2, param3, param4],
            modifiers=["public", "async"],
            annotations=["@PostMapping", "@ResponseBody"],
            javadoc="Processes users asynchronously.",
            line_number=45,
            throws_exceptions=["ProcessingException", "ValidationException"]
        )

        assert len(method.parameters) == 4
        assert method.parameters[0].type == "List<User>"
        assert method.parameters[3].type == "String..."  # Varargs
        assert method.return_type == "CompletableFuture<List<String>>"
        assert len(method.throws_exceptions) == 2

    def test_deeply_nested_classes(self):
        """Test deeply nested class structures."""
        innermost = Class(
            name="Config",
            package="com.example",
            modifiers=["private", "static"],
            annotations=[],
            javadoc=None,
            line_number=60,
            methods=[],
            fields=[],
            inner_classes=[]
        )

        middle = Class(
            name="Builder",
            package="com.example",
            modifiers=["public", "static"],
            annotations=[],
            javadoc=None,
            line_number=50,
            methods=[],
            fields=[],
            inner_classes=[innermost]
        )

        outer = Class(
            name="ComplexClass",
            package="com.example",
            modifiers=["public"],
            annotations=[],
            javadoc=None,
            line_number=40,
            methods=[],
            fields=[],
            inner_classes=[middle]
        )

        assert len(outer.inner_classes) == 1
        assert len(outer.inner_classes[0].inner_classes) == 1
        assert outer.inner_classes[0].inner_classes[0].name == "Config"

    def test_dataclass_equality(self):
        """Test equality comparison between dataclass instances."""
        param1 = Parameter("name", "String", ["@NotNull"])
        param2 = Parameter("name", "String", ["@NotNull"])
        param3 = Parameter("name", "String", [])

        assert param1 == param2
        assert param1 != param3

        field1 = Field("id", "Long", ["private"], ["@Id"], None, 10)
        field2 = Field("id", "Long", ["private"], ["@Id"], None, 10)
        field3 = Field("id", "String", ["private"], ["@Id"], None, 10)

        assert field1 == field2
        assert field1 != field3
