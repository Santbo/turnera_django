from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from django.forms import ValidationError


class Servicio(models.Model):
    emprendedor = models.ForeignKey(
        "usuarios.Emprendimiento",
        on_delete=models.CASCADE,
        related_name="servicios"
    )

    nombre = models.CharField(
        max_length=120,
        null=False,
        blank=False
    )

    duracion = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Duración del servicio en minutos."
    )

    precio = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Precio del servicio (no puede ser negativo)."
    )

    color = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Debe ser un color hex válido, por ejemplo #FF5733",
            )
        ],
        help_text="Color del servicio en el calendario."
    )

    activo = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.emprendedor})"


class Horario(models.Model):
    DIA_SEMANA = (
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    )

    emprendedor = models.ForeignKey(
        "usuarios.Emprendimiento",
        on_delete=models.CASCADE,
        related_name="horarios"
    )

    dia_semana = models.IntegerField(
        choices=DIA_SEMANA,
        validators=[
            MinValueValidator(
                limit_value=0,
                message="Se intentó ingresar un día de la semana negativo"
            ),
            MaxValueValidator(
                limit_value=6,
                message="Se intentó ingresar un día de la semana que no existe (mayor a domingo)."
            )
        ],
        verbose_name="Día de la semana"
    )

    intervalo = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                limit_value=5,
                message="El intervalo tiene que ser de por lo menos 5 minutos."
            )
        ]
    )

    inicio = models.TimeField(
        verbose_name="Hora de inicio"
    )
    fin = models.TimeField(
        verbose_name="Hora de fin"
    )

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ["dia_semana", "inicio"]

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.inicio} - {self.fin}"

    def clean(self):
        # Validar inicio < fin
        if self.inicio >= self.fin:
            raise ValidationError(f"En el horario de {self.inicio.strftime("%H:%M")} a {self.fin.strftime("%H:%M")}, la hora de inicio debe ser anterior a la hora de fin.")

        # Validar solapamiento con otros horarios del mismo emprendedor y día
        superpuestos = Horario.objects.filter(
            emprendedor=self.emprendedor,
            dia_semana=self.dia_semana
        ).exclude(pk=self.pk).filter(
            inicio__lt=self.fin,
            fin__gt=self.inicio
        )

        if superpuestos.exists():
            raise ValidationError(f"El horario de {self.inicio.strftime("%H:%M")} a {self.fin.strftime("%H:%M")} se solapa con otro horario existente ese mismo día.")


class Turno(models.Model):
    ESTADOS = [
        ("reservado", "Reservado"),
        # ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
    ]

    emprendedor = models.ForeignKey(
        "usuarios.Emprendimiento",
        on_delete=models.CASCADE,
        related_name="turnos",
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="turnos",
    )
    inicio = models.DateTimeField(
        verbose_name="Fecha y hora de inicio"
    )
    fin = models.DateTimeField(
        verbose_name="Fecha y hora de fin"
    )
    cliente_nombre = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Nombre del cliente"
    )
    cliente_contacto = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Contacto del cliente"
    )
    nota = models.TextField(
        null=True,
        blank=True
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS, 
        default="reservado",
    )
    cliente = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="turnos_creados",
    )

    def clean(self):
        if self.fin <= self.inicio:
            raise ValidationError("La fecha y hora de fin debe ser posterior a la de inicio.")

        # Si no lo sacó un cliente, entonces se tiene que tener un nombre del cliente
        if not self.cliente and not self.cliente_nombre:
            raise ValidationError(
                "Si no está asignado un usuario (cliente), los campos 'Nombre del cliente' deben estar completos."
            )

    def __str__(self):
        return f"Turno {self.id} - {self.emprendedor} - {self.inicio} a {self.fin}"