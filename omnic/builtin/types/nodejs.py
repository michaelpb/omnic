import os

from omnic.types.typestring import TypeString
from omnic.types.detectors import DIRECTORY, Detector

NODE_PACKAGE = TypeString('nodepackage')


class NodePackageDetector(Detector):
    def can_improve(self, typestring):
        return typestring == DIRECTORY

    def can_detect(self, path):
        return os.path.isdir(path) and 'package.json' in os.listdir(path)

    def detect(self, path):
        package_path = os.path.join(path, 'package.json')
        with open(package_path, 'rb') as fd:
            if b'{' in fd.read(128):  # resembles a package.json
                return NODE_PACKAGE
