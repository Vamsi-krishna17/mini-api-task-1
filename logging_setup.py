
import sys
from time import perf_counter

from loguru import logger

from config import settings

def configure_logging():
    """Configure Loguru application logging."""

    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level} | "
            "{message}"
        ),
        colorize=False,
        backtrace=False,
        diagnose=False,
    )

async def request_logging_middleware(request, call_next):
    """Log every incoming HTTP request and its response time."""

    start_time = perf_counter()

    try:
        response = await call_next(request)

        duration_ms = (perf_counter() - start_time) * 1000

        logger.info(
            "{} {} | Status: {} | Duration: {:.2f} ms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception:
        duration_ms = (perf_counter() - start_time) * 1000

        logger.exception(
            "{} {} | Status: 500 | Duration: {:.2f} ms",
            request.method,
            request.url.path,
            duration_ms,
        )

        raise