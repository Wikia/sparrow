# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from phantomas.results import Results
from phantomas.results import Runs


class PhantomasMock(object):

    def __init__(self, url, **kwargs):
        self._url = url
        self._runs = kwargs['runs']

    @classmethod
    def __generate_result(cls):
        return {
            'generator': 'phantomas v1.10.2',
            'metrics': {
                'DOMelementMaxDepth': 19, 'DOMelementsCount': 885, 'DOMidDuplicated': 0, 'DOMinserts': 98,
                'DOMmutationsAttributes': 0, 'DOMmutationsInserts': 0, 'DOMmutationsRemoves': 0, 'DOMqueries': 460,
                'DOMqueriesAvoidable': 237, 'DOMqueriesByClassName': 45, 'DOMqueriesById': 184,
                'DOMqueriesByQuerySelectorAll': 36, 'DOMqueriesByTagName': 195, 'DOMqueriesDuplicated': 65,
                'DOMqueriesWithoutResults': 103, 'ajaxRequests': 5, 'assetsNotGzipped': 7, 'assetsWithCookies': 67,
                'assetsWithQueryString': 54, 'base64Count': 13, 'base64Size': 6932, 'biggestLatency': 1827,
                'biggestResponse': 303810, 'bodyHTMLSize': 99709, 'bodySize': 1304562, 'cacheHits': 14,
                'cacheMisses': 46, 'cachePasses': 0, 'cachingDisabled': 40, 'cachingNotSpecified': 5,
                'cachingTooShort': 14, 'closedConnections': 1, 'commentsSize': 1665, 'consoleMessages': 2,
                'contentLength': 1922742, 'cookiesRecv': 9990, 'cookiesSent': 0, 'cssCount': 5, 'cssSize': 141514,
                'documentCookiesCount': 11, 'documentCookiesLength': 519, 'documentHeight': 4466,
                'documentWriteCalls': 3, 'domComplete': 3234, 'domContentLoaded': 2572, 'domContentLoadedEnd': 2732,
                'domInteractive': 2572, 'domains': 56, 'domainsWithCookies': 35, 'evalCalls': 0, 'eventsBound': 140,
                'eventsDispatched': 0, 'eventsScrollBound': 3, 'fastestResponse': 31, 'firstPaint': 0,
                'globalVariables': 361, 'globalVariablesFalsy': 38, 'gzipRequests': 43, 'headersBiggerThanContent': 57,
                'headersCount': 2087, 'headersRecvCount': 1672, 'headersRecvSize': 72731, 'headersSentCount': 415,
                'headersSentSize': 22620, 'headersSize': 95351, 'hiddenContentSize': 47261, 'htmlCount': 15,
                'htmlSize': 124541, 'httpTrafficCompleted': 5460, 'httpsRequests': 18, 'iframesCount': 12,
                'imageCount': 55, 'imageSize': 724272, 'imagesScaledDown': 0, 'imagesWithoutDimensions': 16,
                'jQueryDOMReads': 115, 'jQueryDOMWriteReadSwitches': 25, 'jQueryDOMWrites': 53,
                'jQueryEventTriggers': 43, 'jQueryOnDOMReadyFunctions': 45, 'jQuerySizzleCalls': 78,
                'jQueryVersion': '1.8.2', 'jQueryVersionsLoaded': 1, 'jQueryWindowOnLoadFunctions': 4,
                'jsCount': 39, 'jsErrors': 0, 'jsSize': 927221, 'jsonCount': 2, 'jsonSize': 5189,
                'localStorageEntries': 35, 'maxRequestsPerDomain': 12, 'medianLatency': 234,
                'medianRequestsPerDomain': 1, 'medianResponse': 227, 'multipleRequests': 0,
                'nodesWithInlineCSS': 59, 'notFound': 0, 'oldCachingHeaders': 91, 'otherCount': 19, 'otherSize': 5,
                'postRequests': 0, 'redirects': 26, 'redirectsTime': 3659, 'repaints': 0, 'requests': 135,
                'requestsToDomComplete': 83, 'requestsToDomContentLoaded': 63, 'slowestResponse': 2005,
                'smallCssFiles': 2, 'smallImages': 40, 'smallJsFiles': 13, 'smallestLatency': 21,
                'smallestResponse': 35, 'statusCodesTrail': '200', 'timeBackend': 29, 'timeFrontend': 71,
                'timeToFirstByte': 1303, 'timeToFirstCss': 2206, 'timeToFirstImage': 2513, 'timeToFirstJs': 2205,
                'timeToLastByte': 1321, 'videoCount': 0, 'videoSize': 0, 'webfontCount': 0, 'webfontSize': 0,
                'whiteSpacesSize': 8841, 'windowAlerts': 0, 'windowConfirms': 0, 'windowPrompts': 0,
            },
            'offenders': {},
        }

    def run(self):
        if self._runs > 1:
            return Runs(
                url=self._url,
                data={
                    'runs': [self.__generate_result() for _ in range(self._runs)],
                    'stats': [],
                }
            )

        return Results(self._url, data=self.__generate_result())
