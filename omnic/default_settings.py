# Modules which are automatically loaded as soon as settings is loaded, to
# ensure singletons etc get hooked up correctly
AUTOLOAD = [
    'omnic.conversion.converter',
    'omnic.responses.placeholder',
    'omnic.web.server',
]

WEB_SERVER = 'sanic'

# Set up logging format
LOGGING = {
    'format': '[%(asctime)s] %(process)d-%(levelname)s '
              '%(module)s::%(funcName)s():l%(lineno)d: '
              '%(message)s',
    'level': 10,  # logging.DEBUG,
}

SERVICES = [
    'omnic.builtin.services.media',
    'omnic.builtin.services.test',
    'omnic.builtin.services.admin',
    'omnic.builtin.services.viewer',
]

CONVERTERS = [
    'omnic.builtin.converters.thumb.PILThumb',
    'omnic.builtin.converters.document.Unoconv',
    'omnic.builtin.converters.document.ImageMagickPageRasterizer',
    'omnic.builtin.converters.mesh.MeshLabConverter',
    'omnic.builtin.converters.mesh.Jsc3dRenderer',
    'omnic.builtin.converters.chemical.OpenBabelConverter',
    'omnic.builtin.converters.vector.InkscapeConverter',
    'omnic.builtin.converters.vector.InkscapeRasterizer',
]


PLACEHOLDERS = [
    'omnic.builtin.responses.placeholders.PNGPixelAll',
]

PATH_PREFIX = '/tmp/omnic/'
PATH_GROUPING = 'MD5'
ALLOWED_LOCATIONS = {
    # local
    'localhost', '127.0.0.1',

    # test sites mentioned in README
    'unsplash.it', 'people.sc.fsu.edu', 'imr.sandia.gov', 'wiki.jmol.org',
}
