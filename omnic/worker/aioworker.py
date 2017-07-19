
from omnic import singletons

from .base import BaseWorker


class AioWorker(BaseWorker):
    '''
    Uses an asyncio Queue to enqueue tasks
    '''

    def __init__(self, queue=None):
        super().__init__()
        self.running = True
        if queue is None:
            # If no specific queue was specified, use singleton one
            queue = singletons.eventloop.worker_queue
        self.queue = queue

        # Sets for locking to prevent race conditions
        self.downloading_resources = set()
        self.converting_resources = set()

    async def queue_size(self):
        return self.queue.qsize()

    async def enqueue(self, task_type, args):
        await self.queue.put((task_type, args))

    async def get_next(self):
        '''
        Await the next item on the queue
        '''
        task_type, args = await self.queue.get()
        return task_type, args

    async def check_download(self, foreign_resource):
        if foreign_resource in self.downloading_resources:
            return False
        self.downloading_resources.add(foreign_resource)
        return True

    async def check_convert(self, converter, in_r, out_r):
        key = (in_r, out_r)
        if key in self.converting_resources:
            return False
        self.converting_resources.add(key)
        return True

    async def check_multiconvert(self, url_string, to_type):
        key = (url_string, to_type)
        if key in self.multiconverting_resources:
            return False
        self.converting_resources.add(key)
        return True
