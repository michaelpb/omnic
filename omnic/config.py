import os


def load_settings():
    from omnic import default_settings
    from omnic.conversion.converter import ConverterGraph
    from omnic.responses.placeholder import PlaceholderSelector
    settings = default_settings
    custom_settings_path = os.environ.get('OMNIC_SETTINGS')
    if custom_settings_path:
        # TODO import here
        pass
    settings.converter_graph = ConverterGraph(settings.CONVERTERS)
    settings.placeholders = PlaceholderSelector(settings)
    return default_settings


def override_settings(new_settings):
    global settings
    old_settings = settings
    settings = new_settings
    return old_settings


def get_settings():
    global settings
    if not settings:
        settings = load_settings()
    return settings


settings = load_settings()
