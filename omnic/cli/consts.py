SETTINGS_PY = '''
##### Web server settings

HOST = '127.0.0.1'
PORT = 8080
DEBUG = True


##### Security settings

# Whitelist allowed foreign hosts. This should point to your app servers, your
# CDN, or cloud hosting such as your S3 buckets.
ALLOWED_LOCATIONS = {
    'localhost', '127.0.0.1',
    # Example: 'media.mysite.com', 's3-media.mysite.com'
}


##### Conversion settings

# Conversion graph settings
CONVERSION_PROFILES = {
    # Add in profiles here, like the following:
    # 'media-gallery-thumb.png': ('PNG', 'thumb.png:300x300'),
}

# Where to store cache
PATH_PREFIX = '/var/tmp/omnic/'
'''


CLI_HELP_EPILOG_TEMPLATE = '''

available subcommands:
%s
'''
