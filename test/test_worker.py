"""
Tests for `worker` module.
"""

import pytest

from omnic.worker.aioworker import AioWorker
from omnic.worker.enums import Task
from omnic import singletons

from .testing_utils import MockWorker, MockAioQueue


class WorkerTestBase:
    @classmethod
    def setup_class(cls):
        class FakeSettings:
            LOGGING = {}
        singletons.settings.use_settings(FakeSettings)

    @classmethod
    def teardown_class(cls):
        singletons.settings.use_previous_settings()


class TestBaseWorker(WorkerTestBase):
    @pytest.mark.asyncio
    async def test_run_func(self):
        worker = MockWorker()

        def fake_func(*args):
            worker.called_args = args
        worker.fake_next = (Task.FUNC, (fake_func, 1, 2, 3))
        res = await worker.run()
        assert res is None
        assert worker.called_args == (1, 2, 3)


class TestAsyncioWorker(WorkerTestBase):
    @pytest.mark.asyncio
    async def test_run_once(self):
        worker = AioWorker(MockAioQueue())
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
