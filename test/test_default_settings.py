from omnic import singletons


class TestBuiltinDefaults:
    '''
    High-level sanity tests for built-ins
    '''
    @classmethod
    def setup_class(cls):
        # Ensure no custom settings
        singletons.settings.use_settings(object())

    @classmethod
    def teardown_class(cls):
        # Ensure no custom settings
        singletons.settings.use_previous_settings()

    def test_default_settings_exist(self):
        s = singletons.settings
        assert hasattr(s, 'PATH_PREFIX') and s.PATH_PREFIX
        assert hasattr(s, 'PATH_GROUPING') and s.PATH_GROUPING
        assert hasattr(s, 'WEB_SERVER') and s.WEB_SERVER
        assert hasattr(s, 'EVENT_LOOP') and s.EVENT_LOOP

    def test_default_modules_exist(self):
        s = singletons.settings
        assert hasattr(s, 'CONVERTERS')
        assert len(s.CONVERTERS) > 7  # shouldn't drop below this
        assert hasattr(s, 'SERVICES')
        assert len(s.SERVICES) > 3  # shouldn't drop below this
        assert hasattr(s, 'PLACEHOLDERS')
        assert hasattr(s, 'ALLOWED_LOCATIONS')
        assert len(s.ALLOWED_LOCATIONS) > 1  # at least localhost
        assert hasattr(s, 'LOGGING')
        assert s.LOGGING.keys()

    def test_default_settings_are_importable(self):
        s = singletons.settings
        assert len(s.load_all('PLACEHOLDERS')) > 1
        assert len(s.load_all('VIEWERS')) > 1
        assert len(s.load_all('AUTOLOAD')) > 3
        assert len(s.load_all('CONVERTERS')) > 7
        assert len(s.load_all('SERVICES')) > 3
        assert s.load('WORKER')

    def test_singletons(self):
        cg = singletons.converter_graph
        assert len(cg.converters) > 7
        v = singletons.viewers
        assert len(v.viewers) > 1
