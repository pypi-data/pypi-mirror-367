import os
import json
from typing import Union, Dict, List, Optional, Tuple
import asyncio
from .base import BaseChannel
from .gitlab import GitLabManager
from ..core.exceptions import ChannelConnectionError, CommandExecutionError


class Lando(BaseChannel):
    """
    Lando operation channel for local development environments.

    Responsible for:
    - Checking Lando status
    - Executing Lando commands
    - Retrieving project information via Lando
    - Interacting with GitLab for package information
    """

    def __init__(self, gitlab: Optional[GitLabManager] = None, debug=False):
        """
        Initialize Lando channel.

        Args:
            gitlab: Optional GitLab manager
            debug: Enable debug output
        """
        super().__init__(debug=debug)
        self._gitlab = gitlab or GitLabManager(debug=debug)
        self._check_connection_sync()

    def _check_connection_sync(self):
        """Synchronous connection checker for constructor."""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.ensure_future(self.check_connection())
            else:
                asyncio.run(self.check_connection())
        except RuntimeError:
            asyncio.run(self.check_connection())

    async def check_connection(self) -> bool:
        """
        Check if Lando is running in the current directory.

        Returns:
            True if Lando is running, False otherwise
        """
        result, output = await self._process('lando info --service appserver')
        if not result:
            raise ChannelConnectionError(f"Lando command failed: {output}")
        if not output or output == ['[]']:
            self.debug_print(
                f"Lando is not running in the directory ({os.getcwd()}). Please start Lando and try again.")
            return False
        return True

    async def execute(self, command: str) -> Tuple[bool, Union[List[str], str]]:
        """
        Execute a command through Lando.

        Args:
            command: The command to execute

        Returns:
            Tuple of (success, output)
        """
        return await self._process(f'lando {command}')

    @property
    def gitlab_manager(self) -> GitLabManager:
        """Get the GitLab manager."""
        return self._gitlab

    @gitlab_manager.setter
    def gitlab_manager(self, gitlab: GitLabManager):
        """Set the GitLab manager."""
        self._gitlab = gitlab

    async def get_clone_url(self, package_name: str) -> Optional[str]:
        """
        Get the clone URL for a package.

        Args:
            package_name: The name of the package

        Returns:
            The clone URL or None if not found
        """
        success, output = await self.execute(f'composer show {package_name} --format=json')
        if not success:
            self.debug_print(f"Lando composer command failed: {output}")
            return None

        try:
            data = json.loads(''.join(output))
            project_name = GitLabManager.project_string_from_url(data.get('source', {}).get('url', ''))

            if not project_name:
                self.debug_print(f"Project name is invalid")
                return None

            project = await self._gitlab.get_project(project_name)

            if not project:
                self.debug_print(f"Could not get project for {project_name}")
                return None

            return project.get('ssh_url_to_repo')
        except json.JSONDecodeError:
            self.debug_print(f"Failed to parse composer output for {package_name}")
            return None

    async def get_core_project_info(self) -> Optional[Dict[str, str]]:
        """
        Get information about core Drupal projects.

        Returns:
            Dictionary mapping module names to 'drupal' or None on failure
        """
        success, output = await self.execute('drush pml --field=name')

        if not success:
            self.debug_print(f"Could not retrieve project info: {output}")
            return None

        return {item: 'drupal' for item in output}

    async def get_noncore_project_info(self) -> Optional[Dict[str, str]]:
        """
        Get information about non-core Drupal projects.

        Returns:
            Dictionary mapping module names to project names or None on failure
        """
        success, output = await self.execute('drush pml --no-core --fields=name,project --format=json')

        if not success:
            self.debug_print(f"Could not retrieve project info: {output}")
            return None

        try:
            data = json.loads(''.join(output))
            return {item['name']: item['project'] for item in data.values()}
        except json.JSONDecodeError:
            self.debug_print("Failed to parse non-core project info.")
            return None

    async def execute_drush(self, command: str) -> Tuple[bool, Union[List[str], str]]:
        """
        Execute a Drush command through Lando.

        Args:
            command: The Drush command to execute

        Returns:
            Tuple of (success, output)
        """
        return await self.execute(f'drush {command}')

    async def execute_composer(self, command: str) -> Tuple[bool, Union[List[str], str]]:
        """
        Execute a Composer command through Lando.

        Args:
            command: The Composer command to execute

        Returns:
            Tuple of (success, output)
        """
        return await self.execute(f'composer {command}')
