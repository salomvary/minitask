from tasks.models import Note
from django.forms import ModelForm


class NoteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Note
        fields = ("body",)
