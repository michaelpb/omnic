import re
from unittest.mock import MagicMock, call, patch

import pytest

from omnic.cli import consts
from omnic.cli.commandparser import CommandParser
from omnic.types.typestring import TypeString
from omnic.utils.asynctools import CoroutineMock


class TestCommandParser:
    def _check_silent(self, capsys):
        out, err = capsys.readouterr()
        assert err == ''
        assert out == ''

    def _check_help(self, info):
        assert 'testcmd1' in info
        assert 'testcmd2' in info
        assert 'testcmd3' in info
        assert 'test 1' in info
        assert 'test 2' in info
        assert 'test 3' in info

    def test_parse_empty_args(self, capsys):
        with pytest.raises(SystemExit) as e:
            CommandParser().parse_args([])
        out, err = capsys.readouterr()
        assert err == ''
        assert 'usage: omnic' in out
        assert 'vailable subcommands' in out

    def test_parse_help(self, capsys):
        with pytest.raises(SystemExit) as e:
            CommandParser().parse_args(['--help'])
        out, err = capsys.readouterr()
        assert err == ''
        assert 'usage: omnic' in out
        assert 'available subcommands' in out
        assert 'file conversion framework' in out

    def test_parse_version(self, capsys):
        with pytest.raises(SystemExit) as e:
            CommandParser().parse_args(['--version'])
        out, err = capsys.readouterr()
        assert err == ''
        assert re.match(r'omnic v\d+.\d+.\d+.*', out)

    def test_parse_args_with_subcommand(self, capsys):
        p = CommandParser()

        @p.subcommand()
        def testcmd1(): pass

        args = p.parse_args(['testcmd1'])
        assert args.subcommand == 'testcmd1'
        self._check_silent(capsys)

    def test_parse_args_with_subcommand_with_args(self, capsys):
        p = CommandParser()

        @p.subcommand('test 1', {('-f', '--force'): {'action': 'store_true'}})
        def testcmd1(): pass

        args = p.parse_args(['testcmd1', '-f'])
        assert hasattr(args, 'force')
        assert args.force
        self._check_silent(capsys)

    def test_parse_args_to_action_args(self, capsys):
        p = CommandParser()

        @p.subcommand('test 1', {('-f', '--force'): {'action': 'store_true'}})
        def testcmd1(): pass

        action, args = p.parse_args_to_action_args(['testcmd1', '-f'])
        assert action is testcmd1
        assert args.force
        self._check_silent(capsys)

    def test_gen_subcommand_help(self, capsys):
        p = CommandParser()

        @p.subcommand('test 1')
        def testcmd1(args): pass

        @p.subcommand('test 2')
        def testcmd2(args): pass

        @p.subcommand('test 3')
        def testcmd3(args): pass

        self._check_help(p.gen_subcommand_help())

        with pytest.raises(SystemExit) as e:
            p.parse_args(['-h'])
        out, err = capsys.readouterr()
        self._check_help(out)

    def test_create_parser(self):
        p = CommandParser()
        p.register_subparser(
            name='testcmd',
            description='desc',
            arguments={},
            action=MagicMock(),
        )
        assert list(p.subcommands.keys()) == ['testcmd']

        action2 = MagicMock()
        p.register_subparser(
            name='testcmd2',
            description='desc2',
            arguments={'--force': {'action': 'store_true'}},
            action=action2,
        )
        assert set(p.subcommands.keys()) == {'testcmd', 'testcmd2'}
        description, action, opts = p.subcommands['testcmd2']
        assert description == 'desc2'
        assert action == action2
        assert opts == [(('--force', ), {'action': 'store_true'})]

    def test_function_decorator(self):
        p = CommandParser()

        @p.subcommand('description')
        def testcmd(args):
            pass

        assert list(p.subcommands.keys()) == ['testcmd']

    def test_print(self, capsys):
        p = CommandParser()

        @p.subcommand()
        def testcmd1():
            pass
        p.parse_args(['testcmd1'])
        p.print('test')
        self._check_silent(capsys)

        # Check stderr
        p.printerr('test')
        out, err = capsys.readouterr()
        assert out == ''
        assert err == 'test\n'

        # Now check verbose
        p.parse_args(['-v', 'testcmd1'])
        p.print('test')
        out, err = capsys.readouterr()
        assert out == 'test\n'
        assert err == ''

    def test_asyncio_subcommands(self, capsys):
        p = CommandParser()

        @p.subcommand()
        async def testcmd(args):
            print('was called')

        action, args = p.parse_args_to_action_args(['testcmd'])
        action(args)

        out, err = capsys.readouterr()
        assert out == 'was called\n'


class TestCoreCommands:
    def setup_method(self, method):
        from omnic.cli import commands
        self.commands = commands

        self.patchers = []

        patcher = patch('omnic.cli.commands.convert_local',
                        new_callable=CoroutineMock)
        self.convert_local = patcher.start()
        self.patchers.append(patcher)

        patcher = patch('omnic.cli.commands.os.path.abspath',
                        new_callable=lambda: (lambda p: '/fake/to/' + p))
        patcher.start()
        self.patchers.append(patcher)

        patcher = patch('omnic.cli.commands.singletons')
        self.singletons = patcher.start()
        self.singletons.settings.HOST = 'host'
        self.singletons.settings.PORT = 1337
        self.singletons.settings.DEBUG = False
        self.patchers.append(patcher)

        patcher = patch('omnic.cli.commands.open')
        self.open = patcher.start()
        self.patchers.append(patcher)

        patcher = patch('omnic.cli.commands.os.mkdir')
        self.mkdir = patcher.start()
        self.patchers.append(patcher)

    def teardown_method(self, method):
        for patcher in self.patchers:
            patcher.stop()

    @pytest.mark.asyncio
    async def test_convert_command(self):
        class args:
            files = ['/path/to/file1', 'file2']
            type = 'test'
        await self.commands.convert(args)
        self.convert_local.assert_has_calls((
            call('/path/to/file1', TypeString('test')),
            call('/fake/to/file2', TypeString('test')),
        ))

    def test_runserver_command(self):
        class args:
            pass
        self.commands.runserver(args)
        server_kwargs = dict(host='host', port=1337, debug=False)
        assert self.singletons.mock_calls[0] == call.eventloop.reconfigure()
        assert self.singletons.mock_calls[1] == call.workers.gather_run()
        assert self.singletons.mock_calls[2] == call.server \
            .create_server_coro(**server_kwargs)
        assert self.singletons.mock_calls[3]
        # Not sure how to test this:
        # assert self.singletons.mock_calls[3] == call.eventloop \
        #    .run(
        #        self.singletons.create_server_coro(),
        #        self.singletons.workers.gather_run(),
        #    )

    def test_startproject_command(self):
        class args:
            name = ['testproj']
        self.commands.startproject(args)
        assert self.mkdir.mock_calls == [
            call('/fake/to/testproj'),
        ]
        assert self.open.mock_calls[0] == call(
            '/fake/to/testproj/settings.py', 'w+')
        assert self.open.mock_calls[1] == call().__enter__()
        assert self.open.mock_calls[2] == call(
        ).__enter__().write(consts.SETTINGS_PY)
