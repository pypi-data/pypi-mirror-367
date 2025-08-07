"""
Regression tests for specific issues that were identified and fixed.

These tests ensure that the exact problems found in the original code
cannot be reintroduced.
"""

import io
import logging
import threading
import time
from unittest.mock import patch

import pytest

from quick_colorlog import ColorizedFormatter, init_colors, reset_colors


class TestOriginalDoubleLoggingIssue:
    """
    Regression tests for the original double logging issue.

    The original issue was that calling init_colors() multiple times
    would add multiple handlers to the root logger, causing duplicate
    log messages.
    """

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()
        root_logger.setLevel(logging.WARNING)

    def teardown_method(self):
        """Clean up after each test."""
        self.setup_method()

    def test_original_double_logging_scenario(self):
        """
        Test the exact scenario that caused double logging.

        This simulates the original problematic code:
        1. Call init_colors()
        2. Call init_colors() again (e.g., in a different module)
        3. Log a message
        4. Verify it only appears once
        """
        log_capture = io.StringIO()

        # Simulate first module calling init_colors
        init_colors(level=logging.INFO, output=log_capture)

        # Simulate second module calling init_colors (the problem scenario)
        init_colors(level=logging.INFO, output=log_capture)

        # Log a message
        logger = logging.getLogger()
        test_message = "This should only appear once"
        logger.info(test_message)

        # Count occurrences
        log_output = log_capture.getvalue()
        message_count = log_output.count(test_message)

        assert message_count == 1, f"Message appeared {message_count} times, expected 1"

    def test_root_logger_handler_accumulation(self):
        """
        Test that handlers don't accumulate on the root logger.

        The original issue was handler accumulation causing multiple
        identical handlers on the same logger.
        """
        # Call init_colors multiple times
        for i in range(5):
            init_colors(level=logging.INFO)

        root_logger = logging.getLogger()

        # Count ColorizedFormatter handlers
        colorized_handlers = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, ColorizedFormatter)
        ]

        assert (
            len(colorized_handlers) == 1
        ), f"Expected 1 ColorizedFormatter handler, found {len(colorized_handlers)}"

    def test_import_based_double_initialization(self):
        """
        Test scenario where init_colors might be called during imports.

        This simulates the case where multiple modules import and initialize
        the logger, which was a common cause of the double logging issue.
        """
        log_capture = io.StringIO()

        def simulate_module_import():
            """Simulate a module that initializes logging on import."""
            return init_colors(level=logging.INFO, output=log_capture)

        # Simulate multiple module imports
        loggers = []
        for _ in range(3):
            logger = simulate_module_import()
            loggers.append(logger)

        # All should return the same logger instance (root logger)
        assert all(logger is loggers[0] for logger in loggers)

        # Test message appears only once
        test_message = "Import-based initialization test"
        loggers[0].info(test_message)

        log_output = log_capture.getvalue()
        message_count = log_output.count(test_message)
        assert message_count == 1

    def test_library_usage_pattern(self):
        """
        Test common library usage pattern that caused double logging.

        Libraries often initialize logging in their __init__.py or main module,
        and users might also call init_colors in their application code.
        """
        log_capture = io.StringIO()

        # Simulate library initialization
        library_logger = init_colors(level=logging.WARNING, output=log_capture)

        # Simulate user application initialization
        user_logger = init_colors(level=logging.INFO, output=log_capture)

        # Both should be the same logger instance
        assert library_logger is user_logger

        # Test that messages don't duplicate
        test_message = "Library and user initialization"
        user_logger.info(test_message)

        log_output = log_capture.getvalue()
        message_count = log_output.count(test_message)
        assert message_count == 1


class TestRootLoggerModificationIssue:
    """
    Regression tests for issues related to root logger modification.

    The original code modified the root logger without proper isolation,
    which could interfere with other logging in the application.
    """

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()
        root_logger.setLevel(logging.WARNING)

    def test_root_logger_level_preservation(self):
        """
        Test that root logger level is properly managed.

        The original code always set the root logger level without
        considering existing configuration.
        """
        # Set initial level
        root_logger = logging.getLogger()
        original_level = logging.ERROR
        root_logger.setLevel(original_level)

        # Initialize with different level
        init_colors(level=logging.DEBUG)

        # Level should be changed to the requested level
        assert root_logger.level == logging.DEBUG

        # Calling again with same level should not change it
        init_colors(level=logging.DEBUG)
        assert root_logger.level == logging.DEBUG

    def test_existing_handlers_preservation(self):
        """
        Test that existing non-colorized handlers are preserved.

        The original code might interfere with existing logging setup.
        """
        root_logger = logging.getLogger()

        # Add a custom handler before initialization
        custom_stream = io.StringIO()
        custom_handler = logging.StreamHandler(custom_stream)
        custom_handler.setFormatter(logging.Formatter("CUSTOM: %(message)s"))
        root_logger.addHandler(custom_handler)

        # Initialize colorized logging
        colorized_stream = io.StringIO()
        init_colors(output=colorized_stream)

        # Both handlers should exist
        assert len(root_logger.handlers) == 2

        # Custom handler should still be there
        assert custom_handler in root_logger.handlers

        # Test that both handlers work
        test_message = "Handler preservation test"
        root_logger.info(test_message)

        assert test_message in custom_stream.getvalue()
        assert test_message in colorized_stream.getvalue()

        # Cleanup
        root_logger.removeHandler(custom_handler)
        custom_handler.close()


