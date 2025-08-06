# smooth_operator/core/exceptions.py

class SmoothOperatorError(Exception):
    """Base exception for all smooth_operator errors."""
    pass

class ChannelConnectionError(SmoothOperatorError):
    """Raised when a channel connection fails."""
    pass

class CommandExecutionError(SmoothOperatorError):
    """Raised when a command execution fails."""
    pass

class ManifestError(SmoothOperatorError):
    """Raised for errors related to manifest parsing or validation."""
    pass

class TaskExecutionError(SmoothOperatorError):
    """Raised when a task fails to execute."""
    pass

