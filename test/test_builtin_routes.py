import io
import json
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
    def setup_method(self, method):
        from omnic.server import runserver

        self.host = '127.0.0.1:42101'
        self.tmp_path_prefix = tempfile.mkdtemp()

        class FakeSettings:
            PATH_PREFIX = self.tmp_path_prefix
            PATH_GROUPING = None
            ALLOWED_LOCATIONS = {self.host}
            LOGGING = None
        singletons.settings.use_settings(FakeSettings)

        self.app = runserver('ignored', 0, just_setup_app=True)

        singletons.workers.clear()
        self.worker = RunOnceWorker()
        singletons.workers.append(self.worker)

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

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()


class TestBuiltinTestRoutes(BaseRoutes):
    @pytest.mark.skip('figuring out which ones are noisy')
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

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_images_sync(self):
        response = self._get('/test/test.jpg')
        assert response.status == 200
        response = self._get('/test/test.png')
        assert response.status == 200

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_misc_binary_sync(self):
        # For now we just skip testing magic bytes for these, since too
        # too specific
        response = self._get('/test/empty.zip')
        assert response.status == 200
        response = self._get('/test/test.3ds')
        assert response.status == 200

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_manifest_json(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/test/manifest.json')
        assert response.status == 200
        value = await_async(response.read())
        assert value[:7] == b'{"files'

    @pytest.mark.skip('figuring out which ones are noisy')
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
    @pytest.mark.skip('figuring out which ones are noisy')
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
    @pytest.mark.skip('figuring out which ones are noisy')
    def test_admin_page(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_conversion_page(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/conversion/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_ajax_workers(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/ajax/workers/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'queue' in value

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_graph(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/graph/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_subgraph(self, event_loop):
        await_async = event_loop.run_until_complete
        response = self._get('/admin/graph/JPEG/')
        assert response.status == 200
        value = await_async(response.read())
        assert b'Conversion' in value
        assert b'Graph Explorer' in value


class TestBuiltinMediaServer(BaseRoutes):
    @pytest.mark.skip('figuring out which ones are noisy')
    def test_media(self, event_loop):
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
        self._do_check_enqueued(await_async)

    @pytest.mark.skip('figuring out which ones are noisy')
    def test_media_just_checking_api(self, event_loop):
        # NOTE: For some reason due to incorrect event loops, etc, one can't
        # use pytest.mark.asyncio, making the tests themselves async
        await_async = event_loop.run_until_complete

        # reverse test.png route
        url = '%s/test.png' % self.host
        qs = '?%s' % urlencode({
            'url': url,
            'just_checking': 'y',
        })

        # ensure that it correctly gets a ready = false
        response = self._get('/media/thumb.jpg:200x200/%s' % qs)
        value = await_async(response.read()).decode('utf-8')
        assert response.status == 200
        assert response.headers['Content-Type'] == 'application/json'
        assert json.loads(value) == {'url': 'http://%s' % url, 'ready': False}
        self._do_check_enqueued(await_async)

    def _do_check_enqueued(self, await_async):
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
    @pytest.mark.skip('figuring out which ones are noisy')
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
        return  # TODO finish this crap

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
        assert len(q) == 5  # five steps?


class TestMediaViews(BaseUnitTest):
    def setup_method(self, method):
        from omnic.builtin.services import media
        singletons.server.configure()
        self.v = media
        self.url = '%s/test.png' % self.host

        class MockRequest:
            args = {'url': [self.url]}
        self.request = MockRequest
        self.ts = 'thumb.png:200x200'

    @pytest.mark.asyncio
    @pytest.mark.skip('figuring out which ones are noisy')
    async def test_media_view_placeholder(self):
        # Check that we get a placeholder
        response = await self.v.media_route(self.request, self.ts)
        response.transport = io.BytesIO()
        await response.stream()
        response.transport.seek(0)
        r = response.transport.read()
        assert b'200 OK' in r
        assert b'image/png' in r
        assert Magic.PNG in r

    @pytest.mark.asyncio
    @pytest.mark.skip('figuring out which ones are noisy')
    async def test_media_view_just_checking(self):
        # Check that we get a json
        self.request.args['just_checking'] = ['y']
        response = await self.v.media_route(self.request, self.ts)
        r = response.output()
        assert b'200 OK' in r
        assert b'application/json' in r
        assert b'false' in r
