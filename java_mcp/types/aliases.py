"""
Type Aliases for Java Code Analysis

This module provides convenient type aliases and union types for working with
Java code analysis types in the MCP server. These aliases improve code readability,
enable better type checking, and provide flexible type constraints for functions
that work with collections of Java code elements.

The aliases are designed to make the codebase more maintainable by providing
semantic meaning to common type patterns and enabling polymorphic operations
across different Java code element types.

Type Categories:
===============

Collection Aliases:
- Provide semantic meaning for lists of specific Java elements
- Enable clear function signatures and return types
- Improve IDE autocomplete and type checking

Union Types:
- Enable polymorphic functions that work with multiple element types
- Provide flexibility for operations that apply to different Java constructs
- Support visitor patterns and generic processing algorithms

Usage Examples:
==============

```python
# Function that processes multiple classes
def analyze_classes(classes: JavaClasses) -> AnalysisResult:
    for java_class in classes:
        process_class(java_class)

# Function that works with any Java element
def extract_annotations(element: JavaElement) -> JavaAnnotations:
    if hasattr(element, 'annotations'):
        return element.annotations
    return []

# Function that processes method collections
def find_public_methods(methods: JavaMethods) -> JavaMethods:
    return [m for m in methods if 'public' in m.modifiers]
```

Design Principles:
=================

1. **Semantic Clarity**: Aliases provide clear intent for what types of data
   functions expect and return.

2. **Type Safety**: Enable static type checking to catch type-related errors
   at development time.

3. **Flexibility**: Union types allow functions to work with multiple related
   types without sacrificing type safety.

4. **Consistency**: Standardized naming patterns across the codebase for
   similar type concepts.

5. **Extensibility**: Easy to add new aliases as the type system evolves.
"""

from typing import List, Union, Callable, Optional, Dict, Any, Tuple

# Import all Java code element types
from .field import Field
from .method import Method
from .parameter import Parameter
from .annotation import Annotation
from .java_class import Class

# Collection Type Aliases
# =======================
# These aliases provide semantic meaning for collections of specific Java elements,
# making function signatures more readable and self-documenting.

JavaClasses = List[Class]
"""
Collection of Java classes, interfaces, enums, records, or annotation types.

Used for representing:
- All classes found in a package or project
- Results from class discovery operations
- Input to batch processing operations on multiple classes
- Class hierarchy analysis results

Example:
    def find_classes_with_annotation(classes: JavaClasses, 
                                   annotation_name: str) -> JavaClasses:
        return [cls for cls in classes 
                if any(ann.name == annotation_name for ann in cls.annotations)]
"""

JavaMethods = List[Method]
"""
Collection of Java methods including constructors and regular methods.

Used for representing:
- All methods in a class or interface
- Filtered method collections (e.g., public methods, static methods)
- Method analysis results
- Method signature comparisons

Example:
    def get_overloaded_methods(methods: JavaMethods) -> Dict[str, JavaMethods]:
        grouped = {}
        for method in methods:
            grouped.setdefault(method.name, []).append(method)
        return {name: methods for name, methods in grouped.items() if len(methods) > 1}
"""

JavaFields = List[Field]
"""
Collection of Java fields (instance variables, class variables, constants).

Used for representing:
- All fields in a class
- Filtered field collections (e.g., static fields, final fields)
- Field analysis results
- Data structure analysis

Example:
    def find_uninitialized_fields(fields: JavaFields) -> JavaFields:
        return [field for field in fields 
                if field.initial_value is None and 'final' in field.modifiers]
"""

JavaParameters = List[Parameter]
"""
Collection of Java method parameters.

Used for representing:
- Method parameter lists
- Constructor parameter lists
- Parameter analysis across multiple methods
- Method signature comparisons

Example:
    def count_annotated_parameters(parameters: JavaParameters) -> int:
        return sum(1 for param in parameters if param.annotations)
"""

