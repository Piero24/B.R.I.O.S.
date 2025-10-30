import sys
import logging

import structlog

def setup_logging() -> None:
    """Configures structlog for structured logging in the application.

    This function sets up structlog to use context variables, standard library 
        log levels, and a JSON renderer for log messages. It also configures 
        the root logger to output structured logs to stdout.
    
    The log level can be controlled via the LOG_LEVEL environment variable.
    Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: DEBUG)
    
    Third-party library log levels can be controlled via specific 
        environment variables:
    - PIKA_LOG_LEVEL: Controls RabbitMQ client verbosity (default: WARNING)
    - URLLIB3_LOG_LEVEL: Controls HTTP client verbosity (default: WARNING)
    """
    # Map string to logging level
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    log_level = log_level_map.get("INFO", logging.DEBUG)
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(logging.StreamHandler(sys.stdout))
    root_logger.setLevel(log_level)