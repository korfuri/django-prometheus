from django_prometheus.management import PushgatewayCommand


class Command(PushgatewayCommand):

    job_name = 'my-cron-job'
    help = 'Does a long running job'

    def handle(self, *args, **options):
        self.gauge('my_gauge', 'My gauge', ['foo']).labels(foo='bar').set(42)
        self.counter('my_counter', 'My counter description').inc(123)
        self.push_metrics()
