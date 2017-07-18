import asyncio
import json

import aiohttp

from omnic import singletons
from omnic.builtin.types.core import DIRECTORY, MANIFEST_JSON
from omnic.conversion import converter


class ManifestDownloader(converter.Converter):
    # TODO: Possibly switch to using binary system packages like curl?
    inputs = [
        str(MANIFEST_JSON),
    ]
    outputs = [
        str(DIRECTORY),
    ]

    async def convert(self, in_resource, out_resource):
        # TODO: Create Manifest JSON helper util, support TXT format too
        with in_resource.cache_open('r') as fd:
            parsed = json.load(fd)
        files = parsed['files'].items()

        # Download all files with the same client session
        self._new_aiohttp_client()
        self.file_descriptors = {
            relpath: out_resource.cache_open_as_dir(relpath, 'wb')
            for relpath, file_url in files
        }
        await asyncio.wait([
            self._download_async(file_url, self.file_descriptors[relpath])
            for relpath, file_url in files
        ])
        self._close()

    # TODO: move all this to a helper class
    def _new_aiohttp_client(self):
        loop = singletons.eventloop.loop
        self.aiohttp = aiohttp.ClientSession(loop=loop)

    def _close(self):
        '''
        Closes aiohttp session and all open file descriptors
        '''
        if hasattr(self, 'aiohttp'):
            if not self.aiohttp.closed:
                self.aiohttp.close()
        if hasattr(self, 'file_descriptors'):
            for fd in self.file_descriptors.values():
                if not fd.closed:
                    fd.close()

    async def _download_async(self, url, f_handle):
        DOWNLOAD_TIMEOUT = 10
        DOWNLOAD_CHUNK_SIZE = 1024
        with aiohttp.Timeout(DOWNLOAD_TIMEOUT):
            async with self.aiohttp.get(url) as response:
                while True:
                    chunk = await response.content.read(DOWNLOAD_CHUNK_SIZE)
                    if not chunk:
                        break
                    f_handle.write(chunk)
                return await response.release()
