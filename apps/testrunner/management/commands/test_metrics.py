from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
import ujson

from testrunner.tasks.http_get import MWProfilerGet, HttpGet
from testrunner.tasks.phantomas_get import PhantomasGet
from testrunner.tasks.process_results import ProcessResponses
from testrunner.tasks.selenium_get import SeleniumGet


def build_absolute_uri(uri):
    api_url = settings.SPARROW_TEST_RUNNER['api_server']
    api_url = api_url[:api_url.index('/api/v1/')]
    return api_url + uri


class Command(BaseCommand):
    help = 'Runs phantomas and prints all metrics gathered'

    def add_arguments(self, parser):
        parser.add_argument('--runs', default=2, type=int)
        parser.add_argument('--seleniumout', type=str)
        parser.add_argument('--out', type=str)

    def handle(self, *args, **options):
        params = {
            'url': 'http://www.wikia.com/Wikia?noexternals=1',
            'retries': options['runs'],
        }

        pg = PhantomasGet()
        pg_metrics = pg.run(**params)

        mg = MWProfilerGet()
        mg_metrics = mg.run(**params)

        hg = HttpGet()
        hg_metrics = hg.run(**params)

        sg = SeleniumGet()
        sg_metrics = sg.run(**params)

        if options['seleniumout']:
            with open(options['seleniumout'], 'w') as f:
                ujson.dump(sg_metrics,f)

        data = [pg_metrics, mg_metrics, hg_metrics, sg_metrics]

        # print data

        rg = ProcessResponses()
        rr = rg.run(data,
                    result_uri=build_absolute_uri(reverse('testresult-list')),
                    task_uri=build_absolute_uri(reverse('task-detail', args=[1, ])),
                    test_run_uri=build_absolute_uri(reverse('testrun-detail', args=[1, ])),
        )

        if options['out']:
            with open(options['out'],'w') as f:
                ujson.dump(rr,f)


