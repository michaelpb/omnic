import hmac

from omnic import singletons
from omnic.utils.security import get_hmac_sha1_digest
from omnic.types.resource import ForeignResource

class SecurityException(Exception):
    pass

class InvalidDigestException(SecurityException):
    pass

class InvalidQueryDataException(SecurityException):
    pass

class SecurityChecker:
    pass

class DummySecurity(SecurityChecker):
    async def check(self, typestring, querydata):
        pass

# Simple built-in hmac request checker
class HmacSha1(SecurityChecker):
    async def check(self, typestring, querydata):
        if 'url' not in querydata:
            raise InvalidQueryDataException('URL missing')
        if 'digest' not in querydata:
            raise InvalidQueryDataException('digest missing')

        url_string = querydata.get('url')[0]
        supplied_digest = querydata.get('digest')[0]
        correct_digest = get_hmac_sha1_digest(
            singletons.settings.HMAC_SECRET,
            url_string,
            typestring,
        )

        if not hmac.compare_digest(supplied_digest.lower(), correct_digest):
            raise InvalidDigestException('Incorrect digest supplied: ' + correct_digest)

async def check(typestring, querydata):
    if singletons.settings.SECURITY is not None:
        checker_class = singletons.settings.load('SECURITY')
    else:
        checker_class = DummySecurity
    checker = checker_class()
    url_string = querydata['url'][0]
    foreign_res = ForeignResource(url_string)
    foreign_res.validate()  # TODO move domain checks into this module
    await checker.check(typestring, querydata)

