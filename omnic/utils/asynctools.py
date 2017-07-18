import asyncio
import functools
import inspect
from unittest.mock import MagicMock


async def await_all():
    '''
    Simple utility function that drains all pending tasks
    '''
    tasks = asyncio.Task.all_tasks()
    for task in tasks:
        try:
            await task
        except RuntimeError as e:
            # Python 3.5.x: Error if attempting to await parent task
            if 'Task cannot await on itself' not in str(e):
                raise e
        except AssertionError as e:
            # Python 3.6.x: Error if attempting to await parent task
            if 'yield from wasn\'t used with future' not in str(e):
                raise e


def coerce_to_synchronous(func):
    '''
    Given a function that might be async, wrap it in an explicit loop so it can
    be run in a synchronous context.
    '''
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(func(*args, **kwargs))
            finally:
                loop.close()
        return sync_wrapper
    return func


class CoroutineMock(MagicMock):
    '''
    MagicMock that yields a coroutine, for mocking async functions
    '''

    def __await__(self, *args, **kwargs):
        future = asyncio.Future()
        future.set_result(self)
        result = yield from future
        return result
