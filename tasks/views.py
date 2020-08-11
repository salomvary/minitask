from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string


def index(request):
    return HttpResponse(render_to_string("index.html", {"user": request.user}))
