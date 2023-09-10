from django.db import models
import datetime

# Create your models here.

class TipoProveedor(models.Model):
    nom_tipoproveedor = models.CharField(max_length=264)

    def __str__(self): return "%s" % (self.nom_tipoproveedor)

class TipoSuministro(models.Model):
    nom_tiposuministro = models.CharField(max_length=264)

    def __str__(self): return "%s" % (self.nom_tiposuministro)


class Proveedor(models.Model):
    nom_proveedor = models.CharField(max_length=264)
    nif_proveedor = models.CharField(max_length=9)
    dir_proveedor = models.CharField(max_length=264)
    cont_nom_proveedor = models.CharField(max_length=264)
    cont_tel_proveedor = models.CharField(max_length=264)
    cont_mai_proveedor = models.EmailField(max_length=264)
    tip_proveedor = models.ForeignKey(TipoProveedor,on_delete=models.CASCADE)
    com_proveedor = models.CharField(max_length=264,blank=True,null=True)

    def __str__(self): return "%s" % (self.nom_proveedor)

class Suministro(models.Model):
    sku_suministro = models.CharField(max_length=264)
    nom_suministro = models.CharField(max_length=264)
    tip_suministro = models.ForeignKey(TipoSuministro,on_delete=models.CASCADE)
    prov_suministro = models.ForeignKey(Proveedor,on_delete=models.CASCADE)

    def __str__(self): return "%s" % (self.nom_suministro)

class Equipos(models.Model):
    ACTIVO = "AC"
    MANTENIMIENTO = "MA"
    REPARACION = "RE"
    FUERA_SERVICIO = "FS"
    ESTADOS_EQUIPOS = [
        (ACTIVO, "Activo"),
        (MANTENIMIENTO, "Mantenimiento"),
        (REPARACION, "Reparacion"),
        (FUERA_SERVICIO, "Fuera de Servicio")
    ]

    nom_equipo = models.CharField(max_length=264)
    fabr_equipo = models.CharField(max_length=264)
    ser_equipo = models.CharField(max_length=264)
    fec_adqui_equipo = models.DateField()
    vida_equipo = models.IntegerField()
    est_equipo  = models.CharField(
        max_length=2,
        choices=ESTADOS_EQUIPOS,
        default=ACTIVO,
    )    
    ubi_equipo = models.CharField(max_length=264)
    gar_equipo = models.IntegerField()
    prov_equipo = models.ForeignKey(Proveedor,on_delete=models.CASCADE)
    potencia_equipo = models.FloatField(default=0)

    def __str__(self): return "%s" % (self.nom_equipo)