import logging

from omnic import singletons
from omnic.types.typestring import TypeString
from omnic.utils.graph import DirectedGraph
from omnic.utils.iters import pair_looper
from omnic.conversion.exceptions import ConverterUnavailable

log = logging.getLogger()

class ConverterGraph:
    def __init__(self, converter_list=None, prune_converters=False):
        self.converter_list = converter_list
        self.preferred_conversions = []
        if self.converter_list is None:
            self.converter_list = singletons.settings.load_all('CONVERTERS')
            self.preferred_conversions = singletons.settings.CONVERSIONS
        self.dgraph = DirectedGraph()
        self.converters = {}
        for converter in self.converter_list:
            if prune_converters:
                try:
                    converter.configure()
                except ConverterUnavailable as e:
                    log.warn('%s unavailable: %s' %
                        (converter.__class__.__name__, str(e)))
                    continue

            for in_ in converter.inputs:
                for out in converter.outputs:
                    self.dgraph.add_edge(in_, out, converter.cost)
                    self.converters[(in_, out)] = converter


        # Add all valid preferred conversions
        for path in self.preferred_conversions:
            for pair in pair_looper(path):
                if pair not in self.converters:
                    log.warn('Invalid conversion path %s, unknown step %s' %
                        (repr(path), repr(pair)))
                    break
            else:
                # If it did not break, then add to dgraph
                self.dgraph.add_preferred_path(*path)

    def find_path(self, in_, out):
        in_f = in_.ts_format
        out_f = out.ts_format
        path = self.dgraph.shortest_path(in_f, out_f)
        results = []
        # Loop through each edge traversal, adding converters and type
        # string pairs as we go along
        for left, right in pair_looper(path):
            converter = self.converters.get((left, right))
            ts_left = TypeString(left)
            ts_right = out if out.ts_format == right else TypeString(right)
            results.append((converter, ts_left, ts_right))
        return results


singletons.register('converter_graph', ConverterGraph)
