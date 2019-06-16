import hmac

from omnic import singletons
from omnic.types.resource import ForeignResource
from omnic.utils.security import get_hmac_sha1_digest


class SecurityException(Exception):
    pass


class InvalidDigestException(SecurityException):
    pass


class InvalidQueryDataException(SecurityException):
    pass


class SecurityChecker:
    async def rewrite(self, request):
        return request.path

    async def check(self, typestring, querydata):
        pass


class DummySecurity(SecurityChecker):
    pass


class HmacSha1(SecurityChecker):
    '''
    Built-in HMAC SHA1 security checker
    '''
    async def check(self, typestring, querydata):
        if 'url' not in querydata:
            raise InvalidQueryDataException('URL missing')
        if 'digest' not in querydata:
            raise InvalidQueryDataException('digest missing')

        url_string = querydata['url'][0]
        supplied_digest = querydata['digest'][0]
        correct_digest = get_hmac_sha1_digest(
            singletons.settings.HMAC_SECRET,
            url_string,
            typestring,
        )

        if not hmac.compare_digest(supplied_digest.lower(), correct_digest):
            raise InvalidDigestException(
                'Incorrect digest supplied: ' + correct_digest)


async def check(typestring, querydata):
    if singletons.settings.SECURITY is not None:
        checker_class = singletons.settings.load('SECURITY')
    else:
        checker_class = DummySecurity
    checker = checker_class()
    await checker.check(typestring, querydata)
    url_string = querydata['url'][0]
    foreign_res = ForeignResource(url_string)
    foreign_res.validate()


async def rewrite_middleware(server, request):
    '''
    Sanic middleware that utilizes a security class's "rewrite" method to
    check
    '''
    if singletons.settings.SECURITY is not None:
        security_class = singletons.settings.load('SECURITY')
    else:
        security_class = DummySecurity
    security = security_class()
    try:
        new_path = await security.rewrite(request)
    except SecurityException as e:
        msg = ''
        # if DEBUG:
        #    msg = str(e)
        return server.response.text(msg, status=400)
    request.path = new_path
