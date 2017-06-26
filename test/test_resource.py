"""
Tests for `resource` module.
"""
import tempfile
import os

import pytest
import requests_mock

from omnic.types.typestring import TypeString
from omnic.types.resource import TypedResource, ForeignResource, URLError, CacheError
from omnic import singletons
from .testing_utils import Magic


URL = 'http://mocksite.local/file.png'
URL1 = 'http://mocksite.local/otherthing/file.png'
URL2 = 'http://mocksite2.local/otherthing/file.png'
URL_GIF = 'http://mocksite.local/file.png.gif'


class MockConfig:
    PATH_GROUPING = 'MD5'
    PATH_PREFIX = ''
    ALLOWED_LOCATIONS = '*'
    LOGGING = None


class MockConfigRestrictive(MockConfig):
    ALLOWED_LOCATIONS = {'mocksite.local'}


class TestForeignResource:
    def setup_method(self, method):
        MockConfig.PATH_PREFIX = tempfile.mkdtemp(prefix='omnic_test_')
        singletons.settings.use_settings(MockConfig)
        self.res = ForeignResource(URL)

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()
        try:
            os.remove(self.res.cache_path)
        except OSError:
            pass
        try:
            os.removedirs(os.path.dirname(self.res.cache_path))
        except OSError:
            pass

    def test_properties(self):
        assert self.res.url_string == URL
        assert self.res.url_path_basename == 'file.png'
        assert self.res.cache_path.endswith('file.png')
        assert not self.res.cache_exists()

    def test_uniqueness(self):
        res1 = ForeignResource(URL1)
        res2 = ForeignResource(URL2)
        assert self.res.cache_path != res1.cache_path
        assert self.res.cache_path != res2.cache_path
        assert res2.cache_path != res1.cache_path

    def test_download(self):
        with requests_mock.mock() as m:
            m.register_uri('GET', URL, content=Magic.JPEG)
            self.res.download()
            assert self.res.cache_exists()
        with self.res.cache_open() as f:
            assert f.read() == Magic.JPEG

    def test_cache_open(self):
        with self.res.cache_open('wb') as f:
            f.write(b'test')
        with self.res.cache_open() as f:
            assert f.read() == b'test'

    def test_type_identification_exception(self):
        with pytest.raises(CacheError):
            self.res.guess_typed()

    def test_type_identification(self):
        with requests_mock.mock() as m:
            m.register_uri('GET', URL, content=Magic.JPEG)
            self.res.download()
            assert self.res.cache_exists()
        tr = self.res.guess_typed()
        assert tr.typestring.mimetype == 'image/jpeg'


class TestForeignResourceDirectory:
    def setup_method(self, method):
        MockConfig.PATH_PREFIX = tempfile.mkdtemp(prefix='omnic_test_')
        singletons.settings.use_settings(MockConfig)
        self.res = ForeignResource(URL)

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()
        try:
            os.remove(os.path.join(self.res.cache_path, 'testfile'))
        except OSError:
            pass
        os.removedirs(self.res.cache_path)

    def test_cache_open_as_dir(self):
        with self.res.cache_open_as_dir('testfile', 'wb') as f:
            f.write(b'test')
        with self.res.cache_open_as_dir('testfile') as f:
            assert f.read() == b'test'


class TestResourceValidate:
    def test_validate_global(self):
        res = ForeignResource(URL)
        res1 = ForeignResource(URL1)
        res2 = ForeignResource(URL2)
        singletons.settings.use_settings(MockConfig)
        res.validate()  # no exceptions since config is loose
        res1.validate()  # no exceptions since config is loose
        res2.validate()  # no exceptions since config is loose

    def test_validate_restrictive(self):
        singletons.settings.use_settings(MockConfigRestrictive)
        res = ForeignResource(URL)
        res1 = ForeignResource(URL1)
        res2 = ForeignResource(URL2)
        res.validate()  # no exceptions since okay
        res1.validate()  # no exceptions since okay
        with pytest.raises(URLError):
            res2.validate()  # exception since different domain


class TestTypedResource:
    @classmethod
    def setup_class(cls):
        singletons.settings.use_settings(MockConfig)
        cls.res = TypedResource(URL, TypeString('image/gif'))

    @classmethod
    def teardown_class(cls):
        singletons.settings.use_previous_settings()

    def test_properties(self):
        assert self.res.url_string == URL
        assert self.res.cache_path.endswith('file.png.gif')
        assert not self.res.cache_exists()

    def test_uniqueness(self):
        paths = set([
            TypedResource(URL, TypeString(
                'image/gif')).cache_path,
            TypedResource(URL, TypeString(
                'image/png')).cache_path,
            TypedResource(URL_GIF,
                          TypeString('image/gif')).cache_path,
            TypedResource(URL1, TypeString(
                'image/gif')).cache_path,
            TypedResource(URL2, TypeString(
                'image/gif')).cache_path,
        ])
        assert len(paths) == 5
