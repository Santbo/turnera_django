from django import forms 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import Emprendimiento, Usuario

class RegistroUsuarioForm(UserCreationForm):

    class Meta:

        model = Usuario
        fields = ["username", "password1", "password2", "first_name", "last_name", "email", "telefono"]

class PerfilUsuarioForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', "telefono", "imagen"]


class EmprendimientoForm(forms.ModelForm):
    class Meta:
        model = Emprendimiento
        fields = [
            "nombre",
            "codigo_busqueda",
            "direccion",
            "telefono",
            "rubro",
            "descripcion",
            "imagen",
        ]
