from django.urls import path
from .views import RegistroUsuarioView, LoginUsuarioView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

]
