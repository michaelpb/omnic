import importlib
import logging
import os
import sys
from logging import config
from types import ModuleType

from omnic.config import default_settings
from omnic.config.exceptions import ConfigurationError

# Useful during debugging to force all logging enabled, even when tests silence
# logging
_FORCE_PREVENT_LOGGING_DISABLE = False


class SettingsManager:
    '''
    The `settings' singleton, used to house project settings, including logic
    to default to default settings for unset settings.
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
            if not _FORCE_PREVENT_LOGGING_DISABLE:
                logging.disable(logging.CRITICAL)
        else:
            raise ConfigurationError('Invalid LOGGING: must be string, dict')

    def load(self, key):
        '''
        Import settings key as import path
        '''
        return self.load_path(getattr(self, key))

    def load_all(self, key, default=None):
        '''
        Import settings key as a dict or list with values of importable paths
        If a default constructor is specified, and a path is not importable, it
        falls back to running the given constructor.
        '''
        value = getattr(self, key)
        if default is not None:
            def loader(path): return self.load_path_with_default(path, default)
        else:
            loader = self.load_path
        if isinstance(value, dict):
            return {key: loader(value) for key, value in value.items()}
        elif isinstance(value, list):
            return [loader(value) for value in value]
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
            except AttributeError:
                msg = 'Cannot import "%s". ' \
                    '(Hint: CamelCase is only for classes)' % last_item
                raise ConfigurationError(msg)
        return imported_obj

    def load_path_with_default(self, path, default_constructor):
        '''
        Same as `load_path(path)', except uses default_constructor on import
        errors, or if loaded a auto-generated namespace package (e.g. bare
        directory).
        '''
        try:
            imported_obj = self.load_path(path)
        except (ImportError, ConfigurationError):
            imported_obj = default_constructor(path)
        else:
            # Ugly but seemingly expedient way to check a module was an
            # namespace type module
            if (isinstance(imported_obj, ModuleType) and
                    imported_obj.__spec__.origin == 'namespace'):
                imported_obj = default_constructor(path)
        return imported_obj

    def use_settings(self, settings_module):
        '''
        Useful for tests for overriding current settings manually
        '''
        self._previous_settings = self.settings_module
        self.settings_module = settings_module
        self.reconfigure()

    def use_settings_dict(self, settings_dict):
        '''
        Slightly cleaner interface to override settings that autogenerates a
        settings module based on a given dict.
        '''
        class SettingsDictModule:
            __slots__ = tuple(key.upper() for key in settings_dict.keys())
        settings_obj = SettingsDictModule()
        for key, value in settings_dict.items():
            setattr(settings_obj, key.upper(), value)
        self.use_settings(settings_obj)

    def use_previous_settings(self):
        '''
        Useful for tests for restoring previous state of singleton
        '''
        self.settings_module = self._previous_settings
        self.reconfigure()

    @staticmethod
    def import_path_to_absolute_path(import_path, file_marker):
        '''
        Given a Python import path, convert to a likely absolute filesystem
        path, by searching for the given filename marker (such as
        'package.json' or '__init__.py') through the Python system path. Do not
        return given filename.
        '''
        path_fragment = import_path.replace('.', os.path.sep)
        path_suffix = os.path.join(path_fragment, file_marker)
        for path_base in sys.path:
            path = os.path.join(path_base, path_suffix)
            if os.path.exists(path):
                return os.path.join(path_base, path_fragment)
        msg = 'Cannot find import path: %s, %s'
        raise ConfigurationError(msg % (import_path, file_marker))
