from unittest.mock import call, mock_open, patch, MagicMock

import pytest

from omnic.conversion import resolver
from omnic.conversion import resolvergraph
from omnic.types.resourceurl import ResourceURL
from omnic import singletons

class Settings:
    PATH_PREFIX = '/t/'
    PATH_GROUPING = None
    INTERFIX = None
    RESOURCE_CACHE_INTERFIX = 'res'
    MUTABLE_RESOURCE_CACHE_INTERFIX = 'mut'
    RESOLVERS = [
        'omnic.builtin.resolvers.http.CurlDownloader',
        'omnic.builtin.resolvers.git.GitCloner',
        'omnic.builtin.resolvers.git.GitUpdater',
        'omnic.builtin.resolvers.git.GitTreeResolver',
        'omnic.builtin.resolvers.git.GitLogResolver',
        'omnic.builtin.resolvers.git.GitFileResolver',
        'omnic.builtin.resolvers.git.GitDirectoryResolver',
    ]

tree_object = '343fa8b9c4ec521fd6d382c8f1f9ec0ac500a240'
class BaseResolverTest:
    def setup_method(self, method):
        self.patchers = []

        patcher = patch('os.mkdir')
        self.mkdir = patcher.start()
        self.patchers.append(patcher)

        patcher = patch('omnic.worker.subprocessmanager.subprocess')
        self.subprocess = patcher.start()
        class FakeResult:
            stdout = tree_object.encode('utf8')
        self.subprocess.run.return_value = FakeResult
        self.patchers.append(patcher)

        self.open = mock_open()
        patcher = patch('builtins.open', self.open)
        patcher.start()
        self.patchers.append(patcher)
        singletons.settings.use_settings(Settings)
        self.rgraph = resolvergraph.ResolverGraph()  # Create resolver graph

        from omnic.builtin.resolvers.git import GitUpdater
        GitUpdater.reset_hash_cache()

    def teardown_method(self, method):
        singletons.settings.use_previous_settings()
        for patcher in self.patchers:
            patcher.stop()

class TestDownloaderFunction(BaseResolverTest):
    @pytest.mark.asyncio
    async def test_download_http(self):
        # info = {'run.return_value': None}
        resource_url = ResourceURL('http://site.com/whatever.png')
        await resolver.download(resource_url)

        # ensure made the required directories
        self.mkdir.assert_has_calls((call('/t', 511), call('/t/res', 511)))

        # ensure the curl command was called
        curl_cmd = ['curl', '-L', '--silent', '--output']
        paths = ['/t/res/whatever.png', 'http://site.com/whatever.png']
        self.subprocess.run.assert_called_once_with(curl_cmd + paths)

    async def _do_download(self, git_url):
        resource_url = ResourceURL(git_url)
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

class TestResolverGraphHelperMethods(BaseResolverTest):
    def test_find_destination_type_http(self):
        resource_url = ResourceURL('http://site.com/whatever.png')
        destination_type = self.rgraph.find_destination_type(resource_url)
        assert destination_type == 'file'

        resource_url = ResourceURL('https://site.com/whatever.png')
        destination_type = self.rgraph.find_destination_type(resource_url)
        assert destination_type == 'file'

    def test_find_destination_type_invalid(self):
        resource_url = ResourceURL('idontexist://site.com/whatever.png')
        destination_type = self.rgraph.find_destination_type(resource_url)
        assert destination_type == None

    def test_find_path_from_url_http(self):
        resource_url = ResourceURL('http://site.com/whatever.png')
        path = self.rgraph.find_path_from_url(resource_url)
        assert len(path) == 1
        assert path[0][0].__name__ == 'CurlDownloader'

    def test_find_destination_type_git(self):
        git_url = 'git://githoobie.com/lol.git<%s>' % tree_object
        resource_url = ResourceURL(git_url)
        destination_type = self.rgraph.find_destination_type(resource_url)
        assert destination_type == 'git-ls-tree'

        git_url = 'git://githoobie.com/lol.git<%s><some/path>' % tree_object
        resource_url = ResourceURL(git_url)
        destination_type = self.rgraph.find_destination_type(resource_url)
        assert destination_type == 'file'

        git_url = 'git://githoobie.com/lol.git'
        resource_url = ResourceURL(git_url)
        destination_type = self.rgraph.find_destination_type(resource_url)
        assert destination_type == 'git-log'

        git_url = 'git://githoobie.com/lol.git<%s></>' % tree_object
        resource_url = ResourceURL(git_url)
        destination_type = self.rgraph.find_destination_type(resource_url)
        assert destination_type == 'directory'

    def test_find_path_git(self):
        git_url = 'git://githoobie.com/lol.git<%s>' % tree_object
        resource_url = ResourceURL(git_url)
        path = self.rgraph.find_path_from_url(resource_url)
        assert len(path) == 3  # clone, update, ls
        assert path[0][0].__name__ == 'GitCloner'
        assert path[1][0].__name__ == 'GitUpdater'
        assert path[2][0].__name__ == 'GitTreeResolver'

        git_url = 'git://githoobie.com/lol.git<%s><some/path>' % tree_object
        resource_url = ResourceURL(git_url)
        path = self.rgraph.find_path_from_url(resource_url)
        assert len(path) == 3  # clone, update, file
        assert path[0][0].__name__ == 'GitCloner'
        assert path[1][0].__name__ == 'GitUpdater'
        assert path[2][0].__name__ == 'GitFileResolver'

        git_url = 'git://githoobie.com/lol.git'
        resource_url = ResourceURL(git_url)
        path = self.rgraph.find_path_from_url(resource_url)
        assert len(path) == 3  # clone, update-log, git-log
        assert path[0][0].__name__ == 'GitCloner'
        assert path[1][0].__name__ == 'GitUpdater'
        assert path[2][0].__name__ == 'GitLogResolver'

