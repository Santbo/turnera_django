from django import forms 
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroUsuarioForm(UserCreationForm):

    class Meta:

        model = Usuario
        fields = ["username", "password1", "password2", "first_name", "last_name", "email", "telefono"]