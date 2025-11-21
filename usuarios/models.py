from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario (AbstractUser):
    es_emprendedor = models.BooleanField(default = False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=20, blank=True, null= True)

    def activar_emprendedor(self):

        self.es_emprendedor = True
        self.save()

    @property
    def inicial_nombre(self):
        if len(self.first_name):
            return self.first_name[0]
        return "U"

    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}"


class Emprendimiento (models.Model):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="emprendimiento") 
    nombre = models.CharField(max_length=45, null=False)
    codigo_busqueda = models.CharField(max_length=255, null=False, unique=True)
    direccion = models.CharField(max_length=255) #Agrego 255 para copiar link de maps
    telefono =  models.CharField(max_length=20, blank=True, null= True)
    rubro = models.CharField(max_length=45)
    descripcion = models.TextField(blank=True, null=True)

    

    def __str__(self):
        return f"{self.nombre} ({self.usuario})"