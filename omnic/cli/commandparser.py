import argparse
import sys
import textwrap

import omnic
from omnic import singletons
from omnic.cli import consts
from omnic.utils.asynctools import coerce_to_synchronous


class CommandParser:
    def __init__(self):
        self.subcommands = {}
        self._last_args = None

    def gen_subcommand_help(self):
        commands = self.subcommands.items()
        return '\n'.join(
            '%s %s' % (
                subcommand.ljust(15),
                textwrap.shorten(description, width=61),
            )
            for subcommand, (description, action, opts) in commands
        )

    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser(
            prog='omnic',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Generalized file conversion framework, useful as '
            'web micro-service.',
            epilog=(
                consts.CLI_HELP_EPILOG_TEMPLATE % self.gen_subcommand_help()
            ),
        )

        parser.add_argument('-V', '--version',
                            action='version',
                            version='%(prog)s v' + omnic.__version__,
                            )

        parser.add_argument('-v', '--verbose',
                            action='store_true',
                            default=False,
                            help='increase output verbosity',
                            )

        subparsers = parser.add_subparsers(dest='subcommand')
        for name, (description, action, opts) in self.subcommands.items():
            subparser = subparsers.add_parser(name, description=description)
            for args, kwargs in opts:
                subparser.add_argument(*args, **kwargs)

        args = parser.parse_args(argv)
        self._last_args = args
        if not args.subcommand:
            parser.print_help()
            sys.exit(1)
        return args

    def parse_args_to_action_args(self, argv=None):
        '''
        Parses args and returns an action and the args that were parsed
        '''
        args = self.parse_args(argv)
        action = self.subcommands[args.subcommand][1]
        return action, args

    def register_subparser(self, action, name, description='', arguments={}):
        '''
        Registers a new subcommand with a given function action.

        If the function action is synchronous
        '''
        action = coerce_to_synchronous(action)
        opts = []
        for flags, kwargs in arguments.items():
            if isinstance(flags, str):
                flags = tuple([flags])
            opts.append((flags, kwargs))
        self.subcommands[name] = (description, action, opts)

    def subcommand(self, description='', arguments={}):
        '''
        Decorator for quickly adding subcommands to the omnic CLI
        '''
        def decorator(func):
            self.register_subparser(
                func,
                func.__name__,
                description=description,
                arguments=arguments,
            )
            return func
        return decorator

    def print(self, *args, **kwargs):
        '''
        Utility function that behaves identically to 'print' except it only
        prints if verbose
        '''
        if self._last_args and self._last_args.verbose:
            print(*args, **kwargs)

    def printerr(self, *args, **kwargs):
        kwargs['file'] = sys.stderr
        print(*args, **kwargs)


singletons.register('cli', CommandParser)
