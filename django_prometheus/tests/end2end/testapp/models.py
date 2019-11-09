from django.db.models import CharField, Model, PositiveIntegerField

from django_prometheus.models import ExportModelOperationsMixin


class Dog(ExportModelOperationsMixin("dog"), Model):
    name = CharField(max_length=100, unique=True)
    breed = CharField(max_length=100, blank=True, null=True)
    age = PositiveIntegerField(blank=True, null=True)


class Lawn(ExportModelOperationsMixin("lawn"), Model):
    location = CharField(max_length=100)
