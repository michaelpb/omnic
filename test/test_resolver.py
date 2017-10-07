from unittest.mock import call, mock_open, patch

import pytest

from omnic.config.utils import use_settings
from omnic.conversion import resolver
from omnic.types.resourceurl import ResourceURL

normalized_settings = dict(
    path_prefix='/t/',
    path_grouping=None,
    interfix=None,
    resource_cache_interfix='res',
    mutable_resource_cache_interfix='mut',
)


class TestDownloaderFunction:
    def setup_method(self, method):
        self.patchers = []

        patcher = patch('os.mkdir')
        self.mkdir = patcher.start()
        self.patchers.append(patcher)

        patcher = patch('omnic.worker.subprocessmanager.subprocess')
        self.subprocess = patcher.start()
        self.patchers.append(patcher)

        self.open = mock_open()
        patcher = patch('omnic.conversion.resolver.open', self.open)
        patcher.start()
        self.patchers.append(patcher)

    def teardown_method(self, method):
        for patcher in self.patchers:
            patcher.stop()

    @pytest.mark.asyncio
    async def test_download_http(self):
        # info = {'run.return_value': None}
        resource_url = ResourceURL('http://site.com/whatever.png')
        with use_settings(**normalized_settings):
            await resolver.download(resource_url)

        # ensure made the required directories
        self.mkdir.assert_has_calls((call('/t', 511), call('/t/res', 511)))

        # ensure the curl command was called
        curl_cmd = ['curl', '-L', '--silent', '--output']
        paths = ['/t/res/whatever.png', 'http://site.com/whatever.png']
        self.subprocess.run.assert_called_once_with(curl_cmd + paths)

    async def _do_download(self, git_url):
        resource_url = ResourceURL(git_url)
        with use_settings(**normalized_settings):
            with patch('os.path.exists') as exists:
                exists.return_value = False
                await resolver.download(resource_url)

    def _check_config(self):
        # ensure git config was appended to
        self.open.assert_called_once_with('/t/mut/lol.git/config', 'a')
        assert len(self.open().write.mock_calls) == 1
        contents = list(self.open().write.mock_calls[0])[1][0]  # first arg
        assert '[tar "raw"]' in contents
        assert 'command = tar xfO -' in contents
        assert '[tar "directory"]' in contents
        assert 'command = tar xf' in contents

    @pytest.mark.asyncio
    async def test_download_path_git(self):
        tree_object = '343fa8b9c4ec521fd6d382c8f1f9ec0ac500a240'
        path = 'README.md'
        git_url = 'git://githoobie.com/lol.git<%s><%s>' % (tree_object, path)
        await self._do_download(git_url)
        self._check_config()

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                  'git://githoobie.com/lol.git', '/t/mut/lol.git']),
            call(['git', 'archive', '--output=/t/res/README.md',
                  '--format=raw', tree_object, 'README.md'],
                 cwd='/t/mut/lol.git'),
        ]

    @pytest.mark.asyncio
    async def test_download_directory_git(self):
        tree_object = '343fa8b9c4ec521fd6d382c8f1f9ec0ac500a240'
        path = '/'
        git_url = 'git://githoobie.com/lol.git<%s><%s>' % (tree_object, path)
        await self._do_download(git_url)
        self._check_config()

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                  'git://githoobie.com/lol.git', '/t/mut/lol.git']),
            call(['git', 'archive', '--prefix=/t/res/lol.git',
                  '--format=directory', tree_object],
                 cwd='/t/mut/lol.git'),
        ]

    @pytest.mark.asyncio
    async def test_download_lstree_git(self):
        tree_object = '343fa8b9c4ec521fd6d382c8f1f9ec0ac500a240'
        git_url = 'git://githoobie.com/lol.git<%s>' % tree_object
        await self._do_download(git_url)

        # ensure git config was appended to, and that the output file was
        # opened
        self.open.assert_any_call('/t/mut/lol.git/config', 'a')
        self.open.assert_any_call('/t/res/lol.git', 'w+')

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                  'git://githoobie.com/lol.git', '/t/mut/lol.git']),
            call(['git', 'ls-tree', '-r', '--long', '--full-tree',
                  tree_object],
                 cwd='/t/mut/lol.git', stdout=self.open()),
        ]
