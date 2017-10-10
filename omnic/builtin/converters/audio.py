from omnic.conversion import converter


class FfmpegAudioWaveformRenderer(converter.ExecConverter):
    inputs = [
        'MPGA',
        'MPEGA',
        'MP2',
        'MP3',
        'M4A',
        'OGA',
        'OGG',
        'OPUS',
        'SPX',

        'audio/ogg',
        'audio/mpeg',
    ]

    outputs = [
        'PNG',
    ]

    command = [
        'ffmpeg',
        '-i',
        '$IN',
        '-filter_complex',
        'compand,showwavespic=s=640x240:colors=SlateGray|SteelBlue',
        '-frames:v',
        '1',
        '-y',
        '$OUT',
    ]

class SoxAudioSpectrogramRenderer(converter.ExecConverter):
    inputs = [
        'OGA',
        'OGG',
        'OPUS',
        'SPX',

        'audio/ogg'
    ]

    outputs = [
        'JPG',
        'PNG',
    ]

    command = [
        'sox',
        '$IN',
        '-n',
        'spectrogram',
        '-Y',
        '500',
        '-l',
        '-w',
        'Kaiser',
        '-a',
        '-r',
        '-o',
        '$OUT',
    ]
