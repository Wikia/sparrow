from collections import defaultdict
import re
import ujson
from metrics import MetricType, Collection, Metric


class MetricGenerator(object):
    ACCEPT_GENERATORS = []

    def __call__(self, metrics, payload):
        generator = payload['generator']
        if generator not in self.ACCEPT_GENERATORS:
            return metrics
        context = payload['context']
        data = payload['data']
        metrics += self.extract(context, data)
        return metrics

    def extract(self, context, data):
        raise NotImplementedError('MetricGenerator does not implement extract()')


class PhantomasMetricGenerator(MetricGenerator):
    ACCEPT_GENERATORS = ['phantomas']

    KNOWN_METRICS = {
        'DOMelementMaxDepth': 'browser.dom.tree.max_depth',
        'DOMelementsCount': 'browser.dom.tree.elements',
        'DOMinserts': 'browser.dom.operations.inserts',
        'DOMqueries': 'browser.dom.operations.queries',
        'ajaxRequests': 'browser.net.ajax.requests',
        'base64Count': 'browser.assets.base64.count',
        'base64Size': 'bytes:browser.assets.base64.size',
        'bodySize': 'bytes:browser.assets.total_size',
        'cssCount': 'browser.assets.css.count',
        'cssSize': 'bytes:browser.assets.css.size',
        'domComplete': 'time:browser.dom.event.complete',
        'domContentLoaded': 'time:browser.dom.event.content_loaded',
        'domContentLoadedEnd': 'time:browser.dom.event.content_loaded.end',
        'domInteractive': 'time:browser.dom.event.interactive',
        'domains': 'browser.net.domains',
        'firstPaint': 'time:browser.dom.event.first_paint',
        'htmlCount': 'browser.assets.html.count',
        'htmlSize': 'bytes:browser.assets.html.size',
        'imageCount': 'browser.assets.image.count',
        'imageSize': 'bytes:browser.assets.image.size',
        'jsCount': 'browser.assets.js.count',
        'jsSize': 'bytes:browser.assets.js.size',
        'jsonCount': 'browser.assets.json.count',
        'jsonSize': 'bytes:browser.assets.json.size',
        'otherCount': 'browser.assets.other.count',
        'otherSize': 'bytes:browser.assets.other.size',
        'repaints': 'browser.screen.repaints',
        'timeToFirstByte': 'time:browser.net.first_byte',
        'timeToFirstCss': 'time:browser.net.first_css',
        'timeToFirstImage': 'time:browser.net.first_image',
        'timeToFirstJs': 'time:browser.net.first_js',
        'timeToLastByte': 'time:browser.net.last_byte',
        'videoCount': 'browser.assets.video.count',
        'videoSize': 'bytes:browser.assets.video.size',
        'webfontCount': 'browser.assets.webfont.count',
        'webfontSize': 'bytes:browser.assets.webfont.size',
    }


    def normalize_phantomas_value(self, s, type):
        if type == 'time':
            # phantomas reports time with millisecond precision whereas we use second as the standard time unit
            s = float(s) / 1000
        return s

    def extract(self, context, data):
        context['origin'] = 'phantomas'

        metrics = Collection()

        if len(data) == 0:
            return metrics

        metric_names = set()
        for run in data:
            metric_names.update(run['metrics'].keys())

        for metric_name in metric_names:
            raw_id = 'raw.phantomas.' + metric_name
            id = raw_id
            type = MetricType.UNKNOWN

            if metric_name in self.KNOWN_METRICS:
                metric_def = self.KNOWN_METRICS[metric_name]
                if ':' in metric_def:
                    type, id = metric_def.split(':')
                else:
                    id = metric_def

            raw_values_and_infos = [
                (
                    self.normalize_phantomas_value(run['metrics'][metric_name], type),
                    run['offenders'][metric_name] if metric_name in run['offenders'] else None
                )
                for run in data
            ]

            metrics.add(Metric(id, context, type, None, raw_values_and_infos))
            if id != raw_id:
                metrics.add(Metric(raw_id, context, type, None, raw_values_and_infos))

        return metrics


