from omnic import singletons


class WebServer:
    def __init__(self):
        self.app = None

    def configure(self, force=False):
        if self.app and not force:
            return  # already configured
        if singletons.settings.WEB_SERVER == 'sanic':
            self._setup_sanic()
        else:
            raise ValueError('Unknown web server configured')

    def _setup_sanic(self):
        from sanic import Sanic
        singletons.register('sanic_app', lambda: Sanic('omnic'))
        self.app = singletons.sanic_app

        # Set up all routes for all services
        for service in singletons.settings.load_all('SERVICES'):
            name = service.SERVICE_NAME
            self.app.blueprint(service.blueprint, url_prefix='/%s' % name)

    def create_server_coro(self, host, port, debug=False):
        self.configure()
        return self.app.create_server(host=host, port=port, debug=debug)


singletons.register('server', WebServer)
