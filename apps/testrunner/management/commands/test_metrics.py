from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse

from testrunner.tasks.http_get import MWProfilerGet, HttpGet
from testrunner.tasks.phantomas_get import PhantomasGet
from testrunner.tasks.process_results import ProcessResponses


def build_absolute_uri(uri):
    return settings.SPARROW_TEST_RUNNER['api_server']


class Command(BaseCommand):
    help = 'Runs phantomas and prints all metrics gathered'

    def handle(self, *args, **options):
        params = {
            'url': 'http://www.wikia.com/Wikia?noexternals=1',
            'retries': 2,
        }

        pg = PhantomasGet()
        pg_metrics = pg.run(**params)

        mg = MWProfilerGet()
        mg_metrics = mg.run(**params)

        hg = HttpGet()
        hg_metrics = hg.run(**params)

        data = [pg_metrics, mg_metrics, hg_metrics]

        # print data

        rg = ProcessResponses()
        rr = rg.run(data,
                    result_uri=build_absolute_uri(reverse('testresult-list')),
                    task_uri=build_absolute_uri(reverse('task-detail', args=[1, ])),
                    test_run_uri=build_absolute_uri(reverse('testrun-detail', args=[1, ])),
        )

