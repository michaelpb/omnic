import os
import shutil
import subprocess

from omnic.conversion.exceptions import (ConversionInputError,
                                         ConverterUnavailable)
from omnic.utils import filesystem


class Converter:
    cost = 1

    @staticmethod
    def configure():
        pass

    async def convert(self, in_resource, out_resource):
        return self.convert_sync(in_resource, out_resource)

    def convert_sync(self, in_resource, out_resource):
        # TODO: Make both optional (run_until_complete here)
        msg = 'Converter subclass must override at least convert_sync.'
        raise NotImplementedError(msg)


class ExecConverter(Converter):
    @classmethod
    def configure(cls):
        binary_path = shutil.which(cls.command[0])
        if not binary_path:
            raise ConverterUnavailable()

    def get_arguments(self, resource):
        return resource.typestring.arguments

    def get_cwd(self, in_resource, out_resource):
        return os.path.dirname(in_resource.cache_path)

    def get_command(self, in_resource, out_resource):
        args = self.get_arguments(out_resource)
        replacements = {
            '$IN': in_resource.cache_path,
            '$OUT': out_resource.cache_path,
        }

        # Add in positional arguments ($0, $1, etc)
        for i, arg in enumerate(args):
            replacements['$' + str(i)] = arg

        # Returns list of truthy replaced arguments in command
        return [replacements.get(arg, arg) for arg in self.command]

    async def convert(self, in_resource, out_resource):
        # TODO: make async
        return self.convert_sync(in_resource, out_resource)

    def convert_sync(self, in_resource, out_resource):
        cmd = self.get_command(in_resource, out_resource)

        # Ensure directories are created
        in_resource.cache_makedirs()
        out_resource.cache_makedirs()

        # Compute working directory
        working_dir = self.get_cwd(in_resource, out_resource)

        # Run the command itself
        result = subprocess.run(cmd, cwd=working_dir)

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
    def convert_sync(self, in_resource, out_resource):
        os.link(in_resource.cache_path, out_resource.cache_path)


class SymLinkConverter(Converter):
    def convert_sync(self, in_resource, out_resource):
        os.symlink(in_resource.cache_path, out_resource.cache_path)


class DetectorConverter(SymLinkConverter):
    def convert_sync(self, in_resource, out_resource):
        path = in_resource.cache_path
        detector = self.detector()
        if not os.path.exists(path):
            raise ConversionInputError('Does not exist: %s' % str(path))
        if not detector.can_detect(path):
            raise ConversionInputError('Cannot detect: %s' % str(path))
        if not detector.detect(path):
            raise ConversionInputError('Invalid: %s' % str(path))
        super().convert_sync(in_resource, out_resource)


class AdditiveDirectoryExecConverter(ExecConverter):
    '''
    Similar to exec converter, except it first recursively symlinks all files,
    thus useful for non-destructive directory-level actions
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
        super().convert_sync(in_resource, out_resource)

    def convert_sync(self, in_resource, out_resource):
        self.recursive_hardlink(in_resource, out_resource)
        super().convert_sync(in_resource, out_resource)
