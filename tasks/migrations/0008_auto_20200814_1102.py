# Generated by Django 3.1 on 2020-08-14 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0007_note"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="task",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notes",
                to="tasks.task",
                verbose_name="notes",
            ),
        ),
    ]