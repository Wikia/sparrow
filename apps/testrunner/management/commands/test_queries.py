from collections import OrderedDict
from django.conf import settings
from django.core.management.base import BaseCommand
import ujson
from metrics import Collection
from metrics.queries import Query



def build_absolute_uri(uri):
    return settings.API_SERVER_URL + uri


class Command(BaseCommand):
    help = 'Runs sample query against collected metrics'

    def add_arguments(self, parser):
        parser.add_argument('datafile', type=str)

    def handle(self, *args, **options):
        with open(options['datafile'], 'r') as f:
            data = ujson.load(f)

        all_metrics = Collection.unserialize(data)

        query = Query().where_eq('id', 'browser.dom.event.interactive')

        result_set = query.execute(all_metrics)
        dump_result_set(result_set)

        # for result in result_set:
        #     print list(result.values)
        #     print result.raw_values
        #     print 'mean', result.stats.mean
        #     print 'median', result.stats.median
        #     print 'stddev', result.stats.stddev
        #     print '5% percentile', result.stats.pct_5
        #     print '50% percentile', result.stats.pct_50
        #     print '90% percentile', result.stats.pct_90
        #     print '95% percentile', result.stats.pct_95


def dump_result_set(result_set, indent=''):
    """
    :param result_set:
    :type result_set: metrics.queries.ResultSet
    :return:
    """
    print(indent + 'RESULT SET')
    dump_query(result_set.query)

    results = list(result_set.results)
    if len(results) > 0:
        r_indent = indent + '    '
        for result in results:
            print(indent + '  RESULT')
            dump_context(result.context, r_indent)
            dump_values(result, r_indent)


def dump_query(query, indent=''):
    """
    :param query:
    :type query: metrics.queries.Query
    :return:
    """
    print(indent + 'QUERY')
    if len(query.where_clause) > 0:
        print(indent + '  WHERE')
        for condition in query.where_clause:
            print(indent + '    ' + condition['text'])
    if len(query.group_by_clause) > 0:
        print(indent + '  UNIFY BY')
        for field in query.group_by_clause:
            print(indent + '    ' + field)


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
    print(indent + 'CONTEXT')
    for k, v in l:
        print(indent + '  {} = {}'.format(k, v))


def dump_values(result, indent=''):
    print(indent + 'VALUES')
    raw_values = sorted(result.raw_values)
    print(indent + '  {}'.format(raw_values))
    stats = result.stats
    print(indent + '  count = {}        median = {}         stddev = {}'.format(stats.count, stats.median, stats.stddev))
    print(indent + '       5%                                 50%                              90%   95%    ')
    print(indent + '  -----|----------------------------------|--------------------------------|-----|------')
    print(indent + '       {:<10}                         {:<10}                             {:<10}'.format(
        stats.pct_5, stats.pct_50, stats.pct_95))
    print(indent + '                                                                           {:<10}'.format(
        stats.pct_90))
