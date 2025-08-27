"""
ANTLR4 Generated Java Parser Components

This module contains Python files that were automatically generated from Java grammar
definitions using ANTLR4 (ANother Tool for Language Recognition). These components
provide lexical analysis and parsing capabilities for Java source code.

Generated Files Overview:
========================

The files in this module were generated from inside the project grammars folder by running:
    antlr -Dlanguage=Python3 JavaLexer.g4 JavaParser.g4 -o ../java_mcp/parser/antlr4

Source Grammar Files:
- JavaLexer.g4: Defines the lexical rules for Java tokens (keywords, operators, literals, etc.)
- JavaParser.g4: Defines the syntactic rules for Java language constructs (classes, methods, expressions, etc.)

Generated Components:
====================

Core Parser Files:
- JavaLexer.py: Lexical analyzer that tokenizes Java source code into meaningful tokens
- JavaParser.py: Syntax parser that builds parse trees from tokenized Java code
- JavaParserListener.py: Listener interface for traversing and processing parse trees

Supporting Files:
- JavaLexer.tokens: Token definitions and mappings used by the lexer
- JavaParser.tokens: Token definitions used by the parser
- JavaLexer.interp: ANTLR interpreter data for the lexer
- JavaParser.interp: ANTLR interpreter data for the parser

Grammar Version:
===============
These parsers are based on Java language grammar version 24, supporting modern Java
syntax and language features.

Usage:
======
These generated components are used by higher-level parser modules in the project
to analyze Java source code structure, extract documentation, and perform code analysis.

Example typical usage flow:
1. JavaLexer tokenizes Java source text
2. JavaParser builds an Abstract Syntax Tree (AST)
3. JavaParserListener implementations traverse the AST to extract information

Dependencies:
============
- antlr4-python3-runtime: Required for the generated parser components to function

Note:
====
These are auto-generated files and should NOT be manually edited. Any changes
will be lost when the grammar files are regenerated. To modify parsing behavior,
update the source grammar files in the grammars/ directory and regenerate.

See Also:
=========
- grammars/README.md: Instructions for regenerating these files
- grammars/JavaLexer.g4: Source lexer grammar
- grammars/JavaParser.g4: Source parser grammar
- https://github.com/antlr/grammars-v4/tree/master/java: Original grammar source

Module Exports:
==============
This module provides access to the generated ANTLR4 components for Java parsing.
Import the specific components as needed:

    from java_mcp.parser.antlr4.JavaLexer import JavaLexer
    from java_mcp.parser.antlr4.JavaParser import JavaParser
    from java_mcp.parser.antlr4.JavaParserListener import JavaParserListener
"""

# Import the main generated components for convenient access
from .JavaLexer import JavaLexer
from .JavaParser import JavaParser
from .JavaParserListener import JavaParserListener

# Define what gets exported when using "from java_mcp.parser.antlr4 import *"
__all__ = [
    'JavaLexer',
    'JavaParser',
    'JavaParserListener'
]
