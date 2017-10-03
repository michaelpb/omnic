from omnic import singletons
from omnic.utils.security import get_hmac_digest

class SecurityChecker:
    pass

# Simple built-in hmac request checker
class Hmac(SecurityChecker):
    async def check(self, typestring, querydata):
        if 'url' not in querydata:
            # TODO replace with proper 500 causing error
            raise ValueError('Invalid querystring: no url')
        if 'digest' not in querydata:
            # TODO replace with proper 500 causing error
            raise ValueError('Invalid querystring: no digest')

        url_string = querydata.get('url')[0]
        supplied_digest = querydata.get('digest')[0]
        correct_digest = get_hmac_digest(
            singletons.settings.HMAC_SECRET,
            url_string,
            typestring,
        )

        if supplied_digest != correct_digest:
            raise Exception('Invalid digest, expected: '+ correct_digest)

