import asyncio

from omnic import singletons


class EventLoopManager:
    def __init__(self):
        self.reconfigure()

    def get_event_loop_lib(self):
        if singletons.settings.EVENT_LOOP == 'uvloop':
            import uvloop
            return uvloop
        elif singletons.settings.EVENT_LOOP == 'asyncio':
            return asyncio
        else:
            raise ValueError('Unknown EVENT_LOOP')

    def reconfigure(self):
        # Set up loop + queue
        event_loop_lib = self.get_event_loop_lib()
        self.loop = event_loop_lib.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.worker_queue = asyncio.Queue(loop=self.loop)

    def run(self, *coros):
        self.loop.run_until_complete(asyncio.gather(*coros))


singletons.register('eventloop', EventLoopManager)
