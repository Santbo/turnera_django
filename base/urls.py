from django.urls import path
from django.views.generic import TemplateView

app_name = "base"
urlpatterns = [
    path("", TemplateView.as_view(template_name="base/index.html"), name="index"),
    path("terminosycondiciones", TemplateView.as_view(template_name="base/terminos.html"), name="terminos"),
    path("privacidad", TemplateView.as_view(template_name="base/privacidad.html"), name="privacidad"),
    path("nosotros", TemplateView.as_view(template_name="base/nosotros.html"), name="nosotros"),


]