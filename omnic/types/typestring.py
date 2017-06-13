'''
TypeString is a core class that extends mimetypes 
'''
import os
import mimetypes

import magic

UNKNOWN_MIMETYPE = ('application/x-empty',
                    'application/octet-stream', 'text/plain')


class TypeString:
    def __init__(self, s):
        self.str = s

        # Extract arguments
        if ':' in s:
            self.ts_format, _, arguments_str = s.partition(':')
            self.arguments = tuple(arguments_str.split(','))
        else:
            self.ts_format = s
            self.arguments = tuple()

        # Check if is mimetype, extension or qualifier
        self.is_qualifier = False
        self.mimetype = None
        self.extension = None
        if '/' in self.ts_format:
            self.mimetype = self.ts_format
            ext = mimetypes.guess_extension(self.mimetype)
            if ext:
                self.extension = ext.strip('.').upper()
        elif self.ts_format.isupper():
            self.extension = self.ts_format
            fn = 'fn.%s' % self.extension
            self.mimetype, _ = mimetypes.guess_type(fn)  # discard encoding
        else:
            # Is qualifier, can't determine mimetype
            self.is_qualifier = True

    def modify_basename(self, basename):
        if self.extension:
            ext = self.extension.lower()
        else:
            ext = self.ts_format.replace('/', ':')

        if self.arguments:
            ext = '.'.join(self.arguments + (ext,))
        return '%s.%s' % (basename, ext)

    def __str__(self):
        return self.str

    def __repr__(self):
        return "TypeString(%s)" % repr(str(self))


def guess_typestring(path):
    '''
    Guesses a TypeString from the given path
    '''
    with open(path, 'rb') as fd:
        mimetype = magic.from_buffer(fd.read(128), mime=True)
        if mimetype and mimetype not in UNKNOWN_MIMETYPE:
            return TypeString(mimetype)

    # Otherwise, tries based on extension
    _, ext = os.path.splitext(path)
    return TypeString(ext.strip('.').upper())
