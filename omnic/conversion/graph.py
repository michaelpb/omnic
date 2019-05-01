import logging

from omnic import singletons
from omnic.conversion.exceptions import ConverterUnavailable
from omnic.types.typestring import TypeString
from omnic.utils.graph import DirectedGraph
from omnic.utils.iters import pair_looper

log = logging.getLogger()


def _format(string):
    '''
    Helper alias to easily extract the TypeString format from a string
    '''
    return TypeString(string).ts_format


class ConverterGraph:
    def __init__(self, converter_list=None, prune_converters=False):
        # Configure graph from arguments and global setting
        if converter_list is None:
            converter_list = singletons.settings.load_all('CONVERTERS')
        self.converter_list = converter_list
        self._init_fields()

        settings = singletons.settings
        self._setup_converter_graph(converter_list, prune_converters)
        self._setup_preferred_paths(settings.PREFERRED_CONVERSION_PATHS)
        self._setup_profiles(settings.CONVERSION_PROFILES)

    def _init_fields(self):
        self.conversion_profiles = {}
        self.direct_converters = {}
        self.dgraph = DirectedGraph()
        self.converters = {}

    def _setup_converter_graph(self, converter_list, prune_converters):
        '''
        Set up directed conversion graph, pruning unavailable converters as
        necessary
        '''
        for converter in converter_list:
            if prune_converters:
                try:
                    converter.configure()
                except ConverterUnavailable as e:
                    log.warning('%s unavailable: %s' %
                                (converter.__class__.__name__, str(e)))
                    continue

            for in_ in converter.inputs:
                for out in converter.outputs:
                    self.dgraph.add_edge(in_, out, converter.cost)
                    self.converters[(in_, out)] = converter

            if hasattr(converter, 'direct_outputs'):
                self._setup_direct_converter(converter)

    def _setup_preferred_paths(self, preferred_conversion_paths):
        '''
        Add given valid preferred conversion paths
        '''
        for path in preferred_conversion_paths:
            for pair in pair_looper(path):
                if pair not in self.converters:
                    log.warning('Invalid conversion path %s, unknown step %s' %
                                (repr(path), repr(pair)))
                    break
            else:
                # If it did not break, then add to dgraph
                self.dgraph.add_preferred_path(*path)

    def _setup_profiles(self, conversion_profiles):
        '''
        Add given conversion profiles checking for invalid profiles
        '''
        # Check for invalid profiles
        for key, path in conversion_profiles.items():
            if isinstance(path, str):
                path = (path, )
            for left, right in pair_looper(path):
                pair = (_format(left), _format(right))
                if pair not in self.converters:
                    msg = 'Invalid conversion profile %s, unknown step %s'
                    log.warning(msg % (repr(key), repr(pair)))
                    break
            else:
                # If it did not break, then add to conversion profiles
                self.conversion_profiles[key] = path

    def _setup_direct_converter(self, converter):
        '''
        Given a converter, set up the direct_output routes for conversions,
        which is used for transcoding between similar datatypes.
        '''
        inputs = (
            converter.direct_inputs
            if hasattr(converter, 'direct_inputs')
            else converter.inputs
        )
        for in_ in inputs:
            for out in converter.direct_outputs:
                self.direct_converters[(in_, out)] = converter

    def find_path(self, in_, out):
        '''
        Given an input and output TypeString, produce a graph traversal,
        keeping in mind special options like Conversion Profiles, Preferred
        Paths, and Direct Conversions.
        '''
        if in_.arguments:
            raise ValueError('Cannot originate path in argumented TypeString')

        # Determine conversion profile. This is either simply the output, OR,
        # if a custom profile has been specified for this output, that custom
        # path or type is used.
        profile = self.conversion_profiles.get(str(out), str(out))
        if isinstance(profile, str):
            profile = (profile, )
        types_by_format = {_format(s): TypeString(s) for s in profile}

        # Normalize input and output types to string
        in_str = str(in_)
        out_str = _format(profile[0])

        # First check for direct conversions, returning immediately if found
        direct_converter = self.direct_converters.get((in_str, out_str))
        if direct_converter:
            out_ts = types_by_format.get(out_str, TypeString(out_str))
            return [(direct_converter, TypeString(in_str), out_ts)]

        # No direct conversions was found, so find path through graph.
        # If profile was plural, add in extra steps.
        path = self.dgraph.shortest_path(in_str, out_str)
        path += profile[1:]

        # Loop through each edge traversal, adding converters and type
        # string pairs as we go along. This is to ensure conversion
        # profiles that have arguments mid-profile get included.
        results = []
        for left, right in pair_looper(path):
            converter = self.converters.get((_format(left), _format(right)))
            right_typestring = types_by_format.get(right, TypeString(right))
            results.append((converter, TypeString(left), right_typestring))
        return results

    def find_path_with_profiles(self, conversion_profiles, in_, out):
        '''
        Like find_path, except forces the conversion profiles to be the given
        conversion profile setting. Useful for "temporarily overriding" the
        global conversion profiles with your own.
        '''
        original_profiles = dict(self.conversion_profiles)
        self._setup_profiles(conversion_profiles)
        results = self.find_path(in_, out)
        self.conversion_profiles = original_profiles
        return results


singletons.register('converter_graph', ConverterGraph)
