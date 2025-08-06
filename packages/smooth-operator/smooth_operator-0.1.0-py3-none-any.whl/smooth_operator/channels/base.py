# smooth_operator/channels/base.py
from abc import ABC, abstractmethod
from typing import Tuple, Union, List
from ..core.mixins.debug import DebugMixin
from ..core.mixins.process import ProcessRunnerMixin


class BaseChannel(ABC, DebugMixin, ProcessRunnerMixin):
    """Base class for operation channels."""

    def __init__(self, debug=False):
        """Initialize the channel."""
        super().__init__(debug=debug)

    @abstractmethod
    async def execute(self, command: str) -> Tuple[bool, Union[List[str], str]]:
        """
        Execute a command through this channel.

        Args:
            command: The command to execute

        Returns:
            Tuple of (success, output)
        """
        pass
