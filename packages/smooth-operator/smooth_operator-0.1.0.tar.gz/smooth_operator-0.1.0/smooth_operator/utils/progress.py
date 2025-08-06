from typing import Any, Dict, List, Optional, Tuple, Union
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, SpinnerColumn


def progress_bar(
        total: int,
        description: str
) -> Tuple[Progress, int]:
    """
    Create a standardized progress bar.

    Args:
        total: Total number of items
        description: Description text

    Returns:
        Tuple of (progress_bar, task_id)
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
    )
    task_id = progress.add_task(description, total=total)

    return progress, task_id