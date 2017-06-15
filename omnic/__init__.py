__author__ = 'michaelb'
__email__ = 'michaelpb@gmail.com'
__version__ = '0.1.0'

# Set up singleton system
from omnic.utils.singleton import SingletonManager
singletons = SingletonManager()

# Ensure settings gets registered as a singleton
from omnic import config
singletons.register('settings', config.Settings)
