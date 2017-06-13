'''
Defines a service useful for writing automated tests or service availability
checks. Serves up Magic Bytes of a few different file types.
'''
from sanic import Blueprint
from sanic import response


class ServiceMeta:
    NAME = 'test'
    blueprint = Blueprint(NAME)
    config = None
    app = None
    log = None
    enqueue = None


JPEG_TEST_BYTES = bytes([0xff, 0xd8, 0xff, 0xe0])


@ServiceMeta.blueprint.get('/test.jpg')
async def jpeg_route(request):
    async def streaming_fn(response):
        response.write(JPEG_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')

PNG_TEST_BYTES = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])


@ServiceMeta.blueprint.get('/test.png')
async def png_route(request):
    async def streaming_fn(response):
        response.write(PNG_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')

EMPTY_ZIP_TEST_BYTES = bytes([0x50, 0x4B, 0x05, 0x06])


@ServiceMeta.blueprint.get('/empty.zip')
async def zip_route(request):
    async def streaming_fn(response):
        response.write(EMPTY_ZIP_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')


TEST_BYTES_3DS = bytes([0x4D, 0x4D])


@ServiceMeta.blueprint.get('/test.3ds')
async def zip_route(request):
    async def streaming_fn(response):
        response.write(TEST_BYTES_3DS)
    return response.stream(streaming_fn, content_type='image/jpeg')
