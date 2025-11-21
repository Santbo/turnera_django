from django.urls import path
from .views import RegistroUsuarioView, LoginUsuarioView, PerfilUsuarioView
from django.contrib.auth.views import LogoutView


app_name="usuarios"
urlpatterns = [
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil"),

]


