# smooth_operator/channels/terminus.py
from typing import List, Dict, Optional, Tuple, Union
import json
import os
import subprocess
from .base import BaseChannel
from ..core.models import Site
from ..config.settings import get_setting
from pydantic import ValidationError


class Terminus(BaseChannel):
    """
    Terminus operation channel for Pantheon platform interaction.

    Responsible for:
    - Retrieving site information from Pantheon
    - Executing Terminus commands
    - Managing Pantheon environments
    - Cloning content between sites
    """

    def __init__(self, debug=False):
        """
        Initialize Terminus channel.

        Args:
            debug: Enable debug output
        """
        super().__init__(debug=debug)
        self._sites_data = {}
        self._terminus_path = self._get_terminus_path()
        self._use_lando = self._should_use_lando()
        self._load_sites_sync()

    def _get_terminus_path(self) -> str:
        """Get the path to the Terminus executable."""
        # Check for explicit terminus path in config
        terminus_path = get_setting("terminus", "terminus_path")
        if terminus_path:
            # Verify the path exists
            if os.path.exists(terminus_path) and os.access(terminus_path, os.X_OK):
                self.debug_print(f"Using external Terminus at {terminus_path}")
                return terminus_path
            else:
                self.debug_print(f"Configured Terminus path {terminus_path} is not executable")

        # Use default binary name
        return get_setting("terminus", "binary", "terminus")

    def _should_use_lando(self) -> bool:
        """Determine if we should use Lando for Terminus commands."""
        # If terminus_path is set, don't use Lando
        if get_setting("terminus", "terminus_path"):
            return False

        return get_setting("terminus", "use_lando", True)

    def _load_sites_sync(self):
        """Synchronous site loader for constructor."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # If in an event loop, schedule it
                asyncio.ensure_future(self._load_sites())
            else:
                # If not in an event loop, run it
                asyncio.run(self._load_sites())
        except RuntimeError:
            # No running event loop
            asyncio.run(self._load_sites())

    async def _load_sites(self):
        """Load the list of Pantheon sites."""
        result, output = await self.execute('site:list --format=json')
        if result:
            try:
                self._sites_data = json.loads(''.join(output))
            except json.JSONDecodeError:
                self.debug_print("Failed to parse site list JSON")
                self._sites_data = {}
        else:
            self.debug_print(f"Failed to get sites: {output}")
            self._sites_data = {}

    @property
    def sites(self) -> List[str]:
        """Get the list of Pantheon site names."""
        return list(self._sites_data.keys())

    def get_sites(self) -> List[Site]:
        """Get a list of Site objects."""
        site_objects = []
        for name, data in self._sites_data.items():
            try:
                # Add the site name to the data dict for validation
                data['name'] = name
                site_objects.append(Site(**data))
            except ValidationError as e:
                self.debug_print(f"Failed to validate site data for {name}: {e}")
        return site_objects

    async def refresh_sites(self):
        """Refresh the list of Pantheon sites."""
        await self._load_sites()

    async def clone_content(
            self,
            source_site: str,
            source_env: str,
            target_site: str,
            target_env: str,
            content_type: str = "all"
    ) -> Tuple[bool, Union[List[str], str]]:
        """
        Clone content between sites/environments.

        Args:
            source_site: Source site name
            source_env: Source environment
            target_site: Target site name
            target_env: Target environment
            content_type: Type of content to clone ('all', 'database', or 'files')

        Returns:
            Tuple of (success, output)
        """
        if content_type not in ["all", "database", "files"]:
            return False, "Invalid content type specified."

        if content_type == "all":
            # Clone both database and files
            db_result, db_output = await self.clone_content(
                source_site, source_env, target_site, target_env, "database")
            files_result, files_output = await self.clone_content(
                source_site, source_env, target_site, target_env, "files")

            success = db_result and files_result
            output = f"Database: {'Success' if db_result else 'Failed'}\nFiles: {'Success' if files_result else 'Failed'}"

            if not db_result:
                output += f"\nDatabase error: {db_output}"
            if not files_result:
                output += f"\nFiles error: {files_output}"

            return success, output

        command = f"{content_type}:clone {source_site}.{source_env} {target_site}.{target_env} --yes"
        return await self.execute(command)

    async def execute(self, command: str) -> Tuple[bool, Union[List[str], str]]:
        """
        Execute a Terminus command.

        Args:
            command: The Terminus command to execute

        Returns:
            Tuple of (success, output)
        """
        if self._use_lando:
            # Use Lando for Terminus commands
            return await self._process(f"lando terminus {command}")
        else:
            # Use direct Terminus path
            return await self._process(f"{self._terminus_path} {command}")
