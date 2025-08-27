from django.db import models

# Create your models here.


class Region(models.Model):
    nro_region = models.CharField(max_length=5)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.nombre} --- numero de region es. {self.nro_region}"  #valparaiso --- numero de region es.:  V

class Comuna(models.Model):
    nombre = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="comunas")

    def __str__(self):
        return f"{self.nombre} --- numero de region es. {self.region}"  #valparaiso --- numero de region es.:  V