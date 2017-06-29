import asyncio

from omnic import singletons

from . import enums


class WorkerManager(list):
    '''
    Singleton that handles either multiple workers, or a single worker
    connection (in the case of workers living in another process), and exposes
    relevant methods to enqueueing tasks related to conversion.
    '''

    def __init__(self):
        # By default setup a single worker
        self.worker_class = singletons.settings.load('WORKER')
        self.append(self.worker_class())
        self._tmp_hack_enqueued_coros = []
        self._tmp_do_hack_enqueue = False

    def gather_run(self):
        '''
        Gather all workers to be run in a loop.
        '''
        return asyncio.gather(*[worker.run() for worker in self])

    def pick_sticky(self, hashable):
        '''
        Choose a worker 'stickily' (keeping with the same)
        '''
        return self[hash(hashable) % len(self)]

    def enqueue_sync(self, func, *func_args):
        '''
        Enqueue an arbitrary synchronous function.

        Deprecated: Use async version instead
        '''
        worker = self.pick_sticky(0)  # just pick first always
        args = (func,) + func_args
        coro = worker.enqueue(enums.Task.FUNC, args)
        asyncio.ensure_future(coro)

    async def async_enqueue_sync(self, func, *func_args):
        '''
        Enqueue an arbitrary synchronous function.
        '''
        worker = self.pick_sticky(0)  # just pick first always
        args = (func,) + func_args
        await worker.enqueue(enums.Task.FUNC, args)

    def enqueue_download(self, resource):
        '''
        Enqueue the download of the given foreign resource.

        Deprecated: Use async version instead
        '''
        worker = self.pick_sticky(resource.url_string)
        coro = worker.enqueue(enums.Task.DOWNLOAD, (resource,))
        asyncio.ensure_future(coro)

    async def async_enqueue_download(self, resource):
        '''
        Enqueue the download of the given foreign resource.
        '''
        worker = self.pick_sticky(resource.url_string)
        await worker.enqueue(enums.Task.DOWNLOAD, (resource,))

    def enqueue_convert(self, converter, from_resource, to_resource):
        '''
        Enqueue use of the given converter to convert to given
        resources.

        Deprecated: Use async version instead
        '''
        worker = self.pick_sticky(from_resource.url_string)
        args = (converter, from_resource, to_resource)
        coro = worker.enqueue(enums.Task.CONVERT, args)
        if self._tmp_do_hack_enqueue:
            # TODO delete this, once we remove this method
            self._tmp_hack_enqueued_coros.append(coro)
        else:
            asyncio.ensure_future(coro)

    async def async_enqueue_convert(self, converter, from_resource, to_resource):
        '''
        Enqueue use of the given converter to convert to given
        resources.
        '''
        worker = self.pick_sticky(from_resource.url_string)
        args = (converter, from_resource, to_resource)
        await worker.enqueue(enums.Task.CONVERT, args)


singletons.register('workers', WorkerManager)
