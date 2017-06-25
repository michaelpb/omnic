"""
Tests for `detectors` module.
"""
import tempfile

import os

from omnic.types.detectors import DetectorManager

from .testing_utils import Magic

class TestAllBuiltinDetectors:
    def setup_method(self, method):
        self.fd = tempfile.NamedTemporaryFile(suffix='test.png', delete=False)
        self.detect = DetectorManager().detect

    def test_extension_detector(self):
        self.fd.close()  # Empty file, no possible guess of mimetype, use ext
        ts = self.detect(self.fd.name)
        assert ts.mimetype == 'image/png'

    def test_magic_bytes_detector(self):
        # Even though ends with png, we write JPG magic bytes into it
        self.fd.write(bytes(Magic.JPEG))
        self.fd.close()
        ts = self.detect(self.fd.name)
        assert ts.mimetype == 'image/jpeg'

    def teardown_method(self, method):
        os.remove(self.fd.name)
