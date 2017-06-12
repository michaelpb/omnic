from base64 import b64decode

from PIL import Image

from sanic import Blueprint
from sanic import response
from sanic import Sanic

from omnic.types.typestring import TypeString
from omnic.types.resource import TypedResource, TypedForeignResource, ForeignResource
from omnic.conversion.utils import enqueue_conversion_path
from omnic.config import settings

class ServiceMeta:
    NAME = 'media'
    blueprint = Blueprint(NAME)
    config = None
    app = None
    log = None
    enqueue = None

@ServiceMeta.blueprint.get('/<ts>/')
async def media_route(request, ts):
    url_suffix = request.args['url'][0]
    url_string = 'http://' + url_suffix

    # Prep ForeignResource and ensure does not validate security settings
    foreign_res = ForeignResource(settings, url_string)
    foreign_res.validate()

    target_ts = TypeString(ts)
    target_resource = TypedResource(settings, url_string, target_ts)

    # Send back cache if it exists
    if target_resource.cache_exists():
        return await response.file(target_resource.cache_path, headers={
                'Content-Type': target_ts.mimetype,
            })

    # Check if already downloaded. If not, queue up download.
    if not foreign_res.cache_exists():
        ServiceMeta.enqueue_download(foreign_res)

    # Queue up a single function that will in turn queue up conversion process
    ServiceMeta.enqueue_sync(
        enqueue_conversion_path,
        url_string,
        str(target_ts),
        ServiceMeta.enqueue_convert
    )

    # Respond with placeholder
    return settings.placeholders.stream_response(target_ts, response)

