from django import forms
from django.forms import formset_factory
from .models import Servicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["nombre", "duracion", "precio", "color", "activo"]
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
        }
