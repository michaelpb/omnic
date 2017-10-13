### XXX These methods are deprecated, were generally replaced by Resolver Grid
### XXX (see #23)

import os

from omnic import singletons
from omnic.types.resource import ForeignResource, MutableResource


async def download_http(resource_url):
    out_resource = ForeignResource(resource_url)
    out_resource.cache_makedirs()
    cmd = [
        'curl',
        '-L',  # follow redirects
        '--silent',
        '--output', out_resource.cache_path,
        resource_url.url,
    ]
    # print('-----------------------------')
    # print(' '.join(cmd))
    # print('-----------------------------')
    await singletons.subprocess.run(cmd)

GIT_ARCHIVE_FORMATS = '''
[tar "raw"]
\tcommand = tar xfO -
[tar "directory"]
\tcommand = tar xf
'''


async def download_git(resource_url):
    # First, ascertain status of Git resource
    git_url = resource_url.url
    out_resource = ForeignResource(resource_url)
    git_resource = MutableResource(git_url)

    if not git_resource.cache_exists():
        # Check out bare repo into cache path
        cmd = ['git', 'clone', '--bare', git_url, git_resource.cache_path]
        await singletons.subprocess.run(cmd)

        # Append to git config customized git archive format
        config_path = os.path.join(git_resource.cache_path, 'config')
        with open(config_path, 'a') as fd:
            # Note: Not too concerned with staying idempotent, unlikely it
            # could happen twice, and extra entries cause no issue
            fd.write(GIT_ARCHIVE_FORMATS)

    subpath = None
    output_file = None
    if len(resource_url.args) == 2:
        hash_or_tag, subpath = resource_url.args
    elif len(resource_url.args) == 1:
        # ls-tree instance
        hash_or_tag = resource_url.args[0]
        output_file = out_resource.cache_path
    else:
        raise ValueError('Requires 1 or 2 positional args for URL')

    if subpath is None:
        # Get the tree structure of the current git repo
        cmd = [
            'git',
            'ls-tree',
            '-r',
            '--long',
            '--full-tree',
            hash_or_tag,
        ]

    elif subpath == '/':
        # Do entire directory, not a particular path
        cmd = [
            'git',
            'archive',
            '--prefix=%s' % out_resource.cache_path,
            '--format=directory',
            hash_or_tag,
        ]

    else:
        # Get a single file
        cmd = [
            'git',
            'archive',
            '--output=%s' % out_resource.cache_path,
            '--format=raw',
            hash_or_tag,
            subpath,
        ]

    out_resource.cache_makedirs()

    if output_file:
        with open(output_file, 'w+') as fd:
            await singletons.subprocess.run(
                cmd,
                cwd=git_resource.cache_path,
                stdout=fd,
            )
    else:
        await singletons.subprocess.run(cmd, cwd=git_resource.cache_path)

    out_resource = ForeignResource(resource_url)


async def download(resource_url):
    '''
    Download given resource_url
    '''
    scheme = resource_url.parsed.scheme
    if scheme in ('http', 'https'):
        await download_http(resource_url)
    elif scheme in ('git', 'git+https', 'git+http'):
        await download_git(resource_url)
    else:
        raise ValueError('Unknown URL scheme: "%s"' % scheme)
