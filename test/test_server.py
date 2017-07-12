import pytest
import requests

from omnic import singletons
from omnic.config.utils import use_settings

from .testing_utils import Magic


class FakeService:
    SERVICE_NAME = 'testservice'
    urls = {
        'thing1/': 'thing1_route',
        '<argument>/thing2': 'thing2_route',
        'thing1/many/things/path': 'thing3_route',
    }

    def thing1_route():
        pass

    def thing2_route():
        pass

    def thing3_route():
        pass


FAKE_SERVICES = [
    'test.test_server.FakeService',
]


class TestServer:
    @use_settings(services=FAKE_SERVICES)
    def test_basic_path_routing(self):
        matches, view = singletons.server.route_path('testservice/thing1')
        assert view == FakeService.thing1_route
        assert matches == []
        matches, view = singletons.server.route_path(
            'testservice/thing1/many/things/path')
        assert view == FakeService.thing3_route
        assert matches == []

    @use_settings(services=FAKE_SERVICES)
    def test_path_routing_with_arguments(self):
        matches, view = singletons.server.route_path(
            'testservice/matched/thing2')
        assert view == FakeService.thing2_route
        assert matches == ['matched']


class BrokenTestForForkingServer:
    # TODO Really should just remove this

    def setup_method(self, method):
        singletons.settings

        class FakeSettings:
            LOGGING = None
        singletons.settings.use_settings(FakeSettings)

    @pytest.mark.skip(':(')
    def test_testing_server_multiple(self):
        # Ensures can be run multiple times
        URL = '%s/test/test.jpg' % singletons.server.TEST_URL
        for i in range(3):
            singletons.server.fork_testing_server()
            req = requests.get(URL)
            assert req.content == Magic.JPEG
            singletons.server.kill_testing_server()

    @pytest.mark.skip(':(')
    def test_raises_runtime_error_on_child_process_error(self):
        original_test_port = singletons.server.TEST_PORT
        singletons.server.TEST_PORT = 1  # Simulate invalid port
        with pytest.raises(RuntimeError):
            singletons.server.fork_testing_server()
        singletons.server.TEST_PORT = original_test_port

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()
