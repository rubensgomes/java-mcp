import logging
from antlr4.error.ErrorListener import ErrorListener

# Configure module-level logging
logger = logging.getLogger(__name__)


class ParseErrorListener(ErrorListener):
    """
    Custom ANTLR4 error listener for capturing Java parse errors.

    This error listener collects syntax errors encountered during parsing
    instead of printing them to stderr. Errors are stored in a list for
    later inspection and logging.

    Attributes:
        errors (List[str]): List of error messages encountered during parsing.
                           Each error includes line number, column, and description.

    Example:
        error_listener = JavaParseErrorListener()
        lexer.addErrorListener(error_listener)
        parser.addErrorListener(error_listener)

        if error_listener.errors:
            for error in error_listener.errors:
                logger.warning(f"Parse error: {error}")
    """

    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Called when a syntax error is encountered during parsing.

        Args:
            recognizer: The parser or lexer that encountered the error
            offendingSymbol: The token that caused the error
            line (int): Line number where the error occurred
            column (int): Column number where the error occurred
            msg (str): Error message from ANTLR
            e: The recognition exception that caused the error
        """
        self.errors.append(f"Line {line}:{column} - {msg}")
