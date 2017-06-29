import os
import tempfile
from urllib.parse import urlencode

import pytest

from omnic import singletons
from omnic.builtin.converters.manifest import ManifestDownloader
from omnic.types.detectors import DIRECTORY
from omnic.types.resource import ForeignResource, TypedResource
from omnic.worker.enums import Task
from omnic.worker.testing import RunOnceWorker

from .testing_utils import Magic


class BaseUnitTest:
    @classmethod
    def setup_class(cls):
        cls.host = '127.0.0.1:42101'
        cls.tmp_path_prefix = tempfile.mkdtemp(prefix='omnic_tests_')

        class FakeSettings:
            PATH_PREFIX = cls.tmp_path_prefix
            PATH_GROUPING = None
            ALLOWED_LOCATIONS = {cls.host}
            LOGGING = None
        singletons.settings.use_settings(FakeSettings)

        singletons.workers.clear()
        cls.worker = RunOnceWorker()
        singletons.workers.append(cls.worker)

    @classmethod
    def teardown_class(cls):
        singletons.settings.use_previous_settings()


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

    def test_manifest_json(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/test/manifest.json')
        assert response.status == 200
        value = await_async(response.read())
        assert value[:7] == b'{"files'

    def test_manifest_json_download(self, event_loop):
        await_async = event_loop.run_until_complete

        # Download the manifest.json file from test server
        url = 'http://%s/test/manifest.json' % self.host
        f_res = ForeignResource(url)
        response = self._get('/test/manifest.json')
        assert response.status == 200
        value = await_async(response.read())
        with f_res.cache_open('wb') as fd:
            fd.write(value)

        # Set up resources
        in_resource = f_res.guess_typed()
        in_resource.symlink_from(f_res)
        out_resource = TypedResource(url, DIRECTORY)

        # Do actual convert (which should entail downloads)
        downloader = ManifestDownloader()
        await_async(downloader.convert(in_resource, out_resource))

        # Ensure everything got created
        files = set(os.listdir(out_resource.cache_path))
        assert files == {'some_zip.zip', 'test.3ds', 'test.jpg', 'test.png'}

    @pytest.mark.skip(':(')
    def test_manifest_json_download_with_testserver(self, event_loop):
        await_async = event_loop.run_until_complete

        # Download the manifest.json file from test server
        url = 'http://%s/test/manifest.json' % self.host
        singletons.server.fork_testing_server()
        f_res = ForeignResource(url)
        f_res.download()
        #response = self._get('/test/manifest.json')
        #assert response.status == 200
        #value = await_async(response.read())
        # with f_res.cache_open('wb') as fd:
        #    fd.write(value)

        # Set up resources
        in_resource = f_res.guess_typed()
        in_resource.symlink_from(f_res)
        out_resource = TypedResource(url, DIRECTORY)

        # Do actual convert (which should entail downloads)
        downloader = ManifestDownloader()
        await_async(downloader.convert(in_resource, out_resource))
        singletons.server.kill_testing_server()

        # Ensure everything got downloaded
        files = set(os.listdir(out_resource.cache_path))
        assert files == {'some_zip.zip', 'test.3ds', 'test.jpg', 'test.png'}
        with open(os.path.join(out_resource.cache_path, 'test.jpg'), 'rb') as f:
            assert f.read() == Magic.JPEG  # check its magic JPEG bytes


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


class TestViewerViews(BaseUnitTest):
    def setup_method(self, method):
        from omnic.builtin.services.viewer import views
        singletons.server.configure()
        self.v = views

    @pytest.mark.asyncio
    async def test_viewers_js(self):
        # Get raw response of view
        r = (await self.v.viewers_js(None)).output()
        assert b'200 OK' in r
        assert b'application/javascript' in r
        assert b'window._OMNIC_VIEWER_BUNDLE_IS_LOADED = false' in r

        # Inspect whats been enqueued, ensure as expected
        q = self.worker.next_queue
        assert len(q) == 1
        assert q
        assert q[0]
        assert q[0][0] == Task.FUNC
        assert q[0][1][2] == 'min.js'
        await self.worker.run_once()
        return # TODO finish this crap

        # Run through appending coros... this should turn enqueue the remaining
        # steps
        # NOTE: Only necessary until we rewrite enqueuing process + clean up
        # async vs sync w.r.t. tasks
        singletons.workers._tmp_do_hack_enqueue = True
        for coro in singletons.workers._tmp_hack_enqueued_coros:
            print('coro!!!', coro)
            await coro
        assert len(self.worker.queue) == 0

        q = self.worker.next_queue
        assert len(q) == 5 # five steps?

