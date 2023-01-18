from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import MacroUser


class MacroUserCreationForm(UserCreationForm):

    class Meta:
        model = MacroUser
        fields = ("email",)


class MacroUserChangeForm(UserChangeForm):

    class Meta:
        model = MacroUser
        fields = ("email",)

