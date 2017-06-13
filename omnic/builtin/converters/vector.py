from omnic.conversion import converter


class InkscapeConverter(converter.ExecConverter):
    inputs = [
        'SVGZ',
        'DIA',
        'AI',
        'WPF',
        'WPM',
        'SK1',
        'PLT',
        'OUTLINE',

        'image/svg+xml'
    ]

    outputs = [
        'SVG',
    ]

    command = [
        'inkscape',
        '-z',
        '-f',
        '$IN',
        '-l',  # means: Export plain SVG
        '$OUT',
    ]


class InkscapeRasterizer(converter.ExecConverter):
    inputs = [
        'SVG',
        'image/svg+xml'
    ]

    outputs = [
        'PNG',
    ]

    command = [
        'inkscape',
        '-z',
        '-f',
        '$IN',
        '-e',  # means: Export PNG
        '$OUT',
    ]
