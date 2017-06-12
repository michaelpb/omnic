import hashlib
import os
import shutil
from urllib.parse import urlparse
from omnic.utils.iters import group_by

import requests

from .typestring import guess_typestring

class Resource:
    '''
    Abstract base class for Resources
    '''
    def __init__(self, config, url):
        # Setup props
        self.url_string = url
        self.config = config

        # Parse and process URL
        self.url = urlparse(url)
        self.url_path_split = self.url.path.split('/')
        self.url_path_basename = self.url_path_split[-1]
        if len(self.url_path_basename) < 1:
            # Path is too small, probably ends with /, try 1 up
            self.url_path_basename = self.url_path_split[-2]
        self.basename = self._get_basename()

        # Generate MD5
        self.md5 = hashlib.md5(self.url_string.encode('utf-8')).hexdigest()

        # Generate filepath
        self.cache_path = os.path.join(
                self.config.PATH_PREFIX,
                *self.path_grouping(),
                self.basename,
            )

    def _get_basename(self):
        NotImplemented

    def path_grouping(self):
        if self.config.PATH_GROUPING == 'MD5':
            return group_by(self.md5, 8)
        return ['']

    def cache_makedirs(self):
        '''
        Make necessary directories to hold cache value
        '''
        dirname = os.path.dirname(self.cache_path)
        os.makedirs(dirname, exist_ok=True)

    def cache_open(self, mode='rb'):
        if mode == 'wb':
            self.cache_makedirs()
        return open(self.cache_path, mode=mode)

    def cache_exists(self):
        return os.path.exists(self.cache_path)

    def __hash__(self):
        return hash(self.url_string)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented



class ForeignResource(Resource):
    def _get_basename(self):
        return self.url_path_basename

    def download(self):
        req = requests.get(self.url_string, stream=True)
        with self.cache_open('wb') as f:
            shutil.copyfileobj(req.raw, f)

    def validate(self):
        if not check_url(self.config, self.url):
            raise URLError('Invalid URL: "%s"' % self.url_string)

    def guess_typed(self):
        if not self.cache_exists():
            raise CacheError('Cannot guess type without first downloaded')
        ts = guess_typestring(self.cache_path)
        return TypedForeignResource(self.config, self.url_string, ts)


class TypedForeignResource(Resource):
    def __init__(self, config, url, typestring):
        self.typestring = typestring
        super().__init__(config, url)

    def _get_basename(self):
        # Ignores URL basename
        base, _ = os.path.splitext(self.url_path_basename)
        return self.typestring.modify_basename(base)

    def symlink_from(self, foreign_resource):
        if foreign_resource.cache_path == self.cache_path:
            return
        os.symlink(foreign_resource.cache_path, self.cache_path)


class TypedResource(Resource):
    def __init__(self, config, url, typestring):
        self.typestring = typestring
        super().__init__(config, url)

    def _get_basename(self):
        return self.typestring.modify_basename(self.url_path_basename)

    def __hash__(self):
        return hash('%s - %s' % (self.url_string, str(self.typestring)))


class TypedLocalResource(Resource):
    def __init__(self, config, path, typestring=None):
        self.path = path

        if typestring:
            # TypeString specified: not foreign, should munge path
            self.foreign = False
        else:
            # No TypeString specified: foreign, keep path but guess type
            self.foreign = True
            typestring = guess_typestring(path)

        self.typestring = typestring
        super().__init__(config, 'file://%s' % path)
        if self.foreign:
            self.cache_path = self.path

    def _get_basename(self):
        if self.foreign:
            return os.path.basename(self.path)
        else:
            return self.typestring.modify_basename(self.url_path_basename)

    def __hash__(self):
        return hash(self.path)


class TypedPathedLocalResource(TypedLocalResource):
    def __init__(self, config, path, typestring):
        super().__init__(config, path, typestring)
        self.cache_path = os.path.join(
            os.path.dirname(path),
            self._get_basename(),
        )

    def _get_basename(self):
        base, _ = os.path.splitext(self.path)
        return self.typestring.modify_basename(base)


class URLError(ValueError): pass
class CacheError(RuntimeError): pass


def check_url(config, url):
    if config.ALLOWED_LOCATIONS == '*':
        return True
    return url.netloc in config.ALLOWED_LOCATIONS
