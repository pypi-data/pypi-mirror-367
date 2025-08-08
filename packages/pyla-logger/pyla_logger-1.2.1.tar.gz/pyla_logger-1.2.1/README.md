# PyLa Logger

[![PyPI version](https://badge.fury.io/py/pyla-logger.svg)](https://badge.fury.io/py/pyla-logger)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A structured logging library for Python applications that provides JSON-formatted logs with context management and flexible configuration.

## Features

- **Structured JSON Logging**: All logs are output in JSON format with ISO timestamps
- **Context Management**: Add persistent context data that appears in all subsequent log messages
- **Environment-Based Configuration**: Control log levels via environment variables
- **Standard Log Levels**: Support for debug, info, warning, error, and critical levels
- **Exception Logging**: Special handling for exceptions with stack trace information
- **Built on Structlog**: Leverages the powerful and reliable structlog library
- **Ready to Use**: Pre-configured logger instance available for immediate use

## Installation

```bash
pip install pyla-logger
```

## Quick Start

```python
from pyla_logger import logger

# Basic logging
logger.info("Application started")
logger.error("Something went wrong", error_code=500)

# Add persistent context
logger.add_context(user_id="12345", session="abc-def")
logger.info("User action")  # Will include user_id and session in output

# Exception logging
try:
    raise ValueError("Invalid input")
except Exception as e:
    logger.exception(e, "Failed to process request")
```

## Configuration

### Log Levels

Control the minimum log level using the `pyla_logger_level` environment variable:

```bash
export pyla_logger_level=info  # Only info, warning, error, and critical logs will be shown
export pyla_logger_level=error  # Only error and critical logs will be shown
```

Supported levels (case-insensitive):
- `debug` (default)
- `info`  
- `warning`
- `error`
- `critical`

## Usage Examples

### Basic Logging

```python
from pyla_logger import logger

logger.debug("Detailed debug information")
logger.info("General information", component="auth")
logger.warning("Warning message", retry_count=3)
logger.error("Error occurred", error_type="validation")
logger.critical("Critical system failure", system="database")
```

### Context Management

```python
from pyla_logger import logger

# Add context that will appear in all subsequent logs
logger.add_context(
    request_id="req-12345",
    user_id="user-67890",
    environment="production"
)

logger.info("Processing request")  
# Output: {"event": "Processing request", "request_id": "req-12345", "user_id": "user-67890", "environment": "production", "timestamp": "2024-01-01T12:00:00.000000Z", "level": "info"}

logger.error("Request failed", error_code=400)
# Output: {"event": "Request failed", "error_code": 400, "request_id": "req-12345", "user_id": "user-67890", "environment": "production", "timestamp": "2024-01-01T12:00:01.000000Z", "level": "error"}
```

### Exception Logging

```python
from pyla_logger import logger

try:
    result = 10 / 0
except Exception as e:
    logger.exception(e, "Division operation failed", operation="divide", operands=[10, 0])
    # Includes full stack trace and exception details
```

### Advanced Usage

```python
from pyla_logger import logger

# Multiple arguments and keyword arguments
logger.info("User logged in", "additional", "arguments", 
           user_name="john_doe", ip_address="192.168.1.1", success=True)

# Adding context incrementally
logger.add_context(service="auth-service")
logger.add_context(version="1.2.3")  # Adds to existing context

logger.info("Service status check")  # Contains all context data
```

### Creating Custom Logger Instances

```python
from pyla_logger.logger import Logger
import structlog

# Create your own logger instance
custom_logger = Logger(structlog.get_logger("my-service"))
custom_logger.add_context(service="my-service")
custom_logger.info("Custom logger message")
```

## Output Format

All logs are formatted as JSON with the following structure:

```json
{
  "event": "Your log message",
  "level": "info",
  "timestamp": "2024-01-01T12:00:00.000000Z",
  "custom_field": "custom_value",
  "context_field": "context_value"
}
```

## Environment Configuration

Set the log level using environment variables:

```bash
# In your shell or .env file
export pyla_logger_level=warning

# In Docker
ENV pyla_logger_level=info

# In Python code (not recommended, use env vars instead)
import os
os.environ['pyla_logger_level'] = 'error'
```

## Requirements

- Python 3.12+
- structlog >= 25.4.0

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
