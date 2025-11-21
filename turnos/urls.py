from django.urls import path
from .views import (
    HorariosAPIView,
    HorariosView,
    ServicioListCreateView,
    ServicioUpdateView,
    ServicioDeleteView,
)

app_name = "turnos"
urlpatterns = [
    path(
        "horarios/",
        HorariosView.as_view(),
        name="horarios",
    ),
    path("api/horarios/", HorariosAPIView.as_view(), name="api_horarios"),
    path("servicios/", ServicioListCreateView.as_view(), name="listado_servicios"),
    path(
        "servicios/<int:pk>/editar/",
        ServicioUpdateView.as_view(),
        name="edicion_servicio",
    ),
    path(
        "servicios/<int:pk>/eliminar/",
        ServicioDeleteView.as_view(),
        name="eliminar_servicio",
    ),
]
