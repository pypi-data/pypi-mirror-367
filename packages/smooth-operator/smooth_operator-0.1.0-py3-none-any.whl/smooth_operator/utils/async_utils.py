import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, Dict, List, Tuple, TypeVar

T = TypeVar('T')


async def run_parallel(
        items: List[T],
        operation: Callable[[T], Any],
        max_workers: int = 5
) -> List[Any]:
    """
    Run an operation on multiple items in parallel.

    Args:
        items: List of items to process
        operation: Function to call for each item
        max_workers: Maximum number of parallel workers

    Returns:
        List of operation results in the same order as the input items
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                operation,
                item
            )
            for item in items
        ]
        return await asyncio.gather(*tasks)


async def run_parallel_coroutines(
    coroutines: List[Coroutine]
) -> List[Any]:
    """
    Run a list of coroutines in parallel.

    Args:
        coroutines: A list of coroutine objects to run.

    Returns:
        A list of results from the coroutines.
    """
    results = await asyncio.gather(*coroutines)
    return results


def run_parallel_sync(
        items: List[T],
        operation: Callable[[T], Any],
        max_workers: int = 5
) -> List[Any]:
    """
    Synchronous wrapper for run_parallel.

    Args:
        items: List of items to process
        operation: Function to call for each item
        max_workers: Maximum number of parallel workers

    Returns:
        List of operation results in the same order as the input items
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_parallel(items, operation, max_workers))
    finally:
        loop.close()


def run_parallel_sync_coroutines(
    func: Callable[..., Coroutine],
    args_list: List[Tuple],
    max_workers: int = 5
) -> List[Any]:
    """
    Synchronously run a function with different arguments in parallel.

    Args:
        func: The asynchronous function to run.
        args_list: A list of argument tuples for the function.
        max_workers: Maximum number of parallel workers.

    Returns:
        List of function results in the same order as the input arguments.
    """
    coroutines = [func(*args) for args in args_list]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_parallel_coroutines(coroutines))
    finally:
        loop.close()
