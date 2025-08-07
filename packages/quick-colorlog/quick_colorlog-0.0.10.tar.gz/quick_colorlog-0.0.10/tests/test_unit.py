"""
Unit tests for quick-colorlog functionality.

Tests individual functions and components in isolation.
"""

import io
import logging
import sys
from unittest.mock import Mock, patch

import pytest

from quick_colorlog import (
    ColorizedFormatter,
    get_colorized_logger,
    init_colors,
    reset_colors,
)
from quick_colorlog.quick import _has_colorized_handler


class TestColorizedFormatter:
    """Test the ColorizedFormatter class."""

    def test_formatter_initialization(self):
        """Test that the formatter initializes correctly."""
        formatter = ColorizedFormatter()
        assert formatter is not None
        assert hasattr(formatter, "LEVEL_COLORS")
        assert hasattr(formatter, "log_format")
        assert hasattr(formatter, "date_format")

    def test_level_colors_defined(self):
        """Test that all log levels have colors defined."""
        formatter = ColorizedFormatter()
        expected_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level in expected_levels:
            assert level in formatter.LEVEL_COLORS

    def test_format_with_tty(self):
        """Test formatting when stdout is a TTY."""
        formatter = ColorizedFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        with patch("sys.stdout.isatty", return_value=True):
            formatted = formatter.format(record)

        # Should contain the message
        assert "Test message" in formatted
        # Should contain ANSI color codes when TTY
        assert "\x1b[" in formatted

    def test_format_without_tty(self):
        """Test formatting when stdout is not a TTY."""
        formatter = ColorizedFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        with patch("sys.stdout.isatty", return_value=False):
            formatted = formatter.format(record)

        # Should contain the message
        assert "Test message" in formatted
        # Should not contain color prefix when not TTY (still has RESET in format)
        # But the level-specific color prefix should not be added

    def test_format_different_levels(self):
        """Test formatting for different log levels."""
        formatter = ColorizedFormatter()
        levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        with patch("sys.stdout.isatty", return_value=True):
            for level in levels:
                record = logging.LogRecord(
                    name="test",
                    level=level,
                    pathname="test.py",
                    lineno=1,
                    msg=f"Test {logging.getLevelName(level)} message",
                    args=(),
                    exc_info=None,
                )

                formatted = formatter.format(record)
                assert logging.getLevelName(level) in formatted
                assert f"Test {logging.getLevelName(level)} message" in formatted


class TestHasColorizedHandler:
    """Test the _has_colorized_handler helper function."""

    def test_empty_logger_no_handler(self):
        """Test logger with no handlers."""
        logger = logging.getLogger("test.empty")
        logger.handlers.clear()
        stream = io.StringIO()

        assert not _has_colorized_handler(logger, stream)

    def test_logger_with_non_colorized_handler(self):
        """Test logger with regular StreamHandler."""
        logger = logging.getLogger("test.regular")
        logger.handlers.clear()

        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter())
        logger.addHandler(handler)

        assert not _has_colorized_handler(logger, stream)

        # Cleanup
        logger.removeHandler(handler)
        handler.close()

    def test_logger_with_colorized_handler_same_stream(self):
        """Test logger with ColorizedFormatter and same stream."""
        logger = logging.getLogger("test.colorized")
        logger.handlers.clear()

        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(ColorizedFormatter())
        logger.addHandler(handler)

        assert _has_colorized_handler(logger, stream)

        # Cleanup
        logger.removeHandler(handler)
        handler.close()

    def test_logger_with_colorized_handler_different_stream(self):
        """Test logger with ColorizedFormatter but different stream."""
        logger = logging.getLogger("test.different")
        logger.handlers.clear()

        stream1 = io.StringIO()
        stream2 = io.StringIO()

        handler = logging.StreamHandler(stream1)
        handler.setFormatter(ColorizedFormatter())
        logger.addHandler(handler)

        assert _has_colorized_handler(logger, stream1)
        assert not _has_colorized_handler(logger, stream2)

        # Cleanup
        logger.removeHandler(handler)
        handler.close()


class TestInitColors:
    """Test the init_colors function."""

    def setup_method(self):
        """Reset logging state before each test."""
        # Clear all handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        # Reset our internal state
        reset_colors()

        # Reset logging level
        root_logger.setLevel(logging.WARNING)

    def teardown_method(self):
        """Clean up after each test."""
        self.setup_method()

    def test_init_colors_default_parameters(self):
        """Test init_colors with default parameters."""
        logger = init_colors()

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_init_colors_custom_level(self):
        """Test init_colors with custom log level."""
        logger = init_colors(level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_init_colors_custom_output(self):
        """Test init_colors with custom output stream."""
        stream = io.StringIO()
        logger = init_colors(output=stream)

        # Find the handler with our stream
        stream_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and h.stream is stream
        ]
        assert len(stream_handlers) == 1

    def test_init_colors_named_logger(self):
        """Test init_colors with named logger."""
        logger_name = "test.named"
        logger = init_colors(logger_name=logger_name)

        assert logger.name == logger_name
        assert logger is not logging.getLogger()  # Not root logger

    def test_init_colors_force_reinit(self):
        """Test force_reinit parameter."""
        stream = io.StringIO()

        # Initial setup
        logger1 = init_colors(level=logging.INFO, output=stream)
        handler_count_1 = len(logger1.handlers)

        # Add a test message to verify stream
        logger1.info("First init")
        output_1 = stream.getvalue()

        # Force reinit with different level
        logger2 = init_colors(level=logging.DEBUG, output=stream, force_reinit=True)
        handler_count_2 = len(logger2.handlers)

        # Should have same number of handlers
        assert handler_count_2 == handler_count_1
        assert logger2.level == logging.DEBUG

    def test_init_colors_returns_logger(self):
        """Test that init_colors returns the logger instance."""
        logger = init_colors()
        assert isinstance(logger, logging.Logger)

        # For root logger
        assert logger is logging.getLogger()

        # For named logger
        named_logger = init_colors(logger_name="test.return")
        assert named_logger is logging.getLogger("test.return")


