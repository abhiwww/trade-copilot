import logging
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict
from fastapi import Request

# Custom JSON formatter for structured logs
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Merge extra attributes if any
        if hasattr(record, "extra"):
            log_record.update(record.extra)

        return json.dumps(log_record)

def setup_logging():
    """Initializes the global structured logger."""
    logger = logging.getLogger("trade_copilot")
    logger.setLevel(logging.INFO)

    # Console handler with JSON formatting
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger

logger = setup_logging()

async def logging_middleware(request: Request, call_next):
    """
    FastAPI middleware to log every request with a unique trace ID.
    """
    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    # Add trace ID to request state
    request.state.trace_id = trace_id

    logger.info(f"Request started: {request.method} {request.url.path}", extra={"trace_id": trace_id})

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Request finished: {request.method} {request.url.path}",
            extra={"trace_id": trace_id, "status_code": response.status_code, "latency_ms": process_time}
        )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(f"Request failed: {request.method} {request.url.path}", extra={"trace_id": trace_id, "latency_ms": process_time, "error": str(e)})
        raise e
