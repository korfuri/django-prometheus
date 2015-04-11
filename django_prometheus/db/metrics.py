from prometheus_client import Counter


connections_total = Counter(
    'django_db_new_connections_total',
    'Counter of created connections by database and by vendor.',
    ['alias', 'vendor'])

connection_errors_total = Counter(
    'django_db_new_connection_errors_total',
    'Counter of connection failures by database and by vendor.',
    ['alias', 'vendor'])

execute_total = Counter(
    'django_db_execute_total',
    ('Counter of executed statements by database and by vendor, including'
     ' bulk executions.'),
    ['alias', 'vendor'])


execute_many_total = Counter(
    'django_db_execute_many_total',
    ('Counter of executed statements in bulk operations by database and'
     ' by vendor.'),
    ['alias', 'vendor'])


errors_total = Counter(
    'django_db_errors_total',
    ('Counter of execution errors by database, vendor and exception type.'),
    ['alias', 'vendor', 'type'])
