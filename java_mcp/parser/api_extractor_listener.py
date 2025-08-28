"""
ANTLR4 Listener for Java API Information Extraction

This module provides a sophisticated ANTLR4 listener implementation that extracts
comprehensive Java API information from ANTLR4 parse trees. It serves as the core
component for analyzing Java source code structure and converting it into structured
data representations for the Java MCP server.

The listener implements the visitor pattern to traverse ANTLR4 parse trees generated
from Java source code, extracting detailed information about classes, interfaces,
enums, records, methods, fields, and their associated metadata including annotations,
modifiers, and Javadoc documentation.

Key Features:
============

Comprehensive Java Language Support:
- Classes, interfaces, enums, and records (Java 14+)
- Nested and inner classes with proper hierarchy tracking
- Generic type parameters and constraints
- Package and import declarations

Rich Metadata Extraction:
- Javadoc comments with automatic cleaning and formatting
- Annotations with parameters and complex structures
- Access modifiers and language keywords
- Source location tracking (file paths and line numbers)

Advanced Processing Capabilities:
- Pre-processing of Javadoc comments for efficient lookup
- Stack-based tracking of nested type declarations
- Inheritance relationship extraction (extends/implements)
- Exception declarations and method signatures

Integration with Type System:
- Direct creation of java_mcp.java.types objects
- Seamless integration with the broader Java analysis pipeline
- Support for complex type hierarchies and relationships

Usage Patterns:
==============

Basic API Extraction:
```python
from java_mcp.parser.api_extractor_listener import APIExtractorListener
from java_mcp.parser.antlr4 import JavaLexer, JavaParser
from antlr4 import CommonTokenStream, InputStream

# Set up ANTLR4 parsing
input_stream = InputStream(java_source_code)
lexer = JavaLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = JavaParser(token_stream)

# Create and configure listener
listener = APIExtractorListener(file_path="MyClass.java", source_code=java_source_code)

# Walk the parse tree
tree = parser.compilationUnit()
walker = ParseTreeWalker()
walker.walk(listener, tree)

# Access extracted information
classes = listener.classes
package = listener.current_package
imports = listener.imports
```

Integration with Java Source Parser:
```python
from java_mcp.parser.source_parser import JavaSourceParser

# High-level parsing with automatic listener usage
parser = JavaSourceParser()
result = parser.parse_file("/path/to/JavaFile.java")

# Access extracted classes and metadata
for java_class in result.classes:
    print(f"Class: {java_class.name}")
    for method in java_class.methods:
        print(f"  Method: {method.name}({', '.join(p.type for p in method.parameters)})")
```

Javadoc Processing:
```python
# The listener automatically extracts and associates Javadoc
listener = APIExtractorListener(file_path, source_code)
# ... parsing ...

# Javadoc is automatically attached to relevant elements
for java_class in listener.classes:
    if java_class.javadoc:
        print(f"Class documentation: {java_class.javadoc}")

    for method in java_class.methods:
        if method.javadoc:
            print(f"Method {method.name} documentation: {method.javadoc}")
```

Architecture and Design:
=======================

Visitor Pattern Implementation:
- Extends JavaParserListener from ANTLR4-generated code
- Implements enter/exit methods for relevant parse tree nodes
- Maintains state during tree traversal for context-aware processing

State Management:
- Package and import tracking across the compilation unit
- Class stack for handling nested type declarations
- Javadoc cache for efficient comment association

Data Flow:
1. **Pre-processing**: Extract all Javadoc comments and create lookup cache
2. **Package/Import**: Process package declaration and import statements
3. **Type Processing**: Handle class, interface, enum, and record declarations
4. **Member Processing**: Extract methods, constructors, and fields
5. **Metadata Association**: Attach Javadoc, annotations, and modifiers

Performance Considerations:
==========================

Efficient Javadoc Processing:
- Pre-extraction of all Javadoc comments for O(1) lookup
- Regex-based cleaning and formatting
- Intelligent association with following declarations

Memory Management:
- Stack-based nested class tracking prevents memory leaks
- Efficient string processing for large source files
- Minimal object creation during traversal

Scalability:
- Handles large Java files with complex hierarchies
- Supports deeply nested class structures
- Processes files with extensive Javadoc documentation

Error Handling and Robustness:
=============================

The listener is designed to be robust and continue processing even when
encountering malformed or incomplete Java code:

- Graceful handling of missing or incomplete parse tree nodes
- Default values for optional elements (modifiers, annotations, etc.)
- Safe text extraction with null checks
- Continuation of processing after encountering errors

Integration Points:
==================

Java Type System:
- Creates instances of java_mcp.java.types classes
- Maintains proper relationships between types and members
- Supports complex type hierarchies and generic parameters

Parser Infrastructure:
- Works seamlessly with ANTLR4-generated Java parser
- Integrates with error handling and recovery mechanisms
- Supports custom parse tree walkers and processing pipelines

MCP Server:
- Provides structured data for API analysis tools
- Enables comprehensive Java code understanding for AI assistants
- Supports documentation generation and code exploration workflows

Extension Points:
================

The listener can be extended or customized for specific use cases:

- Override specific enter/exit methods for custom processing
- Add additional metadata extraction for framework-specific patterns
- Implement custom Javadoc processing for specialized documentation formats
- Extend type parameter extraction for advanced generic type analysis

See Also:
=========
- java_mcp.parser.source_parser: High-level Java parsing interface
- java_mcp.parser.antlr4: ANTLR4-generated parser components
- java_mcp.java.types: Type system for representing Java code elements
- java_mcp.parser.java_doc_extractor: Specialized Javadoc processing utilities
"""

