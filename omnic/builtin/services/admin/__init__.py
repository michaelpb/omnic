from .views import blueprint


class ServiceMeta:
    NAME = 'admin'
    blueprint = blueprint
    config = None
    app = None
    log = None
    enqueue = None
