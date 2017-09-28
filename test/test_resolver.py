import pytest

from unittest.mock import MagicMock, patch, call, mock_open

from omnic.config.utils import use_settings
from omnic.conversion import resolver
from omnic.types.resourceurl import ResourceURL

#class TestExecDownloaderBaseClass:
#    class Subclass(downloader.ExecDownloader):
#        command = ['test', '$IN', '$OUT']
#
#    def _get_mocked_resource(self, ts):
#        res = TypedResource(URL, TypeString(ts))
#        res.cache_makedirs = MagicMock()
#        res.cache_path = 'test/path.%s' % ts
#        return res
#
#    @pytest.skip
#    def test_configure_failure(self):
#        shutil = {'which.return_value': None}
#        with patch('omnic.conversion.downloader.shutil', **shutil):
#            with pytest.raises(downloader.DownloaderUnavailable):
#                self.Subclass.configure()
#
#    @pytest.skip
#    def test_configure_succeed(self):
#        shutil = {'which.return_value': '/bin/test'}
#        with patch('omnic.conversion.downloader.shutil', **shutil):
#            self.Subclass.configure()

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

        patcher = patch('omnic.conversion.resolver.subprocess')
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
        curl_cmd = ['curl', '--silent', '--output']
        paths = ['/t/res/whatever.png', 'http://site.com/whatever.png']
        self.subprocess.run.assert_called_once_with(curl_cmd + paths)

    @pytest.mark.asyncio
    async def test_download_git(self):
        # info = {'run.return_value': None}
        tree_object = '343fa8b9c4ec521fd6d382c8f1f9ec0ac500a240'
        path = 'README.md'
        git_url = 'git://githoobie.com/lol.git<%s><%s>' % (tree_object, path)
        resource_url = ResourceURL(git_url)
        with use_settings(**normalized_settings):
            with patch('os.path.exists') as exists:
                exists.return_value = False
                await resolver.download(resource_url)

        # ensure the sequence of git commands were called
        assert self.subprocess.run.mock_calls == [
            call(['git', 'clone', '--bare',
                'git://githoobie.com/lol.git', '/t/mut/lol.git']),
            call(['git', 'archive', '--output=/t/res/README.md',
                '--format=raw', tree_object, 'README.md'],
                cwd='/t/mut/lol.git'),
        ]

        # ensure called once
        self.open.assert_called_once_with('/t/mut/lol.git/config', 'a')
        assert len(self.open().write.mock_calls) == 1
        contents = list(self.open().write.mock_calls[0])[1][0] # first arg
        assert 'command = tar xfO -' in contents
        assert 'command = tar xf' in contents

