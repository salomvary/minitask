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


class TaskManager(models.Manager):
    CASE_SQL = """
        (case
            when status="done" then 1
            when status="open" then 2
            when status="in_progress" then 3
        end)
    """

    def sorted_for_dashboard(self):
        return self.extra(select={"status_order": self.CASE_SQL}).order_by(
            "-status_order", models.F("due_date").asc(nulls_last=True), "-priority"
        )


class Task(models.Model):
    objects = TaskManager()

    STATUS_CHOICES = [
        ("open", _("open")),
        ("in_progress", _("in progress")),
        ("done", _("done")),
    ]

    PRIORITY_CHOICES = [
        (-2, _("lowest")),
        (-1, _("low")),
        (0, _("normal")),
        (1, _("high")),
        (2, _("highest")),
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

    priority = models.SmallIntegerField(
        _("priority"), default=0, choices=PRIORITY_CHOICES
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

    body = models.TextField(_("body"))

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
