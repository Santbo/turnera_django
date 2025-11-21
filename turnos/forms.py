from django import forms
from django.forms import formset_factory
from .models import Horario

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ["inicio", "fin"]

HorarioFormSet = formset_factory(HorarioForm, extra=1, can_delete=True)
