"""
Tests for `resourceurl` module.
"""


from omnic.types.resourceurl import ResourceURL


class TestResourceURLParsing:
    def test_parse_basic(self):
        url = ResourceURL('some.com/path/to/file')
        assert url.url_string == 'http://some.com/path/to/file'
        assert url.args == tuple()
        assert url.kwargs == {}
        assert url.url_path_basename == 'file'

    def test_parse_kwargs(self):
        url = ResourceURL('some.com/path/to/file<arg1: thing><arg2: val 2>')
        assert url.url_string == 'http://some.com/path/to/file'
        assert url.args == tuple()
        assert url.kwargs == {'arg1': 'thing', 'arg2': 'val 2'}
        assert url.url_path_basename == 'file'

    def test_parse_args(self):
        url = ResourceURL('some.com/path/to/file  < some positional stuff  ><not: so positional>')
        assert url.url_string == 'http://some.com/path/to/file'
        assert url.args == ('some positional stuff', )
        assert url.kwargs == {'not': 'so positional'}

    def test_scheme(self):
        url = ResourceURL('git+https://githoob.com/lol.git<efa09><subpath/to/file>')
        assert url.url_string == 'git+https://githoob.com/lol.git'
        assert url.args == ('efa09', 'subpath/to/file')
        assert url.kwargs == {}

