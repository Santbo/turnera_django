from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import RegistroUsuarioForm

class RegistroUsuarioView(FormView):
    template_name = "usuarios/registro.html"
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy("login")  # redirige al login después de registrarse

    def form_valid(self, form):
        form.save()  # guarda el nuevo usuario
        return super().form_valid(form)