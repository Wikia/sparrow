import re
from metrics import Collection, Metric, MetricType


class MetricGenerator(object):
    ACCEPT_GENERATORS = []

    def __call__(self, metrics, payload):
        generator = payload['generator']
        if generator not in self.ACCEPT_GENERATORS:
            return metrics
        context = payload['context'].copy()
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
        'base64Size': 'size:browser.assets.base64.size',
        'cssCount': 'browser.assets.css.count',
        'cssSize': 'size:browser.assets.css.size',
        'domComplete': 'time:browser.dom.event.complete',
        'domContentLoaded': 'time:browser.dom.event.content_loaded',
        'domContentLoadedEnd': 'time:browser.dom.event.content_loaded.end',
        'domInteractive': 'time:browser.dom.event.interactive',
        'domains': 'browser.net.domains',
        'firstPaint': 'browser.dom.event.first_paint',
        'htmlCount': 'browser.assets.html.count',
        'htmlSize': 'size:browser.assets.html.size',
        'imageCount': 'browser.assets.image.count',
        'imageSize': 'time:browser.assets.image.size',
        'jsCount': 'browser.assets.js.count',
        'jsSize': 'size:browser.assets.js.size',
        'jsonCount': 'browser.assets.json.count',
        'jsonSize': 'size:browser.assets.json.size',
        'otherCount': 'browser.assets.other.count',
        'otherSize': 'size:browser.assets.other.size',
        'repaints': 'browser.screen.repaints',
        'timeToFirstByte': 'time:browser.net.first_byte',
        'timeToFirstCss': 'time:browser.net.first_css',
        'timeToFirstImage': 'time:browser.net.first_image',
        'timeToFirstJs': 'time:browser.net.first_js',
        'timeToLastByte': 'time:browser.net.last_byte',
        'videoCount': 'browser.assets.video.count',
        'videoSize': 'size:browser.assets.video.size',
        'webfontCount': 'browser.assets.webfont.count',
        'webfontSize': 'size:browser.assets.webfont.size',
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

        name_template = 'mediawiki.{}'
        metrics = {
            name: Metric(name_template.format(name), context, type)
            for name, type in metric_defs.items()
        }

        for single_run in data:
            data = self.parse_data(single_run['profiler_data'])
            for name, raw_value in data.items():
                metrics[name].add_value(data, None)

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
            (float(single_run['headers']['x-backend-response-time']), None)
            for single_run in data
        ]))

        return metrics


class SeleniumMetricGenerator(MetricGenerator):
    ACCEPT_GENERATORS = ['selenium']

    def extract(self, context, data):
        context['origin'] = 'selenium'

        noexternals_context = merge_context(context,{
            'mode': 'noexternals'
        })

        noads_context = merge_context(context,{
            'mode': 'noads'
        })

        anon_search_context = merge_context(context,{
            'scenario': 'search',
            'user': 'anon'
        })

        user_search_context = merge_context(context,{
            'scenario': 'search',
            'user': 'user'
        })

        metrics = Collection()
        # noexternals
        metrics.add(Metric(
            'browser.dom.event.load', noexternals_context, MetricType.TIME,
            values=self.metric_values_single_step(
                data, 'oasis_perftest_medium_article_no_externals', 'total_load_time')))
        metrics.add(Metric(
            'browser.dom.event.complete', noexternals_context, MetricType.TIME,
            values=self.metric_values_single_step(
                data, 'oasis_perftest_medium_article_no_externals', 'dom_complete_time')))
        # noads
        metrics.add(Metric(
            'browser.dom.event.load', noads_context, MetricType.TIME,
            values=self.metric_values_single_step(
                data, 'oasis_perftest_medium_article_no_ads', 'total_load_time')))
        metrics.add(Metric(
            'browser.dom.event.complete', noads_context, MetricType.TIME,
            values=self.metric_values_single_step(
                data, 'oasis_perftest_medium_article_no_ads', 'dom_complete_time')))

        metrics.add(Metric(
            'browser.dom.event.complete', noads_context, MetricType.TIME,
            values=self.metric_values_single_step(
                data, 'oasis_perftest_medium_article_no_ads', 'dom_complete_time')))
        # total time
        metrics.add(Metric(
            'browser.transaction.time', anon_search_context, MetricType.TIME,
            values=self.total_load_time_all_steps(data, 'perftest_oasis_anon_search_pageviews')))
        metrics.add(Metric(
            'browser.transaction.time', user_search_context, MetricType.TIME,
            values=self.total_load_time_all_steps(data, 'perftest_oasis_user_search_pageviews')))

        return metrics

    @staticmethod
    def metric_values_single_step(selenium_results, test_name, metric):
        return [x['result']['steps'][0][metric] for x in selenium_results[test_name]]

    @staticmethod
    def total_load_time_all_steps(selenium_results, test_name):
        return [x['result']['total_load_time'] for x in selenium_results[test_name]]

def merge_context(*contexts):
    x = {}
    for context in contexts:
        x.update(context)
    return x