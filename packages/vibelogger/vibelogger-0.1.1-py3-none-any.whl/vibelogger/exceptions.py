"""
VibeCoding Logger - LLM-Friendly Exception Classes

This module provides exception classes with built-in tutorial content to help
LLMs understand and fix errors immediately when using vibelogger.
"""


class VibeLoggerError(Exception):
    """Base exception with tutorial support for LLM-friendly error messages."""
    
    def __init__(self, message, sample_code=None, docs_link=None):
        self.sample_code = sample_code
        self.docs_link = docs_link
        super().__init__(self._format_message(message))
    
    def _format_message(self, message):
        parts = [message]
        if self.sample_code:
            parts.append(f"\n\nSample Code:\n{self.sample_code}")
        if self.docs_link:
            parts.append(f"\n\nLearn more: {self.docs_link}")
        return "\n".join(parts)


class VibeLoggerImportError(VibeLoggerError):
    """Raised when vibelogger module import fails."""
    
    def __init__(self, original_error=None):
        sample = '''# Correct import methods:

# Option 1: Basic import
from vibelogger import create_file_logger
logger = create_file_logger("my_project")

# Option 2: Import specific components
from vibelogger import VibeLogger, LogLevel
logger = VibeLogger()

# Option 3: Import everything
import vibelogger
logger = vibelogger.create_file_logger("my_project")'''
        
        message = "Failed to import vibelogger module"
        if original_error:
            message += f": {str(original_error)}"
            
        super().__init__(
            message,
            sample_code=sample,
            docs_link="https://github.com/user/vibelogger#installation"
        )


class VibeLoggerConfigError(VibeLoggerError):
    """Raised when configuration is invalid."""
    
    def __init__(self, issue):
        sample = '''# Creating configurations:

# Option 1: Use defaults
from vibelogger import create_file_logger
logger = create_file_logger("my_project")  # Auto-configured

# Option 2: Custom config
from vibelogger import VibeLogger, VibeLoggerConfig
config = VibeLoggerConfig(
    log_file="./logs/app.log",
    max_file_size_mb=10,
    auto_save=True
)
logger = VibeLogger(config=config)

# Option 3: Environment variables
# Set: VIBE_LOG_FILE, VIBE_LOG_LEVEL, etc.
from vibelogger import create_env_logger
logger = create_env_logger()'''
        
        super().__init__(
            f"Configuration error: {issue}",
            sample_code=sample
        )


class VibeLoggerUsageError(VibeLoggerError):
    """Raised when logger methods are used incorrectly."""
    
    def __init__(self, method_name, issue):
        sample = '''# Basic logging usage:

from vibelogger import create_file_logger

logger = create_file_logger("my_app")

# Simple log
logger.info("User logged in")

# Log with context
logger.info(
    operation="user_login",
    message="User authentication successful",
    context={"user_id": 123, "ip": "192.168.1.1"},
    human_note="Check for suspicious IPs"
)

# Log exceptions
try:
    risky_operation()
except Exception as e:
    logger.log_exception(
        operation="risky_operation",
        exception=e,
        context={"input": data},
        ai_todo="Analyze error pattern"
    )

# Get logs for AI
ai_context = logger.get_logs_for_ai(max_entries=50)'''
        
        super().__init__(
            f"Usage error in {method_name}: {issue}",
            sample_code=sample
        )


class StandardLoggingCompatibilityError(VibeLoggerError):
    """Raised when trying to use standard logging methods on VibeLogger."""
    
    def __init__(self, method_called, logger_instance):
        sample = '''# VibeCoding Logger vs Standard Python Logging

# ❌ WRONG: Standard logging style (doesn't work)
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("This is standard logging")

# ✅ CORRECT: VibeCoding Logger style
from vibelogger import create_file_logger

# Create logger
logger = create_file_logger("my_project")

# Simple logging (similar to standard)
logger.info("User logged in")
logger.warning("Low memory")
logger.error("Connection failed")

# Rich logging (VibeCoding advantage)
logger.info(
    operation="process_payment",
    message="Payment processing started",
    context={
        "amount": 99.99,
        "currency": "USD",
        "user_id": "user123"
    },
    human_note="This is the critical payment flow"
)

# Standard logging integration
# If you need standard logging compatibility:
from vibelogger import setup_vibe_logging
import logging

# This redirects standard logging to VibeCoding Logger
setup_vibe_logging()
standard_logger = logging.getLogger(__name__)
standard_logger.info("Now this works with VibeLogger!")'''
        
        instance_type = type(logger_instance).__name__
        super().__init__(
            f"Attempted to call '{method_called}' like standard logging.\n"
            f"You have a {instance_type} instance, not a standard logger.\n"
            f"VibeCoding Logger uses different method signatures for richer logging.",
            sample_code=sample,
            docs_link="https://github.com/user/vibelogger#standard-logging-migration"
        )


class VibeLoggerFormatError(VibeLoggerError):
    """Raised when using incompatible string formatting."""
    
    def __init__(self, method_name):
        sample = '''# String formatting in VibeCoding Logger:

from vibelogger import create_file_logger

logger = create_file_logger("my_app")

# ❌ WRONG: % formatting (standard logging style)
logger.info("User %s logged in from %s", username, ip_address)

# ✅ CORRECT: f-string
logger.info(f"User {username} logged in from {ip_address}")

# ✅ BETTER: Rich context
logger.info(
    operation="user_login",
    message=f"User {username} logged in",
    context={
        "username": username,
        "ip_address": ip_address,
        "timestamp": datetime.now().isoformat()
    },
    human_note="Monitor for suspicious IP addresses"
)'''
        
        super().__init__(
            f"Format string style not supported in {method_name}. Use f-strings or pass data in context.",
            sample_code=sample
        )