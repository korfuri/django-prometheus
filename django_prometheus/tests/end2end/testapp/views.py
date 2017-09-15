import django
from django.db import connections
from django.shortcuts import render
from django.template.response import TemplateResponse
from testapp.models import Lawn
import os
import time
from django.http import FileResponse


def index(request):
    return TemplateResponse(request, 'index.html', {})


def help(request):
    # render does not instanciate a TemplateResponse, so it does not
    # increment the "by_templatename" counters.
    return render(request, 'help.html', {})


def slow(request):
    """This view takes .1s to load, on purpose."""
    time.sleep(.1)
    return TemplateResponse(request, 'slow.html', {})


def newlawn(request, location):
    """This view creates a new Lawn instance in the database."""
    l = Lawn()
    l.location = location
    l.save()
    return TemplateResponse(request, 'lawn.html', {'lawn': l})


class ObjectionException(Exception):
    pass


def objection(request):
    raise ObjectionException('Objection!')


def sql(request):
    databases = connections.databases.keys()
    query = request.GET.get('query')
    db = request.GET.get('database')
    if query and db:
        cursor = connections[db].cursor()
        cursor.execute(query, [])
        results = cursor.fetchall()
        return TemplateResponse(request, 'sql.html', {
            'query': query,
            'rows': results,
            'databases': databases,
        })
    else:
        return TemplateResponse(request, 'sql.html', {
            'query': None,
            'rows': None,
            'databases': databases,
        })


def file(request):
    return FileResponse(open(os.devnull, 'rb'))
