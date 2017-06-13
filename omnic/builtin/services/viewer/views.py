'''
Serves JavaScript necessary to refresh thumbs.

Eventually will also gen JS for mounting viewers.
'''
from urllib.parse import urlencode

from sanic import Blueprint
from sanic import response

from omnic.utils.template import Jinja2TemplateHelper

templates = Jinja2TemplateHelper('omnic.builtin.services.viewer', 'templates')

blueprint = Blueprint('viewer')

@blueprint.get('/js/reload-thumb.js')
async def reload_thumb_js(request):
    return templates.render(request, 'reload-thumb.js', {})

