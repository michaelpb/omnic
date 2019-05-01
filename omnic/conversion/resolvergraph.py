import os

from omnic import singletons
from omnic.conversion.graph import ConverterGraph
from omnic.types.resource import ForeignResource, MutableResource
from omnic.types.typestring import TypeString
from omnic.utils.iters import first_last_iterator


def _get_basename_based_on_url(resource_url):
    path_basename = resource_url.path_split[-1]
    if len(path_basename) < 1:
        # Path is too small, probably ends with /, try 1 up
        path_basename = resource_url.path_split[-2]
    return path_basename


class ResolverGraph(ConverterGraph):
    def __init__(self):
        self._init_fields()

        resolvers = singletons.settings.load_all('RESOLVERS')
        self._setup_converter_graph(resolvers, False)

        # Later, might want to enable these features:
        # self._setup_preferred_paths(settings.PREFERRED_RESOLVER_PATHS)
        # self._setup_profiles(settings.RESOLVER_PROFILES)

    def find_resource_url_basename(self, resource_url):
        '''
        Figure out path basename for given resource_url
        '''
        scheme = resource_url.parsed.scheme
        if scheme in ('http', 'https', 'file'):
            return _get_basename_based_on_url(resource_url)

        elif scheme in ('git', 'git+https', 'git+http'):
            if len(resource_url.args) == 2:
                # For now, git has 2 positional args, hash and path
                git_tree, subpath = resource_url.args
                basename = os.path.basename(subpath)
                if basename:
                    return basename  # subpath was not '/' or ''
        return _get_basename_based_on_url(resource_url)

    def find_destination_type(self, resource_url):
        '''
        Given a resource_url, figure out what it would resolve into
        '''
        resolvers = self.converters.values()
        for resolver in resolvers:
            # Not all resolvers are opinionated about destination types
            if not hasattr(resolver, 'get_destination_type'):
                continue

            destination_type = resolver.get_destination_type(resource_url)
            if destination_type:
                return destination_type

    def find_path_from_url(self, resource_url):
        destination_type = self.find_destination_type(resource_url)
        if not destination_type:
            # Means cannot identify resource_url with enabled resolvers
            raise ValueError('Cannot resolve URL: "%s"' % str(resource_url))

        input_type = TypeString(resource_url.parsed.scheme)
        return self.find_path(input_type, TypeString(destination_type))

    async def apply_resolver_path(self, resource_url, resolver_path):
        argument_free_url = resource_url.url
        for is_first, is_last, path_step in first_last_iterator(resolver_path):
            converter_class, _, _ = path_step
            converter = converter_class()
            mutable_resource = MutableResource(argument_free_url)
            out_resource = ForeignResource(resource_url)
            await converter.convert(mutable_resource, out_resource)

    async def download(self, resource_url):
        '''
        Download given Resource URL by finding path through graph and applying
        each step
        '''
        resolver_path = self.find_path_from_url(resource_url)
        await self.apply_resolver_path(resource_url, resolver_path)


singletons.register('resolver_graph', ResolverGraph)
