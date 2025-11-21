import json
from django.views import View
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from .models import Servicio, Horario
from .forms import ServicioForm


# TODO: Esto debería tener un loginrequired y evitar xss


class HorariosAPIView(View):

    def get(self, request, *args, **kwargs):
        usuario = request.user

        if not usuario.es_emprendedor:
            return JsonResponse({"error": "El usuario no es emprendedor"}, status=403)

        horarios = Horario.objects.filter(emprendedor=usuario.emprendimiento).order_by(
            "dia_semana", "inicio"
        )

        # es mas facil crear todos los dias y dejarlos vacios que tener que verificar
        # en la ui si existen o no
        dias = [
            {
                "dia_semana": i,
                "bloques": [],
            }
            for i in range(7)
        ]

        for h in horarios:
            # hay que recorrer todos los horarios, y agregarlos como bloques en cada día
            dias[h.dia_semana]["bloques"].append(
                {
                    "inicio": h.inicio.strftime("%H:%M"),
                    "fin": h.fin.strftime("%H:%M"),
                }
            )

            # se tiene que agregar también el intervalo del día. cada horario tiene su
            # intervalo, asi que simplemente se lo agrega una vez y listo, porque
            # deberían ser siempre iguales
            if not dias[h.dia_semana].get("intervalo"):
                dias[h.dia_semana].update({"intervalo": h.intervalo})

        # convertir valores a lista ordenada por día

        return JsonResponse({"horarios": dias}, safe=False)

    def post(self, request, *args, **kwargs):

        # Nombre de los días para despues mostrarlo bien en el error
        dias = [
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo",
        ]

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        usuario = request.user

        if not usuario.es_emprendedor:
            return JsonResponse({"error": "El usuario no es emprendedor"}, status=403)

        horarios_data = data.get("horarios", [])
        intervalo = data.get("intervalo")

        with transaction.atomic():
            # Borrar horarios existentes del usuario
            Horario.objects.filter(emprendedor=usuario.emprendimiento).delete()

            for h in horarios_data:
                dia = h.get("dia_semana")
                intervalo = h.get("intervalo")
                bloques = h.get("bloques", [])

                for b in bloques:
                    horario = Horario(
                        emprendedor=usuario.emprendimiento,
                        dia_semana=dia,
                        intervalo=intervalo,
                        inicio=b.get("inicio"),
                        fin=b.get("fin"),
                    )

                    try:
                        horario.full_clean()
                        horario.save()
                    except ValidationError as e:
                        # cancelar toda la transacción
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {
                                "error": f"Error en el día {dias[dia]}: {e.messages[0]}",
                                "dia": dia,
                            },
                            status=422,
                        )

        return JsonResponse({"ok": True})


class HorariosView(TemplateView):
    template_name = "horarios.html"

    # Se tiene que pasarle un contexto con los días al template, porque si no hay que hacer todo el html a manopla.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dias"] = [
            (0, "Lunes"),
            (1, "Martes"),
            (2, "Miércoles"),
            (3, "Jueves"),
            (4, "Viernes"),
            (5, "Sábado"),
            (6, "Domingo"),
        ]
        return context


class ServicioListCreateView(CreateView, ListView):
    model = Servicio
    form_class = ServicioForm
    template_name = "servicios.html"
    success_url = reverse_lazy("turnos:listado_servicios")

    def get_queryset(self):
        return Servicio.objects.filter(emprendedor=self.request.user.emprendimiento)

    def form_valid(self, form):
        servicio = form.save(commit=False)
        servicio.emprendedor = self.request.user.emprendimiento
        servicio.save()
        return super().form_valid(form)

    # la listview necesita el context_object_name para saber qué nombre le pone a los datos
    # que tiene que mostrar
    context_object_name = "servicios"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Esto tiene que estar acá porque el template lo usa para saber si mostrar
        # el botón de cancelar edición, total se usa el mismo template para los dos
        context["editando"] = False
        return context


class ServicioUpdateView(UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "servicios.html"
    success_url = reverse_lazy("turnos:listado_servicios")

    def get_queryset(self):
        return Servicio.objects.filter(emprendedor=self.request.user.emprendimiento)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["servicios"] = Servicio.objects.filter(
            emprendedor=self.request.user.emprendimiento
        )
        context["editando"] = True
        context["servicio_editando"] = self.object
        return context


class ServicioDeleteView(View):
    def post(self, request, pk):
        servicio = get_object_or_404(
            Servicio,
            pk=pk,
            emprendedor=request.user.emprendimiento
        )
        servicio.delete()
        return redirect("turnos:listado_servicios")
