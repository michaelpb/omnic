'''
Tests for `viewer` module.
'''
import json
import os
from unittest import mock

from omnic import singletons
from omnic.types.resource import ForeignBytesResource, TypedResource
from omnic.types.typestring import TypeString
from omnic.web import viewer

from .testing_utils import MockPDFViewer

URL = 'http://mocksite.local/file.pdf'


class MockConfig:
    PATH_PREFIX = ''
    ALLOWED_LOCATIONS = '*'
    VIEWERS = [
        MockPDFViewer,
    ]
    LOGGING = None


class TestViewerManager:
    def setup_method(self, method):
        singletons.settings.use_settings(MockConfig)
        self.res = TypedResource(URL, TypeString('PDF'))
        self.viewers = viewer.ViewerManager(viewer_list=MockConfig.VIEWERS)

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()

    def test_get_assets(self):
        assert set(self.viewers.get_assets()) == set([
            '/path/to/assets/example/asset.js',
            '/path/to/assets/example/asset.css',
        ])

    def test_get_node_packages(self):
        assert self.viewers.get_node_packages() == {
            'document_viewer': 'file:/path/to/module',
        }

    def test_get_resource(self):
        assert self.viewers.get_resource() == ForeignBytesResource(
            b'{"document_viewer": "file:/path/to/module"}',
            extension=viewer.VIEWER_EXT,
        )


class TestDefaultViewer:
    JSON_DATA = json.dumps({
        'name': 'pdf_viewer',
        'omnic': {
            'types': ['PDF', 'application/pdf'],
        },
    })
    JSON_PATH = os.path.join(os.path.dirname(__file__), 'package.json')

    def setup_method(self, method):
        singletons.settings.use_settings(MockConfig)
        mocked_file = mock.mock_open(read_data=self.JSON_DATA)

        def mocked_exists(path): return path == self.JSON_PATH
        self.open_patch = mock.patch('omnic.web.viewer.open', mocked_file)
        self.exists_patch = mock.patch('os.path.exists', mocked_exists)
        self.open_patch.start()
        self.exists_patch.start()

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()
        self.open_patch.stop()
        self.exists_patch.stop()

    def test_default_viewer_load(self):
        v = viewer.DefaultViewer('test')
        assert v.name == 'pdf_viewer'
        assert v.node_package == 'file:%s' % os.path.dirname(__file__)
        assert v.types == ['PDF', 'application/pdf']
