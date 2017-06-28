import os

from omnic.types.detectors import DIRECTORY, Detector
from omnic.types.typestring import TypeString

NODE_PACKAGE = TypeString('nodepackage')
INSTALLED_NODE_PACKAGE = TypeString('installed_nodepackage')
WEBPACK_NODE_PACKAGE = TypeString('webpack_nodepackage')
INSTALLED_WEBPACK_NODE_PACKAGE = TypeString('webpack_installed_nodepackage')

PACKAGE_JSON = 'package.json'
NODE_MODULES = 'node_modules'
WEBPACK_CONFIG_JS = 'webpack_config_js'


class NodePackageDetector(Detector):
    def can_improve(self, typestring):
        return typestring == DIRECTORY

    def can_detect(self, path):
        return os.path.isdir(path) and PACKAGE_JSON in os.listdir(path)

    def detect(self, path):
        files = os.listdir(path)
        if PACKAGE_JSON not in files:
            return None

        package_path = os.path.join(path, PACKAGE_JSON)
        try:
            with open(package_path, 'rb') as fd:
                if b'{' not in fd.read(8):
                    return None  # Not even remotely valid package.json
        except OSError:
            return None  # Can't read package.json file

        # Now check which permutation of known node package types
        is_installed = NODE_MODULES in files
        is_webpack = WEBPACK_CONFIG_JS in files
        return {
            is_webpack and is_installed: INSTALLED_WEBPACK_NODE_PACKAGE,
            is_webpack and not is_installed: WEBPACK_NODE_PACKAGE,
            not is_webpack and is_installed: INSTALLED_NODE_PACKAGE,
            not is_webpack and not is_installed: NODE_PACKAGE,
        }[True]
