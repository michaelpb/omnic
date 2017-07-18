'''
TypeString is a core class that extends mimetypes
'''
import mimetypes


class TypeString:
    '''
    Immutable utility class for typestring manipulation.

    A typestring is a string used by OmniC to specify a file-extension, a
    mimetype, or a custom "made up" type which can be more specific.

    A typestring can also include arguments to be even more specific, that
    might signify the process by which a file of that type might be derived
    (example: thumb dimensions).
    '''

    def __init__(self, s):
        self.str = s

        # Extract arguments (anything that follows ':')
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
            # Is qualifier, can't determine mimetype OR extension
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

    def __eq__(self, other):
        return all((
            self.is_qualifier == other.is_qualifier,
            self.mimetype == other.mimetype,
            self.extension == other.extension,
            self.arguments == other.arguments,
        ))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "TypeString(%s)" % repr(str(self))
