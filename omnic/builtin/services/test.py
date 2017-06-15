'''
Defines a service useful for writing automated tests or service availability
checks. Serves up Magic Bytes of a few different file types.
'''
from sanic import Blueprint
from sanic import response


# Required interface for service module
SERVICE_NAME = 'test'
blueprint = Blueprint(SERVICE_NAME)


@blueprint.get('/test.jpg')
async def jpeg_route(request):
    async def streaming_fn(response):
        response.write(JPEG_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')

PNG_TEST_BYTES = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])


@blueprint.get('/test.png')
async def png_route(request):
    async def streaming_fn(response):
        response.write(PNG_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')

EMPTY_ZIP_TEST_BYTES = bytes([0x50, 0x4B, 0x05, 0x06])


@blueprint.get('/empty.zip')
async def zip_route(request):
    async def streaming_fn(response):
        response.write(EMPTY_ZIP_TEST_BYTES)
    return response.stream(streaming_fn, content_type='image/jpeg')


TEST_BYTES_3DS = bytes([0x4D, 0x4D])


@blueprint.get('/test.3ds')
async def zip_route(request):
    async def streaming_fn(response):
        response.write(TEST_BYTES_3DS)
    return response.stream(streaming_fn, content_type='image/jpeg')
