from urllib.parse import urlencode

from omnic.types.resourceurl import ResourceURL
from omnic.types.typestring import TypeString
from omnic.utils.security import get_hmac_sha1_digest
from omnic import singletons


def reverse_media_url(target_type, url_string, *args, **kwargs):
    '''
    Given a target type and an resource URL, generates a valid URL to this via
    '''
    args_str = '<%s>' % '><'.join(args)
    kwargs_str = '<%s>' % '><'.join('%s:%s' % pair for pair in kwargs.items())
    url_str = ''.join([url_string, args_str, kwargs_str])
    normalized_url = str(ResourceURL(url_str))

    query_tuples = []

    if singletons.settings.SECURITY and 'Sha1' in singletons.settings.SECURITY:
        secret = singletons.settings.HMAC_SECRET
        digest = get_hmac_sha1_digest(secret, normalized_url, target_type)
        query_tuples.append(('digest', digest))

    # Add in URL as last querystring argument
    query_tuples.append(('url', normalized_url))

    querystring = urlencode(query_tuples)
    scheme = singletons.settings.EXTERNAL_SCHEME
    host = singletons.settings.EXTERNAL_HOST
    port = singletons.settings.EXTERNAL_PORT
    if not host:
        host = singletons.settings.HOST
    if not port:
        port = singletons.settings.PORT

    port_suffix = ':%s' % port if port != 80 else ''

    typestring_normalized = str(TypeString(target_type))
    return '%s://%s%s/media/%s/?%s' % (
        scheme,
        host,
        port_suffix,
        typestring_normalized,
        querystring,
    )


