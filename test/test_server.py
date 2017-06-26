import pytest

from omnic import singletons

from .testing_utils import Magic

import requests


class TestForkedTestingServer:
    '''
    Some simple tests of the forking test server
    '''

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
