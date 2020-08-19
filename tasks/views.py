from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms.new_task_form import NewTaskForm
from .forms.note_form import NoteForm
from .forms.task_filter_form import TaskFilterForm
from .models import Task, Note, Project


@login_required
def index(request):
    project_choices = [(project.id, str(project)) for project in Project.objects.all()]
    assignee_choices = [(user.id, str(user)) for user in User.objects.all()]
    form = TaskFilterForm(
        request.GET, project_choices=project_choices, assignee_choices=assignee_choices
    )

    # Warning: form.is_valid() has the side-effect of populating form.cleaned_data
    form.is_valid()

    if "previous_due_date" in request.GET:
        form.previous_due_date()

    elif "next_due_date" in request.GET:
        form.next_due_date()

    tasks = (
        Task.objects.visible_to_user(request.user)
        .filtered_by(
            project=form.cleaned_data.get("project"),
            due_date_before=form.cleaned_data.get("due_date_before"),
            due_date_after=form.cleaned_data.get("due_date_after"),
            status=form.cleaned_data.get("status"),
            assignee=form.cleaned_data.get("assignee"),
        )
        .sorted_for_dashboard()
        .all()
    )

    has_filter = (
        next((k for (k, v) in form.cleaned_data.items() if v is not None), None)
        is not None
    )

    return render(
        request,
        "index.html",
        {"user": request.user, "tasks": tasks, "form": form, "has_filter": has_filter},
    )


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
def edit_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    form = NoteForm(request.POST or None, instance=note)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect(
                reverse("detail", args=[note.task.id])
                + "#note-"
                + str(form.instance.id)
            )
        else:
            return render(
                request,
                "notes/edit.html",
                {"user": request.user, "note": note, "form": form},
                status=400,
            )
    else:
        return render(
            request,
            "notes/edit.html",
            {"user": request.user, "note": note, "form": form},
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
