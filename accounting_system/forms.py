from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import Manager, CashMachine, ECP, OFD, FN, TO


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Manager
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class ManagerChangeForm(ModelForm):
    class Meta:
        model = Manager
        fields = ('username', 'first_name', 'last_name')


class CashMachineCreationForm(ModelForm):
    class Meta:
        model = CashMachine
        fields = ('model',)


class FNCreationForm(ModelForm):
    class Meta:
        model = FN
        fields = ('name', 'validity')


class TOCreationForm(ModelForm):
    class Meta:
        model = TO
        fields = ('name', 'validity')


class ECPCreationForm(ModelForm):
    class Meta:
        model = ECP
        fields = ('name', 'validity')


class OFDCreationForm(ModelForm):
    class Meta:
        model = OFD
        fields = ('model', 'validity')
