import shutil
import asyncio
from omnic.conversion.exceptions import DownloaderUnavailable

class Downloader:
    @staticmethod
    def configure():
        pass

    def __init__(self):
        pass

    def check(self, foreign_resource):
        # Check if it can download the given foreign resource
        return False

    async def download(self, foreign_resource):
        pass

    async def copy_to_cache(self, resource, typed_resource):
        pass

class ExecDownloader:
    @classmethod
    def configure(cls):
        binary_path = shutil.which(cls.command[0])
        if not binary_path:
            raise DownloaderUnavailable()

    def get_arguments(self):
        return []

    def get_command(self, resource):
        return apply_command_list_template(
            self.command,
            resource.resource_url.url_string,
            resource.download_cache_path,
            self.get_arguments(resource),
        )

    async def download(self, resource):
        '''
        Download given resource
        '''
        # Compute command and working dir, ensure dirs are made, 
        cmd = self.get_command(resource)
        working_dir = os.path.dirname(resource.cache_path)
        resource.cache_makedirs()

        # Run the command itself
        await asyncio.create_subprocess_exec(cmd, cwd=working_dir)
        typed_resource = resource.guess_typed()
        await self.copy_to_cache(resource, typed_resource)

    async def copy_to_cache(self, resource, typed_resource):
        typed_resource.cache_makedirs()
        # Symlink to new location that includes typed extension
        typed_resource.symlink_from(resource)


class Resolver:
    @staticmethod
    def configure():
        pass

    def __init__(self):
        pass

    def check(self, resource_url):
        # Check if it can resolve the given resource URL
        return False

    async def get(self, resource_url):
        pass

    async def copy_to_cache(self, resource_url):
        pass

class ExecResolver:
    @classmethod
    def configure(cls):
        binary_path = shutil.which(cls.command[0])
        if not binary_path:
            raise DownloaderUnavailable()

    def get_arguments(self, resource_url):
        return []

    def get_command(self, resource_url):
        mr = MutableResource(resource_url)
        return apply_command_list_template(
            self.command,
            resource_url.url,
            mr.cache_path,
            self.get_arguments(resource_url),
        )

    async def download(self, resource):
        '''
        Download given resource
        '''
        # Compute command and working dir, ensure dirs are made, 
        cmd = self.get_command(resource)
        working_dir = os.path.dirname(resource.cache_path)
        resource.cache_makedirs()

        # Run the command itself
        await asyncio.create_subprocess_exec(cmd, cwd=working_dir)
        typed_resource = resource.guess_typed()
        await self.copy_to_cache(resource, typed_resource)

    async def copy_to_cache(self, resource, typed_resource):
        typed_resource.cache_makedirs()
        # Symlink to new location that includes typed extension
        typed_resource.symlink_from(resource)

class CurlResolver(ExecResolver):
    command = [
        'curl',
        '-o',
        '$OUT',
        '$IN',
    ]

class GitCloneResolver(ExecResolver):
    command = [
        'git',
        'clone',
        '$IN',
        '$OUT',
    ]

class GitCheckoutResolver(ExecResolver):
    command = [
        'git',
        'checkout',
        '$HASH',
    ]

    async def check_if_needed(self, url):
        pass


class GitFileResolver(ExecResolver):
    command = [
        'cp',
        '$IN',
        '$OUT',
    ]

class GitResolver(MultistepResolver):
    def get_steps(self, url):
        if 'hash' not in url or 'path' not in url:
            raise ValueError('URL must contain at least hash')
        return [
            GitCloneResolver,
            GitCheckoutResolver,
            # GitFileResolver if 'path' in url else GitDirectoryResolver,
            GitFileResolver,
        ]



# class TestExecDownloaderBaseClass:
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
