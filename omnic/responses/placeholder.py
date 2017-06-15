from omnic import singletons


class PlaceholderNotFound(ValueError):
    pass


class Placeholder:
    types = []
    mimetype = 'application/x-empty'

    def __init__(self, typestring):
        self.typestring = typestring

    @classmethod
    def matches(cls, typestring):
        if cls.types is all:
            return True
        return str(typestring.ts_format) in cls.types

    async def stream_response(self, response):
        pass


class BytesPlaceholder(Placeholder):
    bytes = bytes([0])

    async def stream_response(self, response):
        response.write(self.bytes)


class PlaceholderSelector:
    '''
    Helper singleton that takes in all placeholders
    '''

    def __init__(self, use_settings=None):
        if use_settings:
            # Used by testing, TODO remove
            self.placeholders = use_settings.PLACEHOLDERS
        else:
            self.placeholders = singletons.settings.load_all('PLACEHOLDERS')

    def get_placeholder(self, typestring):
        for placeholder_class in self.placeholders:
            if placeholder_class.matches(typestring):
                return placeholder_class(typestring)
        return None

    def stream_response(self, typestring, response):
        placeholder = self.get_placeholder(typestring)
        if not placeholder:
            raise PlaceholderNotFound(str(typestring))
        return response.stream(
            placeholder.stream_response,
            content_type=placeholder.content_type,
        )


singletons.register('placeholders', PlaceholderSelector)
