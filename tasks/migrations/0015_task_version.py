# Generated by Django 3.1 on 2020-08-20 05:39

from django.db import migrations
import ool


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0014_auto_20200819_1343"),
    ]

    operations = [
        migrations.AddField(
            model_name="task", name="version", field=ool.VersionField(default=0),
        ),
    ]
