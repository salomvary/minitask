from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from ool import ConcurrentUpdate

from .forms.new_task_form import NewTaskForm
from .forms.note_form import NoteForm
from .forms.task_filter_form import TaskFilterForm
from .models import Note, Project, Task
from .templatetags.tasks_extras import user_str


@login_required
def index(request):
    projects = Project.objects.visible_to_user(request.user)

    # Set up the filter form
    project_choices = [(project.id, str(project)) for project in projects]
    assignee_choices = [(user.id, user_str(user)) for user in User.objects.all()]
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
            tags=form.cleaned_data.get("tags"),
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
    form = NewTaskForm(user=request.user)
    return render(request, "tasks/new.html", {"user": request.user, "form": form})


@login_required
def copy_task(request, task_id):
    task = get_object_or_404(Task.objects.visible_to_user(request.user), pk=task_id)
    form = NewTaskForm(None, instance=task, user=request.user)
    return render(request, "tasks/new.html", {"user": request.user, "form": form})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task.objects.visible_to_user(request.user), pk=task_id)
    note_form = NoteForm(request.POST)
    return render(
        request,
        "tasks/detail.html",
        {"user": request.user, "task": task, "note_form": note_form},
    )


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task.objects.visible_to_user(request.user), pk=task_id)
    form = NewTaskForm(request.POST or None, instance=task, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
            except ConcurrentUpdate:
                return render(
                    request,
                    "tasks/edit.html",
                    {
                        "user": request.user,
                        "task": task,
                        "form": form,
                        "is_concurrent_update": True,
                    },
                    status=409,
                )

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
@transaction.atomic
def create_task(request):
    form = NewTaskForm(request.POST, user=request.user)
    if form.is_valid():
        project = (
            Project.objects.visible_to_user(request.user)
            .filter(id=form.cleaned_data["project"].id)
            .first()
        )
        if project:
            form.instance.created_by = request.user
            task = form.save()
            action = request.POST.get("action")
            if action == "copy":
                return redirect("copy", task.id)
            elif action == "new":
                return redirect("new")
            else:
                return redirect("detail", task.id)
        else:
            raise Http404(_("The project you tried to create a task for was not found"))
    else:
        return render(
            request, "tasks/new.html", {"user": request.user, "form": form}, status=400
        )


@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note.objects.visible_to_user(request.user), pk=note_id)
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
    task = get_object_or_404(Task.objects.visible_to_user(request.user), pk=task_id)
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
