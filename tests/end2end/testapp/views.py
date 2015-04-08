from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
import time
import random

def index(request):
    return render(request, 'index.html', {})

class ObjectionException(Exception):
    pass

def objection(request):
    raise ObjectionException('Objection!')
