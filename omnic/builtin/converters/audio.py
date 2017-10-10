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
        'FLAC',
        'RA',
        'WAV',

        'audio/ogg',
        'audio/mp4a-latm',
        'audio/mpa-robust',
        'audio/mpeg',
        'audio/flac',
        'audio/x-realaudio',
        'audio/x-flac',
        'audio/x-wav',
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