class TestHandlerCleanupIssue:
    """
    Regression tests for handler cleanup issues.

    The original code had no way to clean up handlers, which could
    lead to resource leaks and testing issues.
    """

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

    def test_handler_resource_cleanup(self):
        """
        Test that handlers are properly cleaned up.

        The original code had no cleanup mechanism, which could
        lead to resource leaks in long-running applications.
        """
        streams = []

        # Create multiple handlers
        for i in range(5):
            stream = io.StringIO()
            streams.append(stream)
            init_colors(output=stream, force_reinit=True)

        # Reset should close all handlers
        reset_colors()

        root_logger = logging.getLogger()
        colorized_handlers = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, ColorizedFormatter)
        ]

        assert len(colorized_handlers) == 0

    def test_force_reinit_handler_cleanup(self):
        """
        Test that force_reinit properly cleans up old handlers.

        This tests the fix for potential handler accumulation when
        force reinitializing with different parameters.
        """
        # Initial setup
        stream1 = io.StringIO()
        logger = init_colors(output=stream1)

        initial_handler_count = len(logger.handlers)

        # Force reinit with different stream
        stream2 = io.StringIO()
        logger = init_colors(output=stream2, force_reinit=True)

        # Handler count should be the same
        assert len(logger.handlers) == initial_handler_count

        # Old stream should not receive new messages
        test_message = "Force reinit test"
        logger.info(test_message)

        assert test_message not in stream1.getvalue()
        assert test_message in stream2.getvalue()


class TestNamedLoggerPropagationIssue:
    """
    Regression tests for named logger propagation issues.

    Named loggers could cause double logging through propagation
    to parent loggers that also had colorized handlers.
    """

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

    def test_named_logger_propagation_control(self):
        """
        Test that named logger propagation is properly controlled.

        This tests the fix for double logging when named loggers
        propagate to a root logger that also has colorized handlers.
        """
        root_stream = io.StringIO()
        named_stream = io.StringIO()

        # Setup root logger
        root_logger = init_colors(output=root_stream)

        # Setup named logger with propagation disabled
        named_logger = init_colors(logger_name="test.named", output=named_stream)
        named_logger.propagate = False

        # Log to named logger
        test_message = "Named logger propagation test"
        named_logger.info(test_message)

        # Message should only appear in named logger stream
        assert test_message not in root_stream.getvalue()
        assert test_message in named_stream.getvalue()

    def test_get_colorized_logger_no_propagation_default(self):
        """
        Test that get_colorized_logger prevents propagation by default.

        This is a specific fix to prevent the common double logging
        scenario with named loggers.
        """
        from quick_colorlog import get_colorized_logger

        root_stream = io.StringIO()
        named_stream = io.StringIO()

        # Setup root logger
        init_colors(output=root_stream)

        # Get named logger (should have propagate=False by default)
        named_logger = get_colorized_logger("test.named", output=named_stream)

        # Verify propagation is disabled
        assert named_logger.propagate is False

        # Test that message doesn't propagate
        test_message = "Get colorized logger test"
        named_logger.info(test_message)

        assert test_message not in root_stream.getvalue()
        assert test_message in named_stream.getvalue()


class TestConcurrencyIssues:
    """
    Regression tests for concurrency-related issues.

    The original code wasn't thread-safe, which could cause issues
    in multi-threaded applications.
    """

    def setup_method(self):
        """Reset logging state before each test."""
        reset_colors()
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

    def test_concurrent_initialization_thread_safety(self):
        """
        Test that concurrent initialization doesn't cause issues.

        This tests the thread safety of the initialization code.
        """
        results = []
        errors = []
        log_capture = io.StringIO()

        def init_worker():
            """Worker function for concurrent initialization."""
            try:
                logger = init_colors(level=logging.INFO, output=log_capture)
                results.append(logger)

                # Try to log something
                logger.info(f"Thread {threading.current_thread().ident}")

            except Exception as e:
                errors.append(e)

        # Create and start multiple threads
        threads = []
        num_threads = 10

        for _ in range(num_threads):
            thread = threading.Thread(target=init_worker)
            threads.append(thread)

        # Start all threads at roughly the same time
        for thread in threads:
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == num_threads

        # All should return the same logger instance
        assert all(logger is results[0] for logger in results)

        # Should still only have one colorized handler
        root_logger = logging.getLogger()
        colorized_handlers = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, ColorizedFormatter)
        ]
        assert len(colorized_handlers) == 1

    def test_reset_during_logging(self):
        """
        Test that reset during active logging doesn't cause crashes.

        This tests robustness when reset is called while other threads
        might be logging.
        """
        log_capture = io.StringIO()
        init_colors(output=log_capture)

        logger = logging.getLogger()
        stop_logging = threading.Event()
        errors = []

        def logging_worker():
            """Worker that continuously logs messages."""
            counter = 0
            while not stop_logging.is_set():
                try:
                    logger.info(f"Message {counter}")
                    counter += 1
                    time.sleep(0.001)  # Small delay
                except Exception as e:
                    errors.append(e)

        # Start logging thread
        log_thread = threading.Thread(target=logging_worker)
        log_thread.start()

        # Let it log for a bit
        time.sleep(0.1)

        # Reset while logging is happening
        reset_colors()

        # Stop logging
        stop_logging.set()
        log_thread.join()

        # Should not have caused any errors
        assert len(errors) == 0, f"Errors during concurrent logging: {errors}"
