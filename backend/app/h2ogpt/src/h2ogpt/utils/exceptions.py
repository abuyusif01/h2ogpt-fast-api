from functools import wraps
import inspect, os
from typing import Any, Optional

from app.h2ogpt.src.h2ogpt.schemas.response import APIExceptionResponse


class ExceptionHandler(Exception):
    """
    Custom exception handler for H2OGPT application.
    Args:
        exception (Exception): The original exception that occurred.
        msg (Optional[Any]): Additional message describing the exception.
        cls_name (Optional[str]): Name of the class where the exception occurred.
        func_name (Optional[str]): Name of the function where the exception occurred.
        solution (Optional[Any]): Suggested solution for the exception.
    """

    def __init__(
        self,
        exception: Exception,
        msg: Optional[Any] = None,
        solution: Optional[Any] = None,
    ) -> None:
        super().__init__()
        self.exception = exception
        self.msg = msg if isinstance(msg, str) else str(msg.__str__())
        self.func_name = inspect.stack()[2].function    
        self.solution = solution

    def __repr__(self) -> dict:
        verbose: int = int(os.getenv("H2OGPT_VERBOSE", 3))
        exception_name = self.exception.__class__.__name__
        cause = self.msg if verbose != 3 else self.get_cause_details()
        if verbose == 1:
            return {"msg": self.msg, "error": exception_name, "solution": self.solution}
        elif verbose >= 2:
            return {
                "error": exception_name,
                "cause": cause,
                "solution": self.solution,
                "msg": self.msg,
            }
        else:
            return {
                "msg": self.msg,
            }

    def get_cause_details(self) -> str:
        frames = inspect.stack()
        for frame_info in frames:
            frame = frame_info.frame

            if frame.f_code.co_name == self.func_name:
                filename = frame_info.filename
                lineno = frame_info.lineno
                func_name = frame_info.function
                cls_name = frame.f_globals.get("__name__", "Unknown")
                return f"{cls_name}.{func_name} raised the exception at line {lineno} in {filename}"

    @staticmethod
    def raise_exception(exception, msg, cls_name, func_name, solution) -> None:
        raise ExceptionHandler(exception, msg, cls_name, func_name, solution)


def exhandler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cls_name = args[0].__class__.__name__
        func_name = func.__name__
        result = func(*args, **kwargs)

        if isinstance(result, ExceptionHandler):
            if int(os.getenv("H2OGPT_VERBOSE", 0)) == 3:
                return APIExceptionResponse(
                    **result.__repr__(),
                    class_name=cls_name,
                    function_name=func_name,
                )
            else:
                return APIExceptionResponse(**result.__repr__())
        return result

    return wrapper
