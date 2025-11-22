import json
from datetime import datetime, timedelta
from math import ceil

from django.utils.timezone import make_aware, localtime
from django.views import View
from django.db import transaction
from django.http import  JsonResponse
from django.core.exceptions import ValidationError
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist

from .models import Servicio, Horario, Turno
from .forms import ServicioForm


# TODO: Esto debería tener un loginrequired y evitar xss

# ! ------------------------------ Horarios -----------------------------------------
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


# ! --------------------------- Servicios -------------------------------------------

class ServiciosAPIView(View):
    """
    Obtener la lista de servicios del emprendedor.

    Usada para el listado de servicios en /turnos/servicios
    """

    def get(self, request, *args, **kwargs):
        usuario = request.user

        if not usuario.es_emprendedor:
            return JsonResponse({"error": "El usuario no es emprendedor"}, status=403)

        servicios = Servicio.objects.filter(emprendedor = usuario.emprendimiento)

        respuesta = [
            {
                "id": s.id,
                "nombre": s.nombre,
                "duracion": s.duracion,
                "precio": s.precio,
                "color": s.color
            } for s in servicios
        ]

        return JsonResponse({"servicios": respuesta}, safe=False)


class ServicioCreateView(CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "servicios.html"
    success_url = reverse_lazy("turnos:listado_servicios")

    def form_valid(self, form):
        servicio = form.save(commit=False)
        servicio.emprendedor = self.request.user.emprendimiento
        servicio.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


# ! ----------------------------------------- Turnos --------------------------------

class TurnosEmprendedorAPIView(View):
    """
    Obtener la lista de todos los turnos que tiene el emprendedor.

    ! Solo funciona para emprendedor.
    """

    def get(self, request, *args, **kwargs):
        usuario = request.user

        if not usuario.es_emprendedor:
            return JsonResponse({"error": "El usuario no es emprendedor"}, status=403)

        turnos = Turno.objects.filter(emprendedor = usuario.emprendimiento)

        respuesta = [
            {
                "id": t.id,
                "servicio": {
                    "nombre": t.servicio.nombre,
                    "duracion": t.servicio.duracion,
                    "precio": t.servicio.precio,
                    "color": t.servicio.color
                },
                "turno": {
                    "inicio": t.inicio,
                    "fin": t.fin,
                    "nota": t.nota,
                    "estado": t.estado
                },
                "cliente": {
                    "nombre": t.cliente.nombre_completo if t.cliente != None else t.cliente_nombre,
                    "contacto": t.cliente.telefono if t.cliente != None else t.cliente_contacto
                }

            } for t in turnos
        ]

        return JsonResponse({"turnos": respuesta}, safe=False)
    

# TODO: Estas vistas funcionan unicamente para el emprendedor porque dependen de su 
# id, que viene en la request. Los templates que vayan a ser para el usuario deben agregar la id del
# emprendedor en algun lado.
class DiasQueTrabajaEmprendedorAPIView(View):
    """
    Obtener la lista de todos los días (del 0 al 6) que trabaja el emprendedor.

    ! Solo funciona para emprendedor.
    """

    def get(self, request, *args, **kwargs):
        usuario = request.user

        if not usuario.es_emprendedor:
            return JsonResponse({"error": "El usuario no es emprendedor"}, status=403)

        horarios = Horario.objects.filter(emprendedor = usuario.emprendimiento)

        respuesta = list({ h.dia_semana for h in horarios })

        return JsonResponse({"dias_trabajados": respuesta}, safe=False)
    

class HorariosDisponiblesSegunTurnoEmprendedorAPIView(View):
    """
    Obtener la lista de los horarios disponibles para el servicio que se solicitó.

    # ! Solo funciona para emprendedor.

    ## Funcionamiento:

    Se tiene que:
        1. Tomar la fecha que se recibió y obtener todos posibles inicios en las franjas horarias que tiene la fecha
            1.1 Para cada franja horaria, se comienza desde su inicio y se van sumando el intervalo hasta su final,
                Esto genera una lista con horas de inicio, que son todas las horas en las que puede iniciar un turno.

        2. Debido a que los turnos unicamente pueden iniciar en una hora de inicio (no pueden, por ejemplo, iniciar a las 12:03), 
            podemos tomar todos los turnos que se hayan sacado para el día, y obtener sus horas de inicio, las cuales 
            siempre van a coincidir con un intervalo. Una vez que se tienen sus tiempos de inicio, se tiene que determinar los intervalos que ocupan.
            2.1 Esto se hace tomando la duración del servicio al que pertenece el turno y contando cuántos intervalos ocupa.
                siempre se tiene que redondear hacia arriba, porque la fragmentación interna siempre va a estar, y no podes
                permitir que un turno empiece mientras otro está todavía en curso.
                Esto se puede hacer simplemente haciendo `ocupados = ceil(duracion_turno / duracion_intervalo)`
            2.2 Una vez que se tiene la cantidad de intervalos que ocupan, se pueden marcar todos los intervalos desde su 
                hora de inicio hasta `ocupados`.
                Por ejemplo:
                    El servicio dura 45 minutos, el intervalo son 30 minutos, el turno empieza a las 08:00. Esto se repite para todos los turnos del día.
                    intervalos_del_dia = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30"] # El horario de ese día es de 08 a 12.
                    ocupados = ceil(turno.servicio / horario.intervalo) = ceil(45 / 30) = 2
                    intervalos_ocupados_por_turno = ["08:00", "08:30"]

            2.3 Una vez que se tiene la lista de intervalos ocupados, (y, por consecuente, la lista de intervalos disponibles), se tienen que filtrar
                los intervalos disponibles a aquellos que permitan que el turno se complete. Por ejemplo, si mi negocio cierra a las 18:00
                y viene un usuario a sacar un turno de dos horas a las 17:30, no se le debería permitir sacarlo.
                Esto se hace recorriendo la lista de intervalos disponibles, y para cada intervalo:
                    Se prueba si un turno de ese servicio que empieza en ese intervalo, tiene todos sus intervalos subsecuentes disponibles.
                    Por ejemplo, si el turno ocupa tres intervalos:
                        intervalos_disponibles = ["08:00", "08:30", "09:00", "09:30"]
                            Para el intervalo "08:00":
                                El turno ocuparía "08:00", "08:30", "09:00" -> se puede sacar porque todos esos están en intervalos_disponibles.
                            Para el intervalo "08:30":
                                El turno ocuparía "08:30", "09:00", "09:30" -> se puede sacar porque todos esos están en intervalos_disponibles.
                            Para el intervalo "09:00":
                                El turno ocuparía "09:00", "09:30", "10:00" -> no se puede sacar porque "10:00" no está en intervalos disponibles.
        3. Ahora que se tienen los intervalos disponibles filtrados, se los devuelve.

    FUNCION obtener_intervalos_disponibles(horarios_del_dia, turnos_del_dia, duracion_servicio):

        INTERVALOS_DEL_DIA = []
        DURACION_INTERVALO_DEL_DIA = horarios_del_dia[0].intervalo

        # -------------------------------------------
        # 1. GENERAR TODAS LAS HORAS DE INICIO DEL DÍA
        # -------------------------------------------
        PARA CADA horario EN horarios_del_dia:
            hora_actual = horario.inicio
            MIENTRAS hora_actual + horario.intervalo <= horario.fin:
                AGREGAR hora_actual A INTERVALOS_DEL_DIA
                hora_actual = hora_actual + horario.intervalo
        FIN PARA


        # -------------------------------------------
        # 2. MARCAR INTERVALOS OCUPADOS
        # -------------------------------------------

        INTERVALOS_OCUPADOS = []

        PARA CADA turno EN turnos_del_dia:

            hora_inicio_turno = turno.inicio
            indice = índice de hora_inicio_turno en INTERVALOS_DEL_DIA

            # Cuantos intervalos ocupa este turno
            cantidad_intervalos = CEIL(turno.duracion / DURACION_INTERVALO_DEL_DIA)

            PARA i DESDE 0 HASTA cantidad_intervalos - 1:
                AGREGAR INTERVALOS_DEL_DIA[indice + i] A INTERVALOS_OCUPADOS (si existe)
            FIN PARA

        FIN PARA


        # -------------------------------------------
        # 3. OBTENER INTERVALOS LIBRES
        # -------------------------------------------

        INTERVALOS_LIBRES = []

        PARA cada intervalo EN INTERVALOS_DEL_DIA:
            SI intervalo NO está en INTERVALOS_OCUPADOS:
                AGREGAR intervalo A INTERVALOS_LIBRES
        FIN PARA


        # -------------------------------------------
        # 4. FILTRAR POR DURACIÓN DEL SERVICIO
        #    (asegurar que el turno entra completo)
        # -------------------------------------------

        intervalos_necesarios = CEIL(duracion_servicio / DURACION_INTERVALO_DIA)

        INTERVALOS_VALIDOS = []

        PARA cada intervalo INICIO_CANDIDATO EN INTERVALOS_LIBRES:

            indice = índice de INICIO_CANDIDATO en INTERVALOS_DEL_DIA
            puede = VERDADERO

            PARA i DESDE 0 HASTA intervalos_necesarios - 1:
                SI índice + i se sale de rango:
                    puede = FALSO
                    ROMPER

                SI INTERVALOS_DEL_DIA[indice + i] NO está en INTERVALOS_LIBRES:
                    puede = FALSO
                    ROMPER
            FIN PARA

            SI puede == VERDADERO:
                AGREGAR INICIO_CANDIDATO A INTERVALOS_VALIDOS

        FIN PARA


        RETORNAR INTERVALOS_VALIDOS
    FIN FUNCION
    """



    def get(self, request, id_servicio: int, fecha_solicitada: str, *args, **kwargs):
        usuario = request.user

        if not usuario.es_emprendedor:
            return JsonResponse({"error": "El usuario no es emprendedor"}, status=403)

        try:
            fecha_dt = make_aware(datetime.strptime(fecha_solicitada, "%Y-%m-%d")).date()
            servicio = Servicio.objects.get(pk = id_servicio)
        except ValueError:
            return JsonResponse({"error": "Fecha inválida"}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Servicio inexistente"}, status=400)

        #* -------------------------------- Generar todos los intervalos --------------------

        horarios = Horario.objects.filter(emprendedor = usuario.emprendimiento, dia_semana=fecha_dt.weekday())
        if not horarios:
            return JsonResponse({"error": "No hay horarios para el día seleccioando"}, status=400)

        intervalos_del_dia = []
        duracion_intervalo_dia = horarios[0].intervalo

        for horario in horarios:
            # Se tienen que combinar con la fecha para hacerlos datetime, porque 
            # no se le puede sumar un timedelta a time.
            # Se lo tiene que hacer aware también porque el servidor guarda como UTC-3
            # Si no se lo tiene en cuenta, se desfasa la hora. (te muestra que el turno es a las 11 en vez de a las 8)

            hora_actual = make_aware(datetime.combine(fecha_dt, horario.inicio))
            fin_dt = make_aware(datetime.combine(fecha_dt, horario.fin))
            while hora_actual + timedelta(minutes=horario.intervalo) <= fin_dt:
                intervalos_del_dia.append(hora_actual.time())
                hora_actual += timedelta(minutes=horario.intervalo)

        #* -------------------------------- Marcar intervalos ocupados ----------------------
        intervalos_ocupados = set()
        turnos_del_dia = Turno.objects.filter(emprendedor=usuario.emprendimiento, inicio__date = fecha_dt)
        # Como se pueden tener muchos turnos, es mas rapido pasarlos a un dccionario
        # para encontrar mas rapido el indice al que pertenecen
        mapa_indices = { hora: indice for indice, hora in enumerate(intervalos_del_dia) }


        for turno in turnos_del_dia:
            hora_inicio_turno = localtime(turno.inicio).time()
            try:
                indice = mapa_indices[hora_inicio_turno]
            except KeyError:
                # Esto pasa porque el emprendedor modificó un horario que tenía turnos, hay que ignorarlo nomas
                continue

            cantidad_intervalos = ceil(turno.servicio.duracion / duracion_intervalo_dia)

            for i in range(cantidad_intervalos):
                if indice + i < len(intervalos_del_dia):
                    #Esto no debería pasar nunca, porque en teoría
                    # no puede existir un turno cuyo intervalo caiga fuera de la hora
                    # de trabajo, porque no se podría haber sacado en un primer momento
                    intervalos_ocupados.add(intervalos_del_dia[indice + i])

        #* --------------------------------- Obtener intervalos libres ---------------------
        intervalos_libres = []
        for intervalo in intervalos_del_dia:
            if intervalo not in intervalos_ocupados:
                intervalos_libres.append(intervalo)

        #* -------------------------------- Filtrar por duración del servicio ---------------

        intervalos_necesarios = ceil(servicio.duracion / duracion_intervalo_dia)
        intervalos_validos = []

        for inicio_candidato in intervalos_libres:
            indice = mapa_indices[inicio_candidato]
            valido = True

            for i in range(intervalos_necesarios):

                if indice + i >= len(intervalos_del_dia):
                    # Se intentó acceder a un intervalo que no existe, imposible que 
                    # se pueda sacar turno
                    valido = False
                    break

                if intervalos_del_dia[indice + i] not in intervalos_libres:
                    # El turno ocupa intervalos que no están disponibles,
                    # no se puede sacar turno
                    valido = False
                    break

            if valido:
                intervalos_validos.append(inicio_candidato.strftime("%H:%M"))

        return JsonResponse({"horarios_disponibles": intervalos_validos}, safe=False)

