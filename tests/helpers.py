"""
Test helper functions for mocking and utilities.
"""
import functools
from fastapi import FastAPI
from typing import Callable, Any, Dict, List
import importlib

def import_module_function(import_path: str) -> Callable:
    """
    Import a function from a module path string.
    
    Args:
        import_path: String in format 'module.submodule.function'
        
    Returns:
        The imported function
    """
    module_path, function_name = import_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, function_name)

def mock_route_handlers(app: FastAPI, path: str, method: str, callback: Callable) -> None:
    """
    Replace a route handler with a custom callback for testing.
    
    Args:
        app: The FastAPI application
        path: The route path (e.g., "/tips/")
        method: The HTTP method (e.g., "POST")
        callback: The callback function to use instead
    """
    for route in app.routes:
        if hasattr(route, "path") and route.path == path:
            # Find the right endpoint
            if method.upper() in route.methods:
                # Save the original
                original = route.endpoint
                # Patch the endpoint
                route.endpoint = callback
                # Attach the original to the callback for restoration if needed
                callback.__original__ = original
                return
                
    raise ValueError(f"No route found for {method} {path}")

def restore_route_handlers(app: FastAPI) -> None:
    """
    Restore all patched route handlers to their original functions.
    
    Args:
        app: The FastAPI application
    """
    for route in app.routes:
        if hasattr(route, "endpoint") and hasattr(route.endpoint, "__original__"):
            route.endpoint = route.endpoint.__original__

def error_route_handler(*args, **kwargs):
    """
    A route handler that always raises an exception.
    Used for testing error handling.
    """
    raise Exception("Test error")

def get_test_error_handler(status_code: int = 503):
    """
    Get a test error handler that returns a specific status code.
    
    Args:
        status_code: The HTTP status code to return
        
    Returns:
        An error handler function
    """
    async def error_handler(*args, **kwargs):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status_code,
            content={"status": "error", "message": "Error occurred"}
        )
    return error_handler 