

from sanic import Blueprint
from sanic import response

from omnic.types.typestring import TypeString
from omnic.types.resource import ForeignResource, TypedResource
from omnic.conversion.utils import enqueue_conversion_path
from omnic import singletons


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
    # TODO: catch errors one up, and return 4xx errors?
    settings = singletons.settings
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
        singletons.workers.enqueue_download(foreign_res)

    # Queue up a single function that will in turn queue up conversion process
    singletons.workers.enqueue_sync(
        enqueue_conversion_path,
        url_string,
        str(target_ts),
        ServiceMeta.enqueue_convert
    )

    # Respond with placeholder
    return singletons.placeholders.stream_response(target_ts, response)
