from omnic.worker import Worker
from base64 import b64decode


class Magic:
    JPEG = bytes([0xff, 0xd8, 0xff, 0xe0])
    PNG = bytes([0x89, 0x50, 0x4e, 0x47])
    PNG_PIXEL_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    PNG_PIXEL_B = b64decode(PNG_PIXEL_B64)


class RunOnceWorker(Worker):
    '''
    Worker that stops running after it has gone through a given queue.
    New tasks get put into a next_queue that is only accessible after
    switching to it.
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
