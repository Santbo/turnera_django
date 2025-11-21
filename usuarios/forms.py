from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class RegistroUsuarioForm(UserCreationForm):

    class Meta:

        model = Usuario
        fields = ["username", "password1", "password2", "first_name", "last_name", "email", "telefono"]


class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "telefono",
            "es_emprendedor",
        )


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "telefono",
            "es_emprendedor",
            "is_active",
            "is_staff",
        )
