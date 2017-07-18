import logging

from omnic import singletons
from omnic.conversion.exceptions import ConverterUnavailable
from omnic.types.typestring import TypeString
from omnic.utils.graph import DirectedGraph
from omnic.utils.iters import pair_looper

log = logging.getLogger()


def _format(string):
    # Helper alias to easily extract the TypeString format from a string
    return TypeString(string).ts_format


class ConverterGraph:
    def __init__(self, converter_list=None, prune_converters=False):
        # Configure graph from arguments and global setting
        self.converter_list = converter_list
        if self.converter_list is None:
            self.converter_list = singletons.settings.load_all('CONVERTERS')
        self.conversion_profiles = {}

        # Set up directed conversion graph, punning unavailable converters as
        # necessary
        self.dgraph = DirectedGraph()
        self.converters = {}
        for converter in self.converter_list:
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

        # Add all valid preferred conversions
        for path in singletons.settings.PREFERRED_CONVERSION_PATHS:
            for pair in pair_looper(path):
                if pair not in self.converters:
                    log.warning('Invalid conversion path %s, unknown step %s' %
                                (repr(path), repr(pair)))
                    break
            else:
                # If it did not break, then add to dgraph
                self.dgraph.add_preferred_path(*path)

        # Check for invalid profiles
        for key, path in singletons.settings.CONVERSION_PROFILES.items():
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

    def find_path(self, in_, out):
        if in_.arguments:
            raise ValueError('Cannot originate path in argumented TypeString')

        # Determine conversion profile. This is either simply the output, OR,
        # if a custom profile has been specified for this output, that custom
        # path or type is used.
        profile = self.conversion_profiles.get(str(out), str(out))
        if isinstance(profile, str):
            profile = (profile, )
        types_by_format = {_format(s): TypeString(s) for s in profile}

        # Determine full path. If profile was plural, add in extra steps
        path = self.dgraph.shortest_path(str(in_), _format(profile[0]))
        path += profile[1:]

        # Loop through each edge traversal, adding converters and type string
        # pairs as we go along
        results = []
        for left, right in pair_looper(path):
            converter = self.converters.get((_format(left), _format(right)))
            right_typestring = types_by_format.get(right, TypeString(right))
            results.append((converter, TypeString(left), right_typestring))
        return results


singletons.register('converter_graph', ConverterGraph)
