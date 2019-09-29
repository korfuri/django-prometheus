from setuptools import find_packages, setup

LONG_DESCRIPTION = """Django-Prometheus

This library contains code to expose some monitoring metrics relevant
to Django internals so they can be monitored by Prometheus.io.

See https://github.com/korfuri/django-prometheus for usage
instructions.
"""

setup(
    name="django-prometheus",
    version="1.1.0",
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
    tests_require=['pytest', 'pytest-django'],
    setup_requires=["pytest-runner"],
    install_requires=[
        "prometheus-client>=0.7",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
