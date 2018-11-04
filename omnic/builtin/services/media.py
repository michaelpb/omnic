'''
Core media conversion service.
'''
from omnic import singletons
from omnic.conversion.utils import convert_endpoint
from omnic.types.resource import ForeignResource, TypedResource
from omnic.types.typestring import TypeString
from omnic.web import security

# Required interface for service module
SERVICE_NAME = 'media'
urls = {
    '<ts>/': 'media_route',
}


async def media_route(request, ts):
    # url_string = 'http://' + url_suffix
    url_string = request.args['url'][0]
    is_just_checking = bool(request.args.get('just_checking', [''])[0])

    # First do security check
    await security.check(ts, request.args)

    # Perform all actions of convert endpoint
    return await convert_endpoint(url_string, ts, is_just_checking)
