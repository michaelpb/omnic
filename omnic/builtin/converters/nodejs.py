import json
import os

from omnic.builtin.types.core import DIRECTORY
from omnic.builtin.types.nodejs import (INSTALLED_NODE_PACKAGE,
                                        INSTALLED_WEBPACK_NODE_PACKAGE,
                                        NODE_PACKAGE, WEBPACK_NODE_PACKAGE,
                                        NodePackageDetector)
from omnic.conversion import converter


class NodePackageDetector(converter.DetectorConverter):
    detector = NodePackageDetector
    inputs = [
        str(DIRECTORY),
    ]
    outputs = [
        str(NODE_PACKAGE),
        str(WEBPACK_NODE_PACKAGE),
        str(INSTALLED_NODE_PACKAGE),
        str(INSTALLED_WEBPACK_NODE_PACKAGE),
    ]


class NPMInstalledDirectoryConverter(converter.AdditiveDirectoryExecConverter):
    inputs = [
        str(NODE_PACKAGE),
        str(WEBPACK_NODE_PACKAGE),
    ]
    outputs = [
        str(INSTALLED_NODE_PACKAGE),
        str(INSTALLED_WEBPACK_NODE_PACKAGE),
    ]
    command = [
        'npm',
        'install',
    ]


class BrowserifyBundler(converter.ExecConverter):
    inputs = [
        str(INSTALLED_NODE_PACKAGE),
    ]
    outputs = [
        'bundle.js',
    ]

    def get_command(self, in_resource, out_resource):
        # Get probable name of main JS entry point
        pjson_path = os.path.join(in_resource.cache_path, 'package.json')
        package_json = json.load(open(pjson_path))
        main_js = package_json.get('main', 'index.js')
        main_js_path = os.path.join(in_resource.cache_path, main_js)
        return [
            'browserify',
            main_js_path,
            '-o',
            out_resource.cache_path,
        ]


class BabelES6Compiler(converter.ExecConverter):
    # NOTE: npm install -g babel babel-cli babel-preset-es2015
    # NOTE: It's a terrible hack to use es2015 globally, but it is the omnic
    # way, and will pay off once I build out precise containers
    inputs = [
        'JS',
        'bundle.js',
    ]
    outputs = [
        'dev-es5.js',
        'es5.js',
    ]

    def get_command(self, in_resource, out_resource):
        extra_args = []
        out = str(out_resource.typestring)

        if 'dev' in out:
            extra_args.extend(['--source-maps', 'inline'])

        if 'es5' in out:
            # TODO XXX obviously broken hack: Must fix by adding the
            # "configure" step mechanism, that gets the absolute path to
            # whichever programs/libs/whatever are necessary, and also what is
            # supported
            es2015_path = os.path.expanduser('~/.local/lib/node_modules'
                                             '/babel-preset-es2015')
            extra_args.extend(['--presets=%s' % es2015_path])

        return [
            'babel',
            '--no-babelrc',
            in_resource.cache_path,
            '--out-file',
            out_resource.cache_path,
            *extra_args,
        ]


class UglifyJSMinifier(converter.ExecConverter):
    # NOTE: npm install -g uglify-js
    inputs = [
        'es5.js',
    ]
    outputs = [
        'min.js',
    ]

    command = [
        'uglifyjs',
        '$IN',
        '-o',
        '$OUT',
    ]
