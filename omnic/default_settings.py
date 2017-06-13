from omnic.builtin.converters.thumb import PILThumb
from omnic.builtin.converters.document import Unoconv, ImageMagickPageRasterizer
from omnic.builtin.converters.mesh import MeshLabConverter, Jsc3dRenderer
from omnic.builtin.converters.chemical import OpenBabelConverter
from omnic.builtin.converters.vector import InkscapeConverter, InkscapeRasterizer
from omnic.builtin.responses.placeholders import PNGPixel

# Set up logging format
import logging
logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
logging_format += "%(message)s"

logging.basicConfig(
    format=logging_format,
    level=logging.DEBUG
)

SERVICES = [
    'omnic.builtin.services.media',
    'omnic.builtin.services.test',
    'omnic.builtin.services.admin',
    'omnic.builtin.services.viewer',
]

CONVERTERS = [
    PILThumb,
    Unoconv,
    ImageMagickPageRasterizer,
    MeshLabConverter,
    Jsc3dRenderer,
    OpenBabelConverter,
    InkscapeConverter,
    InkscapeRasterizer,
]


class CatchAll(PNGPixel):
    types = all


PLACEHOLDERS = [
    PNGPixel,
    CatchAll,
]

PATH_PREFIX = '/tmp/omnic/'
PATH_GROUPING = 'MD5'
ALLOWED_LOCATIONS = {
    # local
    'localhost', '127.0.0.1',

    # test sites mentioned in README
    'unsplash.it', 'people.sc.fsu.edu', 'imr.sandia.gov',
}
