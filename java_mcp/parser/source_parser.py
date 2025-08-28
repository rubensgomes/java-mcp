import logging
from pathlib import Path
from typing import List

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker

from java_mcp.java.types.java_class import Class
from java_mcp.parser.antlr4.JavaLexer import JavaLexer
from java_mcp.parser.antlr4.JavaParser import JavaParser

from .parser_error_listener import ParseErrorListener
from .api_extractor_listener import APIExtractorListener

# Configure module-level logging
logger = logging.getLogger(__name__)


class SourceParser:
    """Parser for extracting Java API information from source code using ANTLR4."""

    def __init__(self):
        self.error_listener = ParseErrorListener()

    def parse_file(self, file_path: Path, content: str) -> List[Class]:
        """Parse a Java source file and extract class information using ANTLR4."""
        logger.debug(f"Parsing {file_path}")

        try:
            # Create ANTLR input stream
            input_stream = InputStream(content)

            # Create lexer
            logger.debug(f"Lexing the source code for {file_path}")
            lexer = JavaLexer(input_stream)
            lexer.removeErrorListeners()
            lexer.addErrorListener(self.error_listener)

            # Create token stream
            stream = CommonTokenStream(lexer)

            # Create parser
            logger.debug(f"Parsing the token stream for {file_path}")
            parser = JavaParser(stream)
            parser.removeErrorListeners()
            parser.addErrorListener(self.error_listener)

            # Parse the compilation unit
            logger.debug(f"Generating a parser walk tree for {file_path}")
            tree = parser.compilationUnit()

            if self.error_listener.errors:
                logger.warning(f"Parse errors in {file_path}: {self.error_listener.errors}")
                self.error_listener.errors.clear()

            # Create listener and walk the parse tree
            listener = APIExtractorListener(str(file_path), content)
            walker = ParseTreeWalker()
            logger.debug(f"Walking the parse tree for {file_path}")
            walker.walk(listener, tree)

            return listener.classes

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return []
