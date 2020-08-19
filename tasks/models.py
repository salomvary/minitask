from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext


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

    members = models.ManyToManyField(User, through="ProjectMembership")

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self):
        return self.title


class ProjectMembership(models.Model):
    """Represents users participating on a project"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    expires_at = models.DateField(_("expires at"), null=True, blank=True)

    class Meta:
        verbose_name = _("project membership")
        verbose_name_plural = _("project memberships")

    def __str__(self):
        if self.expires_at:
            expires_at = _("until %(expires_at)s" % {"expires_at": self.expires_at})
        else:
            expires_at = _("forever")

        # TODO figure out why this is still English on the Admin
        return gettext(
            "'%(user)s' member of '%(project)s' project %(expires_at)s"
            % {"user": self.user, "project": self.project, "expires_at": expires_at,}
        )


class TaskManager(models.Manager):
    CASE_SQL = """
        (case
            when status='done' then 1
            when status='open' then 2
            when status='in_progress' then 3
        end)
    """

    def sorted_for_dashboard(
        self,
        project=None,
        due_date_before=None,
        due_date_after=None,
        status=None,
        assignee=None,
    ):
        query = self.extra(select={"status_order": self.CASE_SQL}).order_by(
            "-status_order", models.F("due_date").asc(nulls_last=True), "-priority"
        )

        if project is not None:
            query = query.filter(project=project)

        if due_date_after is not None:
            query = query.filter(due_date__gte=due_date_after)

        if due_date_before is not None:
            query = query.filter(due_date__lte=due_date_before)

        if status is not None:
            query = query.filter(status=status)

        if assignee is not None:
            query = query.filter(assignee=assignee)

        return query


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