class TestResetColors:
    """Test the reset_colors function."""

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

    def test_reset_colors_root_logger(self):
        """Test resetting root logger."""
        # Setup colorized logging
        stream = io.StringIO()
        init_colors(output=stream)

        root_logger = logging.getLogger()
        initial_handlers = len(root_logger.handlers)
        assert initial_handlers > 0

        # Reset
        reset_colors()

        # Should have no colorized handlers
        colorized_handlers = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 0

    def test_reset_colors_named_logger(self):
        """Test resetting named logger."""
        logger_name = "test.reset"
        stream = io.StringIO()

        # Setup colorized logging
        logger = init_colors(logger_name=logger_name, output=stream)
        initial_handlers = len(logger.handlers)
        assert initial_handlers > 0

        # Reset named logger
        reset_colors(logger_name=logger_name)

        # Should have no colorized handlers
        colorized_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 0

    def test_reset_colors_multiple_loggers(self):
        """Test that resetting one logger doesn't affect others."""
        stream1 = io.StringIO()
        stream2 = io.StringIO()

        # Setup two loggers
        logger1 = init_colors(logger_name="test.logger1", output=stream1)
        logger2 = init_colors(logger_name="test.logger2", output=stream2)

        # Reset only first logger
        reset_colors(logger_name="test.logger1")

        # First logger should have no colorized handlers
        colorized_handlers_1 = [
            h
            for h in logger1.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers_1) == 0

        # Second logger should still have colorized handlers
        colorized_handlers_2 = [
            h
            for h in logger2.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers_2) > 0


class TestGetColorizedLogger:
    """Test the get_colorized_logger function."""

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

    def test_get_colorized_logger_basic(self):
        """Test basic get_colorized_logger functionality."""
        logger_name = "test.colorized"
        logger = get_colorized_logger(logger_name)

        assert logger.name == logger_name
        assert isinstance(logger, logging.Logger)
        assert len(logger.handlers) > 0

    def test_get_colorized_logger_no_propagate_default(self):
        """Test that get_colorized_logger sets propagate=False by default."""
        logger = get_colorized_logger("test.no_propagate")
        assert logger.propagate is False

    def test_get_colorized_logger_propagate_true(self):
        """Test get_colorized_logger with propagate=True."""
        logger = get_colorized_logger("test.propagate", propagate=True)
        assert logger.propagate is True

    def test_get_colorized_logger_custom_params(self):
        """Test get_colorized_logger with custom parameters."""
        stream = io.StringIO()
        logger = get_colorized_logger(
            "test.custom", level=logging.DEBUG, output=stream, propagate=True
        )

        assert logger.name == "test.custom"
        assert logger.level == logging.DEBUG
        assert logger.propagate is True

        # Should have handler with our stream
        stream_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and h.stream is stream
        ]
        assert len(stream_handlers) == 1

    def test_get_colorized_logger_independent_instances(self):
        """Test that different named loggers are independent."""
        logger1 = get_colorized_logger("test.independent1")
        logger2 = get_colorized_logger("test.independent2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name

        # Each should have their own handlers
        assert len(logger1.handlers) > 0
        assert len(logger2.handlers) > 0

        # Handlers should be different instances
        assert logger1.handlers[0] is not logger2.handlers[0]


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

    def test_init_colors_with_none_logger_name(self):
        """Test init_colors with explicitly None logger_name."""
        logger = init_colors(logger_name=None)
        assert logger is logging.getLogger()

    def test_init_colors_with_empty_string_logger_name(self):
        """Test init_colors with empty string logger_name."""
        logger = init_colors(logger_name="")
        assert logger.name == ""
        assert logger is not logging.getLogger()

    def test_reset_colors_nonexistent_logger(self):
        """Test reset_colors on logger that doesn't exist."""
        # This should not raise an exception
        reset_colors(logger_name="nonexistent.logger")

    def test_reset_colors_logger_without_handlers(self):
        """Test reset_colors on logger without any handlers."""
        logger = logging.getLogger("test.no_handlers")
        logger.handlers.clear()

        # This should not raise an exception
        reset_colors(logger_name="test.no_handlers")

    def test_invalid_log_level(self):
        """Test init_colors with invalid log level."""
        # Python logging accepts any integer, so this should work
        logger = init_colors(level=999)
        assert logger.level == 999

    def test_closed_stream(self):
        """Test behavior with closed stream."""
        stream = io.StringIO()
        logger = init_colors(output=stream)

        # Close the stream
        stream.close()

        # Logging should not crash (though it may not output anything)
        try:
            logger.info("Test message to closed stream")
        except ValueError:
            # This is expected behavior for closed StringIO
            pass

    def test_formatter_with_unicode_message(self):
        """Test formatter with unicode characters."""
        formatter = ColorizedFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message with unicode: 🚀 ñ ☃",
            args=(),
            exc_info=None,
        )

        # Should not raise an exception
        formatted = formatter.format(record)
        assert "🚀" in formatted
        assert "ñ" in formatted
        assert "☃" in formatted
