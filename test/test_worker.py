"""
Tests for `worker` module.
"""

from unittest.mock import MagicMock, patch

import pytest

from omnic import singletons
from omnic.types.resource import TypedForeignResource, TypedResource
from omnic.types.typestring import TypeString
from omnic.worker.aioworker import AioWorker
from omnic.worker.base import BaseWorker
from omnic.worker.enums import Task
from omnic.worker.testing import (ForegroundWorker, RunOnceWorker,
                                  autodrain_worker)

from .testing_utils import MockAioQueue, MockWorker


class WorkerTestBase:
    @classmethod
    def setup_class(cls):
        class FakeSettings:
            LOGGING = None
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

    def test_get_method(self):
        worker = MockWorker()
        assert worker._get_method(Task.FUNC) == worker.run_func
        assert worker._get_method(Task.DOWNLOAD) == worker.run_download
        assert worker._get_method(Task.CONVERT) == worker.run_convert
        assert worker._get_method(Task.MULTICONVERT) == worker.run_multiconvert


class TestWorkerTasks:
    def _step(self, num, a, b):
        return MagicMock(name='con%i' % num), TypeString(a), TypeString(b)

    def setup_method(self, method):
        self.url_string = 'http://test/thing.avi'
        self.patchers = []

        patcher = patch('omnic.worker.tasks.singletons')
        self.singletons = patcher.start()
        self.singletons.converter_graph.find_path.return_value = [
            self._step(0, 'AVI', 'MP4'),
            self._step(1, 'MP4', 'PNG'),
            self._step(2, 'PNG', 'JPG'),
            self._step(3, 'JPG', 'thumb.jpg:123x456'),
        ]
        self.patchers.append(patcher)

        patcher = patch('omnic.worker.tasks.ForeignResource')
        self.foreign_resource = patcher.start()
        self.patchers.append(patcher)

    def teardown_method(self, method):
        for patcher in self.patchers:
            patcher.stop()

    @pytest.mark.asyncio
    async def test_run_multiconvert(self):
        worker = RunOnceWorker()
        await worker.run_multiconvert(self.url_string, 'thumb.jpg:123x456')
        assert len(worker.next_queue) == 4
        for task, args in worker.next_queue:
            assert task == Task.CONVERT
        assert worker.next_queue[0][1][1] == \
            TypedForeignResource(self.url_string, TypeString('AVI'))
        assert worker.next_queue[0][1][2] == \
            TypedResource(self.url_string, TypeString('MP4'))
        assert worker.next_queue[1][1][1] == \
            TypedResource(self.url_string, TypeString('MP4'))
        assert worker.next_queue[1][1][2] == \
            TypedResource(self.url_string, TypeString('PNG'))
        assert worker.next_queue[3][1][1] == \
            TypedResource(self.url_string, TypeString('JPG'))
        assert worker.next_queue[3][1][2] == \
            TypedResource(self.url_string, TypeString('thumb.jpg:123x456'))


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


class TestForegroundWorker(WorkerTestBase):
    @pytest.mark.asyncio
    async def test_run(self):
        worker = ForegroundWorker()
        worker.called = 0

        def fake_func(*args):
            called = worker.called
            assert args == (1 + called, 2 + called, 3 + called)
            worker.called += 1
        await worker.enqueue(Task.FUNC, (fake_func, 1, 2, 3))
        await worker.enqueue(Task.FUNC, (fake_func, 2, 3, 4))
        await worker.enqueue(Task.FUNC, (fake_func, 3, 4, 5))
        assert worker.called == 3

    @pytest.mark.asyncio
    async def test_worker_decorator(self):
        self.called = 0

        def fake_func(*args):
            assert args == (1 + self.called, 2 + self.called, 3 + self.called)
            self.called += 1

        with autodrain_worker() as worker:
            assert worker
            assert isinstance(worker, BaseWorker)
            await singletons.workers.async_enqueue_sync(fake_func, 1, 2, 3)
            await singletons.workers.async_enqueue_sync(fake_func, 2, 3, 4)
            await singletons.workers.async_enqueue_sync(fake_func, 3, 4, 5)
        assert self.called == 3
