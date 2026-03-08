"""
Structured Logging Configuration

This module configures structured JSON logging for the JanMitra AI Phase 1 Backend.
It uses python-json-logger to format log messages as JSON for better parsing and
analysis in production environments.

Requirements: 3.2
"""

import logging
import sys
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds standard fields to all log records.
    
    This formatter ensures consistent structure across all log messages,
    making them easier to parse and analyze in log aggregation systems.
    """
    
    def add_fields(self, log_record, record, message_dict):
        """
        Add custom fields to the log record.
        
        Args:
            log_record: Dictionary that will be serialized to JSON
            record: LogRecord object from Python's logging module
            message_dict: Dictionary of message fields
        """
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def configure_structured_logging(log_level: str = "INFO"):
    """
    Configure structured JSON logging for the application.
    
    This function sets up the root logger with a JSON formatter that outputs
    structured log messages. All loggers in the application will inherit this
    configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Log Levels:
        - INFO: Successful evaluations, health checks, normal operations
        - WARNING: Validation failures, missing fields, retryable errors
        - ERROR: Database failures, unexpected exceptions, system errors
        - DEBUG: Rule evaluation details (disabled in production)
    
    Requirements: 3.2
    """
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(line)s %(message)s'
    )
    
    # Set formatter on handler
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicate logs
    root_logger.handlers.clear()
    
    # Add our handler
    root_logger.addHandler(handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
