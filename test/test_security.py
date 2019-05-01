"""
Tests for `security` module.
"""

from unittest.mock import MagicMock

import pytest

from omnic.config.utils import use_settings
from omnic.web import security

normalized_settings = dict(
    hmac_secret='dummy_secret',
    security='omnic.web.security.HmacSha1',
    allowed_locations={'whatevs.com'},
)


class TestHmacSha1Security:
    @pytest.mark.asyncio
    async def test_check(self):
        hm = security.HmacSha1()
        with use_settings(**normalized_settings):
            await hm.check('JPG', {
                'url': ['http://whatevs.com/stuff.png'],
                'digest': ['6d2a1495209af2d193affbb485d309a2e15bc5b1'],
            })

            # ensure case in-sensitivity and normalization of URL
            await hm.check('JPG', {
                'url': ['whatevs.com/stuff.png'],
                'digest': ['6D2A1495209AF2d193affBB485D309A2E15bc5b1'],
            })

    @pytest.mark.asyncio
    async def test_check_exceptions(self):
        hm = security.HmacSha1()
        with use_settings(**normalized_settings):
            with pytest.raises(security.SecurityException):
                await hm.check('JPG', {
                    'url': ['http://whatevs.com/stuff.png'],
                    'digest': ['a40246fdaa7e7201be545306f80a9e11'],
                })

            with pytest.raises(security.SecurityException):
                await hm.check('JPG', {
                    'url': ['http://whatevs.com/stuff.png'],
                })

            with pytest.raises(security.SecurityException):
                await hm.check('JPG', {
                    'digest': ['6d2a1495209af2d193affbb485d309a2e15bc5b1'],
                })


class TestSecurity:
    @pytest.mark.asyncio
    async def test_check(self):
        with use_settings(**normalized_settings):
            await security.check('JPG', {
                'url': ['http://whatevs.com/stuff.png'],
                'digest': ['6d2a1495209af2d193affbb485d309a2e15bc5b1'],
            })

    @pytest.mark.asyncio
    async def test_rewrite_middleware(self):
        with use_settings(**normalized_settings):
            mock_request = MagicMock()
            mock_request.path = '/stuff.png'
            server = MagicMock()
            ret_val = await security.rewrite_middleware(server, mock_request)
            assert mock_request.path == '/stuff.png'
            assert ret_val == None
