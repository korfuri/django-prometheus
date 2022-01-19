{
  grafanaDashboards: {
    'django-overview.json': (import 'dashboards/django-overview.json'),
  },

  // Helper function to ensure that we don't override other rules, by forcing
  // the patching of the groups list, and not the overall rules object.
  local importRules(rules) = {
    groups+: std.native('parseYaml')(rules)[0].groups,
  },

  // NOTE: Commented cause there's no rules or alerts configured
  // prometheusRules+: importRules(importstr 'rules/rules.yaml'),

  // prometheusAlerts+:
  //   importRules(importstr 'alerts/general.yaml') +
  //   importRules(importstr 'alerts/galera.yaml'),
}
