import os
import shutil

from omnic import singletons
from omnic.types.resourceurl import BytesResourceURL, ResourceURL
from omnic.utils.iters import group_by

try:
    import requests
except ImportError:
    requests = None


class Resource:
    '''
    Abstract base class for Resources
    '''
    __slots__ = (
        # Slots used by all Resources
        'url', 'url_string',
        'basename', 'md5', 'cache_path_base', 'cache_path'

        # Optional slots used by subclasses
        'typestring', 'foreign', 'data',
    )

    def __init__(self, resource_url):
        # Coerce resource_url to ResourceURL if necessary
        if isinstance(resource_url, str):
            resource_url = ResourceURL(resource_url)
        self.url = resource_url

        # Alias properties of URL
        self.url_string = str(self.url)
        self.md5 = self.url.md5

        # Generate filepath
        self.basename = self._get_basename()
        self.cache_path_base = os.path.join(
            singletons.settings.PATH_PREFIX,
            self._get_cache_interfix(),
            *self.path_grouping(),
        )

        self.cache_path = os.path.join(
            self.cache_path_base,
            self.basename,
        )

    def _get_cache_interfix(self):
        return singletons.settings.RESOURCE_CACHE_INTERFIX

    def _get_basename(self):
        raise NotImplementedError()

    def path_grouping(self):
        if singletons.settings.PATH_GROUPING is None:
            return ['']
        if singletons.settings.PATH_GROUPING == 'MD5':
            return group_by(self.md5, 8)
        raise singletons.settings.Error('Invalid PATH_GROUPING')

    def cache_makedirs(self, subdir=None):
        '''
        Make necessary directories to hold cache value
        '''
        if subdir is not None:
            dirname = self.cache_path
            if subdir:
                dirname = os.path.join(dirname, subdir)
        else:
            dirname = os.path.dirname(self.cache_path)
        os.makedirs(dirname, exist_ok=True)

    def cache_lock(self):
        '''
        Call AFTER a resource has been prepared or finished resolving.
        '''
        pass  # TODO fill in

    def cache_open(self, mode='rb'):
        if 'w' in mode:
            self.cache_makedirs()
        return open(self.cache_path, mode=mode)

    def cache_open_as_dir(self, filepath, mode='rb'):
        if 'w' in mode:
            self.cache_makedirs(subdir=os.path.dirname(filepath))
        path = os.path.join(self.cache_path, filepath)
        return open(path, mode=mode)

    def cache_exists(self):
        return os.path.exists(self.cache_path)

    async def cache_ready(self):
        # TODO fill in, check if locked
        return os.path.exists(self.cache_path)

    def cache_remove(self):
        return os.unlink(self.cache_path)

    def cache_remove_as_dir(self):
        return shutil.rmtree(self.cache_path)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, repr(self.url_string))

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
    '''
    A resource from a foreign source (e.g. a URL), which does not have a known
    type, and may or may not be downloaded.
    '''

    def _get_basename(self):
        return self.url.path_basename

    def download(self):
        # DEPRECATED
        if requests is None:
            raise RuntimeError('requests is not installed')
        req = requests.get(self.url_string, stream=True)
        with self.cache_open('wb') as f:
            shutil.copyfileobj(req.raw, f)

    def validate(self):
        if not check_url(singletons.settings, self.url.parsed):
            raise URLError('Invalid URL: "%s"' % self.url_string)

    def guess_typed(self):
        if not self.cache_exists():
            raise CacheError('Cannot guess type without first downloaded')
        ts = singletons.detectors.detect(self.cache_path)
        return TypedForeignResource(self.url_string, ts)

    def cache_remove_all(self):
        return shutil.rmtree(self.cache_path_base)


class MutableResource(ForeignResource):
    '''
    A Mutable Resource resource from a foreign source (e.g. a URL)
    '''

    def _get_cache_interfix(self):
        return singletons.settings.MUTABLE_RESOURCE_CACHE_INTERFIX


class TypedForeignResource(Resource):
    '''
    A resource freshly downloaded from a foreign source that has a known
    (guessed) type.
    '''

    def __init__(self, url, typestring):
        self.typestring = typestring
        super().__init__(url)

    def __repr__(self):
        return '%s%s' % (
            type(self).__name__,
            repr((self.url_string, self.typestring))
        )

    def _get_basename(self):
        # Ignores URL basename
        base, _ = os.path.splitext(self.url.path_basename)
        return self.typestring.modify_basename(base)

    def symlink_from(self, foreign_resource):
        if foreign_resource.cache_path == self.cache_path:
            return
        os.symlink(foreign_resource.cache_path, self.cache_path)


class TypedResource(Resource):
    '''
    A resource that is or will be the result of a conversion, thus having
    a known type.
    '''

    def __init__(self, url_string, typestring):
        self.typestring = typestring
        super().__init__(url_string)

    def __repr__(self):
        name = type(self).__name__
        tup = (name, repr(self.url_string), repr(self.typestring))
        return '%s(%s, %s)' % tup

    def _get_basename(self):
        return self.typestring.modify_basename(self.url.path_basename)

    def __hash__(self):
        return hash('%s - %s' % (self.url_string, str(self.typestring)))


class TypedLocalResource(Resource):
    '''
    A resource which is treated like a foreign resource, but originates from a
    path instead of an URL.

    Used in CLI conversions.
    '''

    def __init__(self, path, typestring=None):
        self.path = path

        if typestring:
            # TypeString specified: not foreign, should munge path
            self.foreign = False
        else:
            # No TypeString specified: foreign, keep path but guess type
            self.foreign = True
            typestring = singletons.detectors.detect(path)

        self.typestring = typestring
        super().__init__('file://%s' % path)
        if self.foreign:
            self.cache_path = self.path

    def _get_basename(self):
        if self.foreign:
            return os.path.basename(self.path)
        else:
            return self.typestring.modify_basename(self.url.path_basename)

    def __hash__(self):
        return hash(self.path)


class TypedPathedLocalResource(TypedLocalResource):
    '''
    Like a TypedLocalResource, but is also opinionated about where it should be
    stored, typically somewhere other than the cache.

    Used in CLI conversions.
    '''

    def __init__(self, path, typestring):
        super().__init__(path, typestring)
        self.cache_path = os.path.join(
            os.path.dirname(path),
            self._get_basename(),
        )

    def _get_basename(self):
        base, _ = os.path.splitext(self.path)
        return self.typestring.modify_basename(base)


class ForeignBytesResource(ForeignResource):
    '''
    A foreign resource that consists of a string of bytes instead of a URL.
    '''

    def __init__(self, data, extension=None, basename='source'):
        self.data = data
        super().__init__(BytesResourceURL(data, extension, basename))

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, repr(self.data))

    def save(self):
        with self.cache_open('wb') as f:
            f.write(self.data)

    def download(self):
        self.save()

    def validate(self):
        # For now, validate all foreign string resources (should eventually add
        # security measures here)
        pass


class URLError(ValueError):
    pass


class CacheError(RuntimeError):
    pass


def check_url(config, url):
    if config.ALLOWED_LOCATIONS == '*':
        return True
    return url.netloc in config.ALLOWED_LOCATIONS
