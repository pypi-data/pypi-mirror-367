# smooth_operator/core/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class TaskType(str, Enum):
    """Enumeration of supported task types."""
    TERMINUS_COMMAND = "terminus_command"
    DRUSH_COMMAND = "drush_command"
    SCRIPT = "script"
    COMPOSER_UPDATE = "composer_update"


class Site(BaseModel):
    """Represents a Pantheon site."""
    name: str = Field(..., description="Machine name of the site.")
    site_id: str = Field(..., description="Pantheon site UUID.", alias="id")
    framework: Optional[str] = None
    organization: Optional[str] = None
    service_level: Optional[str] = None
    upstream: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        frozen = True  # Sites are immutable records


class Task(BaseModel):
    """A single task to be executed by the updater."""
    id: str = Field(..., description="Unique identifier for the task.")
    type: TaskType
    description: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    condition: Optional[str] = Field(
        None,
        description="A Python expression to evaluate for conditional execution."
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="A list of task IDs that must be completed before this task can run."
    )
    ignore_errors: bool = False


class Manifest(BaseModel):
    """Defines an entire upstream update process."""
    name: str
    description: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    hooks: Dict[str, List[str]] = Field(default_factory=dict)
    tasks: List[Task]
