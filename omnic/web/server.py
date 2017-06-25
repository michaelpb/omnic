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
                print(url)
                self.app.add_route(view, url)

    def create_server_coro(self, host, port, debug=False):
        self.configure()
        return self.app.create_server(host=host, port=port, debug=debug)


singletons.register('server', WebServer)
