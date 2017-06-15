import logging
import asyncio
from enum import Enum

import async_timeout
import aiohttp

from omnic import singletons

log = logging.getLogger()


class Task(Enum):
    FUNC = 1          # Synchronous function
    DOWNLOAD = 2      # Downloading a file
    CONVERT = 3       # Running a converter


DOWNLOAD_TIMEOUT = 20
DOWNLOAD_CHUNK_SIZE = 1024


class Worker:
    '''
    Worker base class, for use with coroutines
    '''

    def __init__(self):
        self.aiohttp = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.stats_dequeued = 0
        self.stats_began = 0
        self.stats_success = 0
        self.stats_error = 0

    def __del__(self):
        if hasattr(self, 'aiohttp'):
            if not self.aiohttp.closed:
                self.aiohttp.close()

    async def run(self):
        while self.running:
            # Queue up consuming next item
            task_type, args = await self.get_next()
            self.stats_dequeued += 1
            method = None

            # Determine the type of task, and possibly skip if we have
            # it "locked" that we are already doing it
            if task_type == Task.FUNC:
                method = self.run_func

            elif task_type == Task.DOWNLOAD:
                if not await self.check_download(*args):
                    log.debug('Already downloading %s' % repr(args))
                    continue
                method = self.run_download

            elif task_type == Task.CONVERT:
                if not await self.check_convert(*args):
                    log.debug('Already converting %s' % repr(args))
                    continue
                method = self.run_convert

            # Queue it up and run it
            self.stats_began += 1
            try:
                await method(*args)
                self.stats_success += 1
            except Exception as e:
                self.stats_error += 1
                log.exception('Error in task: "%s"' % repr(e))

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
        with async_timeout.timeout(DOWNLOAD_TIMEOUT):
            async with self.aiohttp.get(url) as response:
                while True:
                    chunk = await response.content.read(DOWNLOAD_CHUNK_SIZE)
                    if not chunk:
                        break
                    f_handle.write(chunk)
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


class AioWorker(Worker):
    '''
    Uses an asyncio Queue to enqueue tasks
    '''

    def __init__(self, queue):
        super().__init__()
        self.running = True
        self.queue = queue

        # Sets for locking to prevent race conditions
        self.downloading_resources = set()
        self.converting_resources = set()

    async def queue_size(self):
        return self.queue.qsize()

    async def enqueue(self, task_type, args):
        await self.queue.put((task_type, args))

    async def get_next(self):
        '''
        Await the next item on the queue
        '''
        task_type, args = await self.queue.get()
        return task_type, args

    async def check_download(self, foreign_resource):
        if foreign_resource in self.downloading_resources:
            return False
        self.downloading_resources.add(foreign_resource)
        return True

    async def check_convert(self, converter, in_r, out_r):
        key = (in_r, out_r)
        if key in self.converting_resources:
            return False
        self.converting_resources.add(key)
        return True


class WorkerManager(list):
    '''
    Singleton that handles either multiple workers, or a single worker
    connection (in the case of workers living in another process), and
    exposes relevant methods to enqueueing tasks related to conversion.
    '''

    def gather_run(self):
        '''
        Gathers all workers to be run in a loop.
        '''
        return asyncio.gather(*[worker.run() for worker in self])

    def pick_sticky(self, hashable):
        '''
        Chooses a worker 'stickily' (keeping with the same)
        '''
        return self[hash(hashable) % len(self)]

    def enqueue_sync(self, func, *func_args):
        '''
        Enqueue an arbitrary synchronous function.
        '''
        worker = self.pick_sticky(0)  # just pick first always
        args = (func,) + func_args
        coro = worker.enqueue(Task.FUNC, args)
        asyncio.ensure_future(coro)

    def enqueue_download(self, resource):
        '''
        Enqueue the download of the given foreign resource.
        '''
        worker = self.pick_sticky(resource.url_string)
        coro = worker.enqueue(Task.DOWNLOAD, (resource,))
        asyncio.ensure_future(coro)

    def enqueue_convert(self, converter, from_resource, to_resource):
        '''
        Enqueue use of the given converter to convert to given
        resources.
        '''
        worker = self.pick_sticky(from_resource.url_string)
        args = (converter, from_resource, to_resource)
        coro = worker.enqueue(Task.CONVERT, args)
        asyncio.ensure_future(coro)


singletons.register('workers', WorkerManager)
