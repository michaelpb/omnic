import hmac
import hashlib

from omnic.types.typestring import TypeString
from omnic.types.resourceurl import ResourceURL

def get_hmac_sha1_digest(secret, resource_url, target_type, api_key=None):
    '''
    Utilize hmac module to hash a secret, a string specifying a resource URL,
    and a string specifying a target type into a (string) hex digest.
    '''
    # Normalize and sanitize input resource URL and target type, and then
    # convert to bytes
    target_type_bytes = str(TypeString(target_type)).encode('utf8')
    resource_url_bytes = str(ResourceURL(resource_url)).encode('utf8')

    # Create new hmac digest, optionally including an optional public api key
    hm = hmac.new(secret.encode('utf8'), digestmod=hashlib.sha1)
    if api_key:
        hm.update(api_key.encode('utf8'))
    hm.update(target_type_bytes)
    hm.update(resource_url_bytes)
    return hm.hexdigest()

