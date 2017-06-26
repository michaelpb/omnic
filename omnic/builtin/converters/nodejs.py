from omnic.builtin.types.nodejs import NodePackageDetector, NODE_PACKAGE, INSTALLED_NODE_PACKAGE
from omnic.builtin.types.core import DIRECTORY
from omnic.conversion import converter


class NodePackageDetector(converter.DetectorConverter):
    detector = NodePackageDetector
    inputs = [
        str(DIRECTORY),
    ]
    outputs = [
        str(NODE_PACKAGE),
    ]


# class NPMInstalledDirectoryConverter(converter.DirectoryConverter):
class NPMInstalledDirectoryConverter(converter.Converter):
    inputs = [
        str(NODE_PACKAGE),
    ]
    outputs = [
        str(INSTALLED_NODE_PACKAGE),
    ]
