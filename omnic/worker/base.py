import logging

import aiohttp

from omnic import singletons
from omnic.worker import tasks
from omnic.worker.enums import Task

log = logging.getLogger()

DOWNLOAD_TIMEOUT = 20
DOWNLOAD_CHUNK_SIZE = 8124


class BaseWorker:
    '''
    Worker base class
    '''

    def __init__(self):
        self.stats_dequeued = 0
        self.stats_began = 0
        self.stats_success = 0
        self.stats_error = 0

    def __del__(self):
        self._close()

    def _close(self):
        if hasattr(self, 'aiohttp'):
            if not self.aiohttp.closed:
                self.aiohttp.close()

    async def run(self):
        while self.running:
            # Queue up consuming next item
            task_type, args = await self.get_next()
            self.stats_dequeued += 1
            method = self._get_method(task_type)

            # Determine the type of task, and possibly skip if we have
            # it "locked" that we are already doing it
            if task_type == Task.FUNC:
                pass

            elif task_type == Task.DOWNLOAD:
                if not await self.check_download(*args):
                    log.debug('Already downloading %s' % repr(args))
                    continue

            elif task_type == Task.CONVERT:
                if not await self.check_convert(*args):
                    log.debug('Already converting %s' % repr(args))
                    continue

            elif task_type == Task.MULTICONVERT:
                if not await self.check_multiconvert(*args):
                    log.debug('Already multiconverting %s' % repr(args))
                    continue

            # Queue it up and run it
            self.stats_began += 1
            try:
                await method(*args)
                self.stats_success += 1
            except Exception as e:
                self.stats_error += 1
                log.exception('Error in task: "%s"' % repr(e))

    def _get_method(self, task_type):
        return {
            Task.FUNC: self.run_func,
            Task.DOWNLOAD: self.run_download,
            Task.CONVERT: self.run_convert,
            Task.MULTICONVERT: self.run_multiconvert,
        }.get(task_type)

    async def run_func(self, func, *func_args):
        '''
        Runs arbitrary synchronous code
        '''
        func(*func_args)

    async def run_download(self, foreign_resource):
        '''
        Downloads a foreign resource asynchronously
        '''
        url = foreign_resource.url_string
        with foreign_resource.cache_open('wb') as f_handle:
            await self._download_async(url, f_handle)

    async def _download_async(self, url, f_handle):
        loop = singletons.eventloop.loop
        self.aiohttp = aiohttp.ClientSession(loop=loop)
        with aiohttp.Timeout(DOWNLOAD_TIMEOUT):
            async with self.aiohttp.get(url) as response:
                while True:
                    chunk = await response.content.read(DOWNLOAD_CHUNK_SIZE)
                    if not chunk:
                        break
                    f_handle.write(chunk)
                self._close()
                return await response.release()

    async def run_convert(self, converter, in_resource, out_resource):
        '''
        Converts using the given converter, asynchronously if available,
        otherwise falls back on sync
        '''
        if hasattr(converter, 'convert'):
            await converter.convert(in_resource, out_resource)
        elif hasattr(converter, 'convert_sync'):
            converter.convert_sync(in_resource, out_resource)
        else:
            raise ValueError('Invalid converter: %s' % repr(converter))

    async def run_multiconvert(self, url_string, to_type):
        '''
        Enqueues in succession all conversions steps necessary to take the
        given URL and convert it to to_type, storing the result in the cache
        '''
        async def enq_convert(*args):
            await self.enqueue(Task.CONVERT, args)
        await tasks.multiconvert(url_string, to_type, enq_convert)
