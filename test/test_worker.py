"""
Tests for `worker` module.
"""
import asyncio

import pytest

from omnic.worker import Worker, AioWorker, Task

class RunOnceWorker(Worker):
    '''
    Test worker to test abstract Worker base class
    '''
    def __init__(self):
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


class TestBaseWorker:
    def setup_class(cls):
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    @pytest.mark.asyncio
    async def test_run_once(self):
        worker = RunOnceWorker()
        def fake_func(*args):
            worker.called_args = args
        worker.fake_next = (Task.FUNC, (fake_func, 1, 2, 3))
        res = await worker.run()
        assert res is None
        assert worker.called_args == (1, 2, 3)


class FakeAioQueue(list):
    async def put(self, item):
        self.append(item)

    async def get(self):
        return self.pop(0)


class TestAsyncioWorker:
    def setup_class(cls):
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    @pytest.mark.asyncio
    async def test_run_once(self):
        worker = AioWorker(FakeAioQueue())
        worker.called = 0
        def fake_func(*args):
            called = worker.called
            assert args == (1 + called, 2 + called, 3 + called)
            worker.called += 1
            if worker.called > 3:
                worker.running = False
        await worker.enqueue(Task.FUNC, (fake_func, 1, 2, 3))
        await worker.enqueue(Task.FUNC, (fake_func, 2, 3, 4))
        await worker.enqueue(Task.FUNC, (fake_func, 3, 4, 5))
        await worker.enqueue(Task.FUNC, (fake_func, 4, 5, 6))
        await worker.enqueue(Task.FUNC, (fake_func, 5, 6, 7))
        res = await worker.run()
        assert res is None
        assert worker.called == 4

