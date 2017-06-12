from omnic.responses import placeholder

from base64 import b64decode

TRANSPARENT_PNG_PIXEL_B64 = '''
    iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=
'''
TRANSPARENT_PNG_PIXEL_BYTES = b64decode(TRANSPARENT_PNG_PIXEL_B64.strip())
class PNGPixel(placeholder.BytesPlaceholder):
    types = [
        'PNG',
        'JPG',
        'JPEG',
        'BMP',
        'GIF',
        'PCX',
        'WEBP',
        'image/png',
        'image/jpeg',
        'image/bmp',
        'image/gif',
        'image/pcx',
        'image/webp',
        'thumb.png',
        'thumb.jpg',
    ]
    content_type = 'image/png'
    bytes = TRANSPARENT_PNG_PIXEL_BYTES

