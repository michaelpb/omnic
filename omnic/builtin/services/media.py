'''
Core media conversion service.
'''
from omnic import singletons
from omnic.conversion.utils import enqueue_conversion_path
from omnic.types.resource import ForeignResource, TypedResource
from omnic.types.typestring import TypeString
from omnic.web import security

# Required interface for service module
SERVICE_NAME = 'media'
urls = {
    '<ts>/': 'media_route',
}


def _just_checking_response(resource_exists, resource):
    response = singletons.server.response
    return response.json({
        'url': resource.url_string,
        'ready': resource_exists,
    })


async def media_route(request, ts):
    response = singletons.server.response

    # url_string = 'http://' + url_suffix
    url_string = request.args['url'][0]
    is_just_checking = bool(request.args.get('just_checking', [''])[0])

    # First do security check
    # TODO: catch errors one up, and return 4xx errors?
    await security.check(ts, request.args)

    # Prep ForeignResource and ensure does not validate security settings
    singletons.settings
    foreign_res = ForeignResource(url_string)

    target_ts = TypeString(ts)
    target_resource = TypedResource(url_string, target_ts)

    # Send back cache if it exists
    if target_resource.cache_exists():
        if is_just_checking:
            return _just_checking_response(True, target_resource)
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
        singletons.workers.enqueue_convert
    )

    if is_just_checking:
        return _just_checking_response(False, target_resource)

    # Respond with placeholder
    return singletons.placeholders.stream_response(target_ts, response)
