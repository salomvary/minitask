from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import Task

@login_required
def index(request):
    tasks = Task.objects.all()
    return HttpResponse(
        render_to_string("index.html", {"user": request.user, "tasks": tasks})
    )
