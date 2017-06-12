"""
Tests for `resource` module.
"""
import tempfile
import os
from base64 import b64decode

import pytest
import requests_mock

from omnic.types.typestring import TypeString
from omnic.types.resource import TypedResource, ForeignResource, URLError, CacheError
from .testing_utils import Magic


URL = 'http://mocksite.local/file.png'
URL1 = 'http://mocksite.local/otherthing/file.png'
URL2 = 'http://mocksite2.local/otherthing/file.png'
URL_GIF = 'http://mocksite.local/file.png.gif'


class MockConfig:
    PATH_GROUPING = 'MD5'
    PATH_PREFIX = ''
    ALLOWED_LOCATIONS = '*'


class MockConfigRestrictive(MockConfig):
    ALLOWED_LOCATIONS = {'mocksite.local'}


class TestForeignResource:
    @classmethod
    def setup_class(cls):
        cls.config = MockConfig
        cls.config.PATH_PREFIX = tempfile.mkdtemp()
        cls.res = ForeignResource(cls.config, URL)

    def test_properties(self):
        assert self.res.url_string == URL
        assert self.res.url_path_basename == 'file.png'
        assert self.res.cache_path.endswith('file.png')
        assert not self.res.cache_exists()

    def test_uniqueness(self):
        res1 = ForeignResource(self.config, URL1)
        res2 = ForeignResource(self.config, URL2)
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

    def teardown_method(self, method):
        # Deletes the file if it exists
        try:
            os.remove(self.res.cache_path)
        except OSError:
            pass


class TestResourceValidate:
    def test_validate_global(self):
        config = MockConfig
        res = ForeignResource(config, URL)
        res1 = ForeignResource(config, URL1)
        res2 = ForeignResource(config, URL2)
        res.validate() # no exceptions since config is loose
        res1.validate() # no exceptions since config is loose
        res2.validate() # no exceptions since config is loose

    def test_validate_restrictive(self):
        config = MockConfigRestrictive
        res = ForeignResource(config, URL)
        res1 = ForeignResource(config, URL1)
        res2 = ForeignResource(config, URL2)
        res.validate() # no exceptions since okay
        res1.validate() # no exceptions since okay
        with pytest.raises(URLError):
            res2.validate() # exception since different domain


class TestTypedResource:
    @classmethod
    def setup_class(cls):
        cls.config = MockConfig
        cls.res = TypedResource(cls.config, URL, TypeString('image/gif'))

    def test_properties(self):
        assert self.res.url_string == URL
        assert self.res.cache_path.endswith('file.png.gif')
        assert not self.res.cache_exists()

    def test_uniqueness(self):
        paths = set([
            TypedResource(self.config, URL, TypeString('image/gif')).cache_path,
            TypedResource(self.config, URL, TypeString('image/png')).cache_path,
            TypedResource(self.config, URL_GIF, TypeString('image/gif')).cache_path,
            TypedResource(self.config, URL1, TypeString('image/gif')).cache_path,
            TypedResource(self.config, URL2, TypeString('image/gif')).cache_path,
        ])
        assert len(paths) == 5

