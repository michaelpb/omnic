"""
Tests for `resource` module.
"""

import tempfile
import os

from omnic import singletons
from omnic.types.typestring import TypeString
from omnic.types.resource import TypedResource
from omnic.conversion import converter
from .testing_utils import Magic

URL = 'http://mocksite.local/file.png'

# TODO: Fix these tests to be less integrate-y, mock out subprocess
# calls


class HardLinkConverter(converter.HardLinkConverter):
    inputs = ['JPEG']
    outputs = ['JPG']


class ExecConverter(converter.ExecConverter):
    inputs = ['JPEG']
    outputs = ['JPG']
    command = [
        'mv',
        '$IN',
        '$OUT',
    ]


class ExecConverterWithArgs(ExecConverter):
    command = [
        'cp',
        '$0',
        '$IN',
        '$OUT',
    ]


class ExecConverterWithOutputFilename(ExecConverter):
    command = [
        'mv',
        '$IN',
        '_tmp_output_file',
    ]

    def get_output_filename(self, in_res, out_res):
        return '_tmp_output_file'


# Set up system of dummy converters
class ConvertMovieToImage(converter.HardLinkConverter):
    inputs = ['MOV', 'AVI', 'MP4']
    outputs = ['JPG']


class ConvertImageToThumb(converter.HardLinkConverter):
    inputs = ['JPG', 'PNG', 'GIF']
    outputs = ['thumb.png']


class Convert3DGraphicsToMovie(converter.HardLinkConverter):
    inputs = ['STL', 'OBJ', 'MESH']
    outputs = ['AVI']


class Convert3DGraphicsToImage(converter.HardLinkConverter):
    inputs = ['STL', 'OBJ', 'MESH']
    outputs = ['PNG']


class CleanUpAudio(converter.HardLinkConverter):
    inputs = ['MP3', 'WAV', 'OGG']
    outputs = ['cleaned.ogg']


class MockConfig:
    PATH_GROUPING = 'MD5'
    PATH_PREFIX = ''
    ALLOWED_LOCATIONS = '*'
    CONVERTERS = [
        ConvertMovieToImage,
        ConvertImageToThumb,
        Convert3DGraphicsToMovie,
        Convert3DGraphicsToImage,
        CleanUpAudio,
    ]


class ConverterTestBase:
    def setup_method(self, method):
        self.config = MockConfig
        self.config.PATH_PREFIX = tempfile.mkdtemp()
        singletons.settings.use_settings(self.config)
        self.res = TypedResource(URL, TypeString('JPEG'))
        self.res2 = TypedResource(URL, TypeString('JPG'))
        with self.res.cache_open('wb') as f:
            f.write(Magic.JPEG)

    def teardown_method(self, method):
        try:
            os.remove(self.res.cache_path)
        except OSError:
            pass
        if self.res2:
            try:
                os.remove(self.res2.cache_path)
            except OSError:
                pass
        try:
            os.removedirs(os.path.dirname(self.res.cache_path))
        except OSError:
            pass
        try:
            os.removedirs(os.path.dirname(self.res2.cache_path))
        except OSError:
            pass

    def _check_convert(self):
        self.converter.convert_sync(self.res, self.res2)
        assert self.res2.cache_exists()
        with self.res2.cache_open() as f:
            assert f.read() == Magic.JPEG


class TestHardLinkConverter(ConverterTestBase):
    def test_convert(self):
        self.converter = HardLinkConverter(self.config)
        self._check_convert()


class TestExecConverter(ConverterTestBase):
    def test_convert(self):
        self.converter = ExecConverter(self.config)
        self._check_convert()

    def test_convert_with_arg(self):
        # cp -s creates a symbolic link
        self.res2 = TypedResource(URL, TypeString('JPG:-s'))
        self.converter = ExecConverterWithArgs(self.config)
        self._check_convert()
        assert os.path.islink(self.res2.cache_path)

    def test_convert_with_custom_filename(self):
        self.res2 = TypedResource(URL, TypeString('JPG'))
        self.converter = ExecConverterWithOutputFilename(self.config)
        self._check_convert()


class TestBasicConverterGraph(ConverterTestBase):
    @classmethod
    def setup_class(cls):
        cls.cgraph = converter.ConverterGraph(MockConfig.CONVERTERS)

    def _path(self, in_str, out_str):
        return self.cgraph.find_path(TypeString(in_str), TypeString(out_str))

    def test_find_path(self):
        # Test typical case
        results = self._path('AVI', 'thumb.png:200x200')
        assert len(results) == 2  # should be 2 steps
        assert all(len(step) == 3 for step in results)  # each step should be 3
        assert results[0][0] is ConvertMovieToImage
        assert results[1][0] is ConvertImageToThumb

    def test_finds_shortest_path(self):
        # Ensure not taking long route
        results = self._path('STL', 'thumb.png:100x100')
        assert len(results) == 2  # should be 2 steps
        assert all(len(step) == 3 for step in results)  # each step should be 3
        assert results[0][0] is Convert3DGraphicsToImage
        assert results[1][0] is ConvertImageToThumb
