import os
import shutil

from omnic import singletons
from omnic.conversion.exceptions import (ConversionInputError,
                                         ConverterUnavailable)
from omnic.conversion.utils import apply_command_list_template
from omnic.utils import filesystem


class Converter:
    cost = 1

    @staticmethod
    def configure():
        pass

    def convert(self, in_resource, out_resource):
        msg = 'Converter subclass must override convert.'
        raise NotImplementedError(msg)


class ExecConverter(Converter):
    @classmethod
    def configure(cls):
        binary_path = shutil.which(cls.command[0])
        if not binary_path:
            raise ConverterUnavailable()

    def get_arguments(self, resource):
        return resource.typestring.arguments

    def get_kwds(self, in_resource, out_resource):
        return {}

    def get_cwd(self, in_resource, out_resource):
        return os.path.dirname(in_resource.cache_path)

    def get_command(self, in_resource, out_resource):
        return apply_command_list_template(
            self.command,
            in_resource.cache_path,
            out_resource.cache_path,
            self.get_arguments(out_resource),
        )

    def get_capture(self, in_resource, out_resource):
        return []

    async def _run_command(self, cmd, kwds, in_resource, out_resource):
        # Compute working directory and misc keyword args
        kwds.setdefault('cwd', self.get_cwd(in_resource, out_resource))

        # Run the command itself, capturing stdout and/or stderr as necessary
        captures = self.get_capture(in_resource, out_resource)
        if captures:
            if set(captures) - set(['stdout', 'stderr']):
                raise ValueError('Invalid captures: %s' % str(captures))
            output_file = out_resource.cache_path
            with open(output_file, 'w+') as fd:
                for capture in captures:
                    kwds[capture] = fd
                result = await singletons.subprocess.run(cmd, **kwds)
        else:
            result = await singletons.subprocess.run(cmd, **kwds)
        return result

    async def convert(self, in_resource, out_resource):
        # Ensure directories are created and run the actual command
        in_resource.cache_makedirs()
        out_resource.cache_makedirs()
        cmd = self.get_command(in_resource, out_resource)
        kwds = self.get_kwds(in_resource, out_resource)
        result = await self._run_command(cmd, kwds, in_resource, out_resource)

        # Some conversion programs don't allow specifying output path. If the
        # command outputs to a non-standard path, fix by renaming it.
        if hasattr(self, 'get_output_filename'):
            output_fn = self.get_output_filename(in_resource, out_resource)
            if not output_fn.startswith('/'):
                # Non absolute path, guess that its next to in_resource
                base_path = os.path.dirname(in_resource.cache_path)
                output_fn = os.path.join(base_path, output_fn)
            if os.path.exists(output_fn):
                os.rename(output_fn, out_resource.cache_path)
        return result


class HardLinkConverter(Converter):
    async def convert(self, in_resource, out_resource):
        os.link(in_resource.cache_path, out_resource.cache_path)


class SymLinkConverter(Converter):
    async def convert(self, in_resource, out_resource):
        os.symlink(in_resource.cache_path, out_resource.cache_path)


class DetectorConverter(SymLinkConverter):
    async def convert(self, in_resource, out_resource):
        path = in_resource.cache_path
        detector = self.detector()
        if not os.path.exists(path):
            raise ConversionInputError('Does not exist: %s' % str(path))
        if not detector.can_detect(path):
            raise ConversionInputError('Cannot detect: %s' % str(path))
        if not detector.detect(path):
            raise ConversionInputError('Invalid: %s' % str(path))
        await super().convert(in_resource, out_resource)


class AdditiveDirectoryExecConverter(ExecConverter):
    '''
    Similar to exec converter, except it first recursively hardlinks all
    files, thus useful for non-destructive directory-level actions
    '''

    def get_cwd(self, in_resource, out_resource):
        return out_resource.cache_path  # change to output dir by default

    def recursive_hardlink(self, in_resource, out_resource):
        filesystem.recursive_hardlink_dirs(
            in_resource.cache_path,
            out_resource.cache_path,
        )

    async def convert(self, in_resource, out_resource):
        self.recursive_hardlink(in_resource, out_resource)
        await super().convert(in_resource, out_resource)
