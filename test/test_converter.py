"""
Tests for `converter` module.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from omnic import singletons
from omnic.config.utils import use_settings
from omnic.conversion import converter
from omnic.conversion.graph import ConverterGraph
from omnic.types.resource import TypedResource
from omnic.types.typestring import TypeString
from omnic.utils.graph import NoPath

from .testing_utils import (AgreeableDetector, DummyDetector, Magic,
                            rm_tmp_files)

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


class UnavailableConverter(converter.Converter):
    inputs = ['in2']
    outputs = ['out2']

    @staticmethod
    def configure():
        raise converter.ConverterUnavailable()


class AvailableConverter(converter.Converter):
    inputs = ['in']
    outputs = ['out']


class MockNpmConverter(converter.AdditiveDirectoryExecConverter):
    inputs = ['nodepackage']
    outputs = ['installed_nodepackage']
    command = ['mkdir', 'node_modules']  # Mock npm install


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

    def _path(self, in_str, out_str):
        return self.cgraph.find_path(TypeString(in_str), TypeString(out_str))

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
        rm_tmp_files(
            'package.json',
            'lib/main.js',
            prefixes=[self.res.cache_path, self.res2.cache_path],
        )


class TestAdditiveDirectoryExecConverter(DirectoryConverterTestBase):
    def test_convert(self):
        self.converter = MockNpmConverter()
        self.converter.convert_sync(self.res, self.res2)
        j = os.path.join
        assert self.res2.cache_exists()

        # ensure only new directory has the 'node_modules'
        assert os.path.isdir(j(self.res2.cache_path, 'node_modules'))
        assert not os.path.isdir(j(self.res.cache_path, 'node_modules'))
        assert not os.path.islink(j(self.res2.cache_path, 'lib'))
        assert not os.path.islink(j(self.res2.cache_path, 'node_modules'))

        # Ensure its just hardlinked and not copied
        assert not os.path.islink(j(self.res2.cache_path, 'package.json'))
        assert os.stat(j(self.res2.cache_path, 'package.json')).st_nlink == 2

        with self.res2.cache_open_as_dir('package.json') as f:
            assert f.read() == b'{}\n'
        with self.res2.cache_open_as_dir('lib/main.js') as f:
            assert f.read() == b'console.log("test stuff");\n'


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


class TestExecConverterUnitTest:
    class Subclass(converter.ExecConverter):
        command = ['test', '$IN', '$OUT']

    def _get_mocked_resource(self, ts):
        res = TypedResource(URL, TypeString(ts))
        res.cache_makedirs = MagicMock()
        res.cache_path = 'test/path.%s' % ts
        return res

    def test_configure_failure(self):
        shutil = {'which.return_value': None}
        with patch('omnic.conversion.converter.shutil', **shutil):
            with pytest.raises(converter.ConverterUnavailable):
                self.Subclass.configure()

    def test_configure_succeed(self):
        shutil = {'which.return_value': '/bin/test'}
        with patch('omnic.conversion.converter.shutil', **shutil):
            self.Subclass.configure()

    def test_convert_sync(self):
        res1 = self._get_mocked_resource('input')
        res2 = self._get_mocked_resource('output')
        sb = self.Subclass()
        info = {'run.return_value': '/bin/test'}
        with patch('omnic.conversion.converter.subprocess', **info) as sp:
            sb.convert_sync(res1, res2)
        res1.cache_makedirs.assert_called_once_with()
        res2.cache_makedirs.assert_called_once_with()
        sp.run.assert_called_once_with(
            ['test', 'test/path.input', 'test/path.output'],
            cwd='test',
        )


class TestBasicConverterGraph(ConverterTestBase):
    @classmethod
    def setup_class(cls):
        cls.cgraph = ConverterGraph(MockConfig.CONVERTERS)

    def test_find_path(self):
        # Test typical case
        results = self._path('AVI', 'thumb.png:200x200')
        assert len(results) == 2  # should be 2 steps
        assert all(len(step) == 3 for step in results)  # each step should be 3
        assert all(
            isinstance(step[1], TypeString) and isinstance(step[2], TypeString)
            for step in results  # Ensure we are getting typestrings
        )
        assert results[0][0] is ConvertMovieToImage
        assert results[1][0] is ConvertImageToThumb

    def test_finds_shortest_path(self):
        # Ensure not taking long route
        results = self._path('STL', 'thumb.png:100x100')
        assert len(results) == 2  # should be 2 steps
        assert all(len(step) == 3 for step in results)  # each step should be 3
        assert results[0][0] is Convert3DGraphicsToImage
        assert results[1][0] is ConvertImageToThumb


class TestConverterGraphCustomPaths:
    def teardown_method(self, method):
        singletons.settings.use_previous_settings()

    def _path(self, in_str, out_str):
        return self.cgraph.find_path(TypeString(in_str), TypeString(out_str))

    def test_pruned_converters(self):
        cgraph = ConverterGraph([
            AvailableConverter,
            UnavailableConverter,
        ], prune_converters=True)
        assert len(cgraph.converters) == 1

    @use_settings(preferred_conversion_paths=[('STL', 'AVI', 'JPG', 'thumb.png')])
    def test_preferred_conversions(self):
        self.cgraph = ConverterGraph(MockConfig.CONVERTERS)
        results = self._path('STL', 'thumb.png')
        assert len(results) == 3  # Forcing it to 1 extra step

    @use_settings(conversion_profiles={'thumb': 'thumb.png:123x456'})
    def test_simple_conversion_profile(self):
        self.cgraph = ConverterGraph(MockConfig.CONVERTERS)
        results = self._path('STL', 'thumb')
        assert len(results) == 2  # should be 2 steps
        assert all(len(step) == 3 for step in results)  # each step should be 3
        assert results[0][0] is Convert3DGraphicsToImage
        assert results[1][0] is ConvertImageToThumb
        assert results[1][2].arguments == ('123x456', )

    @use_settings(conversion_profiles={
        'avithumb': ('AVI', 'JPG', 'thumb.png')})
    def test_conversion_profile_path(self):
        self.cgraph = ConverterGraph(MockConfig.CONVERTERS)
        results = self._path('STL', 'avithumb')
        assert len(results) == 3  # Ensure it is 1 "extra" step
        assert all(len(step) == 3 for step in results)  # each step should be 3
        assert results[0][0] is Convert3DGraphicsToMovie
        assert results[1][0] is ConvertMovieToImage
        assert results[2][0] is ConvertImageToThumb

    @use_settings(conversion_profiles={'avithumb': ('AVI', 'OBJ')})
    def test_invalid_conversion_profile(self):
        self.cgraph = ConverterGraph(MockConfig.CONVERTERS)
        assert not self.cgraph.conversion_profiles.keys()
        with pytest.raises(NoPath):
            self._path('STL', 'avithumb')

    @use_settings(conversion_profiles={
        'avithumb': ('AVI', 'JPG:frame=2', 'thumb.png:123x456')})
    def test_conversion_profile_path_with_internal_args(self):
        self.cgraph = ConverterGraph(MockConfig.CONVERTERS)
        results = self._path('STL', 'avithumb')
        assert len(results) == 3  # Ensure it is 1 "extra" step
        assert all(len(step) == 3 for step in results)  # each step should be 3
        assert results[0][0] is Convert3DGraphicsToMovie
        assert results[1][0] is ConvertMovieToImage
        assert results[2][0] is ConvertImageToThumb
        assert results[1][2].arguments == ('frame=2', )
        assert results[2][2].arguments == ('123x456', )
