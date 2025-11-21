import uuid
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import EmprendimientoForm, RegistroUsuarioForm, PerfilUsuarioForm
from .models import Usuario, Emprendimiento

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

class CambiarPasswordView(PasswordChangeView):
    template_name = "seguridad.html"
    success_url = reverse_lazy("usuarios:login")


class EmprendimientoView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user

        # Si NO activó emprendimiento → Mostrar panel de activación
        if not user.es_emprendedor:
            return render(request, "activar_emprendimiento.html")

        # Si activó, debe tener emprendimiento
        try:
            emp = user.emprendimiento
        except Emprendimiento.DoesNotExist:
            # seguridad ante inconsistencias
            emp = Emprendimiento.objects.create(
                usuario=user,
                codigo_busqueda=str(uuid.uuid4())[:8],
            )

        form = EmprendimientoForm(instance=emp)
        return render(request, "perfil_emprendimiento.html", {"form": form})

    def post(self, request):
        user = request.user

        if not user.es_emprendedor:
            return redirect("usuarios:emprendimiento")  # no debería publicar

        emp = user.emprendimiento
        form = EmprendimientoForm(request.POST, request.FILES, instance=emp)

        if form.is_valid():
            form.save()
            return redirect("usuarios:emprendimiento")

        return render(request, "perfil_emprendimiento.html", {"form": form})
    
class ActivarEmprendimientoView(LoginRequiredMixin, View):

    def post(self, request):
        user = request.user

        # Si ya está activado, no hacer nada
        if user.es_emprendedor:
            return redirect("usuarios:emprendimiento")

        # Activar emprendimiento
        user.es_emprendedor = True
        user.save()

        return redirect("usuarios:emprendimiento")