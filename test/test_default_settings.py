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
        assert hasattr(s, 'CONVERTERS')
        assert len(s.CONVERTERS) > 7  # shouldn't drop below this
        assert hasattr(s, 'SERVICES')
        assert len(s.SERVICES) > 3  # shouldn't drop below this
        assert hasattr(s, 'PLACEHOLDERS')
        assert hasattr(s, 'ALLOWED_LOCATIONS')
        assert len(s.ALLOWED_LOCATIONS) > 1  # at least localhost

    def test_default_settings_are_importable(self):
        s = singletons.settings
        assert len(s.load_all('CONVERTERS')) > 7
        assert len(s.load_all('SERVICES')) > 3

    def test_singletons(self):
        cg = singletons.converter_graph
        assert len(cg.converters) > 7
        singletons.placeholders
