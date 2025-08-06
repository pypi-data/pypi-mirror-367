# smooth_operator/core/mixins/debug.py

from typing import runtime_checkable


@runtime_checkable
class HasDebug:
    """Mixin to indicate a class has debug capability."""
    pass


import logging
from typing import Optional


class DebugMixin:
    """Provides debugging functionality."""

    def __init__(self, debug: bool = False, logger: Optional[logging.Logger] = None, **kwargs):
        """
        Initialize debug functionality.

        Args:
            debug: Whether debug mode is enabled
            logger: Optional logger instance to use
            **kwargs: Additional arguments for parent classes
        """
        self._debug = debug
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        # Call parent class __init__ methods if they exist
        super().__init__(**kwargs)

    @property
    def debug(self) -> bool:
        """Get debug status."""
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        """Set debug status."""
        self._debug = value

        # Adjust logger level based on debug setting
        if value:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(logging.INFO)

    def debug_print(self, message: str) -> None:
        """
        Log a debug message if debug is enabled.

        Args:
            message: Message to log
        """
        if self.debug:
            self._logger.debug(message)