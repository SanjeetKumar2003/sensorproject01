import sys
import traceback


def error_message_detail(error, error_detail: sys):
    """
    Extract detailed error message with filename, line number, and error description.
    """
    _, _, exc_tb = error_detail.exc_info()

    if exc_tb is not None:
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        error_message = (
            f"Error occurred in script: [{file_name}], "
            f"line number: [{line_number}], "
            f"error message: [{str(error)}]"
        )
    else:
        error_message = f"Error message: [{str(error)}] (No traceback available)"

    return error_message


class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        """
        Custom exception class to provide detailed error messages.
        """
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message
