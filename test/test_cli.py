import re
from unittest.mock import MagicMock, call, patch

import pytest

from omnic.cli import consts
from omnic.cli.commandparser import CommandParser
from omnic.config.utils import use_settings
from omnic.types.typestring import TypeString
from omnic.utils.asynctools import CoroutineMock

from .testing_utils import mock_viewer_resource


def _check_silent(capsys):
    out, err = capsys.readouterr()
    assert err == ''
    assert out == ''


class TestCommandParser:
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
        _check_silent(capsys)

    def test_parse_args_with_subcommand_with_args(self, capsys):
        p = CommandParser()

        @p.subcommand('test 1', {('-f', '--force'): {'action': 'store_true'}})
        def testcmd1(): pass

        args = p.parse_args(['testcmd1', '-f'])
        assert hasattr(args, 'force')
        assert args.force
        _check_silent(capsys)

    def test_parse_args_to_action_args(self, capsys):
        p = CommandParser()

        @p.subcommand('test 1', {('-f', '--force'): {'action': 'store_true'}})
        def testcmd1(): pass

        action, args = p.parse_args_to_action_args(['testcmd1', '-f'])
        assert action is testcmd1
        assert args.force
        _check_silent(capsys)

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

    def test_function_decorator_with_underscore(self):
        p = CommandParser()

        @p.subcommand('description')
        def test_cmd(args):
            pass

        assert list(p.subcommands.keys()) == ['test-cmd']

    def test_print(self, capsys):
        p = CommandParser()

        @p.subcommand()
        def testcmd1():
            pass
        p.parse_args(['testcmd1'])
        p.print('test')
        _check_silent(capsys)

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

        patcher = patch('os.mkdir')
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


class TestCacheCommands:
    class args:
        urls = ['http://fake/foreign/resource']
        type = None

    class args_multiple:
        urls = ['http://foreign/resource', 'http://foreign/resource2']
        type = None

    class args_with_type:
        urls = ['http://fake/foreign/resource']
        type = 'EXT'

    class preargs:
        urls = ['http://fake/foreign/resource']
        type = 'EXT'
        force = False

    class preargs_viewer:
        names = ['viewers']
        type = 'min.js'
        force = False

    def setup_method(self, method):
        from omnic.cli import commands
        self.commands = commands

    @use_settings(path_prefix='/some/path/', path_grouping=None)
    def test_clearcache_command(self, capsys):
        # Does not exist
        with patch('os.path.exists') as exists:
            exists.return_value = False
            with patch('shutil.rmtree') as rmtree:
                self.commands.clearcache(self.args)
        assert rmtree.mock_calls == []
        out, err = capsys.readouterr()
        assert self.args.urls[0] in err
        assert 'not' in err
        assert out == ''

        # Does exists
        with patch('os.path.exists') as exists:
            exists.return_value = True
            with patch('shutil.rmtree') as rmtree:
                self.commands.clearcache(self.args)
        assert rmtree.mock_calls == [call('/some/path/')]
        _check_silent(capsys)

        # Does exist multiple
        with patch('os.path.exists') as exists:
            exists.return_value = True
            with patch('shutil.rmtree') as rmtree:
                self.commands.clearcache(self.args_multiple)
        assert rmtree.mock_calls == [call('/some/path/'), call('/some/path/')]
        _check_silent(capsys)

        # Does exist with filetype directory
        with patch('os.path.exists') as exists:
            exists.return_value = True
            with patch('os.path.isdir') as isdir:
                isdir.return_value = True
                with patch('shutil.rmtree') as rmtree:
                    self.commands.clearcache(self.args_with_type)
        assert rmtree.mock_calls == [call('/some/path/resource.ext')]
        _check_silent(capsys)

        # Does exist with filetype file
        with patch('os.path.exists') as exists:
            exists.return_value = True
            with patch('os.path.isdir') as isdir:
                isdir.return_value = False
                with patch('os.unlink') as unlink:
                    self.commands.clearcache(self.args_with_type)
        assert unlink.mock_calls == [call('/some/path/resource.ext')]
        _check_silent(capsys)

    @use_settings(path_prefix='/some/path/')
    @pytest.mark.asyncio
    async def test_precache_command(self, capsys):
        # Wrap around magic mock to make async friendly
        multic = MagicMock()

        async def async_multic(*args, **kwargs):
            multic(*args, **kwargs)

        with patch('omnic.worker.tasks.multiconvert',
                   new_callable=lambda: async_multic):
            await self.commands.precache(self.preargs)
        assert len(multic.mock_calls) == 1

        # Ensure it calls the download attempt
        first_two_args = ('http://fake/foreign/resource', 'EXT')
        assert list(multic.mock_calls[0])[1][:2] == first_two_args
        _check_silent(capsys)

    @pytest.mark.asyncio
    async def test_precache_viewers_command(self, capsys):
        from omnic import singletons
        # Wrap around magic mock to make async friendly
        multic = MagicMock()

        async def async_multic(*args, **kwargs):
            multic(*args, **kwargs)

        with use_settings(viewers=['test.testing_utils.MockPDFViewer']):
            singletons.clear('viewers')
            with patch('omnic.worker.tasks.multiconvert',
                       new_callable=lambda: async_multic):
                await self.commands.precache_named(self.preargs_viewer)
        singletons.clear('viewers')
        assert len(multic.mock_calls) == 1

        # Ensure it starts the right process
        first_two_args = (mock_viewer_resource.url_string, 'min.js')
        assert list(multic.mock_calls[0])[1][:2] == first_two_args
        _check_silent(capsys)
