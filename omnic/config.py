import os
import importlib
import logging
from logging import config

from omnic import default_settings


class ConfigurationError(Exception):
    pass


class Settings:
    def __init__(self):
        self.default_settings_module = default_settings
        path = os.environ.get('OMNIC_SETTINGS')
        self.settings_module = object()
        if path:
            try:
                self.settings_module = importlib.import_module(path)
            except ImportError as e:
                msg = 'Cannot load OMNIC_SETTINGS path: "%s"' % str(e)
                raise ConfigurationError(msg)

        self.reconfigure()

    def __getattr__(self, key):
        if key.upper() != key:  # not upper case
            raise AttributeError('Invalid settings attribute, '
                                 'must be all-uppercase: "%s"' % key)
        try:  # Try with the custom settings
            return getattr(self.settings_module, key)
        except AttributeError:
            pass

        try:  # Try with the default settings
            return getattr(self.default_settings_module, key)
        except AttributeError:
            pass

        raise ConfigurationError('Invalid settings: "%s"' % key)

    def reconfigure(self):
        self.load_all('AUTOLOAD')
        self.configure_logging()

    def configure_logging(self):
        if isinstance(self.LOGGING, str):
            config.fileConfig(self.LOGGING)
        elif isinstance(self.LOGGING, dict):
            config.dictConfig(self.LOGGING)
        elif isinstance(self.LOGGING, type(None)):
            # Disable all logging
            logging.disable(logging.CRITICAL)
        else:
            raise ConfigurationError('Invalid LOGGING: must be string, dict')

    def load_all(self, key):
        '''
        Useful for tests for restoring previous state of singleton
        '''
        value = getattr(self, key)
        if isinstance(value, dict):
            return {key: self.load(value) for key, value in value.items()}
        elif isinstance(value, list):
            return [self.load(value) for value in value]
        else:
            raise ValueError('load_all must be list or dict')

    def load(self, path):
        containing_module, _, last_item = path.rpartition('.')
        if last_item[0].isupper():
            # Is a class definition, should do an "import from"
            path = containing_module
        imported_obj = importlib.import_module(path)
        if last_item[0].isupper():
            try:
                imported_obj = getattr(imported_obj, last_item)
            except:
                msg = 'Cannot import "%s". ' \
                      '(Hint: CamelCase is only for classes)' % last_item
                raise ConfigurationError(msg)
        return imported_obj

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
