#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import click

import asyncio
from omnic import default_settings
from omnic.conversion.utils import convert_local
from omnic.utils.graph import DirectedGraph
from omnic.types.typestring import TypeString
from omnic.config import settings

@click.group()
def cmds():
    pass

@cmds.command()
@click.option('--port', default=os.environ.get('PORT', 8080), type=int,
              help=u'Set application server port')
@click.option('--ip', default=os.environ.get('HOST', 'localhost'), type=str,
              help=u'Set application server ip')
@click.option('--debug', default=False,
              help=u'Set application server debug')
def runserver(port, ip, debug):
    '''
    Runs a Omnic web server
    '''
    from omnic.server import runserver as do_runserver
    click.echo('Start server at: {}:{}'.format(ip, port))
    # TODO: add reloading, add environ 
    do_runserver(settings, host=ip, port=port, debug=debug)

    #register_all()
    #app.run(host=ip, port=port, debug=debug)

@cmds.command()
@click.argument('file', required=True)
@click.argument('type', required=True)
def convert(file, type):
    '''
    Converts a single file to a given type
    '''
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
    cmds()
