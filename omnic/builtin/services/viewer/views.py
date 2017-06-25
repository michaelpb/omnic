'''
Serves JavaScript necessary to refresh thumbs.

Eventually will also gen JS for mounting viewers.
'''
from omnic.responses.template import Jinja2TemplateHelper

templates = Jinja2TemplateHelper('omnic.builtin.services.viewer', 'templates')


async def reload_thumb_js(request):
    return templates.render(request, 'reload-thumb.js', {})
