"""
Tests for `resource` module.
"""

import tempfile
import os
import pytest

from omnic import singletons
from omnic.types.typestring import TypeString
from omnic.types.resource import TypedResource
from omnic.conversion import converter
from omnic.conversion.graph import ConverterGraph
from .testing_utils import Magic, DummyDetector, AgreeableDetector, rm_tmp_files

URL = 'http://mocksite.local/file.png'
DIR_URL = 'http://mocksite.local/my_files'

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
    LOGGING = None


class ConverterTestBase:
    def setup_method(self, method):
        MockConfig.PATH_PREFIX = tempfile.mkdtemp()
        singletons.settings.use_settings(MockConfig)
        self.res = TypedResource(URL, TypeString('JPEG'))
        self.res2 = TypedResource(URL, TypeString('JPG'))
        with self.res.cache_open('wb') as f:
            f.write(Magic.JPEG)

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()
        rm_tmp_files(
            self.res.cache_path,
            self.res2.cache_path,
        )

    def _check_convert(self):
        self.converter.convert_sync(self.res, self.res2)
        assert self.res2.cache_exists()
        with self.res2.cache_open() as f:
            assert f.read() == Magic.JPEG


class DirectoryConverterTestBase:
    def setup_method(self, method):
        MockConfig.PATH_PREFIX = tempfile.mkdtemp()
        singletons.settings.use_settings(MockConfig)
        self.res = TypedResource(DIR_URL, TypeString('nodepackage'))
        self.res2 = TypedResource(DIR_URL, TypeString('installed_nodepackage'))
        with self.res.cache_open_as_dir('package.json', 'wb') as f:
            f.write(b'{}\n')
        with self.res.cache_open_as_dir('lib/main.js', 'wb') as f:
            f.write(b'console.log("test stuff");\n')

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()
        # Remove all the
        rm_tmp_files(
            'package.json',
            'lib/main.js',
            prefixes=[self.res.cache_path, self.res2.cache_path],
        )


class TestHardLinkConverter(ConverterTestBase):
    def test_convert(self):
        self.converter = HardLinkConverter()
        self._check_convert()


class TestDetectorConverter(ConverterTestBase):
    def test_convert_nothing(self):
        self.converter = converter.DetectorConverter()
        self.converter.detector = AgreeableDetector
        with pytest.raises(converter.ConversionInputError):
            # Wrong direction (from nonexistent to existent)
            self.converter.convert_sync(self.res2, self.res)

    def test_convert_invalid(self):
        self.converter = converter.DetectorConverter()
        self.converter.detector = DummyDetector
        with pytest.raises(converter.ConversionInputError):
            self.converter.convert_sync(self.res, self.res2)

    def test_convert_success(self):
        self.converter = converter.DetectorConverter()
        self.converter.detector = AgreeableDetector
        self._check_convert()  # valid conversion


class TestDirectoryConverter(DirectoryConverterTestBase):
    pass


class TestExecConverter(ConverterTestBase):
    def test_convert(self):
        self.converter = ExecConverter()
        self._check_convert()

    def test_convert_with_arg(self):
        # cp -s creates a symbolic link
        self.res2 = TypedResource(URL, TypeString('JPG:-s'))
        self.converter = ExecConverterWithArgs()
        self._check_convert()
        assert os.path.islink(self.res2.cache_path)

    def test_convert_with_custom_filename(self):
        self.res2 = TypedResource(URL, TypeString('JPG'))
        self.converter = ExecConverterWithOutputFilename()
        self._check_convert()


class TestBasicConverterGraph(ConverterTestBase):
    @classmethod
    def setup_class(cls):
        cls.cgraph = ConverterGraph(MockConfig.CONVERTERS)

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
