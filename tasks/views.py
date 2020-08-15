from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms.new_task_form import NewTaskForm
from .forms.note_form import NoteForm
from .models import Task


@login_required
def index(request):
    tasks = Task.objects.all()
    return render(request, "index.html", {"user": request.user, "tasks": tasks})


@login_required
def new_task(request):
    form = NewTaskForm()
    return render(request, "tasks/new.html", {"user": request.user, "form": form})


@login_required
def copy_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    form = NewTaskForm(None, instance=task)
    return render(request, "tasks/new.html", {"user": request.user, "form": form})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    note_form = NoteForm(request.POST)
    return render(
        request,
        "tasks/detail.html",
        {"user": request.user, "task": task, "note_form": note_form},
    )


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    form = NewTaskForm(request.POST or None, instance=task)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            action = request.POST.get("action")
            if action == "copy":
                return redirect("copy", task.id)
            elif action == "new":
                return redirect("new")
            else:
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
        action = request.POST.get("action")
        if action == "copy":
            return redirect("copy", task.id)
        elif action == "new":
            return redirect("new")
        else:
            return redirect("detail", task.id)
    else:
        return render(
            request, "tasks/new.html", {"user": request.user, "form": form}, status=400
        )


@login_required
def create_note(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    form = NoteForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.instance.task = task
            form.instance.author = request.user
            form.save()
            return redirect(
                reverse("detail", args=[task.id]) + "#note-" + str(form.instance.id)
            )
        else:
            return render(
                request,
                "tasks/detail.html",
                {"user": request.user, "task": task, "note_form": form},
                status=400,
            )
    else:
        return redirect("detail", task.id)
