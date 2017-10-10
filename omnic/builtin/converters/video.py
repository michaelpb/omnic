from omnic.conversion import converter


class FfmpegThumbnailer(converter.ExecConverter):
    inputs = [
        'FLV',
        'WEBM',
        'OGV',
        'MOV',
        'MP4',
        'TS',
        'FLI',
        'DL',
        'AXV',
        '3GP',
        'QT',
        'MPEG',
        'MPG',
        'MPE',
        'LSF',
        'LSX',
        'ASF',
        'ASX',
        'WMV',
        'WMX',
        'WVX',
        'AVI',
        'MOVIE',
        'MPV',
        'MKV',
        'video/3gpp',
        'video/annodex',
        'video/dl',
        'video/fli',
        'video/mpeg',
        'video/MP2T',
        'video/mp4',
        'video/quicktime',
        'video/mp4v-es',
        'video/ogg',
        'video/webm',
        'video/x-flv',
        'video/x-la-asf',
        'video/x-ms-asf',
        'video/x-ms-wmv',
        'video/x-ms-wmx',
        'video/x-ms-wvx',
        'video/x-msvideo',
        'video/x-sgi-movie',
        'video/x-matroska',
    ]

    outputs = [
        'JPG',
        'PNG',
    ]

    command = [
        'ffmpegthumbnailer',
        '-s',
        '0',
        '-i',
        '$IN',
        '-o',
        '$OUT',
    ]
