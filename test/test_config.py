"""
Tests for `config` module.
"""
import os

import pytest

from omnic.config.exceptions import ConfigurationError
from omnic.config.settingsmanager import SettingsManager

TEST_SETTING = 123


class ExampleClassA:
    pass


class ExampleClassB:
    pass


class TestForeignResource:
    def test_default(self):
        settings = SettingsManager()
        assert settings.SERVICES

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

    def test_custom(self):
        # Simply use self as a test settings
        os.environ['OMNIC_SETTINGS'] = 'test.test_config'
        settings = SettingsManager()
        assert settings.TEST_SETTING == 123

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
