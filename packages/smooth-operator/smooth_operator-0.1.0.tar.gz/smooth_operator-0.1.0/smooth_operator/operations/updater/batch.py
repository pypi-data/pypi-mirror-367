# smooth_operator/operations/updater/batch.py
import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from ...core.models import Site
from ...utils.logging import get_logger
from .runner import UpstreamUpdater
from ..executor.graph import TaskResult

@dataclass
class BatchResult:
    """Results from a batch execution."""
    batch_id: str
    start_time: float
    end_time: float
    duration_ms: float
    sites_processed: int
    successful_sites: int
    failed_sites: int
    results: Dict[str, List[TaskResult]]

class BatchProcessor:
    """Processes sites in batches for better performance and reliability."""

    def __init__(
        self,
        sites: List[Site],
        manifest_path: List[str],
        batch_size: int = 10,
        wait_between_batches: int = 60,
        max_workers_per_batch: int = 5,
        dry_run: bool = False,
        debug: bool = False,
        state_dir: Optional[str] = None,
        re_run: bool = False,
    ):
        self.sites = sites
        self.manifest_path = manifest_path
        self.batch_size = batch_size
        self.wait_between_batches = wait_between_batches
        self.max_workers_per_batch = max_workers_per_batch
        self.dry_run = dry_run
        self.debug = debug
        self.state_dir = state_dir
        self.re_run = re_run
        self.logger = get_logger("batch_processor")

    def _create_batches(self) -> List[List[Site]]:
        """Divide sites into batches."""
        return [self.sites[i:i + self.batch_size] for i in range(0, len(self.sites), self.batch_size)]

    async def process(self) -> List[BatchResult]:
        """Process all sites in batches."""
        batches = self._create_batches()
        self.logger.info(
            "Starting batch processing",
            total_sites=len(self.sites),
            batch_count=len(batches),
            batch_size=self.batch_size,
        )

        results = []

        for idx, batch in enumerate(batches):
            batch_id = f"batch_{idx+1}"
            self.logger.info(
                f"Processing batch {idx+1}/{len(batches)}",
                batch_id=batch_id,
                site_count=len(batch),
            )

            start_time = time.time()

            updater = UpstreamUpdater(
                manifest_path=self.manifest_path,
                sites=[s.name for s in batch],
                parallel=True,
                max_workers=self.max_workers_per_batch,
                debug=self.debug,
                state_dir=self.state_dir,
                re_run=self.re_run,
            )

            batch_results = await updater.execute(dry_run=self.dry_run)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            successful_sites = sum(1 for r in batch_results.get('sites', {}).values() if r.get('success'))
            failed_sites = len(batch) - successful_sites

            result = BatchResult(
                batch_id=batch_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                sites_processed=len(batch),
                successful_sites=successful_sites,
                failed_sites=failed_sites,
                results=batch_results,
            )
            results.append(result)

            self.logger.info(
                f"Batch {idx+1} completed",
                batch_id=batch_id,
                duration_ms=duration_ms,
                success_rate=f"{successful_sites}/{len(batch)}",
            )

            if idx < len(batches) - 1 and self.wait_between_batches > 0:
                self.logger.info(f"Waiting {self.wait_between_batches}s before next batch")
                await asyncio.sleep(self.wait_between_batches)

        return results

