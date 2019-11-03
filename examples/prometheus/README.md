# Running a demo Prometheus

To run a demo Prometheus, you'll need to follow these steps:

* Have a Django application running and exporting its stats. The
  provided `prometheus.yml` assumes the stats are exported at
  `http://127.0.0.1:8000/metrics`.
* Install Prometheus by cloning it somewhere, see the [installation
  instructions](http://prometheus.io/docs/introduction/install/).
  Let's assume you cloned it to `~/prometheus`.
* Run prometheus like this:

  ```shell
  ~/prometheus/prometheus \
    --config.file=prometheus.yml \
    --web.console.templates consoles/ \
    --web.console.libraries ~/prometheus/console_libraries/
  ```

* Navigate to `http://localhost:9090`.
