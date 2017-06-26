from omnic.types.typestring import TypeString
from omnic.utils.graph import DirectedGraph
from omnic.utils.iters import pair_looper
from omnic import singletons


class ConverterGraph:
    def __init__(self, converter_list=None):
        self.converter_list = converter_list
        if self.converter_list is None:
            self.converter_list = singletons.settings.load_all('CONVERTERS')
            #self.converter_list = singletons.settings.CONVERTERS
        self.dgraph = DirectedGraph()
        self.converters = {}
        for converter in self.converter_list:
            for in_ in converter.inputs:
                for out in converter.outputs:
                    self.dgraph.add_edge(in_, out, converter.cost)
                    self.converters[(in_, out)] = converter

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
