from django.urls import path
from .views import HorariosAPIView, HorariosView
from django.views.generic import TemplateView

app_name = "turnos"
urlpatterns = [
    path(
        "horarios/",
        HorariosView.as_view(),
        name="horarios",
    ),
    path("api/horarios/", HorariosAPIView.as_view(), name="api_horarios"),
]
