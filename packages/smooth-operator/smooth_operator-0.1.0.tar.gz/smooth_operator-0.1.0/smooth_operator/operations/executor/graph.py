# smooth_operator/operations/executor/graph.py
import asyncio
import time
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass

from ...utils.logging import get_logger
from ...operations.updater.task import TaskExecutor
from ...core.models import Task

@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    task_id: str
    task_type: str
    duration_ms: float
    output: Any = None
    error: Optional[str] = None
    context: Dict[str, Any] = None

@dataclass
class ExecutionNode:
    """A node in the execution graph."""
    task: Task
    dependencies: Set[str]
    dependents: Set[str]
    result: Optional[TaskResult] = None

    @property
    def is_ready(self) -> bool:
        """Check if this node is ready to execute."""
        return len(self.dependencies) == 0

    @property
    def is_complete(self) -> bool:
        """Check if this node has completed execution."""
        return self.result is not None

class TaskGraph:
    """A graph of tasks with dependencies."""

    def __init__(self, tasks: List[Task]):
        self.logger = get_logger("task_graph")
        self.nodes: Dict[str, ExecutionNode] = {}
        self._build_graph(tasks)

    def _build_graph(self, tasks: List[Task]) -> None:
        """Build the execution graph from tasks."""
        # First pass: Create nodes for all tasks
        for task in tasks:
            self.nodes[task.id] = ExecutionNode(
                task=task,
                dependencies=set(task.depends_on),
                dependents=set(),
            )

        # Second pass: Set up dependents
        for task_id, node in self.nodes.items():
            for dep_id in node.dependencies:
                if dep_id in self.nodes:
                    self.nodes[dep_id].dependents.add(task_id)
                else:
                    self.logger.warning(
                        "Task dependency not found",
                        task_id=task_id,
                        dependency_id=dep_id
                    )

        self.logger.debug(
            "Built execution graph",
            task_count=len(self.nodes),
        )

    def pre_complete_tasks(self, completed_ids: Set[str]):
        """Mark a set of tasks as already completed without running them."""
        for task_id in completed_ids:
            if task_id in self.nodes:
                result = TaskResult(
                    success=True,
                    task_id=task_id,
                    task_type=self.nodes[task_id].task.type.value,
                    duration_ms=0,
                    output="Skipped (previously completed or before start_stage)",
                )
                self.set_result(task_id, result)

    def get_all_dependencies(self, task_id: str) -> Set[str]:
        """Get all transitive dependencies for a task."""
        if task_id not in self.nodes:
            return set()

        deps = set()
        queue = list(self.nodes[task_id].dependencies)

        while queue:
            dep_id = queue.pop(0)
            if dep_id not in deps:
                deps.add(dep_id)
                if dep_id in self.nodes:
                    queue.extend(self.nodes[dep_id].dependencies)
        return deps

    def get_all_dependents(self, task_id: str) -> Set[str]:
        """Get all transitive dependents for a task."""
        if task_id not in self.nodes:
            return set()

        dependents = set()
        queue = list(self.nodes[task_id].dependents)

        while queue:
            dep_id = queue.pop(0)
            if dep_id not in dependents:
                dependents.add(dep_id)
                if dep_id in self.nodes:
                    queue.extend(self.nodes[dep_id].dependents)
        return dependents

    def get_ready_tasks(self) -> List[str]:
        """Get IDs of tasks that are ready to execute."""
        return [
            task_id for task_id, node in self.nodes.items()
            if node.is_ready and not node.is_complete
        ]

    def update_dependencies(self, completed_task_id: str) -> None:
        """Update dependencies after a task completes."""
        if completed_task_id not in self.nodes:
            return

        dependents = self.nodes[completed_task_id].dependents

        for dependent_id in dependents:
            if dependent_id in self.nodes:
                self.nodes[dependent_id].dependencies.remove(completed_task_id)

    def set_result(self, task_id: str, result: TaskResult) -> None:
        """Set the result for a task."""
        if task_id in self.nodes:
            self.nodes[task_id].result = result
            self.update_dependencies(task_id)

    def all_complete(self) -> bool:
        """Check if all tasks are complete."""
        return all(node.is_complete for node in self.nodes.values())

    def get_results(self) -> Dict[str, TaskResult]:
        """Get all task results."""
        return {
            task_id: node.result
            for task_id, node in self.nodes.items()
            if node.result is not None
        }

