# smooth_operator/operations/updater/manifest.py
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
from ...core.models import Manifest as ManifestModel, Task as TaskModel
from ...utils.logging import get_logger
from pydantic import ValidationError


class UpdateManifest:
    """
    Represents an update manifest with tasks and settings.
    """

    def __init__(self, paths: List[str]):
        """
        Initialize and merge update manifests.

        Args:
            paths: List of paths to the manifest files
        """
        self.paths = [Path(p) for p in paths]
        self.logger = get_logger("manifest")
        self.data = self._load_and_merge()
        try:
            self.model = ManifestModel(**self.data)
        except ValidationError as e:
            self.logger.error(f"Manifest validation failed: {e}")
            raise ValueError(f"Manifest validation failed: {e}")

        self.tasks = self.model.tasks
        self.settings = self.model.settings
        self.name = self.model.name
        self.description = self.model.description
        self.hooks = self.model.hooks

    def _load_and_merge(self) -> Dict[str, Any]:
        """
        Load and merge multiple manifest files.

        Returns:
            Merged manifest data
        """
        merged_data = {
            "settings": {},
            "hooks": {},
            "tasks": []
        }

        for path in self.paths:
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    self.logger.debug(f"Loaded manifest from {path}")

                    # Merge settings (later files override earlier ones)
                    merged_data["settings"].update(data.get("settings", {}))

                    # Merge hooks
                    for hook_name, scripts in data.get("hooks", {}).items():
                        if hook_name not in merged_data["hooks"]:
                            merged_data["hooks"][hook_name] = []
                        merged_data["hooks"][hook_name].extend(scripts)

                    # Append tasks
                    merged_data["tasks"].extend(data.get("tasks", []))

                    # Use name and description from the first manifest
                    if "name" not in merged_data:
                        merged_data["name"] = data.get("name", path.stem)
                    if "description" not in merged_data:
                        merged_data["description"] = data.get("description", "")

            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.logger.error(f"Failed to load manifest {path}: {str(e)}")
                raise ValueError(f"Failed to load manifest {path}: {str(e)}")

        return merged_data

    def get_hook(self, hook_name: str) -> List[str]:
        """Get commands for a specific hook."""
        return self.hooks.get(hook_name, [])

    def get_first_stage(self) -> Optional[TaskModel]:
        """
        Get the first stage of the manifest.

        Returns:
            First task or None if no tasks
        """
        return self.tasks[0] if self.tasks else None
