import calendar
from datetime import date, timedelta

from django import forms
from django.utils.translation import gettext_lazy as _
from taggit.forms import TagField, TagWidget

from tasks.models import Task


class TaskFilterForm(forms.Form):
    """Form to filter the task list"""

    def __init__(self, *args, project_choices=None, assignee_choices=None, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)
        self.fields["project"].choices = [("", "")] + (project_choices or [])
        self.fields["assignee"].choices = [("", "")] + (assignee_choices or [])

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
            # ISO date must be used with <input type=date> all times
            format="%Y-%m-%d",
            attrs={"class": "form-control form-control-sm", "type": "date"},
        ),
    )

    due_date_before = forms.DateField(
        label=_("Before"),
        required=False,
        widget=forms.DateInput(
            # ISO date must be used with <input type=date> all times
            format="%Y-%m-%d",
            attrs={"class": "form-control form-control-sm", "type": "date"},
        ),
    )

    created_after = forms.DateField(
        label=_("Created after"),
        required=False,
        widget=forms.DateInput(
            # ISO date must be used with <input type=date> all times
            format="%Y-%m-%d",
            attrs={"class": "form-control form-control-sm", "type": "date"},
        ),
    )

    created_before = forms.DateField(
        label=_("Before"),
        required=False,
        widget=forms.DateInput(
            # ISO date must be used with <input type=date> all times
            format="%Y-%m-%d",
            attrs={"class": "form-control form-control-sm", "type": "date"},
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

    tags = TagField(
        label=_("Tags"),
        required=False,
        widget=TagWidget(attrs={"class": "form-control form-control-sm"}),
        empty_value=None,
        # widget=forms.Select(attrs={"class": "custom-select custom-select-sm"}),
    )

    def previous_due_date(self):
        """Change the due date interval to the previous"""

        return self._offset_date_range("due_date_after", "due_date_before", -1)

    def next_due_date(self):
        """Change the due date interval to the next"""

        return self._offset_date_range("due_date_after", "due_date_before", 1)

    def previous_created_at(self):
        """Change the create date interval to the previous"""

        return self._offset_date_range("created_after", "created_before", -1)

    def next_created_at(self):
        """Change the create date interval to the next"""

        return self._offset_date_range("created_after", "created_before", 1)

    def _offset_date_range(self, after_field_name, before_field_name, direction):
        """
        Change a date interval by the same range

        If the range includes x days, change to the next/previous x days.
        If the range includes *exactly* x months, change to the next/previous x months.

        Note: this method modifies the form instance in-place.
        """

        if self.cleaned_data:
            after: date = self.cleaned_data.get(after_field_name)
            before: date = self.cleaned_data.get(before_field_name)

            if after is not None and before is not None:
                # Avoid modifying the data argument passed in to the form
                data = self.data.copy()

                # Compute the new interval
                if _is_full_month(after, before):
                    # The range was from beginning to end of month -> step by months
                    diff_months = direction * (_diff_months(after, before) + 1)
                    new_after = _add_months(after, diff_months)
                    new_before = _add_months(before, diff_months)
                else:
                    # Otherwise step by the number of days included in the range
                    diff = direction * (before - after + timedelta(days=1))
                    new_after = after + diff
                    new_before = before + diff

                # Update the parsed and display value of after
                format_after = self.fields[after_field_name].widget.format_value
                data[after_field_name] = format_after(new_after)
                self.cleaned_data[after_field_name] = new_after

                # Update the parsed and display value of before
                format_before = self.fields[before_field_name].widget.format_value
                data[before_field_name] = format_before(new_before)
                self.cleaned_data[before_field_name] = new_before

                self.data = data


def _is_full_month(after: date, before: date) -> bool:
    """Is the given range one or more full months?"""

    (_, end_of_month) = calendar.monthrange(before.year, before.month)
    return after.day == 1 and before.day == end_of_month


def _diff_months(after: date, before: date) -> int:
    """The number of months between two dates"""

    return (before.year - after.year) * 12 + before.month - after.month


def _add_months(source_date: date, months: int) -> date:
    """
    Offset source_date by the given number of months.

    Only works with the last or first day of the month!
    """

    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = (
        source_date.day if source_date.day == 1 else calendar.monthrange(year, month)[1]
    )
    return date(year, month, day)
