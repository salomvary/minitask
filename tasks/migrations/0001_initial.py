# Generated by Django 3.1 on 2020-08-31 17:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import ool
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("taggit", "0003_taggeditem_add_unique_index"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=500, verbose_name="title")),
                (
                    "is_archived",
                    models.BooleanField(default=False, verbose_name="archived"),
                ),
            ],
            options={"verbose_name": "project", "verbose_name_plural": "projects",},
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("version", ool.VersionField(default=0)),
                ("title", models.CharField(max_length=500, verbose_name="title")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "due_date",
                    models.DateField(blank=True, null=True, verbose_name="due date"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "open"),
                            ("in_progress", "in progress"),
                            ("done", "done"),
                        ],
                        default="open",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                (
                    "priority",
                    models.SmallIntegerField(
                        choices=[
                            (-2, "lowest"),
                            (-1, "low"),
                            (0, "normal"),
                            (1, "high"),
                            (2, "highest"),
                        ],
                        default=0,
                        verbose_name="priority",
                    ),
                ),
                (
                    "is_archived",
                    models.BooleanField(default=False, verbose_name="archived"),
                ),
                (
                    "assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="assignee",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="assignee",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="created_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="created by",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to="tasks.project",
                        verbose_name="project",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="tags",
                    ),
                ),
            ],
            options={"verbose_name": "task", "verbose_name_plural": "tasks",},
            bases=(ool.VersionedMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ProjectMembership",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "expires_at",
                    models.DateField(blank=True, null=True, verbose_name="expires at"),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membership",
                        to="tasks.project",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membership",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "project membership",
                "verbose_name_plural": "project memberships",
            },
        ),
        migrations.AddField(
            model_name="project",
            name="members",
            field=models.ManyToManyField(
                through="tasks.ProjectMembership", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField(verbose_name="body")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="author",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="author",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to="tasks.task",
                        verbose_name="notes",
                    ),
                ),
            ],
            options={"verbose_name": "note", "verbose_name_plural": "notes",},
        ),
    ]
