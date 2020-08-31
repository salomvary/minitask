from urllib.parse import SplitResult, urlsplit

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404
from django.http.request import validate_host
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from ool import ConcurrentUpdate

from .forms.archive_task_form import ArchiveTaskForm
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

    # "Remember" the last filter query so that the "back to the task list"
    # links can return to a *filtered* list
    request.session["last_task_filter"] = form.data

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
        .all_visible(is_archived=form.cleaned_data.get("is_archived"))
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
    local_referrer = get_local_referrer(request)
    self_url = reverse("new")
    cancel_url = (
        local_referrer
        if local_referrer and local_referrer != self_url
        else reverse("index")
    )
    return render(
        request,
        "tasks/new.html",
        {"user": request.user, "form": form, "cancel_url": cancel_url},
    )


@login_required
def copy_task(request, task_id):
    task = get_object_or_404(Task.objects.visible_to_user(request.user), pk=task_id)
    form = NewTaskForm(None, instance=task, user=request.user)
    cancel_url = reverse("detail", args=[task.id])
    return render(
        request,
        "tasks/new.html",
        {"user": request.user, "form": form, "cancel_url": cancel_url},
    )


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task.objects.visible_to_user(request.user), pk=task_id)
    note_form = NoteForm(request.POST)
    archive_task_form = ArchiveTaskForm(None, instance=task)
    return render_task_detail(
        request, task, note_form=note_form, archive_task_form=archive_task_form,
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
                return render_task_edit(
                    request, task, form, is_concurrent_update=True, status=409,
                )

            action = request.POST.get("action")
            if action == "copy":
                return redirect("copy", task.id)
            elif action == "new":
                return redirect("new")
            else:
                return redirect("detail", task.id)
        else:
            return render_task_edit(request, task, form, status=400)
    else:
        return render_task_edit(request, task, form)


@login_required
def archive_task(request, task_id):
    """Set the is_archived flag on a task"""

    task = get_object_or_404(Task.objects.visible_to_user(request.user), pk=task_id)
    form = ArchiveTaskForm(request.POST or None, instance=task)
    note_form = NoteForm()

    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
            except ConcurrentUpdate:
                return render_task_detail(
                    request,
                    task,
                    archive_task_form=form,
                    note_form=note_form,
                    is_concurrent_update=True,
                    status=409,
                )
            return redirect("detail", task.id)
        else:
            return redirect("detail", task.id)
    else:
        return redirect("detail", task.id)


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
    archive_task_form = ArchiveTaskForm(None, instance=task)
    if request.method == "POST":
        if form.is_valid():
            form.instance.task = task
            form.instance.author = request.user
            form.save()
            return redirect(
                reverse("detail", args=[task.id]) + "#note-" + str(form.instance.id)
            )
        else:
            return render_task_detail(
                request,
                task,
                note_form=form,
                archive_task_form=archive_task_form,
                status=400,
            )
    else:
        return redirect("detail", task.id)


def render_task_detail(
    request, task, note_form, archive_task_form, is_concurrent_update=False, **kwargs
):
    return render(
        request,
        "tasks/detail.html",
        {
            "user": request.user,
            "task": task,
            "note_form": note_form,
            "archive_task_form": archive_task_form,
            "is_concurrent_update": is_concurrent_update,
            "last_task_filter": request.session.get("last_task_filter"),
        },
        **kwargs
    )


def render_task_edit(request, task, form, is_concurrent_update=False, **kwargs):
    return render(
        request,
        "tasks/edit.html",
        {
            "user": request.user,
            "task": task,
            "form": form,
            "is_concurrent_update": is_concurrent_update,
            "last_task_filter": request.session.get("last_task_filter"),
        },
        **kwargs
    )


def get_local_referrer(request):
    """Get the referrer URL if it is not external to this application"""

    if "HTTP_REFERER" in request.META:
        # Adopted from here:
        # https://github.com/django/django/blob/7fc317ae736e8fda1aaf4d4ede84d95fffaf5281/django/http/request.py#L124-L130
        allowed_hosts = settings.ALLOWED_HOSTS
        if settings.DEBUG and not allowed_hosts:
            allowed_hosts = [".localhost", "127.0.0.1", "[::1]"]

        referrer = urlsplit(request.META["HTTP_REFERER"])

        if validate_host(referrer.hostname, allowed_hosts):
            # If the referrer header points to "ourselves", return a "safe copy"
            # removing everything but the path+query+fragment part
            return SplitResult(
                scheme="",
                netloc="",
                path=referrer.path,
                query=referrer.query,
                fragment=referrer.fragment,
            ).geturl()
        else:
            return None
    else:
        return None
