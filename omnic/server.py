
from omnic import singletons


def runserver(host, port, debug=False, just_setup_app=False):
    singletons.settings  # ensure settings gets loaded

    singletons.eventloop.reconfigure()

    worker_coros = singletons.workers.gather_run()

    if just_setup_app:
        singletons.server.configure()
        return singletons.server.app  # in unit tests likely, no coroutines

    # Start server and worker
    server_coro = singletons.server.create_server_coro(
        host=host, port=port, debug=debug)
    singletons.eventloop.run(server_coro, worker_coros)
    return singletons.server.app
