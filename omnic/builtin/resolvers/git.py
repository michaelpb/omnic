import os
import subprocess

from omnic.conversion import converter


GIT_ARCHIVE_FORMATS = '''
[tar "raw"]
\tcommand = tar xfO -
[tar "directory"]
\tcommand = tar xfP -
'''


class GitExecConverter(converter.ExecConverter):
    @classmethod
    def get_destination_type(cls, resource_url):
        if not hasattr(cls, '_is_output'):
            return

        scheme = resource_url.parsed.scheme
        if scheme not in ('git', 'git+https', 'git+http'):
            return

        if cls._is_output(resource_url.args):
            return cls.outputs[0]

    def get_cwd(self, mutable_resource, out_resource):
        return mutable_resource.cache_path


class GitCloner(converter.ExecConverter):
    '''
    Perform clone command if needed on a git repository
    '''
    inputs = [
        'git',
    ]

    outputs = [
        'git-cloned',
    ]

    def get_command(self, mutable_resource, out_resource):
        # Check out bare repo into cache path
        git_url = mutable_resource.url.url
        return [
            'git',
            'clone',
            '--bare',
            git_url,
            mutable_resource.cache_path,
        ]

    async def convert(self, mutable_resource, out_resource):
        if mutable_resource.cache_exists():
            return  # Already cloned, exit right away

        await super().convert(mutable_resource, out_resource)

        # Append to git config customized git archive format
        config_path = os.path.join(mutable_resource.cache_path, 'config')
        with open(config_path, 'a') as fd:
            # Note: Not too concerned with staying idempotent, unlikely it
            # could happen twice, and extra entries cause no issue
            fd.write(GIT_ARCHIVE_FORMATS)


class GitUpdater(GitExecConverter):
    inputs = [
        'git-cloned',
    ]

    outputs = [
        'git-updated',
    ]

    hash_cache = {}

    @classmethod
    def reset_hash_cache(cls):
        '''
        Hashes are cached which radically cuts down excess system calls
        '''
        # TODO Right now memory leak. Turn into LRU with decently large limit.
        cls.hash_cache = {}

    def get_command(self, mutable_resource, out_resource):
        return [
            'git',
            'fetch',
        ]

    async def convert(self, mutable_resource, out_resource):
        hash_or_tag = out_resource.url.args[0]

        # First check if we have need to update -- cache successes
        if GitUpdater.hash_cache.get(hash_or_tag) is True:
            return

        # Run rev-parse to check if it exists in history
        kwds = self.get_kwds(mutable_resource, out_resource)
        kwds['stdout'] = subprocess.PIPE
        cmd = ['git', 'rev-parse', '--quiet', '--verify', hash_or_tag]
        result = await super()._run_command(cmd, kwds, mutable_resource, out_resource)
        result_str = result.stdout.decode('ascii').strip()

        if result_str != hash_or_tag:
            GitUpdater.hash_cache[hash_or_tag] = False
            # Only try updating if not found
            await super().convert(mutable_resource, out_resource)
            GitUpdater.hash_cache[hash_or_tag] = True

        # TODO: Once error checking system is in place, add check here for
        # everything being squared away


class GitTreeResolver(GitExecConverter):
    inputs = [
        'git-updated',
    ]

    outputs = [
        'git-ls-tree',
    ]

    _is_output = staticmethod(lambda args: len(args) == 1)

    def get_capture(self, mutable_resource, out_resource):
        # The result of this is in stdout
        return ['stdout']

    def get_command(self, mutable_resource, out_resource):
        hash_or_tag = out_resource.url.args[0]
        return [
            'git',
            'ls-tree',
            '-r',
            '--long',
            '--full-tree',
            hash_or_tag,
        ]


class GitLogResolver(GitExecConverter):
    inputs = [
        'git-updated',
    ]

    outputs = [
        'git-log',
    ]

    _is_output = staticmethod(lambda args: len(args) == 0)

    def get_command(self, mutable_resource, out_resource):
        # NOTE: Not implemented yet, for now, just is NOOP
        return [
            'true',
        ]


class GitFileResolver(GitExecConverter):
    inputs = [
        'git-updated',
    ]

    outputs = [
        'file',
    ]

    _is_output = staticmethod(lambda args: len(args) == 2 and args[1] != '/')

    def get_command(self, mutable_resource, out_resource):
        hash_or_tag = out_resource.url.args[0]
        subpath = out_resource.url.args[1]
        return [
            'git',
            'archive',
            '--output=%s' % out_resource.cache_path,
            '--format=raw',
            hash_or_tag,
            subpath,
        ]


class GitDirectoryResolver(GitExecConverter):
    inputs = [
        'git-updated',
    ]

    outputs = [
        'directory',
    ]

    _is_output = staticmethod(lambda args: len(args) == 2 and args[1] == '/')

    # For now, just is NOOP  # Later comment: Or is it?
    def get_command(self, mutable_resource, out_resource):
        hash_or_tag = out_resource.url.args[0]
        subpath = out_resource.url.args[1]
        prefix = out_resource.cache_path + subpath
        a = [
            'git',
            'archive',
            '--prefix=%s' % prefix,
            '--format=directory',
            hash_or_tag,
            #subpath,
        ]
        print(a)
        return a
