# smooth_operator/channels/gitlab.py
from typing import Optional, Dict, Any
import httpx
from ..core.mixins.debug import DebugMixin
from ..config.settings import get_setting
from ..core.exceptions import ChannelConnectionError


class GitLabManager(DebugMixin):
    """
    GitLab operation channel for repository management.

    Responsible for:
    - Authenticating with GitLab
    - Retrieving project information
    - Managing repositories
    """

    def __init__(self, token: Optional[str] = None, api_url: Optional[str] = None, debug: bool = False):
        """
        Initialize GitLab manager.

        Args:
            token: GitLab API token
            api_url: GitLab API URL
            debug: Enable debug output
        """
        super().__init__(debug=debug)
        self.api_url = api_url or get_setting("gitlab", "api_url")
        self.token = token or get_setting("gitlab", "token")

        if not self.token:
            raise ChannelConnectionError("GitLab token is not configured.")

        self.headers = {'Private-Token': self.token}

    @staticmethod
    def project_string_from_url(url: str) -> Optional[str]:
        """
        Extract project string from URL.

        Args:
            url: GitLab URL

        Returns:
            Project string or None if invalid
        """
        if not url:
            return None

        try:
            path = url.split('://', 1)[-1].split(':', 1)[-1].split('/', 1)[-1]
            if path.endswith('.git'):
                path = path[:-4]
            return path
        except (IndexError, AttributeError):
            # self.debug_print is not available in a static method
            # Consider logging this if a logger is available globally
            return None

    async def get_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Get project information from GitLab.

        Args:
            project_name: The project name (e.g., 'group/project')

        Returns:
            Project information or None if not found
        """
        encoded_project_name = project_name.replace('/', '%2F')
        url = f"{self.api_url}/projects/{encoded_project_name}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                self.debug_print(f"Failed to get project '{project_name}': {e}")
                return None
            except httpx.HTTPStatusError as e:
                self.debug_print(f"Error response {e.response.status_code} while requesting project '{project_name}'.")
                return None
