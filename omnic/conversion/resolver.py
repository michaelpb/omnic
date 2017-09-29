import os
import subprocess

from omnic.types.resource import ForeignResource, MutableResource

# TODO:
# * Presently hardcoded, refactor this into a "resolver" conversion system
#    * Can use ConverterGraph except with Resolvers instead, which take a
#    resource_url, and ensure that a ForeignResource is cached from that
# * Replace with async subprocess stuff
# * Possibly create async subprocess base class helpers used by both conversion
# system and resolver system


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
    subprocess.run(cmd)

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

    if not git_resource.cache_exists():
        # Check out bare repo into cache path
        cmd = ['git', 'clone', '--bare', git_url, git_resource.cache_path]
        subprocess.run(cmd)

        # Append to git config customized git archive format
        config_path = os.path.join(git_resource.cache_path, 'config')
        with open(config_path, 'a') as fd:
            # Note: Not too concerned with staying idempotent, unlikely it
            # could happen twice, and extra entries cause no issue
            fd.write(GIT_ARCHIVE_FORMATS)

    # NOW, git bare repo exists, let's extract the given file
    cmd = [
        'git',
        'archive',
        '--output=%s' % out_resource.cache_path,
        '--format=raw',
        hash_or_tag,
        subpath,
    ]
    out_resource.cache_makedirs()
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
