from omnic.conversion import converter


class PandocMarkupCompiler(converter.ExecConverter):
    inputs = [
        'MD',
        'WIKI',
        'RST',
        'T2T',
        'TXT',
        'TEX',
        'RTF',
        'RTX',
        'BIB',
        'CSV',
        'TSV',
        'VCF',
        'VCS',
        'VCARD',

        # Man pages:
        'MAN',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',

        'text/plain',
        'text/x-bibtext',
        'text/vnd.latex-z',
        'text/markdown',
        'text/csv',
        'text/rtf',
        'text/richtext',
        'text/tab-seperated-values',
        'text/vcard',
        'text/x-crontab',
    ]

    outputs = [
        'HTML',
    ]

    command = [
        'pandoc',
        '$IN',
        '-f',
        '$0',
        '-t',
        'html',
        '-o',
        '$OUT',
    ]

    def get_command(self, in_resource, out_resource):
        extra_args = []
        if in_resource.typestring.extension == 'MD':
            extra_args = ['-f', 'markdown_github']

        return [
            'pandoc',
            in_resource.cache_path,
        ] + extra_args + [
            '-t',
            'html',
            '-o',
            out_resource.cache_path,
        ]
