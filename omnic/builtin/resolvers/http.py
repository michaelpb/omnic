
from omnic.conversion import converter


class CurlDownloader(converter.ExecConverter):
    inputs = [
        'http',
        'https',
    ]

    outputs = [
        'file',
    ]

    @classmethod
    def get_destination_type(cls, resource_url):
        scheme = resource_url.parsed.scheme
        if scheme in cls.inputs:
            return 'file'

    def get_command(self, in_resource, out_resource):
        resource_url = in_resource.url
        return [
            'curl',
            '-L',  # follow redirects
            '--silent',
            '--output',
            out_resource.cache_path,
            resource_url.url,
        ]
