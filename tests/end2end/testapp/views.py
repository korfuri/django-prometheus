from django.shortcuts import render
from django.template.response import TemplateResponse
import time


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


class ObjectionException(Exception):
    pass


def objection(request):
    raise ObjectionException('Objection!')
