# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urlparse


def get_hostname_from_url(url):

    domain = urlparse(url)[1]
    pos = domain.find('.')
    if pos > -1:
        return domain[pos + 1:]
    else:
        raise Exception('Invalid media wiki url provided: ' + url)