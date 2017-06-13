'''
A read-only admin interface that is useful for monitoring broad server stats
and testing conversions.
'''
from sanic import Blueprint
from sanic import response

from omnic.utils.template import Jinja2TemplateHelper

templates = Jinja2TemplateHelper('omnic.builtin.services.admin', 'templates')

blueprint = Blueprint('admin')

@blueprint.get('/')
async def admin_route(request):
    return templates.render(request, 'index.html', {})
