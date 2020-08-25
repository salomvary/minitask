from django.forms import ModelForm

from tasks.models import Task


class ArchiveTaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ("version", "is_archived")
