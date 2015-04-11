import os
from setuptools import setup

LONG_DESCRIPTION = """Django-Prometheus

This library contains code to expose some monitoring metrics relevant
to Django internals so they can be monitored by Prometheus.io.

See https://github.com/korfuri/django-prometheus for usage
instructions.
"""

setup(
    name="django-prometheus",
    version="0.0.10",
    author="Uriel Corfa",
    author_email="uriel@corfa.fr",
    description=(
        "Django middlewares to monitor your application with Prometheus.io."),
    license="Apache",
    keywords="django monitoring prometheus",
    url="http://github.com/korfuri/django-prometheus",
    packages=["django_prometheus"],
    test_suite="tests",
    long_description=LONG_DESCRIPTION,
    install_requires=["prometheus_client==0.0.8"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Framework :: Django",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
