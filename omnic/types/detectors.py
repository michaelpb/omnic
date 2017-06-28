from omnic import singletons
from omnic.types.typestring import TypeString

UNKNOWN = TypeString('unknown')
DIRECTORY = TypeString('directory')


class Detector:
    def can_improve(self, typestring):
        return False

    def can_detect(self, path):
        return False

    def detect(self, path):
        return None


class DetectorManager:
    def __init__(self):
        self.detectors = [
            detector_class() for detector_class in
            singletons.settings.load_all('DETECTORS')
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
