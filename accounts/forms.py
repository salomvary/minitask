from django.contrib.auth import forms as auth_forms


class AuthenticationForm(auth_forms.AuthenticationForm):
    """Customized login form"""

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Add mandatory Bootstrap.css class to inputs
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        # Focus username input by default
        self.fields["username"].widget.attrs["autofocus"] = True
