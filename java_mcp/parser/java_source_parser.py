"""
Java Source Code Parser for MCP (Model Context Protocol) Server.

This module provides the main parsing functionality for analyzing Java source code files
and extracting structural information including classes, methods, fields, documentation,
and metadata. The parser uses ANTLR4-generated lexer and parser components to build
a parse tree, then walks the tree to extract meaningful structural data.

The JavaSourceParser serves as the primary entry point for Java code analysis in the
MCP server, coordinating between the ANTLR4 parsing infrastructure, Javadoc extraction,
and structural analysis to produce comprehensive code representations for AI assistants.

Key Features:
- Parse individual Java files or entire directory trees
- Extract complete class hierarchy and structure information
- Associate Javadoc comments with corresponding code elements
- Handle all Java constructs: classes, interfaces, enums, records, nested types
- Robust error handling with detailed error reporting
- Support for both recursive and non-recursive directory parsing

Integration:
- Uses JavaDocExtractor for documentation extraction
- Uses JavaStructureListener for parse tree walking and data extraction
- Returns structured data using types from java_mcp.types module
- Designed for integration with MCP server protocol

Author: Rubens Gomes
License: Apache-2.0
"""

from typing import List, Dict, Any
from dataclasses import asdict
from pathlib import Path

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker

from java_mcp.parser.antlr4 import JavaLexer, JavaParser
from java_mcp.parser.java_doc_extractor import JavaDocExtractor
from java_mcp.parser.java_structure_listener import JavaStructureListener

