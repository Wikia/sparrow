# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools

from django.conf import settings


def camel2snake(text):
    """ Converts a CamelCase name into an under_score name.

        >>> camel2snake('CamelCase')
        'camel_case'
        >>> camel2snake('getHTTPResponseCode')
        'get_http_response_code'
    """
    result = []
    pos = 0

    while pos < len(text):
        if text[pos].isupper():
            if (
                pos - 1 > 0 and text[pos - 1].islower() or
                pos - 1 > 0 and pos + 1 < len(text) and text[pos + 1].islower()
            ):
                result.append("_%s" % text[pos].lower())
            else:
                result.append(text[pos].lower())
        else:
            result.append(text[pos])

        pos += 1

    return "".join(result)


def collect_results(func, count, error_limit=3):
    results = []
    consecutive_errors = 0
    while len(results) < count:
        try:
            result = func()
            if not result:
                raise ValueError('Result evaluates to false: {}'.format(result))
            consecutive_errors = 0
            results.append(result)
        except:
            consecutive_errors += 1
            if consecutive_errors >= error_limit:
                raise
    return results


def build_absolute_uri(uri):
    return settings.API_SERVER_URL + uri


def cached_property(f):
    """returns a cached property that is calculated by function f"""

    @functools.wraps(f)
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x

    return property(get)
