"""
Tests for `resourceurl` module.
"""


from omnic.types.resourceurl import ResourceURL, BytesResourceURL


class TestResourceURLParsing:
    def test_parse_basic(self):
        url = ResourceURL('some.com/path/to/file')
        assert url.url == 'http://some.com/path/to/file'
        assert url.args == tuple()
        assert url.kwargs == {}
        assert url.path_basename == 'file'

    def test_parse_kwargs(self):
        url = ResourceURL('some.com/path/to/file<arg1: thing><arg2: val 2>')
        assert url.url == 'http://some.com/path/to/file'
        assert url.args == tuple()
        assert url.kwargs == {'arg1': 'thing', 'arg2': 'val 2'}
        assert url.path_basename == 'file'

    def test_parse_args(self):
        url = ResourceURL('some.com/path/to/file  < some positional stuff  ><not: so positional>')
        assert url.url == 'http://some.com/path/to/file'
        assert url.args == ('some positional stuff', )
        assert url.kwargs == {'not': 'so positional'}

    def test_str(self):
        url = ResourceURL('some.com/path/to/file  <not: so positional>  < some positional stuff  >')
        assert str(url) == 'http://some.com/path/to/file<some positional stuff><not:so positional>'

    def test_scheme(self):
        url = ResourceURL('git+https://githoob.com/lol.git<efa09><subpath/to/file>')
        assert url.url == 'git+https://githoob.com/lol.git'
        assert url.args == ('efa09', 'subpath/to/file')
        assert url.kwargs == {}

    def test_basename(self):
        url = ResourceURL('git+https://githoob.com/lol.git<efa09><subpath/to/file>')
        assert url.path_basename == 'file'

        url = ResourceURL('git+https://githoob.com/lol.git')
        assert url.path_basename == 'lol.git'

        url = ResourceURL('http://hoob.com/thing.png')
        assert url.path_basename == 'thing.png'

        url = ResourceURL('http://hoob.com/thing.png<some><thing>')
        assert url.path_basename == 'thing.png'


class TestBytesResourceURLParsing:
    def test_faux_url_construction(self):
        url = BytesResourceURL(b'testdata', 'txt', 'input')
        assert url.url.endswith('/input.txt')
        assert url.url.startswith('file://')
        assert '/%s/' % url.data_md5 in url.url


