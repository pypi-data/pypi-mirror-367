# smooth_operator/operations/updater/task.py
from typing import Dict, Any, Optional
import subprocess
import json
import os
import asyncio
import jsonpickle
from ...core.models import Site
from ...utils.logging import get_logger
from ...core.models import Task as TaskModel


class TaskExecutor:
    """Executes a task from the manifest."""

    def __init__(self, task: TaskModel):
        self.task = task
        self.logger = get_logger(f"task.{task.type.value}")

    async def execute(self, site: Site, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute this task against a site.

        Args:
            site: The site to run against
            context: Execution context

        Returns:
            Task result as a dictionary
        """
        self.logger.info(f"Executing {self.task.description or self.task.id} for {site.name}")

        try:
            # Handle different task types
            if self.task.type == "terminus_command":
                result = await self._execute_terminus_command(site, context)
            elif self.task.type == "drush_command":
                result = await self._execute_drush_command(site, context)
            elif self.task.type == "script":
                result = await self._execute_script(site, context)
            elif self.task.type == "composer_update":
                result = await self._execute_composer_update(site, context)
            else:
                raise ValueError(f"Unknown task type: {self.task.type}")

            if not result.get("success", False):
                self.logger.error(
                    f"Task failed: {self.task.description} for {site.name} - "
                    f"{result.get('error', 'Unknown error')}"
                )
            return result

        except Exception as e:
            self.logger.error(f"Exception during task execution: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _execute_terminus_command(self, site: Site, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a terminus command."""
        from ...channels.terminus import Terminus

        terminus = Terminus()
        command = self.task.params.get("command", "")
        command = self._render_template(command, site, context)

        success, output = await terminus.execute(command)
        return {"success": success, "output": output, "command": command}

    async def _execute_drush_command(self, site: Site, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a drush command."""
        from ...channels.terminus import Terminus

        terminus = Terminus()
        command = self.task.params.get("command", "")
        environment = self.task.params.get("environment", "dev")
        command = self._render_template(command, site, context)

        full_command = f"drush {site.name}.{environment} {command}"
        success, output = await terminus.execute(full_command)
        return {"success": success, "output": output, "command": full_command}

    async def _execute_script(self, site: Site, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Python script."""
        script_path = self.task.params.get("path", "")
        script_args = self.task.params.get("args", {})

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Prepare arguments for the script
        cli_args = {"site": site.name}
        cli_args_json = json.dumps(cli_args)
        manifest_json = jsonpickle.encode(context.get("manifest", {}))
        stage_json = jsonpickle.encode(self.task)
        script_args_json = json.dumps(script_args)

        command = f"python {script_path} '{cli_args_json}' '{manifest_json}' '{stage_json}' '{script_args_json}'"

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {
                    "success": False,
                    "output": stderr.decode(),
                    "error": f"Script execution failed with code {process.returncode}"
                }
            try:
                output = json.loads(stdout)
                return {"success": True, "output": output}
            except json.JSONDecodeError:
                return {"success": True, "output": stdout.decode()}
        except Exception as e:
            return {"success": False, "output": str(e), "error": "Script execution error"}

    async def _execute_composer_update(self, site: Site, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a composer update."""
        from ...channels.lando import Lando

        lando = Lando()
        packages = self.task.params.get("packages", [])
        command = "update --with-dependencies"
        if packages:
            command = f"update {' '.join(packages)} --with-dependencies"

        success, output = await lando.execute_composer(command)
        return {"success": success, "output": output, "command": command}

    def _render_template(self, template_string: str, site: Site, context: Dict[str, Any]) -> str:
        """Render a template string with context variables."""
        rendered_string = template_string.replace("{site.name}", site.name)

        for key, value in context.items():
            if isinstance(value, str):
                rendered_string = rendered_string.replace(f"{{{key}}}", value)

        # Render previous results
        for task_id, result in context.get("previous_results", {}).items():
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, str):
                        rendered_string = rendered_string.replace(f"{{{task_id}.{key}}}", value)

        return rendered_string

    def should_run(self, site: Site, context: Dict[str, Any]) -> bool:
        """
        Check if this task should run based on conditions.

        Args:
            site: The site to run against
            context: Execution context

        Returns:
            True if the task should run, False otherwise
        """
        if not self.task.condition:
            return True

        # Create a safe evaluation environment
        eval_globals = {"__builtins__": {}}
        eval_locals = {
            "site": site,
            "context": context,
            "task_type": self.task.type,
            "params": self.task.params
        }

        try:
            result = eval(self.task.condition, eval_globals, eval_locals)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {str(e)}")
            return False
