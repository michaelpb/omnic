from contextlib import contextmanager


@contextmanager
def use_settings(**kwargs):
    '''
    Context manager to temporarily override settings
    '''
    from omnic import singletons
    singletons.settings.use_settings_dict(kwargs)
    yield
    singletons.settings.use_previous_settings()
