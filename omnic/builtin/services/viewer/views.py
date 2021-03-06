'''
Serves JavaScript necessary to refresh and display viewers and thumbs.
'''

from omnic import singletons
from omnic.conversion.utils import enqueue_conversion_path
from omnic.responses.template import Jinja2TemplateHelper
from omnic.types.resource import TypedResource
from omnic.types.typestring import TypeString

templates = Jinja2TemplateHelper('omnic.builtin.services.viewer', 'templates')

NOT_LOADED_JS = '''
    window._OMNIC_VIEWER_BUNDLE_IS_LOADED = false;
'''


async def viewers_js(request):
    '''
    Viewers determines the viewers installed based on settings, then uses the
    conversion infrastructure to convert all these JS files into a single JS
    bundle, that is then served. As with media, it will simply serve a cached
    version if necessary.
    '''
    # Generates single bundle as such:
    # BytesResource -> ViewerNodePackageBuilder -> nodepackage -> ... -> min.js
    response = singletons.server.response

    # Create a viewers resource, which is simply a JSON encoded description of
    # the viewers necessary for this viewers bundle.
    viewers_resource = singletons.viewers.get_resource()
    url_string = viewers_resource.url_string

    target_ts = TypeString('min.js')  # get a minified JS bundle
    target_resource = TypedResource(url_string, target_ts)

    if target_resource.cache_exists():
        return await response.file(target_resource.cache_path, headers={
            'Content-Type': 'application/javascript',
        })

    # Otherwise, does not exist, save this descriptor to cache and kick off
    # conversion process
    if not viewers_resource.cache_exists():
        viewers_resource.save()

    # Queue up a single function that will in turn queue up conversion process
    await singletons.workers.async_enqueue_sync(
        enqueue_conversion_path,
        url_string,
        str(target_ts),
        singletons.workers.enqueue_convert
    )

    return response.text(NOT_LOADED_JS, headers={
        'Content-Type': 'application/javascript',
    })


async def reload_viewers_js(request):
    return templates.render(request, 'reload-viewers.js', {
        'viewer_bundle_url': '/viewer/js/viewers.js',
    })


async def reload_thumb_js(request):
    return templates.render(request, 'reload-thumb.js', {})


async def playbutton_svg(request):
    return templates.render(request, 'playbutton.svg', {})


async def all_js(request):
    return templates.render(request, 'reload-viewers.js', {})
