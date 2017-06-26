import os
import magic

from omnic.types.typestring import TypeString
from omnic import singletons

UNKNOWN_MIMETYPE = (
    'application/x-empty',
    'application/octet-stream',
    'text/plain',
)

UNKNOWN = TypeString('unknown')
DIRECTORY = TypeString('directory')
MANIFEST_JSON = TypeString('manifest.json')
NODE_PACKAGE = TypeString('nodepackage')


class Detector:
    def can_improve(self, typestring):
        return False

    def can_detect(self, path):
        return False

    def detect(self, path):
        return None


class MagicDetector(Detector):
    def can_detect(self, path):
        return os.path.exists(path)

    def detect(self, path):
        if os.path.isdir(path):
            return DIRECTORY
        with open(path, 'rb') as fd:
            mimetype = magic.from_buffer(fd.read(128), mime=True)
            if mimetype and mimetype not in UNKNOWN_MIMETYPE:
                return TypeString(mimetype)


class ExtensionDetector(Detector):
    def can_detect(self, path):
        return '.' in os.path.basename(path)

    def detect(self, path):
        # Otherwise, tries based on extension
        _, ext = os.path.splitext(path)
        ext = ext.strip('.').upper()
        if not ext:
            return
        return TypeString(ext)


class ManifestDetector(Detector):
    def can_improve(self, typestring):
        return typestring.extension == 'JSON'

    def can_detect(self, path):
        return os.path.basename(path).endswith('manifest.json')

    def detect(self, path):
        with open(path, 'rb') as fd:
            if b'{' in fd.read(128):
                return MANIFEST_JSON


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


class DetectorManager:
    def __init__(self):
        # TODO: Make configurable in settings
        self.detectors = [
            MagicDetector(),
            ExtensionDetector(),
            ManifestDetector(),
            NodePackageDetector(),
        ]

    def detect(self, path):
        '''
        Guesses a TypeString from the given path
        '''
        typestring = UNKNOWN
        for detector in self.detectors:
            if typestring != UNKNOWN and not detector.can_improve(typestring):
                continue
            if not detector.can_detect(path):
                continue
            detected = detector.detect(path)
            if detected:
                typestring = detected
        return typestring


singletons.register('detectors', DetectorManager)
