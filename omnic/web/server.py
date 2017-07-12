import os
import re
import signal

from omnic import singletons


class WebServer:
    TEST_HOST = '127.0.0.1'
    TEST_PORT = 989898
    TEST_URL = 'http://%s:%i' % (TEST_HOST, TEST_PORT)
    TEST_SERVER_TIMEOUT = 10

    def __init__(self):
        self.app = None
        self.testing_child_pid = None

    def configure(self, force=False):
        if self.app and not force:
            return  # already configured
        if singletons.settings.WEB_SERVER == 'sanic':
            self._setup_sanic()
        else:
            raise ValueError('Unknown web server configured')

    def _setup_sanic(self):
        from sanic import Sanic
        from sanic import response as sanic_response
        from sanic.response import redirect as sanic_redirect

        singletons.register('sanic_app', lambda: Sanic('omnic'))
        self.app = singletons.sanic_app
        self.response = sanic_response
        self.redirect = sanic_redirect

        # Set up all routes for all services
        for service in singletons.settings.load_all('SERVICES'):
            service_name = service.SERVICE_NAME
            for partial_url, view in service.urls.items():
                if isinstance(view, str):
                    view = getattr(service, view)
                url = '%s/%s' % (service_name, partial_url)
                self.app.add_route(view, url)

    def route_path(self, path):
        '''
        Hacky function that's presently only useful for testing, gets the view
        that handles the given path.
        Later may be incorporated into the URL routing
        '''
        path = path.strip('/')
        name, _, subpath = path.partition('/')
        for service in singletons.settings.load_all('SERVICES'):
            if service.SERVICE_NAME == name:  # Found service!
                break
        else:
            return [], None  # found no service

        for partial_url, view in service.urls.items():
            partial_url = partial_url.strip('/')
            if isinstance(view, str):
                view = getattr(service, view)
            regexp = re.sub(r'<[^>]+>', r'([^/]+)', partial_url)
            matches = re.findall('^%s$' % regexp, subpath)
            if matches:
                if '(' not in regexp:
                    matches = []
                return matches, view

        return [], None  # found no view

    def create_server_coro(self, host, port, debug=False):
        self.configure()
        return self.app.create_server(host=host, port=port, debug=debug)

    def fork_testing_server(self, debug=False):
        '''
        Only useful for writing integration or e2e tests, this is a hacky bit
        of code that forks the py.test process and creates a test server, then
        blocks until it gets some data down a unix pipe
        '''
        self.configure()
        if self.testing_child_pid:
            raise RuntimeError('Forking twice is not permitted')

        # Fork into test server

        # set up some unix pipes
        r, w = os.pipe()
        r, w = os.fdopen(r, 'rb', 0), os.fdopen(w, 'wb', 0)
        pid = os.fork()
        if pid == 0:
            # Child process
            r.close()
            self.testing_child_pid = True

            @self.app.listener('after_server_start')
            def notify_parent(app, loop):
                w.write(b'ready\n')
                # w.flush()
                w.close()

            self.app.run(host=self.TEST_HOST, port=self.TEST_PORT, debug=debug)
            if not w.closed:
                w.write(b'failure\n')
                # w.flush()
                w.close()
            os._exit(0)  # ensure exit of entire process
        else:
            w.close()
            self.testing_child_pid = pid
            result = b''

            import select
            TIMEOUT = self.TEST_SERVER_TIMEOUT
            ready_r, _, _ = select.select([r], [], [], TIMEOUT)
            result = b''
            if r in ready_r:
                result = r.readline()
            r.close()

            if result != b'ready\n':
                self.kill_testing_server()
                raise RuntimeError('Forked process failed')

    def __del__(self):
        # Ensure test server always gets killed
        self.kill_testing_server()

    def kill_testing_server(self):
        if self.testing_child_pid:
            os.kill(self.testing_child_pid, signal.SIGKILL)
            os.waitpid(self.testing_child_pid, 0)
            self.testing_child_pid = None


singletons.register('server', WebServer)
