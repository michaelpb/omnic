'''
Defines a service useful for writing automated tests or service availability
checks. Serves up Magic Bytes of a few different file types.
'''
from omnic import singletons

# Required interface for service module
SERVICE_NAME = 'test'
urls = {
    'test.jpg': 'jpeg_route',
    'test.png': 'png_route',
    'empty.zip': 'zip_route',
    'test.3ds': 'test_3ds_route',
    'manifest.json': 'manifest_json_route',
}

JPEG_TEST_BYTES = bytes([0xff, 0xd8, 0xff, 0xe0])
PNG_TEST_BYTES = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
EMPTY_ZIP_TEST_BYTES = bytes([0x50, 0x4B, 0x05, 0x06])
TEST_BYTES_3DS = bytes([0x4D, 0x4D])

MANIFEST_JSON = {
    'files': {
        'test.jpg': 'http://127.0.0.1:42101/test/test.jpg',
        'test.png': 'http://127.0.0.1:42101/test/test.png',
        'some_zip.zip': 'http://127.0.0.1:42101/test/empty.zip',
        'test.3ds': 'http://127.0.0.1:42101/test/test.3ds',
    },
}


async def jpeg_route(request):
    response = singletons.server.response

    async def streaming_fn(response):
        response.write(JPEG_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')


async def png_route(request):
    response = singletons.server.response

    async def streaming_fn(response):
        response.write(PNG_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')


async def zip_route(request):
    response = singletons.server.response

    async def streaming_fn(response):
        response.write(EMPTY_ZIP_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')


async def manifest_json_route(request):
    return singletons.server.response.json(MANIFEST_JSON)


async def test_3ds_route(request):
    response = singletons.server.response

    async def streaming_fn(response):
        response.write(TEST_BYTES_3DS)
    return response.stream(streaming_fn, content_type='image/jpeg')
