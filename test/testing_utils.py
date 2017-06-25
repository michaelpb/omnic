from base64 import b64decode
from omnic.worker.base import BaseWorker


class Magic:
    JPEG = bytes([0xff, 0xd8, 0xff, 0xe0])
    PNG = bytes([0x89, 0x50, 0x4e, 0x47])
    PNG_PIXEL_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    PNG_PIXEL_B = b64decode(PNG_PIXEL_B64)


class MockWorker(BaseWorker):
    '''
    Test worker to test abstract Worker base class
    '''

    def __init__(self):
        super().__init__()
        self.fake_next = None
        self._running = True
        self.called_args = None

    @property
    def running(self):
        if not self._running:
            return False
        self._running = False
        return True

    async def get_next(self):
        return self.fake_next

    async def check_download(self, foreign_resource):
        self.check_download_was_called = True
        return True

    async def check_convert(self, converter, in_r, out_r):
        self.check_convert_was_called = True
        return True


class MockAioQueue(list):
    async def put(self, item):
        self.append(item)

    async def get(self):
        return self.pop(0)

