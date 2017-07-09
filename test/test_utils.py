"""
Tests for `utils` module.
"""
import tempfile
from os.path import islink, join

import pytest

from omnic.utils import filesystem, graph, iters

from .testing_utils import clear_tmp_files, gen_tmp_files


class TestDirectedGraph:
    #  ,-> F ,-> E
    # A -> B  -> C
    #        '-> D
    def _simple_tree(self):
        self.dg = graph.DirectedGraph()
        self.dg.add_edge('A', 'B', 1)
        self.dg.add_edge('A', 'F', 1)
        self.dg.add_edge('B', 'E', 1)
        self.dg.add_edge('B', 'C', 1)
        self.dg.add_edge('B', 'D', 1)

    def _add_preferred_path(self):
        self.dg.add_preferred_path('A', 'Z', 'B')

    #  ,-> F - - - -.
    # '    v         v
    # A -> B -> G -> C
    def _multi_pathed_graph(self):
        self.dg = graph.DirectedGraph()
        self.dg.add_edge('A', 'B', 1)
        self.dg.add_edge('B', 'G', 1)
        self.dg.add_edge('G', 'C', 1)
        self.dg.add_edge('A', 'F', 1)
        self.dg.add_edge('F', 'C', 1)
        self.dg.add_edge('F', 'B', 1)

    #  5-> F - - - -.
    # '    v         v
    # A -> B -> G -> C
    def _multi_pathed_graph_weighted(self):
        self.dg = graph.DirectedGraph()
        self.dg.add_edge('A', 'B', 1)
        self.dg.add_edge('B', 'G', 1)
        self.dg.add_edge('G', 'C', 1)
        self.dg.add_edge('A', 'F', 5)
        self.dg.add_edge('F', 'C', 1)
        self.dg.add_edge('F', 'B', 1)

    #  STL  .   MOV .   GIF .
    #  OBJ   -> AVI  -> JPG  -> thumb.png
    #  MESH '   MP4 '   PNG '
    #      \\\         .^
    #       ''---------
    #  MP3 .
    #  WAV  -> cleaned.ogg
    #  OGG '

    def _realistic_edges(self):
        self.dg = graph.DirectedGraph()
        self.dg.add_edge('MOV', 'JPG')
        self.dg.add_edge('AVI', 'JPG')
        self.dg.add_edge('MP4', 'JPG')
        self.dg.add_edge('JPG', 'thumb.png')
        self.dg.add_edge('PNG', 'thumb.png')
        self.dg.add_edge('GIF', 'thumb.png')
        self.dg.add_edge('STL', 'AVI')
        self.dg.add_edge('OBJ', 'AVI')
        self.dg.add_edge('MESH', 'AVI')
        self.dg.add_edge('STL', 'PNG')
        self.dg.add_edge('OBJ', 'PNG')
        self.dg.add_edge('MESH', 'PNG')
        self.dg.add_edge('MP3', 'cleaned.ogg')
        self.dg.add_edge('WAV', 'cleaned.ogg')
        self.dg.add_edge('OGG', 'cleaned.ogg')

    def test_simple_routes(self):
        self._simple_tree()
        path = self.dg.shortest_path('A', 'B')
        assert path == ('A', 'B')
        path = self.dg.shortest_path('A', 'C')
        assert path == ('A', 'B', 'C')
        path = self.dg.shortest_path('A', 'E')
        assert path == ('A', 'B', 'E')
        path = self.dg.shortest_path('A', 'D')
        assert path == ('A', 'B', 'D')
        path = self.dg.shortest_path('B', 'C')
        assert path == ('B', 'C')

    def test_special_paths(self):
        self._simple_tree()
        self._add_preferred_path()
        path = self.dg.shortest_path('A', 'B')
        assert path == ('A', 'Z', 'B')
        path = self.dg.shortest_path('A', 'C')
        assert path == ('A', 'B', 'C')

    def test_raises_on_invalid_path(self):
        self._simple_tree()
        with pytest.raises(graph.DirectedGraph.NoPath):
            self.dg.shortest_path('B', 'A')

    def test_shortest_route(self):
        self._multi_pathed_graph()
        path = self.dg.shortest_path('A', 'B')
        assert path == ('A', 'B')
        path = self.dg.shortest_path('F', 'B')
        assert path == ('F', 'B')
        path = self.dg.shortest_path('F', 'G')
        assert path == ('F', 'B', 'G')
        path = self.dg.shortest_path('F', 'C')
        assert path == ('F', 'C')
        path = self.dg.shortest_path('A', 'G')
        assert path == ('A', 'B', 'G')
        path = self.dg.shortest_path('A', 'C')
        assert path == ('A', 'F', 'C')

    def test_weighted_shortest_route(self):
        self._multi_pathed_graph_weighted()
        path = self.dg.shortest_path('A', 'B')
        assert path == ('A', 'B')
        path = self.dg.shortest_path('F', 'B')
        assert path == ('F', 'B')
        path = self.dg.shortest_path('F', 'G')
        assert path == ('F', 'B', 'G')
        path = self.dg.shortest_path('F', 'C')
        assert path == ('F', 'C')
        path = self.dg.shortest_path('A', 'G')
        assert path == ('A', 'B', 'G')
        path = self.dg.shortest_path('A', 'C')
        assert path == ('A', 'B', 'G', 'C')  # Avoid A->F route

    def test_realistic_routing(self):
        self._realistic_edges()
        path = self.dg.shortest_path('STL', 'thumb.png')
        assert path == ('STL', 'PNG', 'thumb.png')
        path = self.dg.shortest_path('MESH', 'JPG')
        assert path == ('MESH', 'AVI', 'JPG')
        path = self.dg.shortest_path('MP3', 'cleaned.ogg')
        assert path == ('MP3', 'cleaned.ogg')
        with pytest.raises(graph.DirectedGraph.NoPath):
            self.dg.shortest_path('MP3', 'thumb.png')


