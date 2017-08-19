'''
ResourceURL is a core class that extends mimetypes
'''
import re

from urllib.parse import urlparse

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
        self.url_string = url_string
        self.url = urlparse(url_string)
        self.url_path_split = self.url.path.split('/')
        self.url_path_basename = self.url_path_split[-1]
        if len(self.url_path_basename) < 1:
            # Path is too small, probably ends with /, try 1 up
            self.url_path_basename = self.url_path_split[-2]

    def __str__(self):
        return '%s%s' % (
            self.url_string,
            ''.join('<%s>' % arg for arg in self.args),
        )

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

