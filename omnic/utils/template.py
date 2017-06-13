from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import response

class Jinja2TemplateHelper:
    def __init__(self, package, path):
        self.env = Environment(
            loader=PackageLoader(package, path),
            autoescape=select_autoescape(['html'])
        )

    def process_context(self, request):
        return {
            'TEMPLATE_TOP': 'lol',
            'TEMPLATE_BOTTOM': 'otherlol',
        }

    def render_to_string(self, request, template_filename, extra_context={}):
        template = self.env.get_template(template_filename)
        context = {}
        context.update(self.process_context(request))
        context.update(extra_context)
        return template.render(**context)

    def render(self, request, template_filename, extra_context={}):
        rendered = self.render_to_string(request, template_filename, extra_context)
        return response.html(rendered)