class TestIterUtils:
    def test_pair_looper(self):
        pair_looper = iters.pair_looper
        assert list(pair_looper([1, 2, 3])) == [(1, 2), (2, 3)]
        assert list(pair_looper([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]
        assert list(pair_looper([1])) == []
        assert list(pair_looper([])) == []

    def test_first_last_iterator(self):
        first_last_iterator = iters.first_last_iterator
        for first, last, i in first_last_iterator([1, 2, 3]):
            assert i in (1, 2, 3)
            if i == 1:
                assert first and not last
            if i == 2:
                assert not first and not last
            if i == 3:
                assert not first and last

        for first, last, i in first_last_iterator([1]):
            assert i == 1
            assert first and last

    def test_group_by(self):
        group_by = iters.group_by
        assert list(group_by('asdf', 2)) == ['as', 'df']


class TestFilesystemUtils:
    FILES = [
        'testfile',
        'config/thing/thing.xml',
    ]

    def setup_method(self, method):
        self.dir = tempfile.mkdtemp(prefix='tmp_omnic_test_')
        self.out = tempfile.mkdtemp(prefix='tmp_omnic_test_out_')
        gen_tmp_files(self.dir, self.FILES)
        self.results = set([
            (join(self.dir, 'testfile'),
                join(self.out, 'testfile')),
            (join(self.dir, 'config/thing/thing.xml'),
                join(self.out, 'config/thing/thing.xml')),
        ])

    def teardown_method(self, method):
        clear_tmp_files(self.dir, self.FILES)
        clear_tmp_files(self.out, self.FILES)

    def test_directory_walk(self):
        results = list(filesystem.directory_walk(self.dir, self.out))
        results_set = set(results)
        assert len(results_set) == len(results)  # ensure no dupes
        assert results_set == self.results

    def test_recursive_symlinks(self):
        filesystem.recursive_symlink_dirs(self.dir, self.out)

        # Now use walk to check that we did it successfully
        results = set(filesystem.directory_walk(self.out, self.out))
        assert len(results) == len(self.results)  # ensure right number
        for path, _ in results:
            assert islink(path)

    def test_recursive_hardlinks(self):
        filesystem.recursive_hardlink_dirs(self.dir, self.out)

        # Now use walk to check that we did it successfully
        results = set(filesystem.directory_walk(self.out, self.out))
        assert len(results) == len(self.results)  # ensure right number
        for path, _ in results:
            assert not islink(path)  # ensure hardlinks
