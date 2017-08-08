'''
Contains main entrypoint of all things Omni Converter
'''
import os

from omnic import singletons
from omnic.cli import consts
from omnic.conversion.utils import convert_local
from omnic.types.resource import ForeignResource, TypedResource
from omnic.types.typestring import TypeString
from omnic.utils.graph import DirectedGraph
from omnic.worker.testing import autodrain_worker

cli = singletons.cli  # Alias


@cli.subcommand('Run HTTP server and workers for on-the-fly conversions', {
    ('--host', '-H'): {'help': 'Host name'},
    ('--port', '-p'): {'help': 'Port to listen on', 'type': int},
})
def runserver(args):
    settings = singletons.settings
    if args.host:
        settings.set(host=args.host)
    if args.port:
        settings.set(port=args.port)

    # Get configuration from settings
    host = settings.HOST
    port = settings.PORT
    debug = settings.DEBUG
    cli.print('Running server at http://%s:%s' % (host, port))
    if debug:
        cli.print('DEBUG MODE ON')

    # Configure main event loop, and start the server and workers
    singletons.eventloop.reconfigure()
    worker_coros = singletons.workers.gather_run()
    server_coro = singletons.server.create_server_coro(
        host=host, port=port, debug=debug)
    singletons.eventloop.run(server_coro, worker_coros)


@cli.subcommand('Convert local files to target type', {
    'files': {
        'help': 'Input files',
        'nargs': '+',
    },
    ('--type', '-t'): {
        'help': 'Desired file type for result, in TypeString format',
        'required': True,
    },
})
async def convert(args):
    to_type = TypeString(args.type)
    for path in args.files:
        if not path.startswith('/'):
            path = os.path.abspath(path)
        cli.print('Converting: %s -> %s' % (path, to_type))
        try:
            await convert_local(path, to_type)
        except DirectedGraph.NoPath as e:
            cli.printerr('ERROR: %s' % str(e))


@cli.subcommand('Minimal scaffolding for a new project', {
    'name': {'help': 'Name to be used for new project', 'nargs': 1},
})
def startproject(args):
    path = args.name[0]
    args.name[0]
    if not path.startswith('/'):
        path = os.path.abspath(path)
    os.mkdir(path)
    with open(os.path.join(path, 'settings.py'), 'w+') as fd:
        fd.write(consts.SETTINGS_PY)


def _clear_cache(url, ts=None):
    '''
    Helper function used by precache and clearcache that clears the cache
    of a given URL and type
    '''
    if ts is None:
        # Clears an entire ForeignResource cache
        res = ForeignResource(url)
        if not os.path.exists(res.cache_path_base):
            cli.printerr('%s is not cached (looked at %s)'
                         % (url, res.cache_path_base))
            return
        cli.print('%s: clearing ALL at %s'
                  % (url, res.cache_path_base))
        res.cache_remove_all()
    else:
        # Clears an entire ForeignResource cache
        res = TypedResource(url, ts)
        if not res.cache_exists():
            cli.printerr('%s is not cached for type %s (looked at %s)'
                         % (url, str(ts), res.cache_path))
            return
        cli.print('%s: clearing "%s" at %s'
                  % (url, str(ts), res.cache_path))
        if os.path.isdir(res.cache_path):
            res.cache_remove_as_dir()
        else:
            res.cache_remove()


async def _precache(url, to_type, force=False):
    '''
    Helper function used by precache and precache-named which does the
    actual precaching
    '''
    if force:
        cli.print('%s: force clearing' % url)
        _clear_cache(url)
    cli.print('%s: precaching "%s"' % (url, to_type))
    with autodrain_worker():
        await singletons.workers.async_enqueue_multiconvert(url, to_type)
    result = TypedResource(url, TypeString(to_type))
    cli.print('%s: %s precached at: %s' % (url, to_type, result.cache_path))


@cli.subcommand('Clears cache for one or more given foreign resource URLs', {
    'urls': {'help': 'URLs for foreign resource to clear', 'nargs': '+'},
    ('--type', '-t'): {
        'help': 'If specified, only target cache of given filetype',
        'default': None,
    },
})
def clearcache(args):
    for url in args.urls:
        ts = None
        if args.type:
            ts = TypeString(args.type)
        _clear_cache(url, ts)


@cli.subcommand('Precaches one or more foreign URL to given target type', {
    'urls': {'help': 'URLs for foreign resource to clear', 'nargs': '+'},
    ('--type', '-t'): {
        'help': 'Desired file type to cache, in TypeString format',
        'required': True,
    },
    ('--force', '-f'): {
        'help': 'Clears cache first before attempting',
        'action': 'store_true',
    },
})
async def precache(args):
    for url in args.urls:
        await _precache(url, args.type, force=args.force)


@cli.subcommand('Precaches special targets (presently just viewers)', {
    'names': {
        'help': 'Names of special pre-cachable urls',
        'nargs': '+',
        'choices': ['viewers'],
    },
    ('--type', '-t'): {
        'help': 'Desired file type to cache, in TypeString format',
        'required': True,
    },
    ('--force', '-f'): {
        'help': 'Clears cache first before attempting',
        'action': 'store_true',
    },
})
async def precache_named(args):
    for name in args.names:
        if name == 'viewers':
            res = singletons.viewers.get_resource()
            if args.force:
                url = res.url_string
                cli.print('%s: force clearing' % url)
                _clear_cache(url)
            if not res.cache_exists():
                res.save()
        await _precache(res.url_string, args.type)


def main():
    action, args = cli.parse_args_to_action_args()
    action(args)
