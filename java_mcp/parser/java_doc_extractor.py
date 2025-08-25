"""
Java Documentation Extractor for MCP (Model Context Protocol) Server.

This module provides utilities for extracting and processing Javadoc comments from Java source code.
The JavaDocExtractor class uses regular expressions to locate, extract, and clean Javadoc comments,
making them available for analysis by AI coding assistants through the MCP server.

Key Features:
- Extracts Javadoc comments from Java source code
- Maps Javadoc comments to their line numbers in the source
- Cleans and formats extracted documentation for better readability
- Handles multi-line Javadoc blocks with proper formatting
- Removes Javadoc-specific formatting characters (asterisks, whitespace)

Author: Rubens Gomes
License: Apache-2.0
"""

import re
from typing import Dict

class JavaDocExtractor:
    """
    Extracts and processes Javadoc comments from Java source code.

    This class provides functionality to locate, extract, and clean Javadoc comments
    from Java source files. It uses regular expressions to identify Javadoc blocks
    (/** ... */) and processes them to remove formatting artifacts while preserving
    the documentation content.

    The extractor is designed to work with the MCP server to provide clean, readable
    documentation to AI coding assistants for better understanding of Java codebases.

    Attributes:
        javadoc_pattern (re.Pattern): Compiled regular expression pattern for matching
                                     Javadoc comment blocks in source code.

    Example:
        extractor = JavaDocExtractor()
        javadocs = extractor.extract_javadocs(java_source_code)

        # javadocs will be a dict like:
        # {
        #     15: "Returns the user's full name concatenated from first and last name.",
        #     42: "Calculates the total price including tax and discounts.\n\n@param basePrice the base price before calculations\n@return the final calculated price"
        # }
    """

    def __init__(self):
        """
        Initialize the JavaDocExtractor with the necessary regex pattern.

        Sets up the compiled regular expression pattern used to identify and extract
        Javadoc comment blocks from Java source code. The pattern uses DOTALL flag
        to match across multiple lines.
        """
        self.javadoc_pattern = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)

    def extract_javadocs(self, source_code: str) -> Dict[int, str]:
        """
        Extract all Javadoc comments from Java source code and map them to line numbers.

        This method searches through the provided Java source code to find all Javadoc
        comment blocks (/** ... */), extracts their content, cleans up the formatting,
        and returns a dictionary mapping the starting line number of each Javadoc block
        to its cleaned content.

        The method processes multi-line Javadoc blocks and handles standard Javadoc
        formatting including @param, @return, @throws tags, and other documentation
        elements.

        Args:
            source_code (str): The complete Java source code as a string to search
                              for Javadoc comments.

        Returns:
            Dict[int, str]: A dictionary where keys are line numbers (1-based) indicating
                           where each Javadoc comment starts in the source code, and values
                           are the cleaned Javadoc content with formatting removed.

        Example:
            source = '''
            /**
             * Represents a user in the system.
             * @author John Doe
             */
            public class User {
                /**
                 * Gets the user's email address.
                 * @return the email address as a string
                 */
                public String getEmail() { ... }
            }
            '''

            extractor = JavaDocExtractor()
            result = extractor.extract_javadocs(source)
            # Result: {
            #     2: "Represents a user in the system.\n@author John Doe",
            #     7: "Gets the user's email address.\n@return the email address as a string"
            # }

        Note:
            Line numbers are 1-based to match standard text editor conventions.
            Empty lines and lines containing only whitespace/asterisks are filtered out
            during the cleaning process.
        """
        javadocs = {}

        for match in self.javadoc_pattern.finditer(source_code):
            start_line = source_code[:match.start()].count('\n') + 1

            # Clean up the Javadoc content
            content = match.group(1)
            cleaned_content = self._clean_javadoc(content)

            javadocs[start_line] = cleaned_content

        return javadocs

    def _clean_javadoc(self, content: str) -> str:
        """
        Clean up raw Javadoc content by removing formatting artifacts.

        This private method processes the raw content extracted from Javadoc comments
        to remove Javadoc-specific formatting characters such as leading asterisks,
        extra whitespace, and empty lines, while preserving the actual documentation
        content and structure.

        The cleaning process:
        1. Splits the content into individual lines
        2. Removes leading whitespace and asterisks from each line
        3. Strips trailing whitespace from each line
        4. Filters out completely empty lines
        5. Rejoins the cleaned lines with newlines

        Args:
            content (str): Raw Javadoc content extracted from the comment block,
                          including asterisks and formatting whitespace.

        Returns:
            str: Cleaned Javadoc content with formatting artifacts removed,
                 preserving the actual documentation text and @tags.

        Example:
            Raw input:
            "\\n     * This is a method description.\\n     * \\n     * @param name the user name\\n     * @return the result\\n     "

            Cleaned output:
            "This is a method description.\\n@param name the user name\\n@return the result"

        Note:
            This method preserves Javadoc tags (@param, @return, @throws, etc.) and
            their structure while removing only the visual formatting artifacts.
        """
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # Remove leading whitespace and asterisks
            cleaned = re.sub(r'^\s*\*\s?', '', line)
            cleaned = cleaned.strip()
            if cleaned:
                cleaned_lines.append(cleaned)

        return '\n'.join(cleaned_lines).strip()
