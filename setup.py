import os
from setuptools import setup, find_packages

LONG_DESCRIPTION = """django-exporter

This library contains code to expose some monitoring metrics relevant
to Django internals so they can be monitored by Prometheus.

See https://github.com/prezi/django-exporter for usage instructions.
"""

setup(
    name="django-exporter",
    version="2.2.1",
    author="David Guerrero",
    author_email="david.guerrero@prezi.com",
    description="Export Django metrics for Prometheus.",
    license="Apache",
    keywords="django monitoring prometheus",
    url="http://github.com/prezi/django-exporter",
    packages=find_packages(),
    test_suite="django_prometheus.tests",
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "prometheus_client==0.5.0",
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
