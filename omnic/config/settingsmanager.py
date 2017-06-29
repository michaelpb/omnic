import importlib
import logging
import os
import sys
from logging import config

from omnic.config import default_settings
from omnic.config.exceptions import ConfigurationError


class SettingsManager:
    '''
    The `settings' singleton, used to house project settings, including logic
    to default to default setings for unset settings.
    '''

    def __init__(self):
        # Initialize main two properties
        self.default_settings_module = default_settings
        self.settings_module = None

        # Now we figure out which (if any) settings module to use
        files = os.listdir(os.getcwd())
        path = os.environ.get('OMNIC_SETTINGS')
        if path:
            try:
                settings_module = importlib.import_module(path)
            except ImportError as e:
                msg = 'Cannot load OMNIC_SETTINGS path: "%s"' % str(e)
                raise ConfigurationError(msg)
        elif 'settings.py' in files:
            # Sometimes current dir is not in path, add it in
            current_dir_set = set(['', os.getcwd(), os.path.curdir])
            if not set(sys.path) & current_dir_set:
                sys.path.append(os.getcwd())

            # Let import errors propagate naturally
            import settings as settings_module
        else:
            # By default, custom settings is an empty object
            settings_module = object()
        self.use_settings(settings_module)
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

    def load(self, key):
        '''
        Import settings key as import path
        '''
        return self.load_path(getattr(self, key))

    def load_all(self, key):
        '''
        Import settings key as a dict or list with values of importable paths
        '''
        value = getattr(self, key)
        if isinstance(value, dict):
            return {key: self.load_path(value) for key, value in value.items()}
        elif isinstance(value, list):
            return [self.load_path(value) for value in value]
        else:
            raise ValueError('load_all must be list or dict')

    def load_path(self, path):
        '''
        Load and return a given import path to a module or class
        '''
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

    def get_cache_string(self):
        '''
        Return a software version string that is useful for caching based on
        OmniConverter software version number, or a random number in the case
        of intentional cache busting scenarios
        '''
        if hasattr(self, 'CACHE_STRING'):
            return self.CACHE_STRING
        return 'no_cache_%i' % random.randint(0, 1000000000)
