import io
import json
import os
import tempfile

import pytest

from omnic import singletons
from omnic.builtin.converters.manifest import ManifestDownloader
from omnic.types.detectors import DIRECTORY
from omnic.types.resource import ForeignResource, TypedResource
from omnic.utils import asynctools
from omnic.worker.enums import Task
from omnic.worker.testing import RunOnceWorker

from .testing_utils import Magic


class BaseUnitTest:
    def setup_method(self, method):
        self.host = '127.0.0.1:42101'
        self.tmp_path_prefix = tempfile.mkdtemp(prefix='omnic_tests_')

        class FakeSettings:
            PATH_PREFIX = self.tmp_path_prefix
            PATH_GROUPING = None
            ALLOWED_LOCATIONS = {self.host}
            LOGGING = None
        singletons.settings.use_settings(FakeSettings)

        singletons.workers.clear()
        self.worker = RunOnceWorker()
        singletons.workers.append(self.worker)

    def teardown_method(self, method):
        try:
            os.rmdir(self.tmp_path_prefix)
        except OSError:
            pass
        singletons.settings.use_previous_settings()

    async def _get(self, path, **get_args):
        class MockRequest:
            args = {k: [v] for k, v in get_args.items()}
        singletons.server.configure()
        matches, view = singletons.server.route_path(path)
        response = await view(MockRequest, *matches)
        if hasattr(response, 'stream'):
            response.transport = io.BytesIO()
            await response.stream()
            response.transport.seek(0)
            data = response.transport.read()
        else:
            data = response.output()
        return data


class TestBuiltinTestRoutes(BaseUnitTest):
    @pytest.mark.asyncio
    async def test_images(self):
        data = await self._get('/test/test.jpg')
        assert b'200 OK' in data
        assert Magic.JPEG in data

        data = await self._get('/test/test.png')
        assert b'200 OK' in data
        assert Magic.PNG in data

    @pytest.mark.asyncio
    async def test_misc_binary_sync(self):
        data = await self._get('/test/empty.zip')
        assert b'200 OK' in data
        data = await self._get('/test/test.3ds')
        assert b'200 OK' in data

    @pytest.mark.asyncio
    async def test_manifest_json(self):
        data = await self._get('/test/manifest.json')
        assert b'200 OK' in data
        assert b'application/json' in data
        assert b'{"files' in data

    @pytest.mark.asyncio
    async def test_manifest_json_download(self):
        # Download the manifest.json file from test server
        url = 'http://%s/test/manifest.json' % self.host
        f_res = ForeignResource(url)
        data = await self._get('/test/manifest.json')
        assert b'200 OK' in data
        with f_res.cache_open('wb') as fd:
            fd.write(b'{' + data.partition(b'{')[2])

        # Set up resources
        in_resource = f_res.guess_typed()
        in_resource.symlink_from(f_res)
        out_resource = TypedResource(url, DIRECTORY)

        # Do actual convert (which should entail downloads)
        downloader = ManifestDownloader()
        await downloader.convert(in_resource, out_resource)

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


class TestAdmin(BaseUnitTest):
    @pytest.mark.asyncio
    async def test_admin_page(self):
        data = await self._get('/admin/')
        assert b'302' in data
        assert b'/conversion/' in data

    @pytest.mark.asyncio
    async def test_conversion_page(self):
        data = await self._get('/admin/conversion/')
        assert b'200 OK' in data
        assert b'Conversion' in data
        assert b'Graph Explorer' in data

    @pytest.mark.asyncio
    async def test_ajax_workers(self):
        data = await self._get('/admin/ajax/workers/')
        assert b'200 OK' in data
        assert b'queue' in data

    @pytest.mark.asyncio
    async def test_graph(self):
        data = await self._get('/admin/graph/')
        assert b'200 OK' in data
        assert b'Conversion' in data
        assert b'Graph Explorer' in data

    @pytest.mark.asyncio
    async def test_subgraph(self):
        data = await self._get('/admin/graph/JPEG/')
        assert b'200 OK' in data
        assert b'Conversion' in data
        assert b'Graph Explorer' in data


class TestBuiltinMediaServer(BaseUnitTest):
    @pytest.mark.asyncio
    async def test_media_view_placeholder(self):
        # Check that we get a placeholder
        url = '%s/test.png' % self.host
        data = await self._get('/media/thumb.png:200x200/', url=url)
        assert b'200 OK' in data
        assert b'image/png' in data
        assert Magic.PNG in data

    @pytest.mark.asyncio
    async def test_media_enqueuing(self):
        # reverse test.png route
        url = '%s/test.png' % self.host
        data = await self._get('/media/thumb.jpg:200x200/', url=url)
        assert Magic.PNG in data  # check its magic PNG bytes
        await self._do_check_enqueued()

    @pytest.mark.asyncio
    async def test_media_just_checking_api(self, event_loop):
        # ensure that it correctly gets a ready = false
        url = '%s/test.png' % self.host
        data = await self._get('/media/thumb.jpg:200x200/',
                               url=url, just_checking='true')
        assert b'200 OK' in data
        assert b'application/json' in data
        data = b'{' + data.partition(b'{')[2]
        assert json.loads(data.decode('utf8')) == {
            'url': 'http://%s' % url,
            'ready': False,
        }
        await self._do_check_enqueued()

    async def _do_check_enqueued(self):
        # Inspect whats been enqueued, ensure as expected
        await asynctools.await_all()
        q = self.worker.next_queue
        assert q
        assert q[0]
        assert q[0][0] == Task.DOWNLOAD
        assert q[1][0] == Task.FUNC
        assert q[1][1][1] == 'http://127.0.0.1:42101/test.png'
        assert q[1][1][2] == 'thumb.jpg:200x200'

        # Run through queue... this should download the resource, and in
        # turn enqueue the remaining steps
        await self.worker.run_once()
        q = self.worker.queue
        assert len(q) == 0

        # Now make sure resource is downloaded to expected spot (no path
        # grouping, so just tmppath/test.png)
        path = os.path.join(self.tmp_path_prefix, 'test.png')
        assert os.path.exists(path)

        # Truly enqueue the remaining steps again
        await asynctools.await_all()

        # TODO: not fully tested here, need to write after refactor of
        # 'enqueue' helper functions in server
        q = self.worker.next_queue
        assert q
        assert len(q) == 1
        assert q[0]
        assert q[0][0] == Task.CONVERT
        await self.worker.run_once()

        # ensure nothing more was added to queue
        q = self.worker.next_queue
        assert not q


class TestViewerViews(BaseUnitTest):
    def setup_method(self, method):
        super().setup_method(method)
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
        return  # TODO finish this crap

        # Run through appending coros... this should turn enqueue the remaining
        # steps
        # NOTE: Only necessary until we rewrite enqueuing process + clean up
        # async vs sync w.r.t. tasks
        singletons.workers._tmp_do_hack_enqueue = True
        for coro in singletons.workers._tmp_hack_enqueued_coros:
            # print('coro!!!', coro)
            await coro
        assert len(self.worker.queue) == 0

        q = self.worker.next_queue
        assert len(q) == 5  # five steps?
