# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase
from common import media_wiki_tools


class TestResultTestCase(APITestCase):

    def test_get_hostname_from_url(self):
        self.assertEqual(media_wiki_tools.get_hostname_from_url('http://muppet.wikia.com/page?noexternals=1'), 'wikia.com', 'Invalid hostname')
        self.assertEqual(media_wiki_tools.get_hostname_from_url('http://muppet.synth1.wikia-dev.com/page?noexternals=1'), 'synth1.wikia-dev.com', 'Invalid hostname')
        try:
            media_wiki_tools.get_hostname_from_url('invalidurl')
            self.fail('Expected exception was not thrown')
        except Exception:
            pass
