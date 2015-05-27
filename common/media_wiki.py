# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class MWUrlGenerator(object):
    """ Common class for generating MW Urls"""

    @staticmethod
    def get_wiki_base_url(hostname, wikiname):
        return 'http://{0}.{1}.wikia-dev.com'.format(wikiname, hostname)
