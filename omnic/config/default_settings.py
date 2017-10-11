# Modules which are automatically loaded as soon as settings is loaded, to
# ensure singletons etc get hooked up correctly
AUTOLOAD = [
    'omnic.conversion.graph',
    'omnic.cli.commandparser',
    'omnic.cli.commands',
    'omnic.responses.placeholder',
    'omnic.web.server',
    'omnic.web.eventloop',
    'omnic.web.viewer',
    'omnic.worker.manager',
    'omnic.worker.subprocessmanager',
    'omnic.types.detectors',
]

HOST = '127.0.0.1'
PORT = 8080
DEBUG = True

# External settings (used for generating external URLs)
EXTERNAL_SCHEME = 'http'
EXTERNAL_HOST = None
EXTERNAL_PORT = None

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
    # 'omnic.builtin.converters.thumb.PILThumb', # Disabling Pillow thumb
    # 'omnic.builtin.converters.audio.SoxAudioSpectrogramRenderer',
    'omnic.builtin.converters.thumb.ImageMagickThumb',
    'omnic.builtin.converters.document.Unoconv',
    'omnic.builtin.converters.document.ImageMagickPageRasterizer',
    'omnic.builtin.converters.mesh.MeshLabConverter',
    'omnic.builtin.converters.mesh.Jsc3dRenderer',
    'omnic.builtin.converters.chemical.OpenBabelConverter',
    'omnic.builtin.converters.vector.InkscapeConverter',
    'omnic.builtin.converters.vector.InkscapeRasterizer',
    'omnic.builtin.converters.manifest.ManifestDownloader',
    'omnic.builtin.converters.video.FfmpegThumbnailer',
    'omnic.builtin.converters.audio.FfmpegAudioWaveformRenderer',
    'omnic.builtin.converters.text.PandocMarkupCompiler',

    # Git preview system
    'omnic.builtin.converters.git.GitLsTreeToJson',
    'omnic.builtin.converters.git.GitTreeJsonToHtml',
    'omnic.builtin.converters.git.InlineJsVariable',

    # Front-end JavaScript build system
    'omnic.builtin.converters.nodejs.NodePackageDetector',
    'omnic.builtin.converters.nodejs.NPMInstalledDirectoryConverter',
    'omnic.builtin.converters.nodejs.BrowserifyBundler',
    'omnic.builtin.converters.nodejs.BabelES6Compiler',
    'omnic.builtin.converters.nodejs.UglifyJSMinifier',

    'omnic.builtin.services.viewer.converters.ViewerNodePackageBuilder',
]

PREFERRED_CONVERSION_PATHS = []
CONVERSION_PROFILES = {}

VIEWERS = [
    'omnic.builtin.viewers.omnic_viewer_core',
    'omnic.builtin.viewers.simple_image_viewer',
    'omnic.builtin.viewers.simple_pdf_embed',
]

PLACEHOLDERS = [
    'omnic.builtin.responses.placeholders.PNGPixel',
    'omnic.builtin.responses.placeholders.JSGlobalVar',
    'omnic.builtin.responses.placeholders.EmptyAll',
]

PATH_PREFIX = '/tmp/omnic/'

RESOURCE_CACHE_INTERFIX = 'resource'
MUTABLE_RESOURCE_CACHE_INTERFIX = 'mutable'

PATH_GROUPING = 'MD5'
ALLOWED_LOCATIONS = {
    # local
    'localhost', '127.0.0.1',

    # github, for omnic-zoo
    'github.com',
    'raw.githubusercontent.com',
}

# Conversion type safety stuff:
CONVERSION_SYSTEM_CHECK = True

SECURITY = None

HMAC_SECRET = 'REPLACE_ME_PRIVATE'