JavaAnnotations = List[Annotation]
"""
Collection of Java annotations applied to code elements.

Used for representing:
- Annotations on classes, methods, fields, or parameters
- Annotation analysis results
- Filtered annotation collections
- Metadata extraction results

Example:
    def group_by_annotation_type(annotations: JavaAnnotations) -> Dict[str, JavaAnnotations]:
        grouped = {}
        for annotation in annotations:
            grouped.setdefault(annotation.name, []).append(annotation)
        return grouped
"""

# Union Type Aliases
# ==================
# These union types enable polymorphic operations across different Java element types,
# supporting flexible processing patterns and visitor-style operations.

JavaElement = Union[Class, Method, Field, Parameter]
"""
Union type representing any Java code element that can have annotations and documentation.

This type enables writing generic functions that can process any type of Java
code element, particularly useful for:
- Annotation extraction and analysis
- Documentation processing
- Generic metadata operations
- Visitor pattern implementations

Example:
    def extract_javadoc(element: JavaElement) -> Optional[str]:
        return getattr(element, 'javadoc', None)
    
    def has_annotation(element: JavaElement, annotation_name: str) -> bool:
        annotations = getattr(element, 'annotations', [])
        return any(ann.name == annotation_name for ann in annotations)
"""

JavaType = Union[str, Class]
"""
Union type representing either a type name string or a resolved Class object.

This flexible type is used in contexts where type information might be:
- A simple type name string (e.g., "String", "int", "List<User>")
- A fully resolved Class object with complete metadata

Commonly used for:
- Type resolution during parsing
- Generic type parameter handling
- Type system analysis
- Cross-reference resolution

Example:
    def resolve_type(type_ref: JavaType) -> Class:
        if isinstance(type_ref, str):
            return lookup_class_by_name(type_ref)
        return type_ref
    
    def get_type_name(type_ref: JavaType) -> str:
        if isinstance(type_ref, str):
            return type_ref
        return type_ref.get_full_name()
"""

JavaCodeElement = Union[Class, Method, Field]
"""
Union type for Java elements that have source code locations and can contain other elements.

This type represents the major structural elements of Java code that:
- Have definite source locations (line numbers, files)
- Can contain documentation
- Represent significant architectural components

Used for:
- Source code navigation
- Architecture analysis
- Code organization operations
- Documentation generation

Example:
    def get_source_location(element: JavaCodeElement) -> Tuple[str, int]:
        file_path = getattr(element, 'file_path', '')
        line_number = getattr(element, 'line_number', 0)
        return (file_path, line_number)
"""

# Functional Type Aliases
# =======================
# These aliases support functional programming patterns and callback-style operations.

JavaElementPredicate = Callable[[JavaElement], bool]
"""
Function type for predicates that test Java elements.

Used for filtering operations, validation checks, and conditional processing.

Example:
    is_public: JavaElementPredicate = lambda elem: 'public' in getattr(elem, 'modifiers', [])
    has_javadoc: JavaElementPredicate = lambda elem: getattr(elem, 'javadoc') is not None
"""

JavaElementTransformer = Callable[[JavaElement], Any]
"""
Function type for transforming Java elements into other types.

Used for mapping operations, data extraction, and format conversion.

Example:
    extract_name: JavaElementTransformer = lambda elem: elem.name
    get_annotation_count: JavaElementTransformer = lambda elem: len(getattr(elem, 'annotations', []))
"""

JavaElementVisitor = Callable[[JavaElement], None]
"""
Function type for visiting Java elements without returning values.

Used for side-effect operations like logging, validation, or accumulation.

Example:
    def log_element(element: JavaElement) -> None:
        print(f"Processing {type(element).__name__}: {element.name}")
    
    collect_names: List[str] = []
    collect_name: JavaElementVisitor = lambda elem: collect_names.append(elem.name)
"""

# Export all aliases for convenient importing
__all__ = [
    # Collection aliases
    'JavaClasses',
    'JavaMethods',
    'JavaFields',
    'JavaParameters',
    'JavaAnnotations',

    # Union type aliases
    'JavaElement',
    'JavaType',
    'JavaCodeElement',

    # Functional aliases
    'JavaElementPredicate',
    'JavaElementTransformer',
    'JavaElementVisitor',
]
