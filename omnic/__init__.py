__author__ = 'michaelb'
__email__ = 'michaelpb@gmail.com'
__version__ = '0.1.6'


# flake8: noqa
# Import all top-level packages
from . import (
    builtin, config, cli, conversion, responses, types, utils, web, worker,
)

# Set up singleton system
from omnic.utils.singleton import SingletonManager
singletons = SingletonManager()

# Ensure settings gets registered as a singleton
from omnic.config.settingsmanager import SettingsManager
singletons.register('settings', SettingsManager)
