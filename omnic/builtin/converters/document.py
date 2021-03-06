import os

from omnic.conversion import converter


class Unoconv(converter.ExecConverter):
    inputs = [
        # Document
        'DOC',
        'HTML',
        'XHTML',
        'HTM',
        'ODT',
        'OTT',
        'LTX',
        'SDW',
        'STW',
        'SXW',
        'UOT',
        'VOR',

        # Spreadsheet
        'XLS',
        'DBF',
        'ODS',
        'XML',

        # Presentation
        'ODP',
        'PPT',
        'PPTX',

        'application/msword',
        'application/vnd.oasis.opendocument.text',
    ]

    outputs = [
        'PDF',
        'application/pdf',
    ]

    command = [
        '/usr/bin/python3',
        '/usr/bin/unoconv',
        '-f',
        '$0',
        '-o',
        '$OUT',
        '$IN',
    ]

    def get_arguments(self, out_resource):
        return [out_resource.typestring.extension.lower()]


class ImageMagickPageRasterizer(converter.ExecConverter):
    inputs = [
        # Document
        'PDF',
        'PS',
        'application/pdf',
        'application/postscript',
    ]

    outputs = [
        'PNG',
        'image/png',
    ]

    command = [
        'convert',
        '$IN',
        '$0',
    ]

    def get_arguments(self, out_resource):
        page_number = 0
        source = '%s[%i]' % (out_resource.cache_path, page_number)
        return [source]

    def get_output_filename(self, in_resource, out_resource):
        dirname = os.path.dirname(out_resource.cache_path)
        basename = os.path.basename(out_resource.cache_path)
        basename_base, _ = os.path.splitext(basename)
        suffix = '0.png'
        return os.path.join(dirname, '%s-%s' % (basename_base, suffix))
