from urllib.parse import urlencode

import os
import tempfile

from omnic.worker.enums import Task
from omnic.worker.testing import RunOnceWorker
from omnic import singletons

from .testing_utils import Magic


class BaseRoutes:
    @classmethod
    def setup_class(cls):
        from omnic.server import runserver

        cls.host = '127.0.0.1:42101'
        cls.tmp_path_prefix = tempfile.mkdtemp()

        class FakeSettings:
            PATH_PREFIX = cls.tmp_path_prefix
            PATH_GROUPING = None
            ALLOWED_LOCATIONS = {cls.host}
            LOGGING = None
        singletons.settings.use_settings(FakeSettings)

        cls.app = runserver('ignored', 0, just_setup_app=True)

        singletons.workers.clear()
        cls.worker = RunOnceWorker()
        singletons.workers.append(cls.worker)

        # Disable all HTTP logging for sanic since it leaves open FDs and
        # causes warnings galore
        from sanic.config import LOGGING
        LOGGING.clear()

    def _get(self, *args, **kwargs):
        kwargs.setdefault('debug', False)
        kwargs.setdefault('gather_request', False)
        kwargs.setdefault('server_kwargs', {
            'log_config': None,
        })
        return self.app.test_client.get(*args, **kwargs)

    @classmethod
    def teardown_class(cls):
        singletons.settings.use_previous_settings()


class TestBuiltinTestRoutes(BaseRoutes):
    def test_images(self, event_loop):
        # NOTE: For some reason due to incorrect event loops, etc, one can't
        # use pytest.mark.asyncio, making the tests themselves async
        await_async = event_loop.run_until_complete
        response = self._get('/test/test.jpg')
        assert response.status == 200
        value = await_async(response.read())
        assert value == Magic.JPEG  # check its magic JPEG bytes

        response = self._get('/test/test.png')
        assert response.status == 200
        value = await_async(response.read())
        assert value[:4] == Magic.PNG  # check its magic PNG bytes

    def test_images_sync(self):
        response = self._get('/test/test.jpg')
        assert response.status == 200
        response = self._get('/test/test.png')
        assert response.status == 200

    def test_misc_binary_sync(self):
        # For now we just skip testing magic bytes for these, since too
        # too specific
        response = self._get('/test/empty.zip')
        assert response.status == 200
        response = self._get('/test/test.3ds')
        assert response.status == 200


class TestAdmin(BaseRoutes):
    def test_admin_page(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value

    def test_conversion_page(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/conversion/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value

    def test_ajax_workers(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/ajax/workers/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'queue' in value

    def test_graph(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/graph/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value

    def test_subgraph(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/graph/JPEG/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value


class TestBuiltinMediaRoutes(BaseRoutes):
    def test_media_placeholder(self, event_loop):
        # NOTE: For some reason due to incorrect event loops, etc, one can't
        # use pytest.mark.asyncio, making the tests themselves async
        await_async = event_loop.run_until_complete

        # reverse test.png route
        qs = '?%s' % urlencode({'url': '%s/test.png' % self.host})
        response = self._get('/media/thumb.jpg:200x200/%s' % qs)

        # ensure that it gave back the placeholder
        value = await_async(response.read())
        assert response.status == 200
        assert response.headers['Content-Type'] == 'image/png'
        assert value[:4] == Magic.PNG  # check its magic PNG bytes

        # Inspect whats been enqueued, ensure as expected
        q = self.worker.next_queue
        assert q
        assert q[0]
        assert q[0][0] == Task.DOWNLOAD
        assert q[1][0] == Task.FUNC
        assert q[1][1][1] == 'http://127.0.0.1:42101/test.png'
        assert q[1][1][2] == 'thumb.jpg:200x200'

        # Run through queue... this should download the resource, and in
        # turn enqueue the remaining steps
        await_async(self.worker.run_once())
        q = self.worker.queue
        assert len(q) == 0

        # Now make sure resource is downloaded to expected spot (no path
        # grouping, so just tmppath/test.png)
        path = os.path.join(self.tmp_path_prefix, 'test.png')
        assert os.path.exists(path)

        # TODO: not fully tested here, need to write after refactor of
        # 'enqueue' helper functions in server
        q = self.worker.next_queue
        assert q
        assert len(q) == 1
        assert q[0]
        assert q[0][0] == Task.CONVERT
        await_async(self.worker.run_once())

        # ensure nothing more was added to queue
        q = self.worker.next_queue
        assert not q
