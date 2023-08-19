from django.db import models
import datetime
from producto_app.models import Producto
from suministro_app.models import Suministro


# Cadena General

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

#Suministros

class CadenaSuministro(models.Model):
    prod_asociado = models.OneToOneField(Producto,on_delete=models.CASCADE)
    fuente_energia = models.ForeignKey(FuenteEnergia,on_delete=models.CASCADE)
    tierra_ocupada = models.ForeignKey(MidpointTierra,on_delete=models.CASCADE)
    tierra_m2 = models.FloatField()

class Suministro_PlanCadena(models.Model):
    
    KILOGRAMOS = "KG"
    METROS_CUBICOS = "M3"
    LITROS = "L"
    METROS = "M"
    METROS_CUADRADOS = "M2"
    UNIDADES = "UN"

    TIPOS_UNIDADES = [
        (KILOGRAMOS,"kg"),
        (METROS_CUBICOS,"m³"),
        (LITROS,"L"),
        (METROS,"m"),
        (METROS_CUADRADOS,"m²"),
        (UNIDADES,"unidad")
    ]

    cadena_asociada = models.ForeignKey(CadenaSuministro,on_delete=models.CASCADE,null=True)
    suministro_asociado = models.ForeignKey(Suministro,on_delete=models.CASCADE)
    unidad_suministro = models.CharField(
        max_length=2,
        choices=TIPOS_UNIDADES,
        default=KILOGRAMOS,
    )    
    cantidad_suministro = models.FloatField()
    
class Midpoint_emision(models.Model):
    nom_midpoint = models.CharField(max_length=264)
    nom_emision = models.CharField(max_length=264)
    def __str__(self): return "%s" % (self.nom_emision)

class Sustancia_emision(models.Model):
    ATMOSFERA = "AT"
    TIERRA = "TI"
    AGUA_DULCE = "AD"
    OCEANOS = "AS"
    RECURSOS_FOSILES = "RF"
    CONSUMO_RECURSOS = "CR"

    TIPOS_DE_EMISIONES = [
        (ATMOSFERA, "Atmósfera"),
        (TIERRA, "Tierra"),
        (AGUA_DULCE, "Agua Dulce"),
        (OCEANOS, "Océanos"),
        (RECURSOS_FOSILES, "Recursos Fosiles"),
        (CONSUMO_RECURSOS,"Consumo Recursos")
    ]
    tipo_emision  = models.CharField(
        max_length=2,
        choices=TIPOS_DE_EMISIONES,
        default=ATMOSFERA,
    )    

    midpoint_emision = models.ForeignKey(Midpoint_emision,on_delete=models.CASCADE)
    componente_emision = models.CharField(max_length=264)
    unidad_emision = models.CharField(max_length=264)
    valor_emision = models.FloatField(default="Kg")

    def __str__(self): return "%s-%s" % (self.componente_emision,self.unidad_emision)

class SuministroEmision_PlanCadena(models.Model):
    sumcadena_asociado = models.ForeignKey(Suministro_PlanCadena,on_delete=models.CASCADE)
    sustancia_asociada = models.ForeignKey(Sustancia_emision, on_delete=models.CASCADE)
    cantidad_sustancia = models.FloatField()

#Tramos de Viaje Plan

class Energia_transporte(models.Model):
    nom_energiatransporte = models.CharField(max_length=264);

class Tipo_transporte(models.Model):
    nom_transporte = models.CharField(max_length=264);

class TramosExternos_PlanCadena(models.Model):
    cadena_asociada = models.ForeignKey(CadenaSuministro,on_delete=models.CASCADE,null=True)
    tipo_tramoexterno = models.ForeignKey(Tipo_transporte,on_delete=models.CASCADE,null=True)
    energia_tramoexterno = models.ForeignKey(Energia_transporte,on_delete=models.CASCADE,null=True)
    km_tramoexterno = models.FloatField()
    