class GraphExecutor:
    """Executes tasks according to a dependency graph."""

    def __init__(
        self,
        tasks: List[Task],
        max_parallel: int = 5,
        context: Optional[Dict[str, Any]] = None,
        tasks_to_skip: Optional[Set[str]] = None,
        tasks_to_stop: Optional[Set[str]] = None,
        dry_run: bool = False,
    ):
        self.graph = TaskGraph(tasks)
        self.max_parallel = max_parallel
        self.context = context or {}
        self.tasks_to_stop = tasks_to_stop or set()
        self.dry_run = dry_run
        self.logger = get_logger("graph_executor")
        self.semaphore = asyncio.Semaphore(max_parallel)

        if tasks_to_skip:
            self.graph.pre_complete_tasks(tasks_to_skip)

    async def execute_task(self, task_id: str) -> None:
        """Execute a single task."""
        node = self.graph.nodes.get(task_id)
        if not node:
            return

        if task_id in self.tasks_to_stop:
            self.logger.info("Skipping task due to stop_stage", task_id=task_id)
            result = TaskResult(
                success=True,
                task_id=task_id,
                task_type=node.task.type.value,
                duration_ms=0,
                output="Task skipped due to stop_stage",
            )
            self.graph.set_result(task_id, result)
            return

        task_model = node.task
        executor = TaskExecutor(task_model)

        if self.dry_run:
            self.logger.info("DRY RUN: Would execute task", task_id=task_id)
            result = TaskResult(
                success=True,
                task_id=task_id,
                task_type=node.task.type.value,
                duration_ms=0,
                output="Dry run - not executed",
            )
            self.graph.set_result(task_id, result)
            return

        if not executor.should_run(self.context.get('site'), self.context):
            self.logger.info(
                "Skipping task due to condition",
                task_id=task_id,
                task_type=task_model.type.value,
            )
            result = TaskResult(
                success=True,
                task_id=task_id,
                task_type=task_model.type.value,
                duration_ms=0,
                output="Task skipped due to condition",
            )
            self.graph.set_result(task_id, result)
            return

        self.logger.info(
            "Executing task",
            task_id=task_id,
            task_type=task_model.type.value,
        )

        start_time = time.time()

        try:
            async with self.semaphore:
                task_result_dict = await executor.execute(self.context.get('site'), self.context)

            duration_ms = (time.time() - start_time) * 1000

            result = TaskResult(
                success=task_result_dict.get('success', False),
                task_id=task_id,
                task_type=task_model.type.value,
                duration_ms=duration_ms,
                output=task_result_dict.get('output'),
                error=task_result_dict.get('error'),
            )

            if result.success:
                self.logger.info(
                    "Task completed successfully",
                    task_id=task_id,
                    duration_ms=duration_ms,
                )
            else:
                self.logger.error(
                    "Task failed",
                    task_id=task_id,
                    error=result.error,
                    duration_ms=duration_ms,
                )

            self.graph.set_result(task_id, result)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Exception during task execution",
                task_id=task_id,
                error=str(e),
            )
            result = TaskResult(
                success=False,
                task_id=task_id,
                task_type=task_model.type.value,
                duration_ms=duration_ms,
                error=str(e),
            )
            self.graph.set_result(task_id, result)

    async def execute(self) -> Dict[str, TaskResult]:
        """Execute all tasks in dependency order."""
        self.logger.info(
            "Starting task graph execution",
            task_count=len(self.graph.nodes),
            max_parallel=self.max_parallel,
        )

        while not self.graph.all_complete():
            ready_tasks = self.graph.get_ready_tasks()

            if not ready_tasks:
                if not self.graph.all_complete():
                    self.logger.warning(
                        "No tasks ready to execute but not all complete - possible circular dependency"
                    )
                    break
                else:
                    break

            await asyncio.gather(*[
                self.execute_task(task_id) for task_id in ready_tasks
            ])

            await asyncio.sleep(0.1)

        return self.graph.get_results()
