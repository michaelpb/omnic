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
            if 'Task cannot await on itself' not in str(e):
                raise e

