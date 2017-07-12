class ConversionError(Exception):
    pass


class ConversionInputError(ConversionError):
    pass


class ConversionProcessError(ConversionError):
    pass


class ConversionOutputError(ConversionError):
    pass


class ConverterUnavailable(Exception):
    pass
