import os
import mimetypes
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

class Detector:
    def can_improve(self, typestring):
        return False

    def can_detect(self, path):
        return False

    def detect(self, path):
        return UNKNOWN


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
        return UNKNOWN


class ExtensionDetector(Detector):
    def can_detect(self, path):
        return '.' in os.path.basename(path)

    def detect(self, path):
        # Otherwise, tries based on extension
        _, ext = os.path.splitext(path)
        ext = ext.strip('.').upper()
        if not ext:
            return UNKNOWN
        return TypeString(ext)


class DetectorManager:
    def __init__(self):
        # TODO: Make configurable in settings
        self.detectors = [
            MagicDetector(),
            ExtensionDetector(),
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
            typestring = detector.detect(path)
        return typestring

singletons.register('detectors', DetectorManager)
