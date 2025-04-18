from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.logger import get_logger
from typing import Dict, Any, Optional, Type, Callable
import traceback

# Get logger for this module
logger = get_logger("error_handler")

class AppError(Exception):
    """
    Base application exception class.
    """
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class InvalidInputError(AppError):
    """Exception for invalid user inputs."""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, detail)


class NotFoundError(AppError):
    """Exception for resource not found errors."""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, detail)


class ServiceUnavailableError(AppError):
    """Exception for service unavailability errors."""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, detail)


class AuthorizationError(AppError):
    """Exception for authorization errors."""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, detail)


# Registry of error handlers
error_handlers: Dict[Type[Exception], Callable] = {}


def register_error_handler(exception_type: Type[Exception]):
    """
    Decorator to register an error handler for a specific exception type.
    
    Args:
        exception_type: The exception type to handle
    """
    def decorator(handler_func: Callable):
        error_handlers[exception_type] = handler_func
        return handler_func
    return decorator


@register_error_handler(AppError)
def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """
    Handle application-specific errors.
    """
    logger.error(f"Application error: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "detail": exc.detail or {}
        }
    )


@register_error_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors from FastAPI.
    """
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Input validation failed",
            "detail": {"errors": exc.errors()}
        }
    )


@register_error_handler(Exception)
def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    """
    Generic exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # In production, we don't want to leak implementation details
    content = {
        "status": "error",
        "message": "An unexpected error occurred"
    }
    
    # In development, include the traceback for debugging
    if logger.parent.level <= 10:  # DEBUG level
        content["detail"] = {
            "traceback": traceback.format_exception(
                type(exc), exc, exc.__traceback__
            )
        }
        
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )


def setup_error_handlers(app):
    """
    Register all error handlers with the FastAPI app.
    
    Args:
        app: The FastAPI application instance
    """
    for exception_type, handler in error_handlers.items():
        app.add_exception_handler(exception_type, handler) 