'''
Serves JavaScript necessary to refresh thumbs.

Eventually will also gen JS for mounting viewers.
'''
from omnic.responses.template import Jinja2TemplateHelper
from omnic import singletons

templates = Jinja2TemplateHelper('omnic.builtin.services.viewer', 'templates')

async def viewers_js(request):
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
    return templates.render(request, 'viewers.js', {})

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

