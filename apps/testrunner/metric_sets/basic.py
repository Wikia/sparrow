from metrics.queries import Query
from metrics.values import Stats


class BasicMetricSet(object):
    def __init__(self, collection):
        self.collection = collection

        url = self.find_url()

        # from phantomas
        self.first_paint_phantomas = self.get_stats({
            'id': 'browser.dom.event.first_paint',
            'origin': 'phantomas'
        })
        self.dom_interactive_phantomas = self.get_stats({
            'id': 'browser.dom.event.interactive',
            'origin': 'phantomas'
        })
        self.dom_content_loaded_phantomas = self.get_stats({
            'id': 'browser.dom.event.content_loaded',
            'origin': 'phantomas'
        })
        self.dom_complete_phantomas = self.get_stats({
            'id': 'browser.dom.event.complete',
            'origin': 'phantomas'
        })
        self.page_size_phantomas = self.get_stats({
            'id': 'browser.assets.total_size',
            'origin': 'phantomas'
        })

        # from python.requests
        self.html_size_requests = self.get_stats({
            'id': 'server.app.response_size',
            'origin': 'requests'
        })
        self.response_time_requests = self.get_stats({
            'id': 'server.app.response_time',
            'origin': 'requests'
        })

        # from selenium
        self.dom_interactive_selenium = self.get_stats({
            'id': 'browser.dom.event.interactive',
            'origin': 'selenium',
            'mode': 'default',
            'url': url,
        })
        self.dom_content_loaded_selenium = self.get_stats({
            'id': 'browser.dom.event.content_loaded',
            'origin': 'selenium',
            'mode': 'default',
            'url': url,
        })
        self.dom_complete_selenium = self.get_stats({
            'id': 'browser.dom.event.complete',
            'origin': 'selenium',
            'mode': 'default',
            'url': url,
        })

        # from mw profiler
        self.response_time_mw_profiler = self.get_stats({
            'id': 'server.app.response_time',
            'origin': 'mw_profiler'
        })

        self.items = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Stats):
                self.items[k] = v

    def get_stats(self, where, group_by=None):
        q = Query()
        for k, v in where.items():
            q.where_eq(k, v)
        map(q.group_by, group_by or [])

        result_set = q.execute(self.collection)
        results = list(result_set)
        if len(results) != 1:
            print(results)
            raise ValueError('Sanity check failed, number of results is not 1')

        """ :type result: Result """
        result = results[0]
        return result.stats

    def find_url(self):
        result_set = (
            Query()
            .where_eq('origin','phantomas')
            .where_eq('id','browser.assets.total_size')
        ).execute(self.collection)

        results = list(result_set)
        if len(results) != 1:
            raise ValueError('Found more than one result when looking for main URL')

        result = results[0]
        return result.context['url']
