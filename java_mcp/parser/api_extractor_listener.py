import re
from typing import List, Optional

from java_mcp.parser.antlr4.JavaParserListener import JavaParserListener
from java_mcp.types import Class
from java_mcp.types import Field
from java_mcp.types import Method
from java_mcp.types.annotation import Annotation
from java_mcp.types.parameter import Parameter


class APIExtractorListener(JavaParserListener):
    """ANTLR4 Listener for extracting Java API information from parse trees."""

    def __init__(self, file_path: str, source_code: str):
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
        """Pre-extract all Javadoc comments and associate with line numbers."""
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
        """Clean up extracted Javadoc text."""
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
        """Get line number from parse context."""
        if hasattr(ctx, 'start') and hasattr(ctx.start, 'line'):
            return ctx.start.line
        return 0

    def _get_javadoc(self, ctx) -> Optional[str]:
        """Get Javadoc for a context based on its line number."""
        line_num = self._get_line_number(ctx)
        return self.javadoc_cache.get(line_num)

    def _extract_modifiers(self, ctx) -> List[str]:
        """Extract modifiers from context based on Java24 grammar."""
        modifiers = []

        # Check for classOrInterfaceModifier in class/interface declarations
        if hasattr(ctx, 'classOrInterfaceModifier'):
            for mod_ctx in ctx.classOrInterfaceModifier():
                if mod_ctx.annotation():
                    continue  # Skip annotations, handle separately
                elif mod_ctx.PUBLIC():
                    modifiers.append('public')
                elif mod_ctx.PROTECTED():
                    modifiers.append('protected')
                elif mod_ctx.PRIVATE():
                    modifiers.append('private')
                elif mod_ctx.STATIC():
                    modifiers.append('static')
                elif mod_ctx.ABSTRACT():
                    modifiers.append('abstract')
                elif mod_ctx.FINAL():
                    modifiers.append('final')
                elif mod_ctx.STRICTFP():
                    modifiers.append('strictfp')
                elif mod_ctx.SEALED():
                    modifiers.append('sealed')
                elif mod_ctx.NON_SEALED():
                    modifiers.append('non-sealed')

        # Check for modifier in method/field declarations
        if hasattr(ctx, 'modifier'):
            for mod_ctx in ctx.modifier():
                if mod_ctx.classOrInterfaceModifier():
                    # Recursively extract from nested classOrInterfaceModifier
                    nested_mods = self._extract_modifiers(mod_ctx.classOrInterfaceModifier())
                    modifiers.extend(nested_mods)
                elif mod_ctx.NATIVE():
                    modifiers.append('native')
                elif mod_ctx.SYNCHRONIZED():
                    modifiers.append('synchronized')
                elif mod_ctx.TRANSIENT():
                    modifiers.append('transient')
                elif mod_ctx.VOLATILE():
                    modifiers.append('volatile')

        # Check for variableModifier in parameters/local variables
        if hasattr(ctx, 'variableModifier'):
            for mod_ctx in ctx.variableModifier():
                if mod_ctx.FINAL():
                    modifiers.append('final')
                # Note: annotations in variableModifier are handled separately

        return modifiers

    def _extract_annotations(self, ctx) -> List[Annotation]:
        """Extract annotations from context based on Java24 grammar."""
        annotations = []

        # Direct annotations on the context
        if hasattr(ctx, 'annotation'):
            for ann_ctx in ctx.annotation():
                annotation = self._parse_single_annotation(ann_ctx)
                if annotation:
                    annotations.append(annotation)

        # Annotations within classOrInterfaceModifier
        if hasattr(ctx, 'classOrInterfaceModifier'):
            for mod_ctx in ctx.classOrInterfaceModifier():
                if mod_ctx.annotation():
                    annotation = self._parse_single_annotation(mod_ctx.annotation())
                    if annotation:
                        annotations.append(annotation)

        # Annotations within modifier
        if hasattr(ctx, 'modifier'):
            for mod_ctx in ctx.modifier():
                if mod_ctx.classOrInterfaceModifier() and mod_ctx.classOrInterfaceModifier().annotation():
                    annotation = self._parse_single_annotation(mod_ctx.classOrInterfaceModifier().annotation())
                    if annotation:
                        annotations.append(annotation)

        # Annotations within variableModifier (for parameters/fields)
        if hasattr(ctx, 'variableModifier'):
            for mod_ctx in ctx.variableModifier():
                if mod_ctx.annotation():
                    annotation = self._parse_single_annotation(mod_ctx.annotation())
                    if annotation:
                        annotations.append(annotation)

        return annotations

    def _parse_single_annotation(self, ann_ctx) -> Optional[Annotation]:
        """Parse a single annotation context into an Annotation object."""
        if not ann_ctx:
            return None

        # Get annotation name from qualifiedName or IDENTIFIER
        ann_name = ""
        if hasattr(ann_ctx, 'qualifiedName') and ann_ctx.qualifiedName():
            ann_name = self._get_text(ann_ctx.qualifiedName())
        elif hasattr(ann_ctx, 'IDENTIFIER') and ann_ctx.IDENTIFIER():
            ann_name = ann_ctx.IDENTIFIER().getText()

        if not ann_name:
            return None

        parameters = {}

        # Check for annotation parameters
        if hasattr(ann_ctx, 'elementValuePairs') and ann_ctx.elementValuePairs():
            # Multiple name-value pairs: @Annotation(name1=value1, name2=value2)
            for pair_ctx in ann_ctx.elementValuePairs().elementValuePair():
                if hasattr(pair_ctx, 'IDENTIFIER') and hasattr(pair_ctx, 'elementValue'):
                    param_name = pair_ctx.IDENTIFIER().getText()
                    param_value = self._extract_element_value(pair_ctx.elementValue())
                    parameters[param_name] = param_value

        elif hasattr(ann_ctx, 'elementValue') and ann_ctx.elementValue():
            # Single value: @Annotation(value) or @Annotation("string")
            param_value = self._extract_element_value(ann_ctx.elementValue())
            parameters['value'] = param_value

        return Annotation(name=ann_name, parameters=parameters)

    def _extract_element_value(self, elem_ctx) -> str:
        """Extract the value from an elementValue context."""
        if not elem_ctx:
            return ""

        # Conditional expression (most common case)
        if hasattr(elem_ctx, 'conditionalExpression') and elem_ctx.conditionalExpression():
            return self._get_text(elem_ctx.conditionalExpression())

        # Annotation (nested annotation)
        elif hasattr(elem_ctx, 'annotation') and elem_ctx.annotation():
            nested_ann = self._parse_single_annotation(elem_ctx.annotation())
            return f"@{nested_ann.name}" if nested_ann else ""

        # Element value array: {value1, value2, ...}
        elif hasattr(elem_ctx, 'elementValueArrayInitializer') and elem_ctx.elementValueArrayInitializer():
            array_values = []
            array_init = elem_ctx.elementValueArrayInitializer()
            if hasattr(array_init, 'elementValueList') and array_init.elementValueList():
                for elem_val in array_init.elementValueList().elementValue():
                    array_values.append(self._extract_element_value(elem_val))
            return '{' + ', '.join(array_values) + '}'

        # Fallback: get raw text
        return self._get_text(elem_ctx)

    def _extract_type_parameters(self, ctx) -> List[str]:
        """Extract generic type parameters based on Java24 grammar."""
        type_params = []

        if hasattr(ctx, 'typeParameters') and ctx.typeParameters():
            type_params_ctx = ctx.typeParameters()
            if hasattr(type_params_ctx, 'typeParameter'):
                for param_ctx in type_params_ctx.typeParameter():
                    if hasattr(param_ctx, 'IDENTIFIER') and param_ctx.IDENTIFIER():
                        param_name = param_ctx.IDENTIFIER().getText()

                        # Check for bounds (extends clause)
                        if hasattr(param_ctx, 'typeBound') and param_ctx.typeBound():
                            bounds = []
                            bound_ctx = param_ctx.typeBound()
                            if hasattr(bound_ctx, 'typeType'):
                                for type_ctx in bound_ctx.typeType():
                                    bounds.append(self._get_text(type_ctx))
                            if bounds:
                                param_name += f" extends {' & '.join(bounds)}"

                        type_params.append(param_name)

        return type_params

    def _extract_parameters(self, ctx) -> List[Parameter]:
        """Extract method parameters based on Java24 grammar."""
        parameters = []

        if hasattr(ctx, 'formalParameters') and ctx.formalParameters():
            formal_params = ctx.formalParameters()

            if hasattr(formal_params, 'formalParameterList') and formal_params.formalParameterList():
                param_list = formal_params.formalParameterList()

                # Regular parameters
                if hasattr(param_list, 'formalParameter'):
                    for param_ctx in param_list.formalParameter():
                        param = self._extract_single_parameter(param_ctx, is_varargs=False)
                        if param:
                            parameters.append(param)

                # Last parameter (might be varargs)
                if hasattr(param_list, 'lastFormalParameter') and param_list.lastFormalParameter():
                    last_param = param_list.lastFormalParameter()
                    param = self._extract_single_parameter(last_param, is_varargs=True)
                    if param:
                        parameters.append(param)

        return parameters

    def _extract_single_parameter(self, param_ctx, is_varargs: bool = False) -> Optional[Parameter]:
        """Extract a single parameter from formalParameter or lastFormalParameter context."""
        if not param_ctx:
            return None

        # Extract parameter modifiers and annotations
        modifiers = self._extract_modifiers(param_ctx)
        annotations = self._extract_annotations(param_ctx)

        # Get parameter type
        param_type = ""
        if hasattr(param_ctx, 'typeType') and param_ctx.typeType():
            param_type = self._get_text(param_ctx.typeType())

            # Handle varargs (...)
            if is_varargs and hasattr(param_ctx, 'ELLIPSIS') and param_ctx.ELLIPSIS():
                param_type += "..."
                is_varargs = True
            else:
                is_varargs = False

        # Get parameter name
        param_name = ""
        if hasattr(param_ctx, 'variableDeclaratorId') and param_ctx.variableDeclaratorId():
            var_id = param_ctx.variableDeclaratorId()
            if hasattr(var_id, 'IDENTIFIER') and var_id.IDENTIFIER():
                param_name = var_id.IDENTIFIER().getText()

        if not param_name or not param_type:
            return None

        return Parameter(
            name=param_name,
            type=param_type,
            annotations=annotations,
            is_varargs=is_varargs
        )

    def _extract_implements_list(self, ctx) -> List[str]:
        """Extract implements clause from class/interface declaration."""
        implements = []

        if hasattr(ctx, 'IMPLEMENTS') and hasattr(ctx, 'typeList') and ctx.typeList():
            type_list = ctx.typeList()
            if hasattr(type_list, 'typeType'):
                for type_ctx in type_list.typeType():
                    implements.append(self._get_text(type_ctx))

        return implements

    def _extract_extends_type(self, ctx) -> Optional[str]:
        """Extract extends clause from class declaration."""
        if hasattr(ctx, 'EXTENDS') and hasattr(ctx, 'typeType') and ctx.typeType():
            return self._get_text(ctx.typeType())
        return None

    def _extract_field_names_and_initializers(self, ctx) -> List[tuple]:
        """Extract field names and their initializers from variableDeclarators."""
        fields = []

        if hasattr(ctx, 'variableDeclarators') and ctx.variableDeclarators():
            var_declarators = ctx.variableDeclarators()
            if hasattr(var_declarators, 'variableDeclarator'):
                for var_decl in var_declarators.variableDeclarator():
                    field_name = ""
                    initial_value = None

                    # Get field name
                    if hasattr(var_decl, 'variableDeclaratorId') and var_decl.variableDeclaratorId():
                        var_id = var_decl.variableDeclaratorId()
                        if hasattr(var_id, 'IDENTIFIER') and var_id.IDENTIFIER():
                            field_name = var_id.IDENTIFIER().getText()

                    # Get initial value if present
                    if hasattr(var_decl, 'variableInitializer') and var_decl.variableInitializer():
                        initial_value = self._get_text(var_decl.variableInitializer())

                    if field_name:
                        fields.append((field_name, initial_value))

        return fields

    def _extract_exception_list(self, ctx) -> List[str]:
        """Extract throws clause from method/constructor declaration."""
        exceptions = []

        if hasattr(ctx, 'THROWS') and hasattr(ctx, 'qualifiedNameList') and ctx.qualifiedNameList():
            qual_name_list = ctx.qualifiedNameList()
            if hasattr(qual_name_list, 'qualifiedName'):
                for qual_name in qual_name_list.qualifiedName():
                    exceptions.append(self._get_text(qual_name))

        return exceptions

    def _get_text(self, ctx) -> str:
        """Get text from context."""
        if ctx is None:
            return ""
        return ctx.getText()

    # Package declaration listener
    def enterPackageDeclaration(self, ctx):
        """Called when entering a package declaration."""
        if hasattr(ctx, 'qualifiedName'):
            self.current_package = self._get_text(ctx.qualifiedName())

    # Import declaration listener
    def enterImportDeclaration(self, ctx):
        """Called when entering an import declaration."""
        if hasattr(ctx, 'qualifiedName'):
            import_name = self._get_text(ctx.qualifiedName())
            self.imports.append(import_name)

    # Class declaration listeners
    def enterClassDeclaration(self, ctx):
        """Called when entering a class declaration."""
        self._enter_type_declaration(ctx, "class")

    def exitClassDeclaration(self, ctx):
        """Called when exiting a class declaration."""
        self._exit_type_declaration()

    def enterInterfaceDeclaration(self, ctx):
        """Called when entering an interface declaration."""
        self._enter_type_declaration(ctx, "interface")

    def exitInterfaceDeclaration(self, ctx):
        """Called when exiting an interface declaration."""
        self._exit_type_declaration()

    def enterEnumDeclaration(self, ctx):
        """Called when entering an enum declaration."""
        self._enter_type_declaration(ctx, "enum")

    def exitEnumDeclaration(self, ctx):
        """Called when exiting an enum declaration."""
        self._exit_type_declaration()

    def enterRecordDeclaration(self, ctx):
        """Called when entering a record declaration (Java 14+)."""
        self._enter_type_declaration(ctx, "record")

    def exitRecordDeclaration(self, ctx):
        """Called when exiting a record declaration."""
        self._exit_type_declaration()

    def _enter_type_declaration(self, ctx, class_type: str):
        """Generic handler for entering any type declaration."""
        # Get class name
        class_name = "Unknown"
        if hasattr(ctx, 'IDENTIFIER') and ctx.IDENTIFIER():
            class_name = ctx.IDENTIFIER().getText()

        # Extract metadata using completed methods
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        type_parameters = self._extract_type_parameters(ctx)
        javadoc = self._get_javadoc(ctx)

        # Get inheritance information using completed methods
        extends = self._extract_extends_type(ctx)
        implements = self._extract_implements_list(ctx)

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

    # Method declaration listeners
    def enterMethodDeclaration(self, ctx):
        """Called when entering a method declaration."""
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

        # Extract metadata using completed methods
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        type_parameters = self._extract_type_parameters(ctx)
        parameters = self._extract_parameters(ctx)
        exceptions = self._extract_exception_list(ctx)
        javadoc = self._get_javadoc(ctx)

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
        """Called when entering a constructor declaration."""
        if not self.class_stack:
            return

        current_class = self.class_stack[-1]

        # Get constructor name (should match class name)
        constructor_name = current_class.name
        if hasattr(ctx, 'IDENTIFIER') and ctx.IDENTIFIER():
            constructor_name = ctx.IDENTIFIER().getText()

        # Extract metadata using completed methods
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        parameters = self._extract_parameters(ctx)
        exceptions = self._extract_exception_list(ctx)
        javadoc = self._get_javadoc(ctx)

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
        """Called when entering a field declaration."""
        if not self.class_stack:
            return

        current_class = self.class_stack[-1]

        # Get field type
        field_type = "Object"
        if hasattr(ctx, 'typeType') and ctx.typeType():
            field_type = self._get_text(ctx.typeType())

        # Extract metadata using completed methods
        modifiers = self._extract_modifiers(ctx)
        annotations = self._extract_annotations(ctx)
        javadoc = self._get_javadoc(ctx)

        # Extract field names and initializers using completed method
        field_info_list = self._extract_field_names_and_initializers(ctx)

        for field_name, initial_value in field_info_list:
            field = Field(
                name=field_name,
                type=field_type,
                modifiers=modifiers,
                javadoc=javadoc,
                annotations=annotations,
                initial_value=initial_value,
                line_number=self._get_line_number(ctx)
            )

            current_class.fields.append(field)
