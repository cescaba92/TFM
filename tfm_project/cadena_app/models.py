from django.db import models
import datetime
from producto_app.models import Producto


# Create your models here.

class FuenteEnergia(models.Model):
    nom_energia = models.CharField(max_length=264)
    co2_energia = models.FloatField()
    Nox_energia = models.FloatField()
    so2_energia = models.FloatField()
    h25_energia = models.FloatField()
    pm_energia = models.FloatField()
    co60_energia = models.FloatField()

    def __str__(self): return "%s" % (self.nom_energia)

class MidpointTierra(models.Model):
    nom_tipouso = models.CharField(max_length=264)
    cfm_tipouso = models.FloatField()

    def __str__(self): return "%s" % (self.nom_tipouso)

class CadenaSuministro(models.Model):
    prod_asociado = models.OneToOneField(Producto,on_delete=models.CASCADE)
    fuente_energia = models.ForeignKey(FuenteEnergia,on_delete=models.CASCADE)
    tierra_ocupada = models.ForeignKey(MidpointTierra,on_delete=models.CASCADE)
    tierra_m2 = models.FloatField()


