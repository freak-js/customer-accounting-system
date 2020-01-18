from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import Manager


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Manager
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class UserChangeForm(ModelForm):
    class Meta:
        model = Manager
        fields = ('username', 'first_name', 'last_name')
