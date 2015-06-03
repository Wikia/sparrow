from common.utils import camel2snake


class MetricType:
    UNKNOWN = 'unknown'
    TIME = 'time'
    SIZE = 'size'
    COUNT = 'count'


class Metric(object):
    def __init__(self, origin_id, id, type, context, meta, data, extra):
        self.origin_id = origin_id
        self.id = id
        self.type = type
        self.context = context
        self.meta = meta
        self.data = data
        self.extra = extra

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<Metric: {} data={}>'.format(self.id, self.data)


KNOWN_PHANTOMAS_METRICS = {
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


def normalize_phantomas_metric_name(s):
    if s.startswith('DOM'):
        s = s[0:3] + s[3].upper() + s[4:]
    return camel2snake(s)

def normalize_phantomas_value(s, type):
    if type == 'time':
        s = float(s) / 1000
    return s


def get_phantomas_metrics(results):
    if len(results) == 0:
        return []

    context = {
        'url': '',  # need to get it from somewhere
    }
    meta = {
        'origin': 'phantomas',
    }
    metric_names = set()
    for run in results:
        metric_names.update(run['metrics'].keys())

    metrics = []
    for metric_name in metric_names:
        origin_id = 'raw.phantomas.' + normalize_phantomas_metric_name(metric_name)
        id = origin_id
        type = MetricType.UNKNOWN
        if metric_name in KNOWN_PHANTOMAS_METRICS:
            type, sep, id = KNOWN_PHANTOMAS_METRICS[metric_name].rpartition(':')

        data = [
            normalize_phantomas_value(run['metrics'][metric_name], type) if metric_name in run['metrics'] else None
            for run in results
        ]
        extra = [
            run['offenders'][metric_name] if metric_name in run['offenders'] else None
            for run in results
        ]

        metrics.append(Metric(origin_id, id, type, context, meta, data, extra))

    return metrics




