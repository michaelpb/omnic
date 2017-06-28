'''
Tests for `viewer` module.
'''
from omnic import singletons
from omnic.web import viewer
from omnic.types.resource import TypedResource
from omnic.types.typestring import TypeString

URL = 'http://mocksite.local/file.pdf'


class MockPDFViewer(viewer.Viewer):
    views = ['PDF']
    asset_dir = '/path/to/assets'
    assets = [
        'example/asset.js',
        'example/asset.css',
    ]


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
