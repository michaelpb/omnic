# Modules which are automatically loaded as soon as settings is loaded, to
# ensure singletons etc get hooked up correctly
AUTOLOAD = [
    'omnic.conversion.graph',
    'omnic.responses.placeholder',
    'omnic.web.server',
    'omnic.web.eventloop',
    'omnic.worker.manager',
    'omnic.types.detectors',
]

WEB_SERVER = 'sanic'
EVENT_LOOP = 'uvloop'
WORKER = 'omnic.worker.aioworker.AioWorker'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
}


DETECTORS = [
    'omnic.builtin.types.core.MagicDetector',
    'omnic.builtin.types.core.ExtensionDetector',
    'omnic.builtin.types.core.ManifestDetector',
    'omnic.builtin.types.nodejs.NodePackageDetector',
]

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
    'omnic.builtin.converters.manifest.ManifestDownloader',

    'omnic.builtin.converters.nodejs.NodePackageDetector',
    'omnic.builtin.converters.nodejs.NPMInstalledDirectoryConverter',
    'omnic.builtin.converters.nodejs.BrowserifyBundler',
    'omnic.builtin.converters.nodejs.BabelES6Compiler',
    'omnic.builtin.converters.nodejs.UglifyJSMinifier',
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
