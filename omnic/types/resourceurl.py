'''
ResourceURL is a core class that extends mimetypes
'''
import hashlib
import re

from urllib.parse import urlparse

from omnic import singletons
from omnic.types.exceptions import URLParseException

DEFAULT_SCHEME = 'http'

URL_ARGUMENTS_RE = re.compile(r'<([^>]+)>')
SPLIT_URL_RE = re.compile(r'^([^<]+)(<?.*)$')
ARG_RE = re.compile(r'^\s*([a-zA-Z0-9]+)\s*:\s*(.*)$')
SCHEME_RE = re.compile(r'^[a-zA-Z0-9+-]+://')



class ResourceURL:
    '''
    Immutable utility class for parsing URLs
    '''

    def __init__(self, s):
        self.str = s

        url_string, args, kwargs = self.parse_string(s)
        self.args = tuple(args)
        self.kwargs = kwargs

        # Parse and process URL
        self.url = url_string
        self.parsed = urlparse(url_string)
        self.path_split = self.parsed.path.split('/')

        # In case something else should drive the basename of paths built from
        # this URL, e.g., in the case of a resource within a git repo
        self.path_basename = self.get_basename(self)

        self.md5 = hashlib.md5(str(self).encode('utf-8')).hexdigest()

    def __str__(self):
        return ''.join((
            self.url,
            ''.join('<%s>' % arg for arg in self.args),
            ''.join('<%s:%s>' % pair for pair in self.kwargs.items()),
        ))

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, repr(str(self)))

    @staticmethod
    def parse_string(s):
        '''
        Parses a foreign resource URL into the URL string itself and any
        relevant args and kwargs
        '''
        matched_obj = SPLIT_URL_RE.match(s)
        if not matched_obj:
            raise URLParseException('Invalid Resource URL: "%s"' % s)

        url_string, arguments_string = matched_obj.groups()
        args_as_strings = URL_ARGUMENTS_RE.findall(arguments_string)

        # Determine args and kwargs
        args = []
        kwargs = {}
        for arg_string in args_as_strings:
            kwarg_match = ARG_RE.match(arg_string)
            if kwarg_match:
                key, value = kwarg_match.groups()
                kwargs[key.strip()] = value.strip()
            else:
                args.append(arg_string.strip())

        # Default to HTTP if url_string has no URL
        if not SCHEME_RE.match(url_string):
            url_string = '%s://%s' % (DEFAULT_SCHEME, url_string)

        return url_string.strip(), args, kwargs

    def guess_basename(self):
        path_basename = self.path_split[-1]
        if len(path_basename) < 1:
            # Path is too small, probably ends with /, try 1 up
            path_basename = self.path_split[-2]
        return path_basename

    @staticmethod
    def get_basename(resource_url):
        try:
            resolver_graph = singletons.resolver_graph
        except AttributeError:
            # For some reason, resolver_graph isn't yet loaded (happens during
            # unit tests), fall back on simplest version
            return resource_url.guess_basename()

        return resolver_graph.find_resource_url_basename(resource_url)


class BytesResourceURL(ResourceURL):
    '''
    Used by Foreign Bytes Resource, when resource data is in memory but has no
    particular foreign URL
    '''

    def __init__(self, data, extension, basename):
        ext = '.%s' % extension if extension else ''
        self.data_md5 = hashlib.md5(data).hexdigest()
        virtual_path = 'file://%s/%s%s' % (self.data_md5, basename, ext)
        super().__init__(virtual_path)
