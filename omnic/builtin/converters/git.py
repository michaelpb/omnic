import json

from omnic.conversion import converter
from omnic.responses.template import Jinja2TemplateHelper
from omnic.utils import filesystem

templates = Jinja2TemplateHelper('omnic.builtin.converters', 'templates')


class GitLsTreeToJson(converter.Converter):
    inputs = [
        'GIT',
    ]
    outputs = [
        'git-tree.json',
    ]

    async def convert(self, in_resource, out_resource):
        with in_resource.cache_open('r') as fd:
            contents = fd.read()
        lines = contents.splitlines()

        # Split results into flat structure
        split_lines = [line.strip().split() for line in lines if line.strip()]

        # Convert flat structure into nested structure
        nested_structure = filesystem.flat_git_tree_to_nested(split_lines)

        # Add some meta data about this structure
        url = in_resource.url
        nested_structure['git_url'] = url.url
        nested_structure['git_sha'] = url.args[0]

        # Dump final into file
        with out_resource.cache_open('w+') as fd:
            json.dump(nested_structure, fd, indent=2)


class GitTreeJsonToHtml(converter.Converter):
    inputs = [
        'git-tree.json',
    ]

    outputs = [
        'git-tree.html',
    ]

    async def convert(self, in_resource, out_resource):
        with in_resource.cache_open('r') as fd:
            root = json.load(fd)
        html_result = templates.render_to_string(None, 'git-tree.html', {
            'root': root,
        })
        with out_resource.cache_open('w+') as fd:
            fd.write(html_result)


class InlineJsVariable(converter.Converter):
    inputs = [
        'git-tree.html',
    ]

    outputs = [
        'inlined.js',
        'docwrite-inject.js',
    ]

    async def convert(self, in_resource, out_resource):
        name = '_OMNIC_DATA'
        should_docwrite = False
        ts = out_resource.typestring
        if ts.ts_format == 'docwrite-inject.js':
            should_docwrite = True
        if ts.arguments:
            name = ts.arguments[0]

        with in_resource.cache_open('r') as fd:
            data = fd.read()
        stringified = json.dumps(data)

        js_result = templates.render_to_string(None, 'inline-js-variable.js', {
            'name': name,
            'stringified': stringified,
            'should_docwrite': should_docwrite,
        })
        with out_resource.cache_open('w+') as fd:
            fd.write(js_result)
