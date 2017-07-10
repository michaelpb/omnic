from omnic.worker.base import BaseWorker


class RunOnceWorker(BaseWorker):
    '''
    Worker that stops running after it has gone through a given queue.
    New tasks get put into a next_queue that is only accessible after
    switching to it.

    Useful for testing.
    '''

    def __init__(self, queue=[]):
        super().__init__()
        self.queue = queue
        self.next_queue = []

    async def run_once(self):
        self.queue = self.next_queue
        self.next_queue = []
        await self.run()

    @property
    def running(self):
        return bool(self.queue)

    async def queue_size(self):
        return len(self.next_queue)

    async def enqueue(self, *args):
        self.next_queue.append(args)

    async def get_next(self):
        return self.queue.pop(0)

    async def check_download(self, foreign_resource):
        self.check_download_was_called = True
        return True

    async def check_convert(self, converter, in_r, out_r):
        self.check_convert_was_called = True
        return True


class ForegroundWorker(BaseWorker):
    '''
    Useful for testing and local conversion, runs tasks as soon as enqueued
    without any checks, or touching the queue, or catching exceptions

    Useful for testing.
    '''

    def __init__(self, queue=None):
        self.running = False
        super().__init__()

    async def queue_size(self):
        return 0

    async def enqueue(self, task_type, args):
        '''
        '''
        method = {
            Task.FUNC: self.run_func,
            Task.DOWNLOAD: self.run_download,
            Task.CONVERT: self.run_convert,
        }[task_type]
        await method(*args)

    async def get_next(self):
        return None

    async def check_download(self, foreign_resource):
        return True

    async def check_convert(self, converter, in_r, out_r):
        return True
