from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# Set up a standard logger
logger = logging.getLogger("trade_copilot")

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to ensure all errors are returned
    in a consistent JSON format.
    """
    # Log the error for server-side debugging
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    # Handle FastAPI's own HTTPExceptions specifically
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail},
        )

    # Generic 500 for everything else
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc) if True else "An unexpected error occurred."
        },
    )

def setup_exception_handlers(app):
    """
    Register the global handler with the FastAPI application.
    """
    app.add_exception_handler(Exception, global_exception_handler)
