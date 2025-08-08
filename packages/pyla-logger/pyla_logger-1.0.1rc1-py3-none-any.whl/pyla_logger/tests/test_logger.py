import os
from unittest.mock import Mock, patch

from pyla_logger.logger import Logger


class TestLogger:
    def setup_method(self):
        self.mock_logger = Mock()
        self.logger = Logger(self.mock_logger)

    def test_init(self):
        assert self.logger.logger == self.mock_logger
        assert self.logger.context == {}

    def test_add_context(self):
        self.logger.add_context(key1="value1", key2="value2")
        assert self.logger.context == {"key1": "value1", "key2": "value2"}

        self.logger.add_context(key3="value3")
        assert self.logger.context == {"key1": "value1", "key2": "value2", "key3": "value3"}

    def test_debug(self):
        self.logger.add_context(context_key="context_value")
        self.logger.debug("debug message", extra_key="extra_value")

        self.mock_logger.debug.assert_called_once_with(
            "debug message", extra_key="extra_value", context_key="context_value"
        )

    def test_info(self):
        self.logger.add_context(context_key="context_value")
        self.logger.info("info message", extra_key="extra_value")

        self.mock_logger.info.assert_called_once_with(
            "info message", extra_key="extra_value", context_key="context_value"
        )

    def test_warning(self):
        self.logger.add_context(context_key="context_value")
        self.logger.warning("warning message", extra_key="extra_value")

        self.mock_logger.warning.assert_called_once_with(
            "warning message", extra_key="extra_value", context_key="context_value"
        )

    def test_error(self):
        self.logger.add_context(context_key="context_value")
        self.logger.error("error message", extra_key="extra_value")

        self.mock_logger.error.assert_called_once_with(
            "error message", extra_key="extra_value", context_key="context_value"
        )

    def test_critical(self):
        self.logger.add_context(context_key="context_value")
        self.logger.critical("critical message", extra_key="extra_value")

        self.mock_logger.critical.assert_called_once_with(
            "critical message", extra_key="extra_value", context_key="context_value"
        )

    def test_exception(self):
        exc = Exception("test exception")
        self.logger.add_context(context_key="context_value")
        self.logger.exception(exc, "exception message", extra_key="extra_value")

        self.mock_logger.exception.assert_called_once_with(
            "exception message", extra_key="extra_value", context_key="context_value", exc_info=exc
        )

    def test_combine_with_context(self):
        self.logger.add_context(context_key="context_value")
        values = {"extra_key": "extra_value"}

        self.logger._combine_with_context(values)

        assert values == {"extra_key": "extra_value", "context_key": "context_value"}

    def test_logging_methods_without_context(self):
        self.logger.debug("debug message")
        self.mock_logger.debug.assert_called_once_with("debug message")

        self.logger.info("info message")
        self.mock_logger.info.assert_called_once_with("info message")

    def test_logging_methods_with_args(self):
        self.logger.info("message", "arg1", "arg2", key="value")
        self.mock_logger.info.assert_called_once_with("message", "arg1", "arg2", key="value")

    @patch.dict(os.environ, {"pyla_logger_level": "info"})
    def test_log_level_filtering_debug_filtered_out(self):
        mock_logger = Mock()
        logger = Logger(mock_logger)

        logger.debug("debug message")
        mock_logger.debug.assert_not_called()

        logger.info("info message")
        mock_logger.info.assert_called_once_with("info message")

    @patch.dict(os.environ, {"pyla_logger_level": "error"})
    def test_log_level_filtering_warning_filtered_out(self):
        mock_logger = Mock()
        logger = Logger(mock_logger)

        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")

        mock_logger.debug.assert_not_called()
        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()

        logger.error("error message")
        mock_logger.error.assert_called_once_with("error message")

    @patch.dict(os.environ, {"pyla_logger_level": "critical"})
    def test_log_level_filtering_only_critical(self):
        mock_logger = Mock()
        logger = Logger(mock_logger)

        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")

        mock_logger.debug.assert_not_called()
        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()
        mock_logger.error.assert_not_called()

        logger.critical("critical message")
        mock_logger.critical.assert_called_once_with("critical message")

    @patch.dict(os.environ, {"pyla_logger_level": "error"})
    def test_exception_treated_as_error_level(self):
        mock_logger = Mock()
        logger = Logger(mock_logger)
        exc = Exception("test exception")

        logger.exception(exc, "exception message")
        mock_logger.exception.assert_called_once_with("exception message", exc_info=exc)

    @patch.dict(os.environ, {"pyla_logger_level": "critical"})
    def test_exception_filtered_out_when_level_too_high(self):
        mock_logger = Mock()
        logger = Logger(mock_logger)
        exc = Exception("test exception")

        logger.exception(exc, "exception message")
        mock_logger.exception.assert_not_called()

    def test_default_log_level_is_debug(self):
        with patch.dict(os.environ, {}, clear=True):
            mock_logger = Mock()
            logger = Logger(mock_logger)

            logger.debug("debug message")
            mock_logger.debug.assert_called_once_with("debug message")

    @patch.dict(os.environ, {"pyla_logger_level": "INVALID"})
    def test_invalid_log_level_defaults_to_debug(self):
        mock_logger = Mock()
        logger = Logger(mock_logger)

        logger.debug("debug message")
        mock_logger.debug.assert_called_once_with("debug message")

    @patch.dict(os.environ, {"pyla_logger_level": "INFO"})
    def test_log_level_case_insensitive(self):
        mock_logger = Mock()
        logger = Logger(mock_logger)

        logger.debug("debug message")
        mock_logger.debug.assert_not_called()

        logger.info("info message")
        mock_logger.info.assert_called_once_with("info message")


class TestLoggerIntegration:
    def test_logger_instance_creation(self):
        from pyla_logger.logger import logger

        assert isinstance(logger, Logger)
        assert logger.logger is not None
        assert logger.context == {}

    def test_structlog_configuration(self):
        import structlog

        config = structlog.get_config()

        assert len(config["processors"]) == 6
        assert config["wrapper_class"] is not None
        assert config["context_class"] == dict
        assert config["cache_logger_on_first_use"] is False
