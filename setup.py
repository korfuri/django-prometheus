import os
from setuptools import setup, find_packages

LONG_DESCRIPTION = """Django-Prometheus

This library contains code to expose some monitoring metrics relevant
to Django internals so they can be monitored by Prometheus.io.

See https://github.com/korfuri/django-prometheus for usage
instructions.
"""

setup(
    name="django-prometheus",
    version="1.0.15",
    author="Uriel Corfa",
    author_email="uriel@corfa.fr",
    description=(
        "Django middlewares to monitor your application with Prometheus.io."),
    license="Apache",
    keywords="django monitoring prometheus",
    url="http://github.com/korfuri/django-prometheus",
    packages=find_packages(),
    test_suite="django_prometheus.tests",
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "prometheus_client>=0.0.21",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Django",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
