from urllib.parse import urlencode

import pytest
import os
import tempfile

from omnic.worker import Task
from omnic import singletons

from .testing_utils import RunOnceWorker
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
        singletons.settings.use_settings(FakeSettings)

        cls.app = runserver('ignored', 0, just_setup_app=True)

        singletons.workers.clear()
        cls.worker = RunOnceWorker()
        singletons.workers.append(cls.worker)

        # Disable all HTTP logging for sanic since it leaves open FDs and
        # causes warnings galore
        from sanic.config import LOGGING
        LOGGING.clear()

    @classmethod
    def teardown_class(cls):
        singletons.settings.use_previous_settings()


class TestBuiltinTestRoutes(BaseRoutes):
    @pytest.mark.asyncio
    async def test_images(self):
        request, response = self.app.test_client.get('/test/test.jpg')
        assert response.status == 200
        value = await response.read()
        assert value == Magic.JPEG  # check its magic JPEG bytes

        request, response = self.app.test_client.get('/test/test.png')
        assert response.status == 200
        value = await response.read()
        assert value[:4] == Magic.PNG  # check its magic PNG bytes

    def test_misc_binary(self):
        # For now we just skip testing magic bytes for these, since too
        # too specific
        request, response = self.app.test_client.get('/test/empty.zip')
        assert response.status == 200
        request, response = self.app.test_client.get('/test/test.3ds')
        assert response.status == 200


class TestBuiltinMediaRoutes(BaseRoutes):
    @pytest.mark.asyncio
    async def test_media_placeholder(self):
        # reverse test.png route
        qs = '?%s' % urlencode({'url': '%s/test.png' % self.host})
        request, response = self.app.test_client.get(
            '/media/thumb.jpg:200x200/%s' % qs)

        # ensure that it gave back the placeholder
        value = await response.read()
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
        await self.worker.run_once()
        q = self.worker.queue
        assert len(q) == 0

        # Now make sure resource is downloaded to expected spot (no path
        # grouping, so just tmppath/test.png)
        path = os.path.join(self.tmp_path_prefix, 'test.png')
        assert os.path.exists(path)

        # TODO: not fully tested here, need to write after refactor of
        # 'enqueue' helper functions in server
        # Give control to the loop again
        # assert 0


class TestBuiltinDefaults:
    '''
    High-level sanity tests for built-ins
    '''
    @classmethod
    def setup_class(cls):
        # Ensure no custom settings
        singletons.settings.use_settings(object())

    @classmethod
    def teardown_class(cls):
        # Ensure no custom settings
        singletons.settings.use_previous_settings()

    def test_default_settings_exist(self):
        s = singletons.settings
        assert hasattr(s, 'CONVERTERS')
        assert len(s.CONVERTERS) > 7  # shouldn't drop below this
        assert hasattr(s, 'SERVICES')
        assert len(s.SERVICES) > 3  # shouldn't drop below this
        assert hasattr(s, 'PLACEHOLDERS')
        assert hasattr(s, 'ALLOWED_LOCATIONS')
        assert len(s.ALLOWED_LOCATIONS) > 1  # at least localhost

    def test_default_settings_are_importable(self):
        s = singletons.settings
        assert len(s.load_all('CONVERTERS')) > 7
        assert len(s.load_all('SERVICES')) > 3

    def test_singletons(self):
        cg = singletons.converter_graph
        assert len(cg.converters) > 7
        singletons.placeholders
