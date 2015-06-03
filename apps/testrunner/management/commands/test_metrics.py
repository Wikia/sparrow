from django.core.management.base import BaseCommand

from metrics import get_phantomas_metrics
from testrunner.tasks.phantomas_get import PhantomasGet


class Command(BaseCommand):
    help = 'Runs phantomas and prints all metrics gathered'

    def handle(self, *args, **options):
        pg = PhantomasGet()
        results = pg.run('http://www.wikia.com/Wikia?noexternals=1',2)

        metrics = get_phantomas_metrics(results['phantomas_get'])
        metrics = sorted(metrics,key=lambda m: m.id)
        for metric in metrics:
            print '{}: {}'.format(metric.id, metric.data)