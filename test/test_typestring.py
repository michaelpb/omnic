"""
Tests for `typestring` module.
"""
import tempfile

import os

from omnic.types.typestring import TypeString, guess_typestring

from .testing_utils import Magic


class TestMimeTypeTypeString:
    @classmethod
    def setup_class(cls):
        cls.ts = TypeString('application/json')

    def test_is_mimetype_method(self):
        assert self.ts.mimetype == 'application/json'
        assert self.ts.extension == 'JSON'
        assert not self.ts.is_qualifier

    def test_str(self):
        assert str(self.ts) == 'application/json'

    def test_has_no_arguments(self):
        assert self.ts.arguments == tuple()

    def test_modify_basename(self):
        assert self.ts.modify_basename('thing.xml') == 'thing.xml.json'
        assert self.ts.modify_basename('thing') == 'thing.json'


class TestExtensionTypeString:
    @classmethod
    def setup_class(cls):
        cls.ts = TypeString('JPEG')

    def test_is_mimetype_method(self):
        assert self.ts.mimetype == 'image/jpeg'
        assert self.ts.extension == 'JPEG'
        assert not self.ts.is_qualifier

    def test_str(self):
        assert str(self.ts) == 'JPEG'

    def test_has_no_arguments(self):
        assert self.ts.arguments == tuple()

    def test_modify_basename(self):
        assert self.ts.modify_basename('thing.xml') == 'thing.xml.jpeg'
        assert self.ts.modify_basename('thing') == 'thing.jpeg'


class TestQualifierArgumentsTypeString:
    @classmethod
    def setup_class(cls):
        cls.ts = TypeString('thumb.png:400x300')

    def test_is_mimetype_method(self):
        assert self.ts.mimetype is None
        assert self.ts.extension is None
        assert self.ts.is_qualifier

    def test_str(self):
        assert str(self.ts) == 'thumb.png:400x300'

    def test_has_arguments(self):
        assert self.ts.arguments == ('400x300',)

    def test_modify_basename(self):
        assert self.ts.modify_basename(
            'thing.xml') == 'thing.xml.400x300.thumb.png'
        assert self.ts.modify_basename('thing') == 'thing.400x300.thumb.png'


class TestGuessPNGTypeString:
    def setup_method(self, method):
        self.fd = tempfile.NamedTemporaryFile(suffix='test.png', delete=False)

    def test_guesses_by_extension(self):
        self.fd.close()  # Empty file, no possible guess of mimetype, use ext
        ts = guess_typestring(self.fd.name)
        assert ts.mimetype == 'image/png'

    def test_guesses_by_magic_bytes(self):
        # Even though ends with png, we write JPG magic bytes into it
        self.fd.write(bytes(Magic.JPEG))
        self.fd.close()
        ts = guess_typestring(self.fd.name)
        assert ts.mimetype == 'image/jpeg'

    def teardown_method(self, method):
        os.remove(self.fd.name)
