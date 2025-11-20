from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistroUsuarioForm, PerfilUsuarioForm
from .models import Usuario

class RegistroUsuarioView(CreateView):
    template_name = "registro.html"
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('usuarios:login')  # redirige al login después de registrarse


class LoginUsuarioView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:        # si es admin
            return reverse_lazy("admin:index")
        return reverse_lazy("base:index") 
    
class PerfilUsuarioView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = PerfilUsuarioForm
    template_name = "perfil.html"
    success_url = reverse_lazy("usuarios:perfil")

    def get_object(self):
        return self.request.user
