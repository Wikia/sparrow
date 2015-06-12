from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
import ujson
from metrics import Collection
from metrics.queries import Query

from testrunner.tasks.http_get import MWProfilerGet, HttpGet
from testrunner.tasks.phantomas_get import PhantomasGet
from testrunner.tasks.process_results import ProcessResponses


def build_absolute_uri(uri):
    api_url = settings.SPARROW_TEST_RUNNER['api_server']
    api_url = api_url[:api_url.index('/api/v1/')]
    return api_url + uri


class Command(BaseCommand):
    help = 'Runs phantomas and prints all metrics gathered'

    def add_arguments(self, parser):
        parser.add_argument('datafile', type=str)

    def handle(self, *args, **options):
        with open(options['datafile'],'r') as f:
            data = ujson.load(f)

        all_metrics = Collection.unserialize(data)

        query = Query().where_eq('id','browser.net.ajax.requests')

        result_set = query.execute(all_metrics)

        for result in result_set:
            print list(result.values)

