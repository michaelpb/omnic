from .views import blueprint


class ServiceMeta:
    NAME = 'viewer'
    blueprint = blueprint
    config = None
    app = None
    log = None
    enqueue = None
