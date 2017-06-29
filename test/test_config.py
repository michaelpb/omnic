"""
Tests for `config` module.
"""
import os
import tempfile

import pytest

from omnic.config.exceptions import ConfigurationError
from omnic.config.settingsmanager import SettingsManager
from .testing_utils import Magic, rm_tmp_files

TEST_SETTING = 123


class ExampleClassA:
    pass


class ExampleClassB:
    pass


class TestSettings:
    def test_overriding(self):
        settings = SettingsManager()
        assert settings.SERVICES

        class MockSettings:
            SERVICES = []
        settings.use_settings(MockSettings)
        assert not settings.SERVICES

    def test_catching_lowercase_errors(self):
        settings = SettingsManager()

        class MockSettings:
            private_thing = 123
        settings.use_settings(MockSettings)
        with pytest.raises(AttributeError):
            settings.private_thing

class TestSettingsCustom:
    def setup_method(self, method):
        self._original = os.environ.get('OMNIC_SETTINGS', None)
        self._original_cwd = os.getcwd()
        if self._original:
            del os.environ['OMNIC_SETTINGS']

    def teardown_method(self, method):
        if not self._original:
            if 'OMNIC_SETTINGS' in os.environ:
                del os.environ['OMNIC_SETTINGS']
        else:
            os.environ['OMNIC_SETTINGS'] = self._original
        os.chdir(self._original_cwd)

    def test_custom_with_environ(self):
        # Simply use self as a test settings
        os.environ['OMNIC_SETTINGS'] = 'test.test_config'
        settings = SettingsManager()
        assert settings.TEST_SETTING == 123

    def test_custom_with_settings_py(self):
        with tempfile.TemporaryDirectory() as tempdir:
            os.chdir(tempdir)
            with open(os.path.join(tempdir, 'settings.py'), 'w+') as f:
                f.write('SOME_TEST_VALUE = 1337')
            settings = SettingsManager()
            assert settings.SOME_TEST_VALUE == 1337


class TestSettingsLoading:
    def test_loading_modules(self):
        # Simply use self as a test settings
        settings = SettingsManager()

        class MockSettings:
            SERVICES = [
                'test.test_config',
            ]
        settings.use_settings(MockSettings)
        assert len(settings.load_all('SERVICES')) == 1
        assert hasattr(settings.load_all('SERVICES')[0], 'TEST_SETTING')

    def test_loading_class_modules(self):
        # Simply use self as a test settings
        settings = SettingsManager()

        class MockSettings:
            SERVICES = [
                'test.test_config.ExampleClassA',
            ]
        settings.use_settings(MockSettings)
        assert len(settings.load_all('SERVICES')) == 1
        assert settings.load_all('SERVICES')[0] is ExampleClassA

    def test_loading_exceptions(self):
        # Simply use self as a test settings
        settings = SettingsManager()

        class MockSettings:
            SERVICES = [
                'test.test_config.DoesntExist',
            ]
        settings.use_settings(MockSettings)
        with pytest.raises(ConfigurationError):
            settings.load_all('SERVICES')

    def test_loading_modules_dict(self):
        # Simply use self as a test settings
        settings = SettingsManager()

        class MockSettings:
            SERVICES = {
                'a': 'test.test_config.ExampleClassA',
                'b': 'test.test_config.ExampleClassB',
            }
        settings.use_settings(MockSettings)
        assert len(settings.load_all('SERVICES')) == 2
        assert settings.load_all('SERVICES')['a'] is ExampleClassA
        assert settings.load_all('SERVICES')['b'] is ExampleClassB
