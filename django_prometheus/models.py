from prometheus_client import Counter
from django_prometheus.conf import APP_NAME

model_inserts = Counter(
    "{0}_model_inserts_total".format(APP_NAME),
    "Number of insert operations by model.",
    ["model"]
)

model_updates = Counter(
    "{0}_model_updates_total".format(APP_NAME),
    "Number of update operations by model.",
    ["model"]
)

model_deletes = Counter(
    "{0}_model_deletes_total".format(APP_NAME),
    "Number of delete operations by model.",
    ["model"]
)


def ExportModelOperationsMixin(model_name):
    """Returns a mixin for models to export counters for lifecycle operations.

    Usage:
      class User(ExportModelOperationsMixin('user'), Model):
          ...
    """
    # Force create the labels for this model in the counters. This
    # is not necessary but it avoids gaps in the aggregated data.
    model_inserts.labels(model_name)
    model_updates.labels(model_name)
    model_deletes.labels(model_name)

    class Mixin(object):
        def _do_insert(self, *args, **kwargs):
            model_inserts.labels(model_name).inc()
            return super(Mixin, self)._do_insert(*args, **kwargs)

        def _do_update(self, *args, **kwargs):
            model_updates.labels(model_name).inc()
            return super(Mixin, self)._do_update(*args, **kwargs)

        def delete(self, *args, **kwargs):
            model_deletes.labels(model_name).inc()
            return super(Mixin, self).delete(*args, **kwargs)

    return Mixin
