import os
import importlib

from omnic import default_settings


class Settings:
    def __init__(self):
        self.default_settings_module = default_settings
        custom_settings_path = os.environ.get('OMNIC_SETTINGS')
        self.settings_module = object()
        if custom_settings_path:
            self.settings_module = importlib.import_module(
                custom_settings_path)

    def use_settings(self, settings_module):
        '''
        Useful for tests for overriding current settings manually
        '''
        self._previous_settings = self.settings_module
        self.settings_module = settings_module

    def use_previous_settings(self):
        '''
        Useful for tests for restoring previous state of singleton
        '''
        self.settings_module = self._previous_settings

    def __getattr__(self, key):
        if key.upper() != key:  # not upper case
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
