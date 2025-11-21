
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Emprendimiento
from .forms import UsuarioCreationForm, UsuarioChangeForm

admin.site.register(Emprendimiento, admin.ModelAdmin)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario

    readonly_fields = ("fecha_creacion",)

    list_display = ("username", "email", "first_name", "last_name", "es_emprendedor", "is_staff")
    list_filter = ("es_emprendedor", "is_staff", "is_superuser")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email", "telefono")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Estado emprendedor", {"fields": ("es_emprendedor",)}),
        ("Fechas importantes", {"fields": ("last_login", "fecha_creacion")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "telefono", "es_emprendedor", "password1", "password2"),
        }),
    )

    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
