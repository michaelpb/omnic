import os

from omnic.types.typestring import TypeString
from omnic.types.detectors import DIRECTORY, Detector

NODE_PACKAGE = TypeString('nodepackage')
INSTALLED_NODE_PACKAGE = TypeString('installed_nodepackage')

PACKAGE_JSON = 'package.json'
NODE_MODULES = 'node_modules'


class NodePackageDetector(Detector):
    def can_improve(self, typestring):
        return typestring == DIRECTORY

    def can_detect(self, path):
        return os.path.isdir(path) and PACKAGE_JSON in os.listdir(path)

    def detect(self, path):
        package_path = os.path.join(path, PACKAGE_JSON)
        try:
            with open(package_path, 'rb') as fd:
                if b'{' not in fd.read(8):
                    return None  # Not even remotely valid package.json
        except OSError:
            return None  # Can't read package.json file

        # Now check which type
        if NODE_MODULES in os.listdir(path):
            return INSTALLED_NODE_PACKAGE  # Has a node_modules dir
        return NODE_PACKAGE
