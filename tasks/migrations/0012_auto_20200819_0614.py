# Generated by Django 3.1 on 2020-08-19 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_auto_20200819_0612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmembership',
            name='expires_at',
            field=models.DateField(null=True, verbose_name='expires at'),
        ),
    ]
