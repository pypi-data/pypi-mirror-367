"""
Quick Color

Colorized logging with Python.
"""

from .quick import ColorizedFormatter, get_colorized_logger, init_colors, reset_colors

__all__ = ["init_colors", "reset_colors", "get_colorized_logger", "ColorizedFormatter"]
