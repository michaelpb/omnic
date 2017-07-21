import json
import os

from omnic import singletons
from omnic.types.resource import ForeignBytesResource

VIEWER_EXT = 'omnic_viewer_descriptor'  # TODO Hack


class ViewerManager:
    def __init__(self, viewer_list=None):
        settings = singletons.settings
        self.viewers = viewer_list
        if self.viewers is None:
            self.viewers = settings.load_all('VIEWERS', default=DefaultViewer)

    def prefix_asset(self, viewer, relpath):
        return os.path.join(viewer.asset_dir, relpath)

    def get_assets(self):
        '''
        Return a flat list of absolute paths to all assets required by this
        viewer
        '''
        return sum([
            [self.prefix_asset(viewer, relpath) for relpath in viewer.assets]
            for viewer in self.viewers
        ], [])

    def get_node_packages(self):
        '''
        Return a flat list of absolute paths to all node modules required by
        this viewer
        '''
        return {
            viewer.name: viewer.node_package
            for viewer in self.viewers
        }

    def get_resource(self):
        '''
        Returns a BytesResource to build the viewers JavaScript
        '''
        # basename = 'viewers_%s' % settings.get_cache_string()
        node_packages = self.get_node_packages()
        viewers_data = json.dumps(node_packages).encode('utf8')
        viewers_resource = ForeignBytesResource(
            viewers_data,
            extension=VIEWER_EXT,
            # basename=basename,
        )
        return viewers_resource


class DefaultViewer:
    def __init__(self, import_path):
        _package_dir = singletons.settings \
            .import_path_to_absolute_path(import_path, 'package.json')
        _package_json_path = os.path.join(_package_dir, 'package.json')

        with open(_package_json_path) as fd:
            package_json = json.load(fd)

        self.types = package_json['omnic']['types']
        self.name = package_json['name']
        self.asset_dir = _package_dir
        self.assets = []
        self.node_package = 'file:%s' % _package_dir


singletons.register('viewers', ViewerManager)
