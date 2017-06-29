'''
Serves JavaScript necessary to refresh and display viewers and thumbs.
'''
import json

from omnic.conversion.utils import enqueue_conversion_path
from omnic.types.typestring import TypeString
from omnic.responses.template import Jinja2TemplateHelper
from omnic.types.resource import ForeignBytesResource, TypedResource
from omnic import singletons
from .converters import VIEWER_EXT

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
    # TODO: Generate single bundle as such:
    # 1. StringResource(list of JS files) -> OmnicViewerBuilder -> nodepackage
    # 2. nodepackage -> ... -> min.js
    # The package.json would look something like this:
    #   {
    #      "OV_document": "file:/path/to/omnic/builtin/viewer/document/js/"
    #   }
    # The index.js would look like:
    #   const {viewer_names} = require('viewerinfo.json')
    #   for (const viewer_name of viewer_names) {
    #      const viewer = require('OV_' + viewer_name);
    #      window.OMNIC_VIEWERS.register(viewer_name, viewer);
    #   }
    response = singletons.server.response

    # Create a viewers resource, which is simply a JSON encoded description of
    # the viewers necessary for this viewers bundle. Basename is used for
    # controlling caching
    # basename = 'viewers_%s' % omnic.settings.get_cache_string()
    node_packages = singletons.viewers.get_node_packages()
    viewers_data = json.dumps(node_packages).encode('utf8')
    viewers_resource = ForeignBytesResource(
        viewers_data,
        extension=VIEWER_EXT,
        # basename=basename,
    )
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
    return templates.render(request, 'reload-viewers.js', {})


async def reload_thumb_js(request):
    return templates.render(request, 'reload-thumb.js', {})


async def all_js(request):
    # TODO:
    # 1. Check if built cache is ready, if it is, include cached JS in the mix
    # 2. Include reload-viewers if not
    # 3. Include reload-thumb
    # 4. Send back cache headers such that only if everything is working it
    # gets a "perma" cache header set
    return templates.render(request, 'reload-viewers.js', {})
