import os

from omnic.conversion import converter

class GitCloner(converter.ExecConverter):
    inputs = [
        'git',
    ]

    outputs = [
        'git-cloned',
    ]

class GitUpdater(converter.ExecConverter):
    inputs = [
        'git-cloned',
    ]

    outputs = [
        'git-updated',
    ]

class GitTreeResolver(converter.ExecConverter):
    inputs = [
        'git-updated',
    ]

    outputs = [
        'git-ls-tree',
    ]

    @classmethod
    def get_destination_type(cls, resource_url):
        scheme = resource_url.parsed.scheme
        if scheme not in ('git', 'git+https', 'git+http'):
            return
        if len(resource_url.args) == 1:
            return 'git-ls-tree'


class GitLogResolver(converter.ExecConverter):
    inputs = [
        'git-updated',
    ]

    outputs = [
        'git-log',
    ]

    @classmethod
    def get_destination_type(cls, resource_url):
        scheme = resource_url.parsed.scheme
        if scheme not in ('git', 'git+https', 'git+http'):
            return
        if len(resource_url.args) == 0:
            return 'git-log'

class GitFileResolver(converter.ExecConverter):
    inputs = [
        'git-updated',
    ]

    outputs = [
        'file',
    ]

    @classmethod
    def get_destination_type(cls, resource_url):
        scheme = resource_url.parsed.scheme
        if scheme not in ('git', 'git+https', 'git+http'):
            return
        if len(resource_url.args) == 2:
            return 'file'

# TODO: Have directory resolver that checks if args[1] == '/'

