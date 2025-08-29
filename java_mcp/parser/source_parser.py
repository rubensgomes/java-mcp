import logging
from pathlib import Path
from typing import List

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker

from java_mcp.types import Class
from java_mcp.parser.antlr4.JavaLexer import JavaLexer
from java_mcp.parser.antlr4.JavaParser import JavaParser

from .parser_error_listener import ParseErrorListener
from .api_extractor_listener import APIExtractorListener

# Configure module-level logging
logger = logging.getLogger(__name__)


class SourceParser:
    """
    ANTLR4-based Java source code parser for API extraction.

    This parser uses the ANTLR4 Java grammar to parse Java source files and
    extract comprehensive API information. It employs the listener pattern
    for efficient parse tree traversal and robust error handling.

    The parser supports all Java language features from Java 8 through Java 24,
    including modern constructs like records, sealed classes, pattern matching,
    and text blocks.

    Attributes:
        error_listener (JavaParseErrorListener): Custom error listener that captures
                                               parse errors instead of printing to stderr

    Examples:
        parser = SourceParser()
        classes = parser.parse_file(Path("User.java"), java_source_code)

        for cls in classes:
            print(f"Found class: {cls.name} in package {cls.package}")
            for method in cls.methods:
                print(f"  Method: {method.name}({method.parameters})")
    """

    def __init__(self):
        self.error_listener = ParseErrorListener()

    def parse_file(self, file_path: Path, content: str) -> List[Class]:
        """
        Parse a Java source file and extract comprehensive API information.

        Uses ANTLR4 lexer and parser to build a parse tree, then walks the tree
        with a custom listener to extract classes, methods, fields, and all
        associated metadata including annotations, modifiers, and documentation.

        Args:
            file_path (Path): Path to the Java source file being parsed
            content (str): Complete source code content of the Java file

        Returns:
            List[Class]: List of Class objects representing all top-level and
                        nested classes, interfaces, enums, records, and annotations
                        found in the source file

        Raises:
            Exception: If ANTLR4 parsing fails due to invalid grammar or
                      other critical errors

        Examples:
            # Parse a single Java file
            with open("User.java", "r") as f:
                content = f.read()
            classes = parser.parse_file(Path("User.java"), content)

            # Handle parse errors
            if parser.error_listener.errors:
                for error in parser.error_listener.errors:
                    logger.warning(f"Parse error: {error}")
        """
        try:
            # Create ANTLR input stream
            input_stream = InputStream(content)
            lexer = JavaLexer(input_stream)
            lexer.removeErrorListeners()
            lexer.addErrorListener(self.error_listener)

            # Create token stream
            stream = CommonTokenStream(lexer)

            # Create parser
            parser = JavaParser(stream)
            parser.removeErrorListeners()
            parser.addErrorListener(self.error_listener)
            parser.removeErrorListeners()
            parser.addErrorListener(self.error_listener)

            # Parse the compilation unit
            tree = parser.compilationUnit()

            if self.error_listener.errors:
                logger.warning(f"Parse errors in {file_path}: {self.error_listener.errors}")
                self.error_listener.errors.clear()

            # Create listener and walk the parse tree
            listener = APIExtractorListener(str(file_path), content)
            walker = ParseTreeWalker()
            walker.walk(listener, tree)

            return listener.classes

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return []
