import json
import tempfile

import pytest

from omnic import singletons
from omnic.builtin.converters.chemical import (NodeSdfToSvgRenderer,
                                               OpenBabelConverter)
from omnic.builtin.converters.document import (ImageMagickPageRasterizer,
                                               Unoconv)
from omnic.builtin.converters.mesh import Jsc3dRenderer, MeshLabConverter
from omnic.builtin.converters.vector import (InkscapeConverter,
                                             InkscapeRasterizer)
from omnic.builtin.services.viewer.converters import (ViewerNodePackageBuilder,
                                                      generate_index_js)
from omnic.types.resource import ForeignBytesResource, TypedResource
from omnic.types.typestring import TypeString
from omnic.worker.testing import RunOnceWorker


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


class TestViewerNodePackageBuilder(BaseUnitTest):
    def _get_resources(self):
        node_packages = {
            'test1': 'file:/path/to/module/',
            'other_module': '1.2.3',  # traditional module
        }
        self.node_packages = node_packages
        viewers_data = json.dumps(node_packages).encode('utf8')
        viewers_resource = ForeignBytesResource(
            viewers_data,
            extension='omnic_viewer_descriptor',
        )
        url_string = viewers_resource.url_string
        target_ts = TypeString('nodepackage')
        target_resource = TypedResource(url_string, target_ts)
        viewers_resource.save()
        return viewers_resource, target_resource

    def test_generate_index_js(self):
        assert generate_index_js([
            'viewer_3d',
            'pdf_viewer',
        ]).startswith('require("viewer_3d");\nrequire("pdf_viewer");')

    @pytest.mark.asyncio
    async def test_convert(self):
        conv = ViewerNodePackageBuilder()
        in_resource, out_resource = self._get_resources()
        await conv.convert(in_resource, out_resource)
        assert out_resource.cache_exists()
        with out_resource.cache_open_as_dir('package.json', 'r') as fd:
            json_data = json.load(fd)
        assert json_data['main'] == 'index.js'
        assert json_data['dependencies'] == self.node_packages

        with out_resource.cache_open_as_dir('index.js') as fd:
            data = fd.read()
            assert b'require("test1")' in data
            assert b'require("other_module")' in data


def _get_resources(*args):
    return [
        TypedResource('http://test.url/file', TypeString(typestr))
        for typestr in args
    ]


class TestDocumentConverterCommands:
    def test_unoconv(self):
        in_resource, out_resource = _get_resources('DOC', 'PDF')
        cmd = Unoconv().get_command(in_resource, out_resource)
        assert cmd == [
            '/usr/bin/python3',
            '/usr/bin/unoconv',
            '-f',
            'pdf',
            '-o',
            out_resource.cache_path,
            in_resource.cache_path,
        ]

    def test_imagemagick_page_rasterizer(self):
        in_resource, out_resource = _get_resources('PDF', 'PNG')
        conv = ImageMagickPageRasterizer()
        cmd = conv.get_command(in_resource, out_resource)
        assert cmd == [
            'convert',
            in_resource.cache_path,
            '%s[0]' % out_resource.cache_path,
        ]
        filename = conv.get_output_filename(in_resource, out_resource)
        assert filename.endswith('/file-0.png')


class TestVectorConverterCommands:
    def test_inkscape_converter(self):
        in_resource, out_resource = _get_resources('AI', 'SVG')
        cmd = InkscapeConverter().get_command(in_resource, out_resource)
        assert cmd == [
            'inkscape',
            '-z',
            '-f',
            in_resource.cache_path,
            '-l',  # means: Export plain SVG
            out_resource.cache_path,
        ]

    def test_inkscape_rasterizer(self):
        in_resource, out_resource = _get_resources('SVG', 'PNG')
        cmd = InkscapeRasterizer().get_command(in_resource, out_resource)
        assert cmd == [
            'inkscape',
            '-z',
            '-f',
            in_resource.cache_path,
            '-e',  # means: Export plain SVG
            out_resource.cache_path,
        ]


class TestMeshConverterCommands:
    def test_meshlab_converter(self):
        in_resource, out_resource = _get_resources('OBJ', 'STL')
        cmd = MeshLabConverter().get_command(in_resource, out_resource)
        assert cmd == [
            'meshlabserver',
            '-i',
            in_resource.cache_path,
            '-o',
            out_resource.cache_path,
        ]

    def test_jsc3d_renderer(self):
        in_resource, out_resource = _get_resources('STL', 'PNG')
        cmd = Jsc3dRenderer().get_command(in_resource, out_resource)
        assert cmd == [
            'jsc3d',
            in_resource.cache_path,
            out_resource.cache_path,
        ]


class TestChemicalConverterCommands:
    def test_nodesdftosvg_renderer(self):
        in_resource, out_resource = _get_resources('SDF', 'SVG')
        cmd = NodeSdfToSvgRenderer().get_command(in_resource, out_resource)
        assert cmd == [
            'sdftosvg',
            in_resource.cache_path,
            out_resource.cache_path,
        ]

    def test_openbabel_converter(self):
        in_resource, out_resource = _get_resources('SDF', 'SVG')
        cmd = OpenBabelConverter().get_command(in_resource, out_resource)
        assert cmd == [
            'obabel',
            in_resource.cache_path,
            '-O%s' % out_resource.cache_path,
        ]
