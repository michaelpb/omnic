from omnic.conversion import converter


class PILThumb(converter.Converter):
    inputs = [
        'JPG',
        'JPE',
        'JPEG',
        'PNG',
        'GIF',
        'BMP',
        'image/jpg',
        'image/jpeg',
        'image/gif',
        'image/png',
    ]
    outputs = [
        'thumb.png',
        'thumb.jpg',
    ]
    default_size = (200, 200)

    def __init__(self):
        super(self).__init__()
        # Import from Image only when in use
        from PIL import Image
        self.Image = Image

    def generate_thumb(self, size, orig_resource, thumb_resource):
        with orig_resource.cache_open() as orig:
            im = self.Image.open(orig)
            im.thumbnail(size)
        with thumb_resource.cache_open('wb') as target:
            if thumb_resource.typestring.ts_format == 'thumb.jpg':
                # Ensure it has no alpha before saving
                p_mode_alpha = (im.mode == 'P' and 'transparency' in im.info)
                if im.mode in ('RGBA', 'LA') or p_mode_alpha:
                    alpha = im.convert('RGBA').split()[-1]
                    no_alpha = self.Image.new("RGB", im.size, (255, 255, 255))
                    no_alpha.paste(im, mask=alpha)
                    no_alpha.save(target, 'JPEG')
                else:
                    im.save(target, 'JPEG')
            else:
                # Save as is
                im.save(target)

    async def convert(self, in_resource, out_resource):
        size = self.default_size
        arguments = out_resource.typestring.arguments
        if arguments:
            width_s, _, height_s = arguments[0].partition('x')
            size = (int(width_s), int(height_s))
        self.generate_thumb(size, in_resource, out_resource)


class ImageMagickThumb(converter.ExecConverter):
    inputs = [
        'JPG',
        'JPE',
        'JPEG',
        'PNG',
        'GIF',
        'BMP',
        'image/jpg',
        'image/jpeg',
        'image/gif',
        'image/png',
    ]

    outputs = [
        'thumb.png',
        'thumb.jpg',
    ]

    command = [
        'convert',
        # -define jpeg:size=500x180 ... should be 2x size, and correspond to
        # JPEG or PNG
        '-thumbnail',
        '$0',
        '-gravity',
        'center',
        '-extent',
        '$1',
        '$IN',
        '$OUT',
    ]

    default_size = (200, 200)

    def get_arguments(self, out_resource):
        args = out_resource.typestring.arguments
        if args:
            width, _, height = args[0].partition('x')
            size = (int(width), int(height))
        else:
            size = self.default_size
        extent_size = (int(size[0] / 2), int(size[1] / 2))
        return ['%ix%i^' % size, '%ix%i' % extent_size]
