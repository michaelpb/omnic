"""
Tests for `typestring` module.
"""


from omnic.types.typestring import TypeString


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

    def test_repr(self):
        assert repr(self.ts) == 'TypeString(\'application/json\')'

    def test_equality(self):
        assert self.ts == TypeString('application/json')

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

    def test_equality(self):
        assert self.ts == TypeString('JPEG')
        assert self.ts != TypeString('jpeg')

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

    def test_equality(self):
        assert self.ts == TypeString('thumb.png:400x300')
        assert self.ts != TypeString('thumb.png:300x300')

    def test_str(self):
        assert str(self.ts) == 'thumb.png:400x300'

    def test_has_arguments(self):
        assert self.ts.arguments == ('400x300',)

    def test_modify_basename(self):
        assert self.ts.modify_basename(
            'thing.xml') == 'thing.xml.400x300.thumb.png'
        assert self.ts.modify_basename('thing') == 'thing.400x300.thumb.png'