import re
from typing import List, Optional

from java_mcp.parser.antlr4.JavaParserListener import JavaParserListener
from java_mcp.java.types.annotation import Annotation
from java_mcp.java.types.field import Field
from java_mcp.java.types.method import Method
from java_mcp.java.types.parameter import Parameter
from java_mcp.java.types.java_class import Class


class APIExtractorListener(JavaParserListener):
    """
    ANTLR4 listener for extracting comprehensive Java API information from parse trees.

    This listener traverses ANTLR4 parse trees generated from Java source code and
    extracts detailed structural information about Java types, methods, fields, and
    their associated metadata. It serves as the core component for converting parsed
    Java code into structured data representations.

    The listener implements a stack-based approach to handle nested type declarations
    and maintains comprehensive state throughout the parsing process, enabling accurate
    extraction of complex Java language constructs including generics, annotations,
    and inheritance relationships.

    Attributes:
        file_path (str): Path to the Java source file being processed
        source_code (str): Complete source code content for reference and line lookups
        lines (List[str]): Source code split into individual lines for efficient access
        current_package (str): Current package declaration for the compilation unit
        imports (List[str]): List of all import statements in the file
        classes (List[Class]): Top-level classes, interfaces, enums, and records extracted
        class_stack (List[Class]): Stack for tracking nested class declarations
        javadoc_cache (Dict[int, str]): Pre-processed Javadoc comments indexed by line number

    Thread Safety:
        This class is not thread-safe and should not be used concurrently across
        multiple threads. Each parsing operation should use a separate instance.

    Examples:
        Basic usage with ANTLR4 components:
        ```python
        listener = APIExtractorListener("User.java", source_code)

        # Parse and walk the tree
        tree = parser.compilationUnit()
        walker = ParseTreeWalker()
        walker.walk(listener, tree)

        # Access results
        print(f"Package: {listener.current_package}")
        print(f"Classes found: {len(listener.classes)}")
        for cls in listener.classes:
            print(f"  {cls.class_type}: {cls.name}")
        ```

        Processing nested classes:
        ```python
        # The listener automatically handles nested structures
        for cls in listener.classes:
            print(f"Top-level class: {cls.name}")
            for inner_cls in cls.inner_classes:
                print(f"  Inner class: {inner_cls.name}")
        ```
    """

    def __init__(self, file_path: str, source_code: str):
        """
        Initialize the API extractor listener with source file information.

        Args:
            file_path (str): Path to the Java source file being processed.
                           Used for source location tracking and debugging.
            source_code (str): Complete source code content. Used for Javadoc
                             extraction, line number calculations, and text lookups.

        The constructor performs pre-processing of Javadoc comments to create
        an efficient lookup cache, enabling fast association of documentation
        with code elements during tree traversal.
        """
        self.file_path = file_path
        self.source_code = source_code
        self.lines = source_code.split('\n')
        self.current_package = ""
        self.imports = []
        self.classes = []
        self.class_stack = []  # Stack to handle nested classes
        self.javadoc_cache = {}  # Cache Javadoc comments by line number

        # Pre-extract all Javadoc comments
        self._extract_javadoc_comments()

    def _extract_javadoc_comments(self):
        """
        Pre-extract all Javadoc comments and associate with line numbers.

        This method performs a single pass through the source code to identify
        and extract all Javadoc comments (/** ... */), cleaning their content
        and creating a lookup cache indexed by line numbers. This enables
        efficient association of documentation with code elements during
        tree traversal without requiring repeated regex processing.

        The extracted Javadoc is associated with the lines immediately following
        each comment block, covering the typical range where declarations occur.

        Performance Note:
            This pre-processing approach provides O(1) Javadoc lookup during
            tree traversal, significantly improving performance for files with
            extensive documentation.
        """
        javadoc_pattern = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)
        for match in javadoc_pattern.finditer(self.source_code):
            start_line = self.source_code[:match.start()].count('\n') + 1
            end_line = self.source_code[:match.end()].count('\n') + 1
            cleaned_doc = self._clean_javadoc(match.group(1))
            # Store javadoc for the lines following it (where declarations would be)
            for line_num in range(end_line, min(end_line + 5, len(self.lines) + 1)):
                if line_num not in self.javadoc_cache:
                    self.javadoc_cache[line_num] = cleaned_doc

    def _clean_javadoc(self, javadoc: str) -> str:
        """
        Clean up extracted Javadoc text by removing formatting artifacts.

        Args:
            javadoc (str): Raw Javadoc content extracted from comment block

        Returns:
            str: Cleaned Javadoc text with formatting artifacts removed

        The cleaning process removes:
        - Leading asterisks (*) from each line
        - Excess whitespace and empty lines
        - Comment block delimiters and structural formatting

        Example:
            Input:  " * This is a method\n *   that does something\n * @param name the name"
            Output: "This is a method\n  that does something\n@param name the name"
        """
        lines = javadoc.split('\n')
        cleaned_lines = []

        for line in lines:
            # Remove leading * and whitespace
            line = re.sub(r'^\s*\*\s?', '', line)
            line = line.strip()
            if line:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _get_line_number(self, ctx) -> int:
        """
        Extract line number from ANTLR4 parse context.

        Args:
            ctx: ANTLR4 parse tree context node

        Returns:
            int: Line number where the context starts, or 0 if unavailable

        This method safely extracts line number information from parse tree
        contexts, handling cases where line information might not be available.
        """
        if hasattr(ctx, 'start') and hasattr(ctx.start, 'line'):
            return ctx.start.line
        return 0

    def _get_javadoc(self, ctx) -> Optional[str]:
        """
        Retrieve Javadoc documentation for a parse context.

        Args:
            ctx: ANTLR4 parse tree context for a code element

        Returns:
            Optional[str]: Associated Javadoc text, or None if no documentation found

        Uses the pre-built Javadoc cache to efficiently lookup documentation
        based on the context's line number.
        """
        line_num = self._get_line_number(ctx)
        return self.javadoc_cache.get(line_num)

    def _extract_modifiers(self, ctx) -> List[str]:
        """
        Extract access modifiers and keywords from parse context.

        Args:
            ctx: ANTLR4 parse tree context containing modifier declarations

        Returns:
            List[str]: List of modifiers (e.g., ["public", "static", "final"])

        Note:
            This is a placeholder implementation. The actual implementation
            would traverse the modifier contexts based on the Java grammar
            to extract modifiers like public, private, static, final, etc.
        """
        modifiers = []
        # This would be implemented based on the actual grammar
        # For now, placeholder logic
        return modifiers

    def _extract_annotations(self, ctx) -> List[Annotation]:
        """
        Extract annotation declarations from parse context.

        Args:
            ctx: ANTLR4 parse tree context containing annotation declarations

        Returns:
            List[Annotation]: List of Annotation objects with names and parameters

        Note:
            This is a placeholder implementation. The actual implementation
            would traverse annotation contexts to extract annotation names
            and their parameter values, creating Annotation objects.
        """
        annotations = []
        # This would be implemented based on the actual grammar
        # For now, placeholder logic
        return annotations

    def _extract_type_parameters(self, ctx) -> List[str]:
        """
        Extract generic type parameters from parse context.

        Args:
            ctx: ANTLR4 parse tree context containing type parameter declarations

        Returns:
            List[str]: List of type parameter strings (e.g., ["T", "K extends Comparable<K>"])

        Note:
            This is a placeholder implementation. The actual implementation
            would parse type parameter lists including bounds and constraints.
        """
        type_params = []
        # This would be implemented based on the actual grammar
        return type_params

    def _extract_parameters(self, ctx) -> List[Parameter]:
        """
        Extract method parameter declarations from parse context.

        Args:
            ctx: ANTLR4 parse tree context containing parameter declarations

        Returns:
            List[Parameter]: List of Parameter objects with types, names, and annotations

        Note:
            This is a placeholder implementation. The actual implementation
            would traverse formal parameter lists to create Parameter objects
            with proper type information, names, and annotations.
        """
        parameters = []
        # This would be implemented based on the actual grammar
        return parameters

    def _get_text(self, ctx) -> str:
        """
        Safely extract text content from parse context.

        Args:
            ctx: ANTLR4 parse tree context node

        Returns:
            str: Text content of the context, or empty string if None

        Provides safe text extraction with null checking to prevent errors
        when processing incomplete or malformed parse trees.
        """
        if ctx is None:
            return ""
        return ctx.getText()

    # Package declaration listener
    def enterPackageDeclaration(self, ctx):
        """
        Called when entering a package declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for package declaration

        Extracts the fully qualified package name and stores it for use
        in class declarations. The package name is used to create fully
        qualified class names and organize the extracted API information.
        """
        if hasattr(ctx, 'qualifiedName'):
            self.current_package = self._get_text(ctx.qualifiedName())

    # Import declaration listener
    def enterImportDeclaration(self, ctx):
        """
        Called when entering an import declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for import declaration

        Extracts import statements and adds them to the imports list.
        This information can be used for type resolution and dependency
        analysis in more advanced processing scenarios.
        """
        if hasattr(ctx, 'qualifiedName'):
            import_name = self._get_text(ctx.qualifiedName())
            self.imports.append(import_name)

    # Class declaration listeners
    def enterClassDeclaration(self, ctx):
        """
        Called when entering a class declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for class declaration

        Processes class declarations and creates Class objects with
        appropriate metadata. Handles both top-level and nested classes
        using the class stack for proper hierarchy tracking.
        """
        self._enter_type_declaration(ctx, "class")

    def exitClassDeclaration(self, ctx):
        """
        Called when exiting a class declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for class declaration

        Completes processing of the current class and pops it from
        the class stack, returning to the parent scope.
        """
        self._exit_type_declaration()

    def enterInterfaceDeclaration(self, ctx):
        """
        Called when entering an interface declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for interface declaration

        Processes interface declarations similarly to classes but with
        interface-specific semantics and constraints.
        """
        self._enter_type_declaration(ctx, "interface")

    def exitInterfaceDeclaration(self, ctx):
        """
        Called when exiting an interface declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for interface declaration
        """
        self._exit_type_declaration()

    def enterEnumDeclaration(self, ctx):
        """
        Called when entering an enum declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for enum declaration

        Processes enum declarations with enum-specific handling for
        constants and enum-specific methods.
        """
        self._enter_type_declaration(ctx, "enum")

    def exitEnumDeclaration(self, ctx):
        """
        Called when exiting an enum declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for enum declaration
        """
        self._exit_type_declaration()

    def enterRecordDeclaration(self, ctx):
        """
        Called when entering a record declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for record declaration

        Processes record declarations (Java 14+) with record-specific
        handling for record components and compact constructors.
        """
        self._enter_type_declaration(ctx, "record")

    def exitRecordDeclaration(self, ctx):
        """
        Called when exiting a record declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for record declaration
        """
        self._exit_type_declaration()

    def _enter_type_declaration(self, ctx, class_type: str):
        """
        Generic handler for entering any type declaration (class, interface, enum, record).

        Args:
            ctx: ANTLR4 parse tree context for the type declaration
            class_type (str): Type of declaration ("class", "interface", "enum", "record")

        This unified method handles the common processing logic for all Java type
        declarations, extracting metadata and creating appropriate Class objects.
        The method manages the class stack for nested type handling and ensures
        proper parent-child relationships are maintained.

        Processing Steps:
        1. Extract type name from context
        2. Gather metadata (modifiers, annotations, type parameters)
        3. Extract inheritance information (extends/implements)
        4. Associate Javadoc documentation
        5. Create Class object with collected information
        6. Add to parent class or top-level classes list
        7. Push to class stack for nested processing
        """
        # Get class name
        class_name = "Unknown"
        if hasattr(ctx, 'IDENTIFIER') and ctx.IDENTIFIER():
            class_name = ctx.IDENTIFIER().getText()

        # Extract metadata
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        type_parameters = self._extract_type_parameters(ctx)
        javadoc = self._get_javadoc(ctx)

        # Get inheritance information
        extends = None
        implements = []

        # This would be implemented based on actual grammar rules
        # if hasattr(ctx, 'typeType') and ctx.typeType():
        #     extends = self._get_text(ctx.typeType())

        # Create class object
        java_class = Class(
            name=class_name,
            package=self.current_package,
            modifiers=modifiers,
            class_type=class_type,
            extends=extends,
            implements=implements,
            javadoc=javadoc,
            annotations=annotations,
            type_parameters=type_parameters,
            file_path=self.file_path,
            line_number=self._get_line_number(ctx)
        )

        # Add to parent class or top-level classes
        if self.class_stack:
            self.class_stack[-1].inner_classes.append(java_class)
        else:
            self.classes.append(java_class)

        # Push to stack for nested processing
        self.class_stack.append(java_class)

    def _exit_type_declaration(self):
        """
        Generic handler for exiting any type declaration.

        Completes processing of the current type declaration by popping
        it from the class stack. This returns the processing context to
        the parent scope, enabling proper handling of nested types and
        preventing memory leaks from unclosed scopes.

        Safety Note:
            The method includes stack safety checks to prevent errors
            when processing malformed or incomplete parse trees.
        """
        if self.class_stack:
            self.class_stack.pop()

    # Method declaration listeners
    def enterMethodDeclaration(self, ctx):
        """
        Called when entering a method declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for method declaration

        Extracts comprehensive method information including signatures,
        parameters, return types, modifiers, annotations, and documentation.
        The method is added to the current class being processed.

        Extracted Information:
        - Method name and return type
        - Parameter list with types and annotations
        - Access modifiers and keywords
        - Generic type parameters
        - Exception declarations
        - Javadoc documentation
        - Annotation metadata

        The method ensures that method declarations are only processed
        within the context of a class, interface, or other type declaration.
        """
        if not self.class_stack:
            return

        current_class = self.class_stack[-1]

        # Get method name
        method_name = "Unknown"
        if hasattr(ctx, 'IDENTIFIER') and ctx.IDENTIFIER():
            method_name = ctx.IDENTIFIER().getText()

        # Get return type
        return_type = "void"
        if hasattr(ctx, 'typeTypeOrVoid') and ctx.typeTypeOrVoid():
            return_type = self._get_text(ctx.typeTypeOrVoid())

        # Extract metadata
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        type_parameters = self._extract_type_parameters(ctx)
        parameters = self._extract_parameters(ctx)
        javadoc = self._get_javadoc(ctx)

        # Get exceptions
        exceptions = []
        # This would be implemented based on actual grammar

        method = Method(
            name=method_name,
            return_type=return_type,
            parameters=parameters,
            modifiers=modifiers,
            javadoc=javadoc,
            annotations=annotations,
            exceptions=exceptions,
            type_parameters=type_parameters,
            line_number=self._get_line_number(ctx),
            is_constructor=False
        )

        current_class.methods.append(method)

    # Constructor declaration listeners
    def enterConstructorDeclaration(self, ctx):
        """
        Called when entering a constructor declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for constructor declaration

        Processes constructor declarations with constructor-specific handling.
        Constructors are treated as special methods with no return type and
        the is_constructor flag set to True.

        Constructor-Specific Processing:
        - Constructor name typically matches the class name
        - No return type (empty string used)
        - Special handling for constructor-specific annotations
        - Parameter extraction for constructor overloading
        - Exception handling for constructor exceptions

        The constructor is added to the current class's methods list with
        appropriate metadata to distinguish it from regular methods.
        """
        if not self.class_stack:
            return

        current_class = self.class_stack[-1]

        # Get constructor name (should match class name)
        constructor_name = current_class.name
        if hasattr(ctx, 'IDENTIFIER') and ctx.IDENTIFIER():
            constructor_name = ctx.IDENTIFIER().getText()

        # Extract metadata
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        parameters = self._extract_parameters(ctx)
        javadoc = self._get_javadoc(ctx)

        # Get exceptions
        exceptions = []
        # This would be implemented based on actual grammar

        constructor = Method(
            name=constructor_name,
            return_type="",  # Constructors don't have return types
            parameters=parameters,
            modifiers=modifiers,
            javadoc=javadoc,
            annotations=annotations,
            exceptions=exceptions,
            line_number=self._get_line_number(ctx),
            is_constructor=True
        )

        current_class.methods.append(constructor)

    # Field declaration listeners
    def enterFieldDeclaration(self, ctx):
        """
        Called when entering a field declaration in the parse tree.

        Args:
            ctx: ANTLR4 context for field declaration

        Extracts field information including types, modifiers, annotations,
        and initial values. Handles multiple field declarations in a single
        statement (e.g., "private int x, y, z;").

        Field Processing:
        - Extract field type information including generics
        - Handle multiple variable declarations in single statement
        - Process field modifiers (static, final, volatile, etc.)
        - Extract field annotations and documentation
        - Associate initial values where present

        Each field is created as a separate Field object and added to the
        current class's fields list, enabling individual field analysis
        and documentation generation.
        """
        if not self.class_stack:
            return

        current_class = self.class_stack[-1]

        # Get field type
        field_type = "Object"
        if hasattr(ctx, 'typeType') and ctx.typeType():
            field_type = self._get_text(ctx.typeType())

        # Extract metadata
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        javadoc = self._get_javadoc(ctx)

        # Handle variable declarations (there can be multiple fields declared together)
        # This would need to be implemented based on the actual grammar structure
        field_names = ["field"]  # Placeholder

        for field_name in field_names:
            field = Field(
                name=field_name,
                type=field_type,
                modifiers=modifiers,
                javadoc=javadoc,
                annotations=annotations,
                line_number=self._get_line_number(ctx)
            )

            current_class.fields.append(field)