class JavaSourceParser:
    """
    Main parser class that coordinates the entire Java source code parsing process.

    This class serves as the primary interface for parsing Java source code and extracting
    structural information. It orchestrates the parsing workflow by coordinating between
    the ANTLR4-generated lexer/parser, Javadoc extraction, and structural analysis to
    produce comprehensive representations of Java code suitable for AI assistant consumption.

    The parser handles the complete parsing pipeline:
    1. Javadoc extraction and cleaning
    2. Lexical analysis and token generation
    3. Syntax parsing and parse tree construction
    4. Semantic analysis via tree walking
    5. Association of documentation with code elements
    6. Structured data generation

    Attributes:
        javadoc_extractor (JavaDocExtractor): Instance for extracting and processing
                                            Javadoc comments from source code.

    Example:
        # Parse a single file
        parser = JavaSourceParser()
        result = parser.parse_file("/path/to/MyClass.java")

        # Parse an entire directory
        results = parser.parse_directory("/path/to/src", recursive=True)

        # Parse source code directly
        source_code = "public class Example { /* ... */ }"
        result = parser.parse_source(source_code, "Example.java")

    Note:
        The parser is designed to be stateless and thread-safe. Each parsing operation
        creates fresh instances of listeners and extractors as needed.
    """

    def __init__(self):
        """
        Initialize the JavaSourceParser with required components.

        Sets up the JavaDocExtractor instance that will be used for extracting
        and processing Javadoc comments during the parsing process. The parser
        maintains a single extractor instance for efficiency while ensuring
        thread safety through stateless operation.
        """
        self.javadoc_extractor = JavaDocExtractor()

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a single Java file and return complete structural information.

        This method reads a Java source file from disk, parses its contents using
        the ANTLR4 parser infrastructure, and extracts comprehensive structural
        information including classes, methods, fields, documentation, and metadata.

        The parsing process includes:
        - File reading with UTF-8 encoding
        - Javadoc extraction and processing
        - ANTLR4 lexical and syntactic analysis
        - Semantic structure extraction via tree walking
        - Error handling and reporting

        Args:
            file_path (str): Absolute or relative path to the Java source file to parse.
                           The file should have a .java extension and contain valid
                           Java source code.

        Returns:
            Dict[str, Any]: A dictionary containing the complete parsing results with
                          the following structure:

                          Success case:
                          {
                              'file_path': str,           # Path to the parsed file
                              'package': str,             # Package declaration
                              'imports': List[str],       # Import statements
                              'classes': List[dict],      # Class/interface/enum definitions
                              'parse_success': True       # Parsing status indicator
                          }

                          Error case:
                          {
                              'error': str,               # Error description
                              'file_path': str,           # Path to the problematic file
                              'parse_success': False      # Parsing status indicator
                          }

        Raises:
            No exceptions are raised directly. All errors are caught and returned
            in the result dictionary with 'parse_success': False and an 'error' field
            containing the error description.

        Example:
            parser = JavaSourceParser()
            result = parser.parse_file("src/main/java/com/example/User.java")

            if result['parse_success']:
                print(f"Found {len(result['classes'])} classes")
                for cls in result['classes']:
                    print(f"Class: {cls['name']} with {len(cls['methods'])} methods")
            else:
                print(f"Parse error: {result['error']}")

        Note:
            The method assumes UTF-8 encoding for source files. Files with different
            encodings may result in parsing errors or incorrect character handling.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()

            return self.parse_source(source_code, file_path)

        except Exception as e:
            return {
                'error': f"Failed to parse {file_path}: {str(e)}",
                'file_path': file_path,
                'parse_success': False
            }

    def parse_source(self, source_code: str, file_path: str = None) -> Dict[str, Any]:
        """
        Parse Java source code directly and return comprehensive structural information.

        This is the core parsing method that processes Java source code through the
        complete parsing pipeline. It coordinates between Javadoc extraction, ANTLR4
        parsing, and structural analysis to produce a complete representation of the
        Java code structure.

        The parsing pipeline consists of:
        1. Javadoc extraction and line number mapping
        2. ANTLR4 lexical analysis (tokenization)
        3. ANTLR4 syntactic analysis (parse tree construction)
        4. Semantic analysis via JavaStructureListener tree walking
        5. Association of Javadocs with corresponding code elements
        6. Structured data compilation and serialization

        Args:
            source_code (str): Complete Java source code as a string. Should contain
                             valid Java syntax including package declaration, imports,
                             and class/interface/enum definitions.
            file_path (str, optional): Path identifier for the source code, used for
                                     error reporting and result identification. Can be
                                     None for in-memory parsing scenarios.

        Returns:
            Dict[str, Any]: Comprehensive parsing results dictionary with the following
                          structure on success:

                          {
                              'file_path': str | None,    # Provided file path identifier
                              'package': str,             # Package declaration (empty if none)
                              'imports': List[str],       # All import statements
                              'classes': List[dict],      # Serialized Class objects containing:
                                                         #   - name, package, modifiers, annotations
                                                         #   - javadoc, line_number, class_type
                                                         #   - methods (List[dict]): Method objects
                                                         #   - fields (List[dict]): Field objects
                                                         #   - inner_classes (List[dict]): Nested classes
                                                         #   - extends, implements relationships
                              'parse_success': True       # Success indicator
                          }

                          On error:
                          {
                              'error': str,               # Detailed error description
                              'file_path': str | None,    # Provided file path identifier
                              'parse_success': False      # Failure indicator
                          }

        Raises:
            No exceptions are raised directly. All parsing errors, including ANTLR4
            parsing errors, I/O errors, and structural analysis errors, are caught
            and returned as error results.

        Example:
            parser = JavaSourceParser()

            source = '''
            package com.example;

            import java.util.List;

            /**
             * Example class for demonstration.
             */
            public class Example {
                /**
                 * Example method.
                 * @param name the name parameter
                 * @return a greeting message
                 */
                public String greet(String name) {
                    return "Hello, " + name;
                }
            }
            '''

            result = parser.parse_source(source, "Example.java")
            if result['parse_success']:
                cls = result['classes'][0]
                print(f"Class: {cls['name']}")
                print(f"Package: {result['package']}")
                print(f"Methods: {len(cls['methods'])}")
                print(f"Javadoc: {cls['javadoc']}")

        Note:
            - The method preserves all structural relationships including inheritance
            - Javadoc comments are automatically associated with their corresponding elements
            - Line numbers are preserved for all structural elements
            - Both top-level and nested classes are fully supported
        """
        try:
            # Extract Javadocs first
            javadocs = self.javadoc_extractor.extract_javadocs(source_code)

            # Create input stream
            input_stream = InputStream(source_code)

            # Create lexer
            lexer = JavaLexer(input_stream)

            # Create token stream
            token_stream = CommonTokenStream(lexer)

            # Create parser
            parser = JavaParser(token_stream)

            # Parse the compilation unit (root of Java file)
            tree = parser.compilationUnit()

            # Create and configure listener
            listener = JavaStructureListener()

            # Associate Javadocs with the listener based on line numbers
            self._associate_javadocs(listener, javadocs, tree)

            # Walk the parse tree
            walker = ParseTreeWalker()
            walker.walk(listener, tree)

            # Build result
            result = {
                'file_path': file_path,
                'package': listener.current_package,
                'imports': listener.import_statements,
                'classes': [asdict(cls) for cls in listener.classes],
                'parse_success': True
            }

            return result

        except Exception as e:
            return {
                'error': f"Failed to parse source: {str(e)}",
                'file_path': file_path,
                'parse_success': False
            }

    def _associate_javadocs(self, listener, javadocs: Dict[int, str], tree):
        """
        Associate extracted Javadoc comments with the parse tree listener.

        This private method provides the extracted Javadoc comments to the
        JavaStructureListener so they can be associated with the appropriate
        code elements during tree walking. The association is based on line
        number proximity and Java's documentation conventions.

        Currently, this implementation stores the Javadocs in the listener
        for access during tree walking. Future enhancements could include
        more sophisticated association logic based on parse tree context
        and proximity analysis.

        Args:
            listener (JavaStructureListener): The listener instance that will walk
                                            the parse tree and extract structural information.
            javadocs (Dict[int, str]): Dictionary mapping line numbers to cleaned
                                     Javadoc content, as returned by JavaDocExtractor.
            tree: The ANTLR4 parse tree root node (compilation unit) that will be
                 walked to extract structural information.

        Note:
            This is a simplified association approach. Production implementations
            might include more sophisticated logic to handle edge cases such as:
            - Multiple Javadoc blocks before a single element
            - Javadoc blocks separated from elements by annotations
            - Complex nested class scenarios
            - Documentation inheritance patterns
        """
        # Store javadocs in listener for use during tree walking
        listener.javadocs = javadocs

    def parse_directory(self, directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Parse all Java files in a directory and return comprehensive results.

        This method provides batch parsing functionality for entire directory trees,
        making it easy to analyze complete Java projects or packages. It automatically
        discovers Java source files and processes each one through the complete parsing
        pipeline, collecting results for all files.

        The method supports both flat directory parsing and recursive traversal of
        subdirectories, making it suitable for analyzing everything from individual
        packages to entire project source trees.

        Args:
            directory_path (str): Path to the directory containing Java source files.
                                Can be absolute or relative. The directory should exist
                                and be accessible for reading.
            recursive (bool, optional): Whether to recursively search subdirectories
                                      for Java files. Defaults to True.
                                      - True: Search all subdirectories recursively
                                      - False: Only search the specified directory

        Returns:
            List[Dict[str, Any]]: List of parsing results, one dictionary per Java file
                                found and processed. Each dictionary has the same structure
                                as returned by parse_file():

                                [
                                    {
                                        'file_path': str,
                                        'package': str,
                                        'imports': List[str],
                                        'classes': List[dict],
                                        'parse_success': True
                                    },
                                    ...
                                ]

                                Failed parses are included with 'parse_success': False
                                and an 'error' field describing the problem.

        Raises:
            No exceptions are raised directly. Directory access errors, file reading
            errors, and parsing errors are all handled gracefully and included in
            the results with appropriate error information.

        Example:
            parser = JavaSourceParser()

            # Parse all Java files in a project recursively
            results = parser.parse_directory("src/main/java", recursive=True)

            # Analyze results
            successful_parses = [r for r in results if r['parse_success']]
            failed_parses = [r for r in results if not r['parse_success']]

            print(f"Successfully parsed {len(successful_parses)} files")
            print(f"Failed to parse {len(failed_parses)} files")

            # Extract all classes from successful parses
            all_classes = []
            for result in successful_parses:
                all_classes.extend(result['classes'])

            print(f"Found {len(all_classes)} total classes")

            # Parse only immediate directory (non-recursive)
            package_results = parser.parse_directory("src/main/java/com/example",
                                                   recursive=False)

        Note:
            - Files are processed in the order returned by pathlib.Path.glob()
            - The method only processes files with .java extension
            - Empty directories or directories with no Java files return empty lists
            - Binary .class files and other non-source files are ignored
            - Symbolic links are followed if they point to valid Java files
        """
        results = []
        directory = Path(directory_path)

        pattern = "**/*.java" if recursive else "*.java"

        for java_file in directory.glob(pattern):
            if java_file.is_file():
                result = self.parse_file(str(java_file))
                results.append(result)

        return results