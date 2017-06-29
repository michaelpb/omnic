import json
import shutil
import os

import aiohttp

from omnic import singletons
from omnic.builtin.types.nodejs import NODE_PACKAGE
from omnic.conversion import converter

VIEWER_EXT = 'omnic_viewer_descriptor'

PACKAGE_JSON_TEMPLATE = {
    "name": "omnicviewer",
    "version": "0.0.0",
    "description": "Auto-generated viewer package",
    "main": "index.js",
    "dependencies": None,
    "author": "",
    "license": "GPL-3.0"
}

def generate_index_js(viewer_names):
    return '\n'.join('require("%s");' % name for name in viewer_names)

class ViewerNodePackageBuilder(converter.Converter):
    inputs = [
        VIEWER_EXT.upper(),
    ]
    outputs = [
        str(NODE_PACKAGE),
    ]

    async def convert(self, in_resource, out_resource):

        # Read in dependencies object from the in resource
        with in_resource.cache_open('r') as fd:
            dependencies = json.load(fd)

        # Assemble the package json and write to file
        package_json_dict = dict(PACKAGE_JSON_TEMPLATE)
        package_json_dict['dependencies'] = dependencies
        with out_resource.cache_open_as_dir('package.json', 'w') as fd:
            json.dump(package_json_dict, fd, indent=4)

        # Write the index JavaScript file that serves as the entry point for
        # all viewers
        with out_resource.cache_open_as_dir('index.js', 'w') as fd:
            fd.write(generate_index_js(dependencies.keys()))

