'''
Public non-secured API to signal when caches are ready
'''
from omnic import singletons
from omnic.types.resource import ForeignResource, TypedResource
from omnic.types.typestring import TypeString

# Required interface for service module
SERVICE_NAME = 'api'
urls = {
    'is-ready/': 'is_ready',
}


def _error(message):
    response = singletons.server.response
    return response.json({'error': message}, status=400)


async def is_ready(request):
    # TODO not sure if this is still useful, since we need to make individual
    # viewer requests to allow caching across multiple nodes in a
    # load-balancing situation, which was more easily implemented as a new
    # feature in the media service
    singletons.settings
    response = singletons.server.response
    urls, types = request.args.get('url'), request.args.get('type', [])
    if not urls or len(urls) != len(types):
        # Respond with error here
        return _error('Must match URL and type GET params.')

    results = []
    for url_string, ts in zip(urls, types):
        # Prep ForeignResource and ensure does not validate security settings
        if not url_string.startswith('http://'):
            url_string = 'http://' + url_string
        foreign_res = ForeignResource(url_string)
        try:
            foreign_res.validate()
        except:
            return _error('Invalid URL: "%s"' % url_string)

        target_ts = TypeString(ts)
        target_resource = TypedResource(url_string, target_ts)
        is_ready = target_resource.cache_exists()
        results.append({
            'url': url_string,
            'type': ts,
            'cached': is_ready,
        })
    return response.json({
        'resources': results,
    })
