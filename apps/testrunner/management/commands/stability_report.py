from collections import OrderedDict
import csv
from django.conf import settings
from django.core.management.base import BaseCommand
import ujson
import requests
from metrics import Collection
from metrics.queries import Query
from testrunner.metric_sets import BasicMetricSet


class Command(BaseCommand):
    help = 'Fetch data from sparrow server and generate stability report'

    def merge_collections(self, *input):
        def metric_context_id(m):
            return '{}'.format(sorted(m.context.items(), key=lambda kv: kv[0]))

        mm = [
            dict([
                (metric_context_id(metric), metric)
                for metric in collection
            ])
            for collection in input
        ]
        keys = set()
        for mmm in mm:
            keys.update(set(mmm.keys()))
        out = Collection()
        for key in keys:
            metrics = filter(lambda x: x is not None, [mmm.get(key) for mmm in mm])
            for i in range(1, len(metrics)):
                metrics[0].add_values([
                    (value.raw_value, value.info)
                    for value in metrics[i].values
                ])
            out.add(metrics[0])
        return out


    def fetch_json(self, url):
        response = requests.get(url)
        return response.json()


    def handle(self, *args, **options):
        test_runs = self.fetch_json('http://sparrow-s1/api/v1/test_runs/')

        q1 = Query().where_eq('id', 'browser.dom.event.interactive')

        for test_run in test_runs['results']:
            result_urls = test_run['results']
            if len(result_urls) == 0:
                continue

            collection = Collection()
            for result_url in result_urls:
                result_data = self.fetch_json(result_url)
                serialized_data = result_data['results']
                this_collection = Collection.unserialize(serialized_data)
                # dump_result_set(q1.execute(this_collection))
                collection = self.merge_collections(collection, this_collection)

            # dump_result_set(q1.execute(collection))

            header = ['ID', 'mean', 'stddev', 'min', 'max', 'pct_5', 'pct_50', 'pct_95'] + ([''] * 25)
            rows = []

            sorted_metrics = sorted([
                                        ('{}/{}'.format(metric.context['origin'], metric.context['id']), metric)
                                        for metric in collection.metrics
                                        if not metric.context['id'].endswith('.list')
                                    ], key=lambda kv: kv[0])
            for id, metric in sorted_metrics:
                # id = '{}/{}'.format(metric.context['origin'], metric.context['id'])
                raw_values = sorted(metric.values.raw_values)
                row = [id]
                try:
                    """:type: Stats"""
                    stats = metric.values.stats
                    row += [
                        stats.mean,
                        stats.stddev,
                        stats.min,
                        stats.max,
                        stats.pct_5,
                        stats.pct_50,
                        stats.pct_95
                    ]
                except:
                    row += [''] * 7
                row += raw_values
                row = [
                    v if type(v) is not float else '{}'.format(v).replace('.', ',')
                    for v in row
                ]
                rows.append(row)

            r = q1.execute(collection)
            rr = list(r.results)
            context = rr[0].context
            url = context['url']
            url = url[url.find('/wiki/') + 6:]
            article, sep, unused = url.partition('?')
            file_name = article + ('-debug' if unused != '' else '') + '.csv'
            print file_name
            with open(file_name, 'wb') as f:
                w = csv.writer(f)
                w.writerow(header)
                w.writerows(rows)

            print '========'


def dump_result_set(result_set, indent=''):
    """
    :param result_set:
    :type result_set: metrics.queries.ResultSet
    :return:
    """
    print indent + 'RESULT SET'
    dump_query(result_set.query)

    results = list(result_set.results)
    if len(results) > 0:
        r_indent = indent + '    '
        for result in results:
            print indent + '  RESULT'
            dump_context(result.context, r_indent)
            dump_values(result, r_indent)


def dump_query(query, indent=''):
    """
    :param query:
    :type query: metrics.queries.Query
    :return:
    """
    print indent + 'QUERY'
    if len(query.where_clause) > 0:
        print indent + '  WHERE'
        for condition in query.where_clause:
            print indent + '    ' + condition['text']
    if len(query.group_by_clause) > 0:
        print indent + '  UNIFY BY'
        for field in query.group_by_clause:
            print indent + '    ' + field


def dump_context(context, indent=''):
    l = []
    c = context.copy()
    if 'id' in c:
        l.append(('id', c['id']))
        c.pop('id')
    if 'type' in c:
        l.append(('type', c['type']))
        c.pop('type')
    l += OrderedDict(c).items()
    print indent + 'CONTEXT'
    for k, v in l:
        print indent + '  {} = {}'.format(k, v)


def dump_values(result, indent=''):
    print indent + 'VALUES'
    raw_values = sorted(result.raw_values)
    print indent + '  {}'.format(raw_values)
    stats = result.stats
    print indent + '  count = {}        median = {}         stddev = {}'.format(stats.count, stats.median, stats.stddev)
    print indent + '       5%                                 50%                              90%   95%    '
    print indent + '  -----|----------------------------------|--------------------------------|-----|------'
    print indent + '       {:<10}                         {:<10}                             {:<10}'.format(
        stats.pct_5, stats.pct_50, stats.pct_95)
    print indent + '                                                                           {:<10}'.format(
        stats.pct_90)


def dump_stats(stats, indent=''):
    print indent + 'VALUES'
    raw_values = sorted(stats.values)
    print indent + '  {}'.format(raw_values)
    print indent + '  count = {}        median = {}         stddev = {}'.format(stats.count, stats.median, stats.stddev)
    print indent + '       5%                                 50%                              90%   95%    '
    print indent + '  -----|----------------------------------|--------------------------------|-----|------'
    print indent + '       {:<10}                         {:<10}                             {:<10}'.format(
        stats.pct_5, stats.pct_50, stats.pct_95)
    print indent + '                                                                           {:<10}'.format(
        stats.pct_90)
