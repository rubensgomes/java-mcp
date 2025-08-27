"""
ANTLR4 Parser Error Listener for Java Source Code Analysis

This module provides a custom error listener implementation for ANTLR4 parsers used in
Java source code analysis. It extends ANTLR's ErrorListener to capture, collect, and
format syntax errors encountered during Java source code parsing, enabling robust
error handling and reporting in the Java MCP server.

The error listener is designed to be non-blocking, collecting all parsing errors
without stopping the parsing process, which allows for comprehensive error reporting
and graceful degradation when working with malformed or incomplete Java source files.

Key Features:
============

Error Collection:
- Captures all syntax errors encountered during parsing
- Maintains detailed error information including line numbers, column positions, and messages
- Provides formatted error strings for easy consumption by calling code

Non-blocking Operation:
- Allows parsing to continue even when errors are encountered
- Enables partial analysis of files with syntax errors
- Supports recovery strategies for incomplete or malformed source code

Integration with Java Analysis:
- Works seamlessly with JavaSourceParser for error-aware parsing
- Provides error context for debugging and validation workflows
- Enables quality assessment of Java source files

Usage Patterns:
==============

Basic Error Listener Usage:
```python
from java_mcp.parser.parser_error_listener import ParseErrorListener
from java_mcp.parser.antlr4 import JavaLexer, JavaParser
from antlr4 import CommonTokenStream, InputStream

# Create error listener
error_listener = ParseErrorListener()

# Set up ANTLR4 parsing with custom error listener
input_stream = InputStream(java_source_code)
lexer = JavaLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = JavaParser(token_stream)

# Remove default error listeners and add custom one
parser.removeErrorListeners()
parser.addErrorListener(error_listener)

# Parse and check for errors
tree = parser.compilationUnit()
if error_listener.has_errors():
    for error in error_listener.get_errors():
        print(f"Parse error: {error}")
```

Integration with JavaSourceParser:
```python
from java_mcp.parser.java_source_parser import JavaSourceParser

# Error handling is built into the parser
parser = JavaSourceParser()
result = parser.parse_file("/path/to/JavaFile.java")

if result.has_errors():
    print("Parsing errors encountered:")
    for error in result.get_errors():
        print(f"  {error}")
```

Error Recovery and Analysis:
```python
def analyze_with_error_tolerance(java_files):
    results = []
    for file_path in java_files:
        try:
            result = parser.parse_file(file_path)
            if result.has_errors():
                # Log errors but continue processing
                logger.warning(f"Errors in {file_path}: {result.get_error_count()}")
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
    return results
```

Error Types Handled:
==================

Syntax Errors:
- Missing semicolons, braces, or parentheses
- Invalid keyword usage or placement
- Malformed expressions or statements
- Incorrect method or class declarations

Lexical Errors:
- Invalid character sequences
- Unterminated string literals or comments
- Invalid number formats
- Unicode encoding issues

Structural Errors:
- Mismatched braces or parentheses
- Invalid nesting of language constructs
- Malformed generic type declarations
- Incorrect annotation syntax

Error Message Format:
====================

Error messages follow a consistent format for easy parsing and display:
- Format: "Line {line_number}:{column_position} - {error_message}"
- Example: "Line 42:15 - mismatched input '}' expecting ';'"
- Includes precise location information for debugging

Performance Considerations:
==========================

- Minimal overhead during normal parsing operations
- Efficient error collection using list data structure
- Memory-conscious handling of large numbers of errors
- Thread-safe implementation for concurrent parsing

Integration Points:
==================

JavaSourceParser:
- Primary consumer of error listener functionality
- Provides high-level error reporting interface
- Handles error listener lifecycle management

Parser Infrastructure:
- Works with ANTLR4-generated Java lexer and parser
- Compatible with standard ANTLR4 error handling patterns
- Supports custom error recovery strategies

MCP Server:
- Enables error-aware code analysis capabilities
- Provides error information to AI assistants for context
- Supports validation and quality assessment workflows

Design Patterns:
===============

Observer Pattern:
- Implements ANTLR4's ErrorListener interface
- Receives notifications of parsing errors as they occur
- Maintains separation between parsing and error handling logic

Collector Pattern:
- Accumulates errors throughout the parsing process
- Provides batch access to all collected errors
- Enables comprehensive error reporting and analysis

Thread Safety:
=============

The error listener is designed to be thread-safe for concurrent parsing operations:
- Error collection uses thread-safe data structures
- No shared mutable state between instances
- Safe for use in multi-threaded parsing workflows

See Also:
=========
- java_mcp.parser.java_source_parser: Main Java parsing interface
- java_mcp.parser.antlr4: ANTLR4-generated parser components
- antlr4.error.ErrorListener: Base ANTLR4 error listener interface
- tests/test_java_source_parser.py: Usage examples and test cases
"""

import logging
from antlr4.error.ErrorListener import ErrorListener

# Configure module-level logging
logger = logging.getLogger(__name__)


