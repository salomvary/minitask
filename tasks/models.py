from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from ool import VersionedMixin, VersionField
from taggit.managers import TaggableManager

from accounts.models import User


class ProjectQuerySet(models.QuerySet):
    """Queries for the Project model"""

    def visible_to_user(self, user):
        """Filter for projects visible to the user"""

        # Fow now, tasks of archived projects are always hidden and there
        # is no way to show them. Later we might add a "Project archives" section
        query = self.exclude(is_archived=True)

        # FIXME: de-duplicate this filter
        if user.is_superuser:
            return query
        else:
            return query.filter(
                Q(membership__user=user)
                & (
                    Q(membership__expires_at__isnull=True)
                    | Q(membership__expires_at__gte=datetime.now())
                )
            )


ProjectManager = models.Manager.from_queryset(ProjectQuerySet)


class Project(models.Model):
    objects = ProjectManager()

    title = models.CharField(_("title"), max_length=500)

    members = models.ManyToManyField(User, through="ProjectMembership")

    is_archived = models.BooleanField(
        default=False, blank=False, null=False, verbose_name=_("archived"),
    )

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self):
        return self.title


class ProjectMembership(models.Model):
    """Represents users participating on a project"""

    user = models.ForeignKey(User, related_name="membership", on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, related_name="membership", on_delete=models.CASCADE
    )
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


class TaskQuerySet(models.QuerySet):
    """Queries for the Task model"""

    # TODO: use Django's Case/When:
    #  https://docs.djangoproject.com/en/3.1/ref/models/conditional-expressions/#case
    CASE_SQL = """
        (case
            when status='done' then 1
            when status='open' then 2
            when status='in_progress' then 3
        end)
    """

    def all_visible(self, is_archived=False):
        """
        Default filtering and sorting of tasks

        Filters out archived tasks and tasks of archived projects
        """

        query = (
            self.select_related("project")
            .prefetch_related("tags")
            .extra(select={"status_order": self.CASE_SQL})
            .order_by(
                "-status_order", models.F("due_date").asc(nulls_last=True), "-priority"
            )
            # Fow now, tasks of archived projects are always hidden and there
            # is no way to show them. Later we might add a "Project archives" section
            .exclude(project__is_archived=True)
        )

        if is_archived:
            query = query.filter(is_archived=True)
        else:
            query = query.exclude(is_archived=True)

        return query

    def filtered_by(
        self,
        project=None,
        due_date_before=None,
        due_date_after=None,
        status: str = None,
        assignee=None,
        tags=None,
    ):
        """Filter by user provided field values"""

        # TODO: Optimize these filters into one:
        # https://djangotricks.blogspot.com/2018/05/queryset-filters-on-many-to-many-relations.html
        query = self

        if project is not None:
            query = query.filter(project=project)

        if due_date_after is not None:
            query = query.filter(due_date__gte=due_date_after)

        if due_date_before is not None:
            query = query.filter(due_date__lte=due_date_before)

        if status is not None:
            if status.startswith("!"):
                query = query.exclude(status=status[1:])
            else:
                query = query.filter(status=status)

        if assignee is not None:
            query = query.filter(assignee=assignee)

        if tags is not None and len(tags) > 0:
            for tag in tags:
                query = query.filter(tags__name=tag)

        return query

    def visible_to_user(self, user):
        """Filter for tasks visible to the user"""

        # FIXME: de-duplicate this filter
        if user.is_superuser:
            return self
        else:
            return self.filter(
                Q(project__membership__user=user)
                & (
                    Q(project__membership__expires_at__isnull=True)
                    | Q(project__membership__expires_at__gte=datetime.now())
                )
            )


TaskManager = models.Manager.from_queryset(TaskQuerySet)


class Task(VersionedMixin, models.Model):
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

    version = VersionField()

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

    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=False,
        null=False,
        default=1,
        related_name="created_tasks",
        verbose_name=_("created by"),
    )

    tags = TaggableManager(
        verbose_name=_("tags"),
        help_text=_("A comma-separated list of tags."),
        blank=True,
    )

    is_archived = models.BooleanField(
        default=False, blank=False, null=False, verbose_name=_("archived"),
    )

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")

    def __str__(self):
        return self.title


class NoteQuerySet(models.QuerySet):
    """Queries for the Note model"""

    def visible_to_user(self, user):
        """Filter for notes visible to the user"""

        # FIXME: de-duplicate this filter
        if user.is_superuser:
            return self
        else:
            return self.filter(
                Q(task__project__membership__user=user)
                & (
                    Q(task__project__membership__expires_at__isnull=True)
                    | Q(task__project__membership__expires_at__gte=datetime.now())
                )
            )


NoteManager = models.Manager.from_queryset(NoteQuerySet)


class Note(models.Model):
    objects = NoteManager()

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
