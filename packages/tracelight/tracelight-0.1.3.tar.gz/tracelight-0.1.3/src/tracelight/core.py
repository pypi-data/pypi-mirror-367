import logging
import traceback
import inspect
from types import FrameType
from typing import Any, Optional, Dict, Union, List, Callable


def log_exception_state(exc: Exception,
                        logger: logging.Logger,
                        level: int = logging.ERROR,
                        *,
                        max_var_length: int = 1000,
                        exclude_vars: Optional[List[str]] = None,
                        format_var: Optional[Callable[[str, Any], str]] = None) -> Dict[str, Any]:
    """
    Walk the traceback of `exc`, logging each frame's local variables and return structured data.

    Args:
        exc: The caught exception.
        logger: A logging.Logger (or logger-like) instance.
        level: The log level to use (e.g. logging.ERROR, logging.DEBUG).
        max_var_length: If repr(var) exceeds this, it will be truncated with '...'.
        exclude_vars: List of variable names to exclude from logging (e.g. passwords).
        format_var: Optional function to customize variable formatting: 
                    format_var(var_name, var_value) -> formatted_string
                    
    Returns:
        Dict containing structured exception data with error info and frame details.
    """
    exclude_vars = exclude_vars or []
    tb = exc.__traceback__
    
    # Build structured data
    error_data = {
        "error": str(exc),
        "error_type": type(exc).__name__,
        "frames": []
    }
    
    # Header for context
    logger.log(level, "Logging exception state for: %s: %s",
              type(exc).__name__, exc)
    
    frame_count = 0
    while tb is not None:
        frame: FrameType = tb.tb_frame
        lineno: int = tb.tb_lineno
        func_name: str = frame.f_code.co_name
        filename: str = frame.f_code.co_filename
        
        frame_count += 1
        
        logger.log(level,
                  "-- Frame %d: %r in %s at line %d --",
                  frame_count, func_name, filename, lineno)

        # Build frame data
        frame_data = {
            "frame_number": frame_count,
            "function": func_name,
            "file": filename,
            "line": lineno,
            "locals": {}
        }

        for var_name, var_val in frame.f_locals.items():
            if var_name in exclude_vars:
                continue
                
            try:
                # Check if it's a Pydantic BaseModel and handle specially
                if hasattr(var_val, '__class__'):
                    # Try model_dump for Pydantic v2
                    if hasattr(var_val.__class__, 'model_dump'):
                        try:
                            frame_data["locals"][var_name] = var_val.model_dump()
                            continue
                        except Exception:
                            # Fall through to next approach
                            pass
                    
                    # Try dict() for Pydantic v1
                    if hasattr(var_val, 'dict') and callable(var_val.dict):
                        try:
                            frame_data["locals"][var_name] = var_val.dict()
                            continue
                        except Exception:
                            # Fall through to regular processing
                            pass
                
                # Regular variable processing
                if format_var is not None:
                    rep = format_var(var_name, var_val)
                else:
                    rep = repr(var_val)
                    # truncate if too long
                    if len(rep) > max_var_length:
                        rep = rep[:max_var_length] + "...<truncated>"
                        
                # Try to keep the actual value if it's JSON-serializable
                try:
                    # Test if value is JSON-serializable basic types
                    if isinstance(var_val, (str, int, float, bool, type(None))) or \
                       (isinstance(var_val, (list, dict)) and not var_name.startswith('__')):
                        # For basic types, store the actual value
                        frame_data["locals"][var_name] = var_val
                    else:
                        # For complex types, store the string representation
                        frame_data["locals"][var_name] = rep
                except (TypeError, ValueError):
                    # Fallback to string representation
                    frame_data["locals"][var_name] = rep
                    
            except Exception as format_err:
                rep = f"<unrepresentable: {type(format_err).__name__}>"
                frame_data["locals"][var_name] = rep

            logger.log(level, "    %s = %s", var_name, rep)

        error_data["frames"].append(frame_data)
        tb = tb.tb_next
    
    return error_data
        

class TracedError(Exception):
    """An exception that automatically logs its traceback and all local variables.
    
    This can be raised directly or used as a context manager to automatically catch,
    log, and re-raise exceptions with detailed state information.
    """
    
    def __init__(self, 
                 message: str = "", 
                 logger: Optional[logging.Logger] = None,
                 level: int = logging.ERROR,
                 max_var_length: int = 1000,
                 exclude_vars: Optional[List[str]] = None):
        super().__init__(message)
        self.logger = logger or logging.getLogger(__name__)
        self.level = level
        self.max_var_length = max_var_length
        self.exclude_vars = exclude_vars or []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            log_exception_state(
                exc_val, 
                self.logger, 
                self.level, 
                max_var_length=self.max_var_length,
                exclude_vars=self.exclude_vars
            )
            # Don't suppress the exception
            return False
        return True
