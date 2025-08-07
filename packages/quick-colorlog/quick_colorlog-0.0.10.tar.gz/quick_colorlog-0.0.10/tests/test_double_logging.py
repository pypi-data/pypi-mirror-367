"""
Tests specifically for double logging prevention.

These tests ensure that the double logging issue identified and fixed
cannot be reintroduced.
"""

import io
import logging
import sys
from unittest.mock import patch

import pytest

from quick_colorlog import ColorizedFormatter, init_colors, reset_colors


class TestDoubleLoggingPrevention:
    """Test cases to prevent double logging regression."""

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

    def test_multiple_init_colors_calls_no_duplicates(self):
        """Test that calling init_colors multiple times doesn't create duplicate handlers."""
        # Capture log output
        log_capture = io.StringIO()

        # Call init_colors multiple times
        logger1 = init_colors(level=logging.INFO, output=log_capture)
        logger2 = init_colors(level=logging.INFO, output=log_capture)
        logger3 = init_colors(level=logging.INFO, output=log_capture)

        # All should return the same logger instance
        assert logger1 is logger2 is logger3

        # Root logger should only have one handler
        root_logger = logging.getLogger()
        colorized_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 1

        # Log a message and verify it appears only once
        test_message = "Test message for duplicate check"
        root_logger.info(test_message)

        log_output = log_capture.getvalue()
        message_count = log_output.count(test_message)
        assert message_count == 1, f"Message appeared {message_count} times, expected 1"

    def test_different_output_streams_multiple_handlers(self):
        """Test that different output streams create separate handlers."""
        stream1 = io.StringIO()
        stream2 = io.StringIO()

        # Initialize with different streams
        logger1 = init_colors(level=logging.INFO, output=stream1)
        logger2 = init_colors(level=logging.INFO, output=stream2)

        # Should have two handlers (one for each stream)
        root_logger = logging.getLogger()
        colorized_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 2

        # Test that messages go to correct streams
        test_message = "Stream test message"
        root_logger.info(test_message)

        assert test_message in stream1.getvalue()
        assert test_message in stream2.getvalue()

    def test_force_reinit_replaces_handlers(self):
        """Test that force_reinit removes existing handlers."""
        stream1 = io.StringIO()
        stream2 = io.StringIO()

        # Initial setup
        init_colors(level=logging.INFO, output=stream1)
        root_logger = logging.getLogger()
        initial_handler_count = len(root_logger.handlers)

        # Force reinit with different stream
        init_colors(level=logging.DEBUG, output=stream2, force_reinit=True)

        # Should still have same number of handlers
        assert len(root_logger.handlers) == initial_handler_count

        # But message should only go to new stream
        test_message = "Force reinit test"
        root_logger.info(test_message)

        assert test_message not in stream1.getvalue()
        assert test_message in stream2.getvalue()

    def test_same_stream_same_level_no_duplicate(self):
        """Test calling init_colors with identical parameters doesn't duplicate."""
        stream = io.StringIO()

        # Call with identical parameters
        for _ in range(5):
            init_colors(level=logging.INFO, output=stream)

        root_logger = logging.getLogger()
        colorized_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, ColorizedFormatter) and
               h.stream is stream
        ]
        assert len(colorized_handlers) == 1

    def test_different_levels_same_stream_no_duplicate(self):
        """Test that changing level doesn't create duplicate handlers."""
        stream = io.StringIO()

        # Initialize with different levels
        init_colors(level=logging.DEBUG, output=stream)
        init_colors(level=logging.INFO, output=stream)
        init_colors(level=logging.WARNING, output=stream)

        root_logger = logging.getLogger()
        colorized_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, ColorizedFormatter) and
               h.stream is stream
        ]
        assert len(colorized_handlers) == 1

    def test_named_logger_no_propagation_no_double_logging(self):
        """Test that named loggers don't cause double logging via propagation."""
        root_stream = io.StringIO()
        named_stream = io.StringIO()

        # Setup root logger
        root_logger = init_colors(level=logging.INFO, output=root_stream)

        # Setup named logger without propagation
        named_logger = init_colors(
            level=logging.INFO,
            output=named_stream,
            logger_name="test.module"
        )
        named_logger.propagate = False

        # Log to named logger
        test_message = "Named logger test"
        named_logger.info(test_message)

        # Message should only appear in named logger stream
        assert test_message not in root_stream.getvalue()
        assert test_message in named_stream.getvalue()

    def test_reset_and_reinit_works(self):
        """Test that reset_colors followed by init_colors works correctly."""
        stream = io.StringIO()

        # Initial setup
        init_colors(level=logging.INFO, output=stream)
        root_logger = logging.getLogger()

        # Log initial message
        root_logger.info("Before reset")
        initial_output = stream.getvalue()

        # Reset
        reset_colors()

        # Verify handlers are removed
        colorized_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 0

        # Reinitialize
        new_stream = io.StringIO()
        init_colors(level=logging.INFO, output=new_stream)

        # Log after reinit
        root_logger.info("After reset")

        # Old stream should not have new message
        assert "After reset" not in stream.getvalue()
        assert "After reset" in new_stream.getvalue()

    def test_concurrent_initialization_safety(self):
        """Test that concurrent calls don't create race conditions."""
        import threading
        import time

        stream = io.StringIO()
        results = []

        def init_worker():
            """Worker function for concurrent initialization."""
            try:
                logger = init_colors(level=logging.INFO, output=stream)
                results.append(logger)
            except Exception as e:
                results.append(e)

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=init_worker)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All should succeed and return logger instances
        assert len(results) == 10
        assert all(isinstance(r, logging.Logger) for r in results)

        # Should still only have one handler
        root_logger = logging.getLogger()
        colorized_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 1

    def test_module_import_safety(self):
        """Test that importing the module multiple times doesn't cause issues."""
        # This is more of a documentation test since Python's import system
        # prevents actual re-imports, but we can test the module state

        import importlib

        import quick_colorlog

        stream = io.StringIO()

        # Initial import and setup
        logger1 = quick_colorlog.init_colors(level=logging.INFO, output=stream)

        # Reload module (this doesn't actually reload in Python, but tests our assumption)
        importlib.reload(quick_colorlog)

        # Try to initialize again
        logger2 = quick_colorlog.init_colors(level=logging.INFO, output=stream)

        # Should not create duplicate handlers
        root_logger = logging.getLogger()
        colorized_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 1        assert len(colorized_handlers) == 1
