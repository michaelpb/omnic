'''
Contains main entrypoint of all things Omni Converter
'''
import asyncio
import os

import click

from omnic import singletons
from omnic.conversion.utils import convert_local
from omnic.types.typestring import TypeString
from omnic.utils.graph import DirectedGraph

# aliases
settings = singletons.settings
cli = singletons.cli

@cli.subcommand('Run web conversion microservice web-server')
def runserver(args):
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
    ('--type', '-t'): {'help': 'Target type for type conversion'},
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
            cli.print('ERROR: %s' % str(e))


@click.argument('file', required=True)
@click.argument('type', required=True)
def old_convert(file, type):
    '''
    Converts a single file to a given type
    '''

    # Ensure settings gets setup so everything is imported
    from omnic import singletons
    singletons.settings

    path = file
    to_type = TypeString(type)
    if not path.startswith('/'):
        path = os.path.abspath(path)
    click.echo('Converting: {} -> {}'.format(path, to_type))
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(convert_local(path, to_type))
    except DirectedGraph.NoPath as e:
        print('ERROR: %s' % str(e))
    loop.close()

def main():
    action, args = cli.parse_args_to_action_args()
    action(args)
