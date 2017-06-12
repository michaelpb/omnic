from urllib.parse import urlencode

import pytest
import asyncio
import sys
import os
import tempfile

from omnic.worker import Task
from .testing_utils import RunOnceWorker
from .testing_utils import Magic

class BaseRoutes:
    @classmethod
    def setup_class(cls):
        from omnic.config import settings
        from omnic.server import runserver
        cls.app = runserver(settings, 'ignored', 0, just_setup_app=True)
        cls.host = '127.0.0.1:42101'
        cls.settings = settings
        settings.PATH_PREFIX = tempfile.mkdtemp()
        settings.PATH_GROUPING = None
        settings.ALLOWED_LOCATIONS = {cls.host}
        settings.worker = RunOnceWorker()

        # Disable all HTTP logging for sanic since it leaves open FDs and
        # causes warnings galore
        from sanic.config import LOGGING
        LOGGING.clear()


class TestBuiltinTestRoutes(BaseRoutes):
    @pytest.mark.asyncio
    async def test_images(self):
        request, response = self.app.test_client.get('/test/test.jpg')
        assert response.status == 200
        value = await response.read()
        assert value == Magic.JPEG # check its magic JPEG bytes

        request, response = self.app.test_client.get('/test/test.png')
        assert response.status == 200
        value = await response.read()
        assert value[:4] == Magic.PNG # check its magic PNG bytes

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
        request, response = self.app.test_client.get('/media/thumb.jpg:200x200/%s' % qs)

        # ensure that it gave back the placeholder
        value = await response.read()
        assert response.status == 200
        assert response.headers['Content-Type'] == 'image/png'
        assert value[:4] == Magic.PNG # check its magic PNG bytes

        # Inspect whats been enqueued, ensure as expected
        q = self.settings.worker.next_queue
        assert q[0][0] == Task.DOWNLOAD
        assert q[1][0] == Task.FUNC
        assert q[1][1][1] == 'http://127.0.0.1:42101/test.png'
        assert q[1][1][2] == 'thumb.jpg:200x200'

        # Run through queue... this should download the resource, and in
        # turn enqueue the remaining steps
        await self.settings.worker.run_once()
        q = self.settings.worker.queue
        assert len(q) == 0

        # Now make sure resource is downloaded to expected spot (no path
        # grouping, so just tmppath/test.png)
        path = os.path.join(self.settings.PATH_PREFIX, 'test.png')
        assert os.path.exists(path)

        # TODO: not fully tested here, need to write after refactor of
        # 'enqueue' helper functions in server
        # Give control to the loop again
        #await asyncio.sleep(1)
        #await self.settings.worker.run_once()
        #await asyncio.sleep(0)
        #assert 0


