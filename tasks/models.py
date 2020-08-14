from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    title = models.CharField(_("title"), max_length=500)

    owner = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="owner",
        verbose_name=_("owner"),
    )

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ("open", _("open")),
        ("in_progress", _("in progress")),
        ("done", _("done")),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name=_("project"),
    )

    title = models.CharField(_("title"), max_length=500)

    description = models.TextField(_("description"), blank=True)

    due_date = models.DateField(_("due date"), blank=True, null=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    status = models.CharField(
        _("status"), max_length=20, default="open", choices=STATUS_CHOICES
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="assignee",
        verbose_name=_("assignee"),
    )

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")

    def __str__(self):
        return self.title


class Note(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="notes", verbose_name=_("notes"),
    )

    body = models.TextField(_("body"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="author",
        verbose_name=_("author"),
    )

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")

    def __str__(self):
        return f"Note by {self.author} on {self.created_at}"
