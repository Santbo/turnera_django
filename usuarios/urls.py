from django.urls import path, reverse_lazy
from .views import ActivarEmprendimientoView, EmprendimientoView, RegistroUsuarioView, LoginUsuarioView, PerfilUsuarioView, CambiarPasswordView
from django.contrib.auth.views import LogoutView



app_name="usuarios"
urlpatterns = [
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("usuarios:login")), name="logout"),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil"),
    path("seguridad/", CambiarPasswordView.as_view(), name="seguridad"),
    path("emprendimiento/", EmprendimientoView.as_view(), name="emprendimiento"),
    path("emprendimiento/activar/", ActivarEmprendimientoView.as_view(),name="activar_emprendimiento")


]


