# smooth_operator/operations/updater/runner.py
import sys
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from ...core.models import Site, Task as TaskModel
from ...channels.terminus import Terminus
from ...utils.async_utils import run_parallel_coroutines
from ...utils.logging import get_logger
from ..executor.graph import GraphExecutor, TaskGraph
from ..stages.manager import StageManager
from .manifest import UpdateManifest


class UpstreamUpdater:
    """
    Orchestrates the update process across multiple sites.
    """

    def __init__(
            self,
            manifest_path: List[str],
            sites: Optional[List[str]] = None,
            parallel: bool = False,
            max_workers: int = 5,
            debug: bool = False,
            state_dir: Optional[str] = None,
            start_stage: Optional[str] = None,
            stop_stage: Optional[str] = None,
            re_run: bool = False,
            refresh: bool = False
    ):
        """
        Initialize the updater.

        Args:
            manifest_path: List of paths to the manifest files
            sites: List of site names (if None, all sites will be used)
            parallel: Whether to run updates in parallel
            max_workers: Maximum number of parallel workers
            debug: Enable debug output
            state_dir: Directory to store state information
            start_stage: Stage to start from
            stop_stage: Stage to stop at
            re_run: Whether to re-run previously completed sites
            refresh: Force a refresh of the Pantheon site list
        """
        self.manifest = UpdateManifest(manifest_path)
        self.parallel = parallel
        self.max_workers = max_workers
        self.debug = debug
        self.start_stage = start_stage
        self.stop_stage = stop_stage
        self.re_run = re_run
        self.state_dir = state_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "logs"
        )
        self.logger = get_logger("upstream_updater")

        # Load sites
        terminus = Terminus(debug=debug)
        if refresh:
            self.logger.info("Refreshing site list from Pantheon...")
            terminus.refresh_sites()

        all_sites = [Site(**s) for s in terminus.get_sites()]

        if sites:
            self.sites = [s for s in all_sites if s.name in sites]
        else:
            self.sites = all_sites

        # Filter out completed sites if not re-running
        if not re_run:
            self.sites = [
                s for s in self.sites
                if not StageManager(self.state_dir, s.id).is_completed('__all__')
            ]

        self.logger.info(f"Loaded {len(self.sites)} sites for update")

    async def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute the update process.

        Args:
            dry_run: Whether to perform a dry run

        Returns:
            Results of the update process
        """
        start_time = time.time()

        self.logger.info(f"Starting update process for {len(self.sites)} sites")
        self.logger.info(f"Manifest: {self.manifest.name} - {self.manifest.description}")

        if not self.sites:
            self.logger.warning("No sites found for update")
            return {
                "success": False,
                "error": "No sites found for update",
                "sites_processed": 0,
                "elapsed_time": time.time() - start_time
            }

        if dry_run:
            self.logger.info("DRY RUN MODE - No changes will be made")

        # Execute pre-process hooks
        if not dry_run:
            await self._execute_hooks("pre-process")

        results = {
            "success": True,
            "sites": {}
        }

        # Execute tasks for each site
        if self.parallel and not dry_run and len(self.sites) > 1:
            # Process sites in parallel
            coroutines = [self._update_site(site, dry_run) for site in self.sites]
            site_results = await run_parallel_coroutines(coroutines)

            # Store results
            for site, site_result in zip(self.sites, site_results):
                results["sites"][site.name] = site_result
                if not site_result.get("success", False):
                    results["success"] = False
        else:
            # Process sites sequentially
            for site in self.sites:
                site_result = await self._update_site(site, dry_run)
                results["sites"][site.name] = site_result
                if not site_result.get("success", False):
                    results["success"] = False

        # Execute post-process hooks
        if not dry_run:
            await self._execute_hooks("post-process")

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        results["elapsed_time"] = elapsed_time
        results["sites_processed"] = len(self.sites)

        self.logger.info(f"Update process completed in {elapsed_time:.2f} seconds")
        self.logger.info(f"Processed {len(self.sites)} sites with "
                        f"success: {results['success']}")

        return results

    async def _update_site(self, site: Site, dry_run: bool) -> Dict[str, Any]:
        """
        Update a single site according to the manifest.

        Args:
            site: The site to update
            dry_run: Whether to perform a dry run

        Returns:
            Results of the update process for this site
        """
        self.logger.info(f"Updating site: {site.name}", site_id=site.id)

        stage_manager = StageManager(self.state_dir, site.id)
        if self.re_run:
            stage_manager.reset()

        # Execute pre-run hooks for this site
        if not dry_run:
            await self._execute_hooks("pre-run", site)

        context = {
            "site": site,
            "site_name": site.name,
            "manifest": self.manifest.model,
            "dry_run": dry_run,
            "previous_results": {},
            "stage_manager": stage_manager,
        }

        # Use a temporary graph to resolve dependencies for start/stop stages
        graph = TaskGraph(self.manifest.tasks)
        tasks_to_skip = set()
        tasks_to_stop = set()

        if not self.re_run:
            tasks_to_skip.update(stage_manager.completed_stages)

        if self.start_stage:
            tasks_to_skip.update(graph.get_all_dependencies(self.start_stage))

        if self.stop_stage:
            tasks_to_stop.update(graph.get_all_dependents(self.stop_stage))

        executor = GraphExecutor(
            tasks=self.manifest.tasks,
            max_parallel=self.max_workers,
            context=context,
            tasks_to_skip=tasks_to_skip,
            tasks_to_stop=tasks_to_stop,
            dry_run=dry_run
        )

        task_results = await executor.execute()

        # Update stage manager with completed tasks
        for task_id, result in task_results.items():
            if result.success:
                stage_manager.mark_completed(task_id)

        site_results = {
            "success": all(r.success for r in task_results.values() if not r.error),
            "tasks": {res.task_id: res.__dict__ for res in task_results.values()}
        }

        # If all tasks completed successfully, mark the site as fully completed
        if site_results["success"] and not dry_run:
            stage_manager.mark_completed('__all__')
            # Execute post-update hooks for this site
            await self._execute_hooks("post-update", site)

        return site_results

    async def _execute_hooks(self, hook_name: str, site: Optional[Site] = None):
        """
        Execute scripts for a given hook.

        Args:
            hook_name: The name of the hook to execute (e.g., "pre-run")
            site: The site context for the hook (if applicable)
        """
        scripts = self.manifest.get_hook(hook_name)
        if not scripts:
            return

        self.logger.info(f"Executing {hook_name} hooks...")
        for script_path in scripts:
            if not os.path.exists(script_path):
                self.logger.error(f"Hook script not found: {script_path}")
                continue

            context = {
                "manifest": self.manifest.model,
                "site": site,
                "hook_name": hook_name,
            }

            # Create a task-like object for execution
            hook_task_model = TaskModel(
                id=f"hook_{hook_name}_{os.path.basename(script_path)}",
                type=TaskModel.SCRIPT,
                params={"path": script_path, "args": {}},
                description=f"Hook script: {os.path.basename(script_path)}"
            )
            executor = TaskExecutor(hook_task_model)

            try:
                # Hooks should not have conditions, they always run
                result = await executor.execute(site, context)
                if not result.get("success"):
                    self.logger.error(
                        f"Hook script {script_path} failed: {result.get('error')}"
                    )
            except Exception as e:
                self.logger.error(f"Exception executing hook script {script_path}: {str(e)}")
