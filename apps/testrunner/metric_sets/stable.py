from metrics.queries import Query
from metrics.values import Stats


class StableMetricSet(object):
    def __init__(self, collection):
        self.collection = collection

        url = self.find_url()

        # database
        self.master_queries_count = self.get_stats(
            id='server.app.database.queries.master_count',
            origin='mw_profiler'
        )
        self.slave_queries_count = self.get_stats(
            id='server.app.database.queries.slave_count',
            origin='mw_profiler'
        )

        # page size
        self.css_size = self.get_stats(
            id='browser.assets.css.size',
            origin='phantomas'
        )

        self.html_size = self.get_stats(
            id='browser.assets.html.size',
            origin='phantomas'
        )

        self.js_size =  self.get_stats(
            id='browser.assets.js.size',
            origin='phantomas'
        )
        self.ajax_requests = self.get_stats(
            id='browser.net.ajax.requests',
            origin='phantomas'
        )


        # DOM events
        self.dom_interactive_phantomas = self.get_stats(
            id='browser.dom.event.interactive',
            origin='phantomas'
        )
        self.dom_complete_phantomas = self.get_stats(
            id='browser.dom.event.complete',
            origin='phantomas'
        )
        self.dom_complete_selenium = self.get_stats(
            id='browser.dom.event.complete',
            origin='selenium',
            mode='default',
            url=url,
        )

        # DOM operations
        self.dom_inserts = self.get_stats(
            id='browser.dom.operations.inserts',
            origin='phantomas'
        )
        self.dom_queries = self.get_stats(
            id='browser.dom.operations.queries',
            origin='phantomas'
        )
        self.dom_queries_by_query_selector_all = self.get_stats(
            id='raw.phantomas.DOMqueriesByQuerySelectorAll',
            origin='phantomas'
        )
        self.dom_duplicated_queries = self.get_stats(
            id='raw.phantomas.DOMqueriesDuplicated',
            origin='phantomas'
        )

        # DOM event bindings
        self.dom_events_bound = self.get_stats(
            id='raw.phantomas.eventsBound',
            origin='phantomas'
        )
        self.dom_scroll_events_bound = self.get_stats(
            id='raw.phantomas.eventsScrollBound',
            origin='phantomas'
        )

        # time
        self.response_time_requests = self.get_stats(
            id='server.app.response_time',
            origin='requests'
        )

        self.items = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Stats):
                self.items[k] = v

    def get_stats(self, group_by=None, **kwargs):
        q = Query()
        for k, v in kwargs.items():
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
