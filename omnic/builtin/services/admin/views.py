'''
A read-only admin interface that is useful for monitoring broad server stats
and testing conversions.
'''
import functools
import os

from sanic import Blueprint
from sanic import response


@functools.lru_cache(maxsize=None)
def get_template(name):
    dirname = os.path.dirname(__file__)
    return open(os.path.join(dirname, 'templates', name)).read()


def render(request, template_filename, extra_context={}):
    context = {}
    context.update(get_shared_context(request))
    context.update(extra_context)
    template_text = get_template(template_filename)
    rendered = template_text.format(**context)
    return response.html(rendered)


def get_shared_context(request):
    return {
        'TEMPLATE_TOP': get_template('template_top.html'),
        'TEMPLATE_BOTTOM': get_template('template_bottom.html'),
    }


blueprint = Blueprint('admin')


@blueprint.get('/')
async def admin_route(request):
    return render(request, 'index.html', {})
