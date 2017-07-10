from contextlib import contextmanager
from unittest import mock

DEFAULT_TARGETS = (
    'omnic.converter',
)

@contextmanager
def patch_system(*bins, targets=[]):
    '''
    Create a fake system environment with 
    '''
    bins += ('which', 'mv', 'cp', 'ln')  # Add in a few built-ins
    system = dict()
    for bin_name in bins:
        system[bin_name] = []
    # TODO finish this...
    yield system




