import json
import os

from omnic import singletons


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
