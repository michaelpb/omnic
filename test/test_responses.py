"""
Tests for `responses` module.
"""


from omnic.responses import placeholder
from omnic.types.typestring import TypeString

from .testing_utils import Magic


class ExampleBytesPlaceholder(placeholder.BytesPlaceholder):
    types = [
        'PNG',
        'JPG',
    ]
    content_type = 'image/png'
    bytes = Magic.PNG_PIXEL_B


class ExampleCustomPlaceholder(placeholder.Placeholder):
    types = [
        'JPEG',
        'JPG',
    ]
    content_type = 'image/jpeg'

    async def stream_response(self, response):
        response.write(Magic.JPEG)


class ExampleWildcardPlaceholder(placeholder.Placeholder):
    types = all
    content_type = 'image/png'

    async def stream_response(self, response):
        response.write(Magic.PNG)


class MockConfig:
    PLACEHOLDERS = [
        ExampleBytesPlaceholder,
        ExampleCustomPlaceholder,
        ExampleWildcardPlaceholder,
    ]


class TestResponsePlaceholders:
    @classmethod
    def setup_class(cls):
        cls.phs = placeholder.PlaceholderSelector(MockConfig)

    def test_get_placeholder(self):
        ph = self.phs.get_placeholder(TypeString('PNG'))
        assert isinstance(ph, ExampleBytesPlaceholder)
        ph = self.phs.get_placeholder(TypeString('JPEG'))
        assert isinstance(ph, ExampleCustomPlaceholder)
        ph = self.phs.get_placeholder(TypeString('nonexistent'))
        assert isinstance(ph, ExampleWildcardPlaceholder)

        # Temporarily disable
        ExampleWildcardPlaceholder.types = []
        ph = self.phs.get_placeholder(TypeString('nonexistent'))
        assert ph is None
        ExampleWildcardPlaceholder.types = all  # restore

    def test_placeholder_stream_response(self):
        class mock_response:
            @staticmethod
            def write(data):
                mock_response.data = data

            @staticmethod
            def stream(streamer=None, content_type=None):
                mock_response.ct = content_type
                # For now, too hard to test this bit
                #coro = streamer(mock_response)
                #assert iscoroutine(coro)
                # yield from coro(mock_response)

        self.phs.stream_response(TypeString('PNG'), mock_response)
        assert mock_response.ct == 'image/png'
        #assert mock_response.data == Magic.PNG_PIXEL_B

        self.phs.stream_response(TypeString('JPEG'), mock_response)
        assert mock_response.ct == 'image/jpeg'
        #assert mock_response.data == Magic.JPEG

        self.phs.stream_response(TypeString('lol'), mock_response)
        assert mock_response.ct == 'image/png'
        #assert mock_response.data == Magic.PNG
