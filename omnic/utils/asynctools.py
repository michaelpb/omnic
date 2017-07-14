import asyncio


async def await_all():
    '''
    Simple utility function that drains all tasks
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
