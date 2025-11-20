from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from .forms import RegistroUsuarioForm

class RegistroUsuarioView(CreateView):
    template_name = "registro.html"
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('login')  # redirige al login después de registrarse


class LoginUsuarioView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:        # si es admin
            return reverse_lazy("admin:index")
        return reverse_lazy("base:index") 
    
