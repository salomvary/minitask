from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404

from .models import Task
from .forms.new_task_form import NewTaskForm


@login_required
def index(request):
    tasks = Task.objects.all()
    return render(request, "index.html", {"user": request.user, "tasks": tasks})


@login_required
def new_task(request):
    form = NewTaskForm()
    return render(request, "tasks/new.html", {"user": request.user, "form": form})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    return render(request, "tasks/detail.html", {"user": request.user, "task": task})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    form = NewTaskForm(request.POST or None, instance=task)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("detail", task.id)
        else:
            return render(
                request,
                "tasks/edit.html",
                {"user": request.user, "task": task, "form": form},
                status=400,
            )
    else:
        return render(
            request,
            "tasks/edit.html",
            {"user": request.user, "task": task, "form": form},
        )


@login_required
def create_task(request):
    form = NewTaskForm(request.POST)
    if form.is_valid():
        task = form.save()
        return redirect("detail", task.id)
    else:
        return render(
            request, "tasks/new.html", {"user": request.user, "form": form}, status=400
        )