class TestResolverGraphDownload(BaseResolverTest):
    @pytest.mark.asyncio
    async def test_download_http(self):
        # info = {'run.return_value': None}
        resource_url = ResourceURL('http://site.com/whatever.png')
        await self.rgraph.download(resource_url)

        # ensure made the required directories
        self.mkdir.assert_has_calls((call('/t', 511), call('/t/res', 511)))

        # ensure the curl command was called
        curl_cmd = ['curl', '-L', '--silent', '--output']
        paths = ['/t/res/whatever.png', 'http://site.com/whatever.png']
        kwds = {'cwd': '/t/mut'}
        self.subprocess.run.assert_called_once_with(curl_cmd + paths, **kwds)

    async def _do_download(self, git_url):
        resource_url = ResourceURL(git_url)
        with patch('os.path.exists') as exists:
            exists.return_value = False
            await self.rgraph.download(resource_url)

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
        path = 'README.md'
        git_url = 'git://githoobie.com/lol.git<%s><%s>' % (tree_object, path)
        await self._do_download(git_url)
        self._check_config()

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                  'git://githoobie.com/lol.git', '/t/mut/lol.git'],
                  cwd='/t/mut'),
            call(['git', 'rev-parse', '--quiet', '--verify', tree_object],
                 cwd='/t/mut/lol.git', stdout=-1),
            call(['git', 'archive', '--output=/t/res/README.md',
                  '--format=raw', tree_object, 'README.md'],
                 cwd='/t/mut/lol.git'),
        ]

    @pytest.mark.asyncio
    async def test_download_directory_git(self):
        path = '/'
        git_url = 'git://githoobie.com/lol.git<%s><%s>' % (tree_object, path)
        await self._do_download(git_url)
        self._check_config()

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                  'git://githoobie.com/lol.git', '/t/mut/lol.git'],
                  cwd='/t/mut'),
            call(['git', 'rev-parse', '--quiet', '--verify', tree_object],
                 cwd='/t/mut/lol.git', stdout=-1),
            call(['git', 'archive', '--prefix=/t/res/lol.git',
                  '--format=directory', tree_object],
                 cwd='/t/mut/lol.git'),
        ]

    @pytest.mark.asyncio
    async def test_download_lstree_git(self):
        git_url = 'git://githoobie.com/lol.git<%s>' % tree_object
        await self._do_download(git_url)

        # ensure git config was appended to, and that the output file was
        # opened
        self.open.assert_any_call('/t/mut/lol.git/config', 'a')
        self.open.assert_any_call('/t/res/lol.git', 'w+')

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                  'git://githoobie.com/lol.git', '/t/mut/lol.git'],
                  cwd='/t/mut'),
            call(['git', 'rev-parse', '--quiet', '--verify', tree_object],
                 cwd='/t/mut/lol.git', stdout=-1),
            call(['git', 'ls-tree', '-r', '--long', '--full-tree',
                  tree_object],
                 cwd='/t/mut/lol.git', stdout=self.open()),
        ]

    @pytest.mark.asyncio
    async def test_update_when_hash_not_present(self):
        class FakeResult:
            stdout = b''
        self.subprocess.run.return_value = FakeResult
        path = 'README.md'
        git_url = 'git://githoobie.com/lol.git<%s><%s>' % (tree_object, path)
        await self._do_download(git_url)
        self._check_config()

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                  'git://githoobie.com/lol.git', '/t/mut/lol.git'],
                  cwd='/t/mut'),
            call(['git', 'rev-parse', '--quiet', '--verify', tree_object],
                 cwd='/t/mut/lol.git', stdout=-1),
            call(['git', 'fetch'], cwd='/t/mut/lol.git'),
            call(['git', 'archive', '--output=/t/res/README.md',
                  '--format=raw', tree_object, 'README.md'],
                 cwd='/t/mut/lol.git'),
        ]

