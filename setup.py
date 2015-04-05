import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="django-prometheus",
    version="0.0.1",
    author="Uriel Corfa",
    author_email="uriel@corfa.fr",
    description=(
        "Django middlewares to monitor your application with Prometheus.io."),
    license="Apache",
    keywords="django monitoring prometheus",
    url="http://github.com/korfuri/django-prometheus",
    packages=['django_prometheus'],
    long_description=read('README.md'),
    install_requires=['prometheus_client'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
