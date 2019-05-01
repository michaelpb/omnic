import os

from omnic.builtin.types.core import DIRECTORY
from omnic.conversion import converter
from omnic.conversion.exceptions import ConversionError

class ArchiveConverter(converter.ExecConverter):
    inputs = [
        str(DIRECTORY),
    ]

    outputs = [
        'ZIP',
        'TGZ',
    ]

    def get_command(self, in_resource, out_resource):
        in_path = in_resource.cache_path
        arguments = out_resource.typestring.arguments

        if arguments:
            # Determine the directory we are drilling down into
            drill_down = arguments[0]
            in_path = os.path.join(in_path, drill_down)

        desired_ext = out_resource.typestring.extension
        if desired_ext == 'ZIP':
            return [
                'zip',
                out_resource.cache_path,
                '-r',
                in_path,
            ]

        elif desired_ext == 'TGZ':
            return [
                'tar',
                '-pczf',
                out_resource.cache_path,
                in_path,
            ]

        else:
            # Should never happen, this is a sanity check
            raise ConversionError('Unknown extension: ' + desired_ext)
