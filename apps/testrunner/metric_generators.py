import re
from metrics import MetricCollection, Metric, MetricType


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

        metrics = MetricCollection()

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
            'server_time': MetricType.TIME,
            'query_time': MetricType.TIME,
            'query_master': MetricType.COUNT,
            'query_slave': MetricType.COUNT,
            'memc_time': MetricType.TIME,
            'memc_misses': MetricType.COUNT,
            'memc_hits': MetricType.COUNT,
            'memc_dupes': MetricType.COUNT,
        }
        name_template = 'server.app.{}'
        metrics = {
            name: Metric(name_template.format(name), context, type)
            for name, type in metric_defs.items()
        }

        for single_run in data:
            profiler_metrics, profiler_infos = self.parse_data(single_run['profiler_data'])
            for name, raw_value in profiler_metrics.items():
                info = None
                if name == 'query_time':
                    info = profiler_infos['queries']

                metrics[name].add_value(raw_value, info)

        return MetricCollection(metrics.values())

    def parse_data(self, raw_data):
        metrics = {
            'server_time': 0.0,
            'query_time': 0.0,
            'query_master': 0,
            'query_slave': 0,
            'memc_time': 0.0,
            'memc_misses': 0,
            'memc_hits': 0,
            'memc_dupes': 0
        }
        infos = {
            'queries': [],
        }

        for line in raw_data.splitlines():
            match = self.__PROFILER_REGEXP.match(line)

            if match is not None:
                (percent, time, count, name) = match.groups()

                percent = float(percent.strip('%'))
                time = float(time)
                count = int(count)

                if name == '-total':
                    metrics['server_time'] += time
                elif name == 'DatabaseBase::query' or name == 'DatabaseBase::query-master':
                    metrics['query_time'] += time

                    if name == 'DatabaseBase::query-master':
                        metrics['query_master'] += count
                    else:
                        metrics['query_slave'] += count
                elif name == 'MWMemcached::get':
                    metrics['memc_time'] += time
                else:
                    match = self.__MEMCACHE_REGEXP.match(name)

                    if match is not None:
                        memc_type = match.group(1)
                        if memc_type == 'HIT':
                            metrics['memc_hits'] += count
                        elif memc_type == 'MISS':
                            metrics['memc_misses'] += count
                        elif memc_type == 'DUPE':
                            metrics['memc_dupes'] += count

                    match = self.__QUERY_REGEXP.match(name)

                    if match is not None:
                        infos['queries'].append({
                            'statement': match.group(1),
                            'count': count,
                            'time': time,
                        })

        return metrics, infos


class RequestsMetricGenerator(MetricGenerator):
    ACCEPT_GENERATORS = ['python.requests']

    def extract(self, context, data):
        context['origin'] = 'requests'

        metrics = MetricCollection()
        metrics.add(Metric('server.app.response_time', context, MetricType.TIME, values=[
            (float(single_run['headers']['x-backend-response-time']), None)
            for single_run in data
        ]))

        return metrics
