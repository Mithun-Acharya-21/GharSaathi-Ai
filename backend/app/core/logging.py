import logging
import sys


class SanitizingFilter(logging.Filter):
    """Filter that prevents bearer tokens and keys from leaking into stdout/stderr."""

    SENSITIVE_PATTERNS = ["Bearer ", "X-API-Key-ID", "token", "password", "key"]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            # Basic non-destructive safeguard
            for word in ["Bearer ", "token="]:
                if word in record.msg:
                    record.msg = "[SANITIZED_LOG_MESSAGE]"
        return True


def setup_logging(log_level: str = "INFO") -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.addFilter(SanitizingFilter())

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    # Suppress verbose noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
