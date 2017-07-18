'''
Contains main entrypoint of all things Omni Converter
'''
import os

from omnic import singletons
from omnic.cli import consts
from omnic.conversion.utils import convert_local
from omnic.types.typestring import TypeString
from omnic.utils.graph import DirectedGraph

cli = singletons.cli  # Alias


@cli.subcommand('Run HTTP server and workers for on-the-fly conversions')
def runserver(args):
    # Get configuration from settings
    host = singletons.settings.HOST
    port = singletons.settings.PORT
    debug = singletons.settings.DEBUG
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
    # Ensure settings gets setup so everything is imported
    path = args.name[0]
    args.name[0]
    if not path.startswith('/'):
        path = os.path.abspath(path)
    os.mkdir(path)
    with open(os.path.join(path, 'settings.py'), 'w+') as fd:
        fd.write(consts.SETTINGS_PY)


def main():
    action, args = cli.parse_args_to_action_args()
    action(args)
