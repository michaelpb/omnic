import uvloop
import asyncio

from omnic.worker import AioWorker
from omnic import singletons


def runserver(host, port, debug=False, just_setup_app=False):
    singletons.settings
    # Set up loop + queue
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    async_queue = asyncio.Queue(loop=loop)
    worker = AioWorker(async_queue)
    singletons.workers.append(worker)

    if just_setup_app:
        singletons.server.configure()
        return singletons.server.app  # in unit tests likely, no coroutines

    # Start server and worker
    server_coro = singletons.server.create_server_coro(
        host=host, port=port, debug=debug)
    worker_coros = singletons.workers.gather_run()
    loop.run_until_complete(asyncio.gather(server_coro, worker_coros))

    return singletons.server.app
