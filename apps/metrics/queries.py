from collections import defaultdict
from metrics.values import ValueSet


class Query(object):
    def __init__(self):
        self.where_clause = []
        self.group_by_clause = []

    def where_eq(self, field, value):
        self.where_clause.append({
            'text': '{} = "{}"'.format(field, value),
            'fn': lambda c: c.get(field, None) == value
        })
        return self

    def group_by(self, field):
        if field == 'type':
            raise ValueError('Group by "type" is not allowed')
        self.group_by_clause.append(field)
        return self

    def execute(self, collection):
        return ExecuteQuery(collection, self).run()


class ResultSet(object):
    def __init__(self, collection, query, results):
        self.collection = collection
        self.query = query
        self.results = results

    def __iter__(self):
        return iter(self.results)


class Result(ValueSet):
    def __init__(self, context, metrics):
        self.context = context
        self.metrics = metrics
        super(Result, self).__init__(context['type'],[
            v
            for metric in metrics
            for v in metric.values
        ])

    @property
    def id(self):
        return self.context['id']


class ExecuteQuery(object):
    def __init__(self, collection, query):
        self.collection = collection
        self.query = query

    def run(self):
        context_filters = [condition['fn'] for condition in self.query.where_clause]
        ignore_context_fields = set(self.query.group_by_clause)

        buckets = defaultdict(list)

        for metric in self.collection:
            context = metric.context.copy()
            if any([not filter_fn(context) for filter_fn in context_filters]):
                continue
            bucket_id = tuple((
                (k, v)
                for k, v in sorted(context.items(), key=lambda kv: kv[0])
                if k not in ignore_context_fields
            ))
            buckets[bucket_id].append(metric)

        results = []
        for bucket, metrics in buckets.items():
            context = dict(bucket)
            results.append(Result(context, metrics))

        return ResultSet(self.collection, self.query, results)

