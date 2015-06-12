class MetricType:
    UNKNOWN = 'unknown'
    TIME = 'time'
    SIZE = 'size'
    COUNT = 'count'
    QUERY_LIST = 'query_list'


class Collection(object):
    def __init__(self, metrics=None):
        if metrics is None:
            metrics = []
        self.metrics = metrics

    def add(self, metric):
        self.metrics.append(metric)

    def __iter__(self):
        return iter(self.metrics)

    def sort(self, *args, **kwargs):
        return Collection(sorted(self.metrics, *args, **kwargs))

    def filter(self, function):
        return Collection(filter(function, self.metrics))

    def __add__(self, other):
        new_collection = Collection()
        new_collection += self
        new_collection += other
        return new_collection

    def __iadd__(self, other):
        self.metrics.extend(other.metrics)

    def serialize(self):
        return [
            metric.serialize()
            for metric in self.metrics
        ]


class Metric(object):
    def __init__(self, id, context, type, info=None, values=None):
        context = context.copy()
        context['id'] = id
        context['type'] = type
        self.context = context

        self.info = info

        self.values = []
        if values is not None:
            self.add_values(values)

    @property
    def id(self):
        return self.context['id']

    @property
    def type(self):
        return self.context['type']

    def add_value(self, raw_value, info=None):
        self.values.append(Value(raw_value, info))

    def add_values(self, values):
        for raw_value, info in values:
            self.add_value(raw_value, info)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return u'<Metric id={} context={} info={} values=[{}]>'.format(self.id, self.context, self.info, self.values)

    def serialize(self):
        return {
            'type': self.type,
            'context': self.context,
            'info': self.info,
            'values': [
                value.serialize()
                for value in self.values
            ]
        }

class Value(object):
    def __init__(self, raw_value, info=None):
        self.raw_value = raw_value
        self.info = info

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return u'<MetricValue raw_value={} info={}>'.format(self.raw_value, self.info)

    def serialize(self):
        return {
            'value': self.raw_value,
            'info': self.info
        }




