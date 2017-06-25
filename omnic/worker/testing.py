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
