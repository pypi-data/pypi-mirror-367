# smooth_operator/core/mixins/process.py
import asyncio
from typing import Tuple, List, Union


class ProcessRunnerMixin:
    """Provides async process running functionality."""

    async def _process(self, command: str) -> Tuple[bool, Union[List[str], str]]:
        """
        Run a command asynchronously and return result and output.

        Args:
            command: The command to run

        Returns:
            Tuple of (success, output)
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_output = stderr.decode().strip()
                if hasattr(self, 'debug_print'):
                    self.debug_print(f"Command failed: {command}\nError: {error_output}")
                return False, error_output

            # Split output into lines and remove empty lines
            output = [line for line in stdout.decode().split('\n') if line]
            return True, output
        except Exception as e:
            if hasattr(self, 'debug_print'):
                self.debug_print(f"Command execution error: {str(e)}")
            return False, str(e)
