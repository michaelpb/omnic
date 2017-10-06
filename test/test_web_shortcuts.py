"""
Tests for `web.shortcuts` module.
"""
import tempfile
from os.path import islink, join

import pytest

from omnic.web import shortcuts

from unittest.mock import call, mock_open, patch

import pytest

from omnic.config.utils import use_settings
from omnic.conversion import resolver
from omnic.types.resourceurl import ResourceURL

settings = dict(
    host='testhost.com',
    port=80,
    external_port=None,
    external_host=None,
    external_scheme='http',
    security='omnic.web.security.HmacSha1',
    hmac_secret='dummy_secret',
    allowed_locations={'whatevs.com'},
)

external_settings = dict(settings)
external_settings.update(dict(
    external_port=8080,
    external_scheme='https',
    external_host='sillyplace.com',
))


no_sec_settings = dict(settings)
no_sec_settings.update(dict(
    security=None,
    hmac_secret=None,
))


class TestUrlShortcuts:
    @use_settings(**settings)
    def test_simple_case(self):
        url = 'whatevs.com/stuff.png'
        ts = 'JPG'
        digest = '6d2a1495209af2d193affbb485d309a2e15bc5b1'
        result_url = shortcuts.reverse_media_url(ts, url)
        assert result_url == ('http://testhost.com/media/JPG/' +
            '?digest=%s' % digest +
            '&url=http%3A%2F%2Fwhatevs.com%2Fstuff.png'
        )

    @use_settings(**external_settings)
    def test_external_settings(self):
        url = 'whatevs.com/stuff.png'
        ts = 'JPG'
        digest = '6d2a1495209af2d193affbb485d309a2e15bc5b1'
        result_url = shortcuts.reverse_media_url(ts, url)
        assert result_url == ('https://sillyplace.com:8080/media/JPG/' +
            '?digest=%s' % digest +
            '&url=http%3A%2F%2Fwhatevs.com%2Fstuff.png'
        )

    @use_settings(**no_sec_settings)
    def test_without_digest(self):
        url = 'whatevs.com/stuff.png'
        ts = 'thumb.png:200x200'
        result_url = shortcuts.reverse_media_url(ts, url)
        assert result_url == ('http://testhost.com/media/thumb.png:200x200/' +
            '?url=http%3A%2F%2Fwhatevs.com%2Fstuff.png'
        )

