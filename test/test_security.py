"""
Tests for `security` module.
"""

import pytest

from omnic.config.utils import use_settings
from omnic.web.security import Hmac

normalized_settings = dict(
    hmac_secret='dummy_secret',
)

class TestHmacSec:
    @pytest.mark.asyncio
    async def test_check(self):
        hm = Hmac()
        with use_settings(**normalized_settings):
            await hm.check('asdf', {
                'url': ['http://whatevs.com/stuff.png'],
                'digest': ['a40246fdaa7e7201be545306f80a9e11'],
            })