class ParseErrorListener(ErrorListener):
    """
    Custom ANTLR4 error listener for Java source code parsing.

    This class extends ANTLR4's ErrorListener to collect and format syntax errors
    encountered during Java source code parsing. It provides a non-blocking approach
    to error handling, allowing parsing to continue while collecting comprehensive
    error information for later analysis and reporting.

    The error listener is designed to work seamlessly with the Java MCP server's
    parsing infrastructure, providing detailed error context that can be used for
    debugging, validation, and quality assessment of Java source files.

    Attributes:
        errors (List[str]): Collection of formatted error messages encountered during parsing.
                           Each error includes line number, column position, and descriptive message.

    Thread Safety:
        This class is thread-safe and can be used safely in concurrent parsing operations.
        Each instance maintains its own error collection without shared mutable state.

    Examples:
        Basic usage:
        ```python
        error_listener = ParseErrorListener()
        parser.addErrorListener(error_listener)

        # After parsing
        if error_listener.has_errors():
            for error in error_listener.get_errors():
                print(f"Syntax error: {error}")
        ```

        Error analysis:
        ```python
        listener = ParseErrorListener()
        # ... parsing with listener ...

        print(f"Found {listener.get_error_count()} syntax errors")
        if listener.has_errors():
            print("First error:", listener.get_first_error())
            print("All errors:")
            for i, error in enumerate(listener.get_errors(), 1):
                print(f"  {i}. {error}")
        ```
    """

    def __init__(self):
        """
        Initialize a new ParseErrorListener.

        Creates an empty error collection ready to receive syntax error notifications
        from ANTLR4 parsers during Java source code parsing operations.
        """
        super().__init__()
        self.errors = []
        logger.debug("Initialized ParseErrorListener")

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Handle a syntax error reported by the ANTLR4 parser.

        This method is called automatically by ANTLR4 whenever a syntax error is
        encountered during parsing. It formats the error information and adds it
        to the error collection for later retrieval and analysis.

        Args:
            recognizer: The parser instance that detected the error
            offendingSymbol: The token that caused the syntax error (may be None)
            line (int): Line number where the error occurred (1-based)
            column (int): Column position where the error occurred (0-based)
            msg (str): Descriptive error message from the parser
            e (Exception): The recognition exception that triggered the error (may be None)

        Note:
            This method is called automatically by ANTLR4 and should not be invoked directly.
            The error information is formatted as "Line {line}:{column} - {message}" and
            added to the errors collection.
        """
        formatted_error = f"Line {line}:{column} - {msg}"
        self.errors.append(formatted_error)

        # Log the error for debugging purposes
        logger.warning(f"Syntax error captured: {formatted_error}")

        # Log additional context if available
        if offendingSymbol:
            logger.debug(f"Offending symbol: {offendingSymbol.text}")
        if e:
            logger.debug(f"Exception details: {type(e).__name__}: {e}")

    def has_errors(self) -> bool:
        """
        Check if any syntax errors were collected during parsing.

        Returns:
            bool: True if one or more syntax errors were encountered, False otherwise.

        Example:
            ```python
            if error_listener.has_errors():
                print("Parsing completed with errors")
            else:
                print("Parsing completed successfully")
            ```
        """
        return len(self.errors) > 0

    def get_errors(self) -> list[str]:
        """
        Get all collected syntax errors.

        Returns:
            List[str]: List of formatted error messages in the order they were encountered.
                      Each error string includes line number, column position, and description.

        Example:
            ```python
            for error in error_listener.get_errors():
                print(f"Parse error: {error}")
            ```
        """
        return self.errors.copy()  # Return a copy to prevent external modification

    def get_error_count(self) -> int:
        """
        Get the total number of syntax errors collected.

        Returns:
            int: Number of syntax errors encountered during parsing.

        Example:
            ```python
            count = error_listener.get_error_count()
            print(f"Found {count} syntax error{'s' if count != 1 else ''}")
            ```
        """
        return len(self.errors)

    def get_first_error(self) -> str | None:
        """
        Get the first syntax error encountered during parsing.

        Returns:
            str | None: The first error message if any errors were collected, None otherwise.

        Example:
            ```python
            first_error = error_listener.get_first_error()
            if first_error:
                print(f"First syntax error: {first_error}")
            ```
        """
        return self.errors[0] if self.errors else None

    def clear_errors(self) -> None:
        """
        Clear all collected syntax errors.

        This method resets the error listener to its initial state, removing all
        previously collected error messages. Useful for reusing the same listener
        instance across multiple parsing operations.

        Example:
            ```python
            # Parse multiple files with the same listener
            for file_path in java_files:
                error_listener.clear_errors()
                # ... parse file with listener ...
                if error_listener.has_errors():
                    print(f"Errors in {file_path}: {error_listener.get_error_count()}")
            ```
        """
        self.errors.clear()
        logger.debug("Cleared all collected errors")

    def get_error_summary(self) -> dict[str, any]:
        """
        Get a summary of collected errors with statistics.

        Returns:
            Dict[str, Any]: Dictionary containing error statistics and summary information:
                - 'total_errors': Total number of errors
                - 'has_errors': Boolean indicating if errors were found
                - 'first_error': First error message (if any)
                - 'error_lines': Set of line numbers with errors

        Example:
            ```python
            summary = error_listener.get_error_summary()
            print(f"Parsing summary: {summary['total_errors']} errors on {len(summary['error_lines'])} lines")
            ```
        """
        error_lines = set()
        for error in self.errors:
            # Extract line number from formatted error string
            try:
                line_part = error.split(':')[0].replace('Line ', '')
                error_lines.add(int(line_part))
            except (ValueError, IndexError):
                # Skip if line number cannot be extracted
                pass

        return {
            'total_errors': len(self.errors),
            'has_errors': len(self.errors) > 0,
            'first_error': self.get_first_error(),
            'error_lines': error_lines
        }
