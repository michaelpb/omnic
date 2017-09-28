import asyncio
import subprocess
import os

from omnic.types.resource import MutableResource, ForeignResource

# TODO Presently hardcoded, refactor this into a "resolver" conversion system

# TODO Replace with async subprocess stuff (if necessary..?)


async def download_http(resource_url):
    out_resource = ForeignResource(resource_url)
    out_resource.cache_makedirs()
    cmd = [
        'curl',
        '--silent',
        '--output', out_resource.cache_path,
        resource_url.url,
    ]
    subprocess.run(cmd)

# git archive --output=../index.html --format=raw befd15d index.html
# [tar "raw"]
#    command = tar xfO -

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
    hash_or_tag, subpath = resource_url.args

    # NOTE: Should do validation on GIT resource urls, notably disallowing
    # HEAD, and branch names (should only be tags or commit hashes)

    if not os.path.exists(git_resource.cache_path):
        cmd = ['git', 'clone', '--bare', git_url, git_resource.cache_path]
        subprocess.run(cmd)
        config_path = os.path.join(git_resource.cache_path, 'config')
        with open(config_path, 'a') as fd:
            fd.write(GIT_ARCHIVE_FORMATS)

        # TODO Append this to end of config (no need to check for idem, multiple is OK)
    # NOW, git bare repo exists, let's extract the given file
    cmd = [
        'git',
        'archive',
        '--output=%s' % out_resource.cache_path,
        '--format=raw',
        hash_or_tag,
        subpath,
    ]
    subprocess.run(cmd, cwd=git_resource.cache_path)

    # TODO: Have another mode specified by a kwarg that simply gets recursive
    # dir listing, as plaintext file, e.g.  /file1.html\n/path/to/file2.html
    # etc

    # TODO: Have failure handling here, if this command fails and can't find
    # given hash, it should attempt to update, if that fails, then we know that
    # the specified "tree object" does not exist, 404
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


