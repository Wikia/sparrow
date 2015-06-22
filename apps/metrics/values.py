import numpy


class ValueSet(object):
    def __init__(self, type, values=None):
        self.type = type
        if values is None:
            values = []
        self.values = values

        self._stats = None

    def append(self, value):
        self.values.append(value)

    def __iter__(self):
        return iter(self.values)

    @property
    def raw_values(self):
        return list(
            v.raw_value
            for v in self
        )

    @property
    def stats(self):
        if self._stats is None:
            self._stats = Stats(self.raw_values)
        return self._stats


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

    @staticmethod
    def unserialize(data):
        return Value(data['value'], data['info'])


class Stats(object):
    def __init__(self, raw_values):
        raw_values = list(raw_values)
        self.values = raw_values

        self.count = len(raw_values)
        self.pct_5 = 0.0
        self.pct_50 = 0.0
        self.pct_50 = 0.0
        self.pct_90 = 0.0
        self.pct_95 = 0.0
        self.stddev = 0.0
        self.mean = 0.0
        self.median = 0.0
        self.min = 0.0
        self.max = 0.0

        if len(raw_values) > 0:
            # self.pct_5 = float(numpy.percentile(raw_values, 5))
            # self.pct_50 = float(numpy.percentile(raw_values, 50))
            # self.pct_90 = float(numpy.percentile(raw_values, 90))
            # self.pct_95 = float(numpy.percentile(raw_values, 95))
            self.pct_5, self.pct_50, self.pct_90, self.pct_95 = [
                float(x)
                for x in numpy.percentile(raw_values, [5, 50, 90, 95])]

            self.stddev = float(numpy.std(raw_values))
            self.mean = float(numpy.mean(raw_values))
            self.median = float(numpy.median(raw_values))
            self.min = float(numpy.min(raw_values))
            self.max = float(numpy.max(raw_values))
