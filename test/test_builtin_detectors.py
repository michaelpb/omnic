"""
Tests for `detectors` module.
"""
import os
import tempfile

from omnic.builtin.types.core import ManifestDetector
from omnic.builtin.types.nodejs import NodePackageDetector
from omnic.types.detectors import DetectorManager
from omnic.types.typestring import TypeString

from .testing_utils import Magic


class TestManifestDetector:
    def setup_method(self, method):
        self.fd = tempfile.NamedTemporaryFile(
            suffix='manifest.json', delete=False)
        self.d = ManifestDetector()

    def teardown_method(self, method):
        if not self.fd.closed:
            self.fd.close()
        os.remove(self.fd.name)

    def test_can_improve(self):
        assert not self.d.can_improve(TypeString('PNG'))
        assert not self.d.can_improve(TypeString('manifest.json'))
        assert self.d.can_improve(TypeString('application/json'))
        assert self.d.can_improve(TypeString('JSON'))

    def test_can_detect(self):
        assert self.d.can_detect('/path/to/manifest.json')
        assert not self.d.can_detect('/path/to/manifest.json.js')
        assert not self.d.can_detect('/path/to/other.json')

    def test_detect_empty(self):
        assert self.d.detect(self.fd.name) == None

    def test_detect_json(self):
        self.fd.write(b'{"JSON": true}')
        self.fd.close()  # Empty file
        assert str(self.d.detect(self.fd.name)) == 'manifest.json'


class TestNodePackageDetector:
    def setup_method(self, method):
        self.path = tempfile.mkdtemp(prefix='omnic_test_')
        self.pjson_path = os.path.join(self.path, 'package.json')
        self.d = NodePackageDetector()
        self.fd = None

    def teardown_method(self, method):
        if self.fd and not self.fd.closed:
            self.fd.close()
        try:
            os.remove(self.pjson_path)
        except OSError:
            pass
        os.removedirs(self.path)

    def _write_pjson(self):
        self.fd = open(self.pjson_path, 'w+')
        self.fd.write('{}')
        self.fd.close()

    def test_can_improve(self):
        assert not self.d.can_improve(TypeString('PNG'))
        assert self.d.can_improve(TypeString('directory'))

    def test_can_detect(self):
        assert not self.d.can_detect(self.path)
        self._write_pjson()
        assert self.d.can_detect(self.path)

    def test_detect_empty(self):
        assert self.d.detect(self.path) == None

    def test_detect_json(self):
        self._write_pjson()
        assert str(self.d.detect(self.path)) == 'nodepackage'

    def test_detect_node_modules(self):
        self._write_pjson()
        _nm_path = os.path.join(self.path, 'node_modules')
        os.mkdir(_nm_path)
        assert str(self.d.detect(self.path)) == 'installed_nodepackage'
        os.rmdir(_nm_path)  # clean up


class TestBuiltinDetectorsForImages:
    '''
    Integration test for mimetype + extension detectors, using image examples
    '''

    def setup_method(self, method):
        self.fd = tempfile.NamedTemporaryFile(suffix='test.png', delete=False)
        self.detect = DetectorManager().detect

    def teardown_method(self, method):
        os.remove(self.fd.name)

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


class TestBuiltinDetectorsForManifest:
    '''
    Integration test for manifest detector
    '''

    def setup_method(self, method):
        self.fd = tempfile.NamedTemporaryFile(
            suffix='manifest.json', delete=False)
        self.detect = DetectorManager().detect

    def teardown_method(self, method):
        os.remove(self.fd.name)

    def test_detects_json(self):
        self.fd.write(b'{"JSON": true}')
        self.fd.close()
        ts = self.detect(self.fd.name)
        assert str(ts) == 'manifest.json'
