import os

import magic

from omnic.types.detectors import DIRECTORY, Detector
from omnic.types.typestring import TypeString

UNKNOWN_MIMETYPE = (
    'application/x-empty',
    'application/octet-stream',
    'text/plain',
)

MANIFEST_JSON = TypeString('manifest.json')


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
