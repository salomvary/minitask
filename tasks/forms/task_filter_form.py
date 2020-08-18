from django import forms
from django.utils.translation import gettext_lazy as _

from tasks.models import Task


class TaskFilterForm(forms.Form):
    def __init__(self, *args, project_choices, assignee_choices, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)
        self.fields["project"].choices = [("", "")] + project_choices
        self.fields["assignee"].choices = [("", "")] + assignee_choices

    project = forms.TypedChoiceField(
        label=_("Project"),
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={"class": "custom-select custom-select-sm"}),
    )

    due_date_after = forms.DateField(
        label=_("Due after"),
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"}
        ),
    )

    due_date_before = forms.DateField(
        label=_("Before"),
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"}
        ),
    )

    status = forms.TypedChoiceField(
        label=_("Status"),
        choices=[("", "")] + Task.STATUS_CHOICES,
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={"class": "custom-select custom-select-sm"}),
    )

    assignee = forms.TypedChoiceField(
        label=_("Assignee"),
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={"class": "custom-select custom-select-sm"}),
    )
