# smooth_operator/operations/stages/manager.py
import json
import os
from typing import Dict, Set, Any, Optional
from pathlib import Path

from ...utils.logging import get_logger

class StageManager:
    """Manages execution stages for a site across multiple runs."""
    
    def __init__(
        self,
        storage_path: str,
        site_id: str,
    ):
        self.storage_path = Path(storage_path)
        self.site_id = site_id
        self.logger = get_logger("stage_manager").bind(site_id=site_id)
        self.completed_stages: Set[str] = set()
        self._load_state()
    
    def _get_state_file(self) -> Path:
        """Get the path to the state file for the site."""
        return self.storage_path / f"{self.site_id}_state.json"
    
    def _load_state(self) -> None:
        """Load the current state from storage."""
        state_file = self._get_state_file()
        
        if not state_file.exists():
            self.logger.debug("No existing state file found.")
            return
            
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            self.completed_stages = set(state.get('completed_stages', []))
            self.logger.debug(
                "Loaded state",
                completed_stages=len(self.completed_stages),
            )
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error("Failed to load state file", error=str(e))
    
    def _save_state(self) -> None:
        """Save the current state to storage."""
        state_file = self._get_state_file()
        
        try:
            os.makedirs(state_file.parent, exist_ok=True)
            state = {'completed_stages': list(self.completed_stages)}
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            self.logger.debug("Saved state")
        except IOError as e:
            self.logger.error("Failed to save state file", error=str(e))
    
    def is_completed(self, stage_id: str) -> bool:
        """Check if a stage has been completed."""
        return stage_id in self.completed_stages
    
    def mark_completed(self, stage_id: str) -> None:
        """Mark a stage as completed."""
        if stage_id not in self.completed_stages:
            self.completed_stages.add(stage_id)
            self._save_state()
            self.logger.info("Marked stage as completed", stage_id=stage_id)
    
    def reset(self, stage_id: Optional[str] = None) -> None:
        """Reset completion status for a specific stage or all stages."""
        if stage_id:
            if stage_id in self.completed_stages:
                self.completed_stages.remove(stage_id)
                self.logger.info("Reset stage completion status", stage_id=stage_id)
        else:
            self.completed_stages.clear()
            self.logger.info("Reset all stage completion statuses")
        self._save_state()

