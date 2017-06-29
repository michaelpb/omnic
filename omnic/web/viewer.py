import os

from omnic import singletons


class ViewerManager:
    def __init__(self, viewer_list=None):
        self.viewers = viewer_list
        if self.viewers is None:
            self.viewers = singletons.settings.load_all('VIEWERS')

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


class Viewer:
    pass


singletons.register('viewers', ViewerManager)
