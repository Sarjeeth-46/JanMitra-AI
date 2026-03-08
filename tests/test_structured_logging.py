"""
Tests for structured logging configuration

This module tests that structured JSON logging is properly configured
and produces the expected log format.
"""

import json
import logging
from io import StringIO
from utils.logging_config import configure_structured_logging, CustomJsonFormatter


def test_custom_json_formatter_adds_standard_fields():
    """Test that CustomJsonFormatter adds standard fields to log records"""
    # Create a string buffer to capture log output
    log_buffer = StringIO()
    handler = logging.StreamHandler(log_buffer)
    
    # Create and set the custom JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(line)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Create a test logger
    test_logger = logging.getLogger('test_logger')
    test_logger.setLevel(logging.INFO)
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    
    # Log a test message
    test_logger.info("Test message", extra={"custom_field": "custom_value"})
    
    # Get the log output
    log_output = log_buffer.getvalue()
    
    # Parse the JSON log
    log_record = json.loads(log_output.strip())
    
    # Verify standard fields are present
    assert 'timestamp' in log_record
    assert 'level' in log_record
    assert 'logger' in log_record
    assert 'module' in log_record
    assert 'function' in log_record
    assert 'line' in log_record
    assert 'message' in log_record
    
    # Verify field values
    assert log_record['level'] == 'INFO'
    assert log_record['logger'] == 'test_logger'
    assert log_record['message'] == 'Test message'
    assert log_record['custom_field'] == 'custom_value'


def test_configure_structured_logging_sets_json_format():
    """Test that configure_structured_logging sets up JSON logging"""
    # Configure structured logging
    configure_structured_logging(log_level="INFO")
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Verify logger is configured
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) > 0
    
    # Verify the handler has a JSON formatter
    handler = root_logger.handlers[0]
    assert isinstance(handler.formatter, CustomJsonFormatter)


def test_structured_logging_with_extra_fields():
    """Test that extra fields are included in JSON logs"""
    # Create a string buffer to capture log output
    log_buffer = StringIO()
    handler = logging.StreamHandler(log_buffer)
    
    # Create and set the custom JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Create a test logger
    test_logger = logging.getLogger('test_extra_fields')
    test_logger.setLevel(logging.INFO)
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    
    # Log a message with extra fields
    test_logger.info(
        "Evaluation completed",
        extra={
            "event": "evaluation_completed",
            "user_name": "Test User",
            "eligible_schemes": 3
        }
    )
    
    # Get the log output
    log_output = log_buffer.getvalue()
    
    # Parse the JSON log
    log_record = json.loads(log_output.strip())
    
    # Verify extra fields are present
    assert log_record['event'] == 'evaluation_completed'
    assert log_record['user_name'] == 'Test User'
    assert log_record['eligible_schemes'] == 3


def test_structured_logging_different_levels():
    """Test that different log levels are properly formatted"""
    # Create a string buffer to capture log output
    log_buffer = StringIO()
    handler = logging.StreamHandler(log_buffer)
    
    # Create and set the custom JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Create a test logger
    test_logger = logging.getLogger('test_levels')
    test_logger.setLevel(logging.DEBUG)
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    
    # Log messages at different levels
    test_logger.info("Info message")
    test_logger.warning("Warning message")
    test_logger.error("Error message")
    
    # Get the log output
    log_output = log_buffer.getvalue()
    log_lines = log_output.strip().split('\n')
    
    # Parse each log line
    info_log = json.loads(log_lines[0])
    warning_log = json.loads(log_lines[1])
    error_log = json.loads(log_lines[2])
    
    # Verify log levels
    assert info_log['level'] == 'INFO'
    assert warning_log['level'] == 'WARNING'
    assert error_log['level'] == 'ERROR'
    
    # Verify messages
    assert info_log['message'] == 'Info message'
    assert warning_log['message'] == 'Warning message'
    assert error_log['message'] == 'Error message'
