import os
from base64 import b64decode
from os.path import exists, join

from omnic.types.detectors import Detector
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


class DummyDetector(Detector):
    pass


class AgreeableDetector(Detector):
    def can_detect(self, path):
        return True

    def detect(self, path):
        return 'something'


def rm_tmp_file(path):
    # Utility function for completely removing a temp file and any superfluous
    # dirs used to contain it
    try:
        os.remove(path)
    except OSError:
        pass
    try:
        os.removedirs(os.path.dirname(path))
    except OSError:
        pass


def rm_tmp_files(*paths, prefixes=[]):
    # For a group of paths that could be in multiple locations
    for path in paths:
        if prefixes:
            for prefix in prefixes:
                rm_tmp_file(os.path.join(prefix, path))
        else:
            rm_tmp_file(path)


# Some testing utilities borrowed from another python package (stowage)
# TODO: refactor these into above
def write_tmp_file(path):
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass
    with open(path, 'w+') as f:
        f.write('%s contents' % path)


def gen_tmp_files(root, files):
    for fn in files:
        write_tmp_file(join(root, fn))


def clear_tmp_files(root, files):
    for fn in files:
        path = join(root, fn)
        if exists(path):
            os.remove(path)
        try:
            os.removedirs(os.path.dirname(path))
        except OSError:
            pass