class ProfilerMetricGenerator(MetricGenerator):
    ACCEPT_GENERATORS = ['mw_profiler']

    __PROFILER_REGEXP = re.compile(r'^\s*([\d\.]+\%)\s+([\d\.]+)\s+(\d+)\s+\-\s+([^\s].*[^\s])\s*$')
    __MEMCACHE_REGEXP = re.compile(r'MWMemcached::get.*!(HIT|MISS|DUPE)')
    __QUERY_REGEXP = re.compile(r'^\s*query(?:-m)?:\s*(.*)\s*$')

    def extract(self, context, data):
        context['origin'] = 'mw_profiler'

        metric_defs = {
            'response_time': MetricType.TIME,
            'database.queries.list': MetricType.QUERY_LIST,
            'database.queries.time': MetricType.TIME,
            'database.queries.master_count': MetricType.COUNT,
            'database.queries.slave_count': MetricType.COUNT,
            'memcached.time': MetricType.TIME,
            'memcached.miss_count': MetricType.COUNT,
            'memcached.hit_count': MetricType.COUNT,
            'memcached.dupe_count': MetricType.COUNT,
        }

        name_template = 'server.app.{}'
        metrics = {
            name: Metric(name_template.format(name), context, type)
            for name, type in metric_defs.items()
        }

        for single_run in data:
            data = self.parse_data(single_run['content'])
            for name, raw_value in data.items():
                metrics[name].add_value(raw_value, None)

        return Collection(metrics.values())

    def parse_data(self, raw_data):
        out_data = {
            'response_time': 0.0,
            'database.queries.time': 0.0,
            'database.queries.master_count': 0,
            'database.queries.slave_count': 0,
            'memcached.time': 0.0,
            'memcached.miss_count': 0,
            'memcached.hit_count': 0,
            'memcached.dupe_count': 0,
            'database.queries.list': [],
        }

        for line in raw_data.splitlines():
            match = self.__PROFILER_REGEXP.match(line)

            if match is not None:
                (percent, time, count, name) = match.groups()

                percent = float(percent.strip('%'))
                time = float(time)
                count = int(count)

                if name == '-total':
                    out_data['response_time'] += time
                elif name == 'DatabaseBase::query' or name == 'DatabaseBase::query-master':
                    out_data['database.queries.time'] += time

                    if name == 'DatabaseBase::query-master':
                        out_data['database.queries.master_count'] += count
                    else:
                        out_data['database.queries.slave_count'] += count
                elif name == 'MWMemcached::get':
                    out_data['memcached.time'] += time
                else:
                    match = self.__MEMCACHE_REGEXP.match(name)

                    if match is not None:
                        memc_type = match.group(1)
                        if memc_type == 'HIT':
                            out_data['memcached.hit_count'] += count
                        elif memc_type == 'MISS':
                            out_data['memcached.miss_count'] += count
                        elif memc_type == 'DUPE':
                            out_data['memcached.dupe_count'] += count

                    match = self.__QUERY_REGEXP.match(name)

                    if match is not None:
                        out_data['database.queries.list'].append({
                            'statement': match.group(1),
                            'count': count,
                            'time': time,
                        })

        return out_data


class RequestsMetricGenerator(MetricGenerator):
    ACCEPT_GENERATORS = ['python.requests']

    def extract(self, context, data):
        context['origin'] = 'requests'

        metrics = Collection()
        metrics.add(Metric('server.app.response_time', context, MetricType.TIME, values=[
            (float(single_run['time']), None)
            for single_run in data
        ]))

        metrics.add(Metric('server.app.response_size', context, MetricType.BYTES, values=[
            (len(single_run['content']), None)
            for single_run in data
        ]))

        return metrics


class SeleniumMetricGenerator(MetricGenerator):
    ACCEPT_GENERATORS = ['selenium']

    def extract(self, context, data):
        context['origin'] = 'selenium'

        noexternals_context = merge_context(context, {
            'mode': 'noexternals'
        })

        noads_context = merge_context(context, {
            'mode': 'noads'
        })

        anon_search_context = merge_context(context, {
            'scenario': 'anon_visit',
        })
        anon_search_context.pop('url', None)

        user_search_context = merge_context(context, {
            'scenario': 'user_visit',
        })
        user_search_context.pop('url', None)

        context['mode'] = 'default'

        metrics = Collection()

        types = [
            # (noexternals_context, 'oasis_perftest_medium_article_no_externals'),
            # (noads_context, 'oasis_perftest_medium_article_no_ads'),
            (context, 'load_provided_url'),
        ]
        metric_defs = [
            ('browser.transaction.time', MetricType.TIME, 'total_load_time'),
            ('browser.dom.event.interactive', MetricType.TIME, 'interactive_time'),
            ('browser.dom.event.content_loaded', MetricType.TIME, 'dom_content_loaded_time'),
            ('browser.dom.event.complete', MetricType.TIME, 'dom_complete_time'),
        ]
        for test_context, test_name in types:
            for out_name, data_type, in_name in metric_defs:
                self.fan_out_by_url_and_push_metrics(
                    metrics, out_name, context, data_type,
                    values=self.metric_values_single_step_with_urls(data, test_name, in_name))
        # total time
        # metrics.add(Metric(
        #     'browser.transaction.time', anon_search_context, MetricType.TIME,
        #     values=self.total_load_time_all_steps(data, 'perftest_oasis_anon_search_pageviews')))
        # metrics.add(Metric(
        #     'browser.transaction.time', user_search_context, MetricType.TIME,
        #     values=self.total_load_time_all_steps(data, 'perftest_oasis_user_search_pageviews')))

        return metrics

    @staticmethod
    def fan_out_by_url_and_push_metrics(metrics, out_name, base_context, data_type, values):
        by_url = defaultdict(list)
        for url, value in values:
            by_url[url].append(value)

        for url, values in by_url.items():
            context = base_context.copy()
            context['url'] = url
            metrics.add(Metric(out_name, context, data_type, values=values))

    @staticmethod
    def metric_values_single_step_with_urls(selenium_results, test_name, metric):
        return [(x['result']['steps'][0]['url'], (x['result']['steps'][0][metric], None)) for x in
                selenium_results[test_name]]

    @staticmethod
    def total_load_time_all_steps(selenium_results, test_name):
        return [(x['result']['total_load_time'], None) for x in selenium_results[test_name]]


def merge_context(*contexts):
    x = {}
    for context in contexts:
        x.update(context)
    return x