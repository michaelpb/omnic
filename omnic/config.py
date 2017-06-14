import os
import importlib

from omnic import default_settings
from omnic import singletons


class Settings:
    def __init__(self):
        self.default_settings_module = default_settings
        custom_settings_path = os.environ.get('OMNIC_SETTINGS')
        self.settings_module = object()
        if custom_settings_path:
            self.settings_module = importlib.import_module(custom_settings_path)

    def use_settings(self, settings_module):
        self.settings_module = settings_module

    def __getattr__(self, key):
        if key.upper() != key: # not upper case
            raise AttributeError('Invalid settings attribute, '
                'must be all-uppercase: "%s"' % key)
        try:
            return getattr(self.settings_module, key)
        except AttributeError:
            pass

        try:
            return getattr(self.default_settings_module, key)
        except AttributeError:
            pass

        raise AttributeError('Invalid settings: "%s"' % key)

singletons.register('settings', Settings)


def load_settings():
    from omnic import default_settings
    from omnic.conversion.converter import ConverterGraph
    from omnic.responses.placeholder import PlaceholderSelector
    settings = default_settings
    custom_settings_path = os.environ.get('OMNIC_SETTINGS')
    if custom_settings_path:
        # TODO import here
        pass
    return default_settings


def override_settings(new_settings):
    global settings
    old_settings = settings
    settings = new_settings
    return old_settings


def get_settings():
    global settings
    if not settings:
        settings = load_settings()
    return settings


settings = load_settings()
