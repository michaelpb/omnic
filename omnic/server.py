from sanic import Sanic

import logging
import importlib
import uvloop
import asyncio

from omnic.worker import AioWorker
from omnic import singletons

app = None

def runserver(host, port, debug=False, just_setup_app=False):
    # Only import if actually running server (so that Sanic is not a dependency
    # if only using for convert mode)
    global app
    app = Sanic(__name__)

    # Set up all routes for all services
    for service in singletons.settings.load_all('SERVICES'):
        info = service.ServiceMeta
        app.blueprint(info.blueprint, url_prefix='/%s' % info.NAME)

    # Set up loop + queue
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    async_queue = asyncio.Queue(loop=loop)
    worker = AioWorker(async_queue)
    singletons.workers.append(worker)

    if just_setup_app:
        return app  # in unit tests likely, don't make the coroutines

    # Start server and worker
    server_coro = app.create_server(host=host, port=port, debug=debug)
    worker_coros = singletons.workers.gather_run()
    loop.run_until_complete(asyncio.gather(server_coro, worker_coros))

    return app
