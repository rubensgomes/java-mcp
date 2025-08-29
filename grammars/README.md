# grammars

This folder contains Java (version 24) grammars to be used by ANTLR4. The files
were downloaded from:

- [antlr grammars-v4 java](https://github.com/antlr/grammars-v4/tree/master/java)

## Generate Python antlr lexer and parser

```shell
# generates Python3 lexer and parser files into ../java_mcp/antlr4
antlr -Dlanguage=Python3 JavaLexer.g4 JavaParser.g4 -o ../java_mcp/parser/antlr4
```
