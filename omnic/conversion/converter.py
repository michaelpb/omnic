import os
import subprocess

from omnic.conversion.exceptions import ConversionInputError


class Converter:
    cost = 1

    async def convert(self, in_resource, out_resource):
        return self.convert_sync(in_resource, out_resource)

    def convert_sync(self, in_resource, out_resource):
        # TODO: Make both optional (run_until_complete here)
        raise Exception(
            'Converter subclass must override at least convert_sync.')


class ExecConverter(Converter):
    def get_arguments(self, resource):
        return resource.typestring.arguments

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
        return self.convert_sync(in_resource, out_resource)

        # TODO: make async
        cmd = self.get_command(in_resource, out_resource)
        return subprocess.run(cmd)

    def convert_sync(self, in_resource, out_resource):
        cmd = self.get_command(in_resource, out_resource)

        # Ensure directories are created
        in_resource.cache_makedirs()
        out_resource.cache_makedirs()

        # Run the command itself
        result = subprocess.run(cmd)

        # If the command uses a non-standard path, fix by renaming it
        if hasattr(self, 'get_output_filename'):
            output_fn = self.get_output_filename(in_resource, out_resource)
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
