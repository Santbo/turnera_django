from django.contrib import admin
from .models import Servicio, Horario, Turno


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "emprendedor", "duracion", "precio", "activo")
    list_filter = ("emprendedor", "activo")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("emprendedor", "dia_semana", "inicio", "fin", "intervalo")
    list_filter = ("emprendedor", "dia_semana")
    search_fields = ("emprendedor__nombre",)
    ordering = ("dia_semana", "inicio")


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "emprendedor",
        "servicio",
        "inicio",
        "fin",
        "estado",
        "cliente",
        "cliente_nombre",
    )
    list_filter = ("estado", "emprendedor", "servicio")
    search_fields = ("cliente_nombre", "cliente_contacto", "servicio", "nota")
    ordering = ("-inicio",)