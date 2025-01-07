import os
import sys
from cine_notes.logger import logging
import traceback
from from_root import from_root


class CineNotesException(Exception):
    """
    Custom exception class for CineNotes application that provides detailed error information and logging.

    This class extends the base Exception class to provide:
    - Detailed error messages including file name and line number
    - Automatic logging of exceptions with full stack traces
    - Formatted string representation of errors

    Attributes:
        error_message (str): The formatted error message containing file, line and error details
    """

    def __init__(self, error_message, error_detail: sys):
        """
        Initialize the CineNotes exception with error details and logging.

        Args:
            error_message (str): The original error message describing what went wrong
            error_detail (sys): The sys module object containing error traceback information
        """
        super().__init__(error_message)
        self.error_message = self._get_error_message(error_message, error_detail)
        self._log_exception()

    def _get_error_message(self, error, error_detail: sys) -> str:
        """
        Formats a detailed error message with file name and line number information.

        Args:
            error: The original error message or exception
            error_detail (sys): System details containing traceback information

        Returns:
            str: A formatted error message string with file, line and error details
        """
        _, _, exc_tb = error_detail.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        error_message = "Error occurred in python script: [{0}] at line number: [{1}] with error: [{2}]".format(
            file_name, exc_tb.tb_lineno, str(error)
        )
        return error_message

    def _log_exception(self) -> None:
        """
        Logs the full exception stack trace using the configured logger.
        
        The exception is logged at ERROR level and includes the complete stack trace
        for debugging purposes.
        """
        stack_trace = traceback.format_exc()
        logging.error(f"Full stack trace:\n{stack_trace}")

    def __str__(self) -> str:
        """
        Returns the string representation of the exception.

        Returns:
            str: The formatted error message
        """
        return self.error_message
