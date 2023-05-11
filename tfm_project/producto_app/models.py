from django.db import models
import datetime

# Create your models here.

#puede ser Producto o Servicio
class TipoProducto(models.Model):
    nom_tipproducto = models.CharField(max_length=264)

    def __str__(self): return "%s" % (self.nom_tipproducto)

class Producto(models.Model):
    sku_producto =  models.CharField(max_length=264)
    nom_producto = models.CharField(max_length=264)
    canal_producto = models.CharField(max_length=264)
    tip_producto = models.ForeignKey(TipoProducto,on_delete=models.CASCADE)
    des_producto = models.CharField(max_length=264)
    fec_crea_producto = models.DateField(default=datetime.date.today)

class VariacionProducto(models.Model):
    sku_producto = models.CharField(max_length=264)
    nom_producto = models.CharField(max_length=264)
    pes_producto = models.FloatField()
    lar_producto = models.FloatField()
    anc_producto = models.FloatField()
    prof_producto = models.FloatField()
    prod_asociado = models.ForeignKey(Producto,on_delete=models.CASCADE)


