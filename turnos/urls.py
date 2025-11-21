from django.urls import path
from django.views.generic import TemplateView
from .views import (
    HorariosAPIView,
    HorariosView,
    ServicioCreateView,
    ServicioUpdateView,
    ServiciosAPIView,
    ServicioDeleteView,
    TurnosEmprendedorAPIView
)

app_name = "turnos"
urlpatterns = [
    path("horarios/", HorariosView.as_view(), name="horarios"),
    path("api/horarios/", HorariosAPIView.as_view(), name="api_horarios"),
    path("servicios/", ServicioCreateView.as_view(), name="listado_servicios"),
    path("api/servicios/", ServiciosAPIView.as_view(), name="api_servicios"),
    path("servicios/<int:pk>/editar/", ServicioUpdateView.as_view(), name="edicion_servicio",), #! Si esto cambia, hay que cambiar el js del template de servicios
    path("servicios/<int:pk>/eliminar/", ServicioDeleteView.as_view(), name="eliminar_servicio",), #! Si esto cambia, hay que cambiar el js del template de servicios
    path("emprendedor/", TemplateView.as_view(template_name="turnos_emprendedor.html"), name="turnos_emprendedor"),
    path("api/turnos/emprendedor", TurnosEmprendedorAPIView.as_view(), name="api_turnos_emprendedor"),
]
