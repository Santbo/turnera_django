from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario (AbstractUser):
    es_emprendedor = models.BooleanField(default = False)
    fecha_creacion = models.DateTimeField()
    telefono = models.CharField(max_length=20, blank=True, null= True)

    def activar_emprendedor(self):

        self.es_emprendedor = True
        self.save()


class Emprendimiento (models.Model):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="emprendimiento") 
    nombre = models.CharField(max_length=45, null=False)
    codigo_busqueda = models.CharField(max_length=255, null=False, unique=True)
    direccion = models.CharField(max_length=255) #Agrego 255 para copiar link de maps
    telefono =  models.CharField(max_length=20, blank=True, null= True)
    rubro = models.CharField(max_length=45)
    descripcion = models.TextField(blank=True, null=True)