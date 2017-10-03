import asyncio
import json

import aiohttp

from omnic import singletons
from omnic.builtin.types.core import DIRECTORY, MANIFEST_JSON
from omnic.responses.template import Jinja2TemplateHelper
from omnic.conversion import converter
from omnic.utils import filesystem

templates = Jinja2TemplateHelper('omnic.builtin.converters', 'templates')

class GitLsTreeToJson(converter.Converter):
    inputs = [
        'GIT',
        # TODO: Clean this up, use the detector system instead
        # ALSO TODO: 
        # When finishing Resolver graph system, give option of popping out
        # known types in addition to unknown (for example, known type of
        # .git-ls-tree)
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
            lines = json.load(fd)
        html_result = templates.render_to_string(None, 'git-tree.html', {
            'items': lines,
        })
        with out_resource.cache_open('w+') as fd:
            fd.write(html_result)

