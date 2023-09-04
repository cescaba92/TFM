from django.db import models
import datetime
from producto_app.models import Producto
from suministro_app.models import (Suministro,Equipos)


# ============================================================
# Cadena de Valor Plan & General
# ============================================================


class FuenteEnergia(models.Model):
    nom_energia = models.CharField(max_length=264)
    co2_energia = models.FloatField()
    nox_energia = models.FloatField()
    so2_energia = models.FloatField()
    pm_energia = models.FloatField()
    co60_energia = models.FloatField()

    def __str__(self): return "%s" % (self.nom_energia)

class MidpointTierra(models.Model):
    nom_tipouso = models.CharField(max_length=264)
    cfm_tipouso = models.FloatField()
    cfm_relax_tipouso = models.FloatField(null=True)

    def __str__(self): return "%s" % (self.nom_tipouso)

class CadenaSuministro(models.Model):
    prod_asociado = models.OneToOneField(Producto,on_delete=models.CASCADE)
    fuente_energia = models.ForeignKey(FuenteEnergia,on_delete=models.CASCADE)
    tierra_ocupada = models.ForeignKey(MidpointTierra,on_delete=models.CASCADE)
    tierra_m2 = models.FloatField()

# ============================================================
# Suministros Cadena de Valor Plan
# ============================================================

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

class Categoria_emision(models.Model):
    nom_categoria = models.CharField(max_length=264)
    def __str__(self): return "%s" % (self.nom_categoria)

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


    #midpoint_emision = models.ForeignKey(Midpoint_emision,on_delete=models.CASCADE)
    categoria_asociada = models.ForeignKey(Categoria_emision,on_delete=models.CASCADE,null=True)
    componente_emision = models.CharField(max_length=264)
    formula_emision = models.CharField(max_length=264)
    #valor_emision = models.FloatField(default="0")

    def __str__(self): return "%s-%s(%s)" % (self.tipo_emision,self.componente_emision,self.formula_emision)

class Sustancia_Midpoint_emision(models.Model):
    sustancia_emision = models.ForeignKey(Sustancia_emision,on_delete=models.CASCADE)
    midpoint_emision = models.ForeignKey(Midpoint_emision,on_delete=models.CASCADE)
    valor_emision = models.FloatField(default="0")

class SuministroEmision_PlanCadena(models.Model):
    sumcadena_asociado = models.ForeignKey(Suministro_PlanCadena,on_delete=models.CASCADE)
    sustancia_asociada = models.ForeignKey(Sustancia_emision, on_delete=models.CASCADE)
    cantidad_sustancia = models.FloatField()


# ============================================================
# Tramos Cadena de Valor Plan
# ============================================================

class Energia_transporte(models.Model):
    nom_energiatransporte = models.CharField(max_length=264);

    def __str__(self): return "%s" % (self.nom_energiatransporte)

class Tipo_transporte(models.Model):
    nom_transporte = models.CharField(max_length=264);

    def __str__(self): return "%s" % (self.nom_transporte)

class Tramos_PlanCadena(models.Model):

    INTERNO = "IN"
    EXTERNO = "EX"
    ENVIO = "EN"

    TIPO_TRANSPORTE = [(INTERNO,"Interno"),(EXTERNO,"Suministro"),(ENVIO,"Envio")]
 
    cadena_asociada = models.ForeignKey(CadenaSuministro,on_delete=models.CASCADE,null=True)
    tipo_transporte = models.CharField(
        max_length=2,
        choices=TIPO_TRANSPORTE,
        default=EXTERNO,
    )    
    tipo_tramoexterno = models.ForeignKey(Tipo_transporte,on_delete=models.CASCADE,null=True)
    energia_tramoexterno = models.ForeignKey(Energia_transporte,on_delete=models.CASCADE,null=True)
    descripcion_tramoexterno = models.CharField(max_length=264,null=True)
    km_tramoexterno = models.FloatField()
    
# ============================================================
# Actividades Cadena de Valor Plan
# ============================================================

class Actividad_PlanCadena(models.Model):

    PRODUCTIVA = "PR"
    ENVIO = "EN"

    TIPO_ACTIVIDAD = [(PRODUCTIVA,"Productiva"),(ENVIO,"Envio")]

    cadena_asociada = models.ForeignKey(CadenaSuministro,on_delete=models.CASCADE,null=True)
    tipo_actividad = models.CharField(
        max_length=2,
        choices=TIPO_ACTIVIDAD,
        default=PRODUCTIVA,
    )
    nom_actividad = models.CharField(max_length=264,null=True)
    equipo_asociado = models.ForeignKey(Equipos,on_delete=models.CASCADE,null=True)
    tiempo_equipo_asociado = models.FloatField()

class ActividadEmision_PlanCadena(models.Model):
    actividadplan_asociado = models.ForeignKey(Actividad_PlanCadena,on_delete=models.CASCADE)
    sustancia_asociada = models.ForeignKey(Sustancia_emision, on_delete=models.CASCADE)
    cantidad_sustancia = models.FloatField()

# ============================================================
# Algoritmos de Emisiones
# ============================================================

class MidpointEmision_PlanCadena(models.Model):
    TIERRAO = "TO"
    TIERRAR ="TX"
    SUMINISTRO = "SU"
    TRAMOS_NOX = "TN"
    TRAMOS_OTR  = "TR"
    ACTIVIDADES = "AC"
    CONSUMO_EQUIPO = "CE"

    TIPO_MIDPOINT = [(TIERRAO,"Tierra Ocupacion"),(TIERRAR,"Tierra Relax"),(SUMINISTRO,"Suministro"),(TRAMOS_NOX,"Tramos NOX"),(TRAMOS_OTR,"Tramos Otros"),(ACTIVIDADES,"Actividades"),(CONSUMO_EQUIPO,"Consumo de Equipo")]

    cadena_asociada = models.ForeignKey(CadenaSuministro,on_delete=models.CASCADE,null=True)
    tipo_midpoint = models.CharField(
        max_length=2,
        choices=TIPO_MIDPOINT,
        default=SUMINISTRO,
    )
    midpoints_emision_asociada = models.ForeignKey(Midpoint_emision,on_delete=models.CASCADE,null=True)
    suministroEmision_asociado = models.ForeignKey(SuministroEmision_PlanCadena,on_delete=models.CASCADE,null=True)
    tramos_PlanCadena = models.ForeignKey(Tramos_PlanCadena,on_delete=models.CASCADE,null=True)
    actividademision_asociado = models.ForeignKey(ActividadEmision_PlanCadena,on_delete=models.CASCADE,null=True)
    sustancia_midpoint_asociado = models.ForeignKey(Sustancia_Midpoint_emision,on_delete=models.CASCADE,null=True)
    actividad_asociada = models.ForeignKey(Actividad_PlanCadena,on_delete=models.CASCADE,null=True)
    points_midpoint = models.FloatField()

class MidpointTramos(models.Model):
    energia_transporte = models.ForeignKey(Energia_transporte,on_delete=models.CASCADE,null=True)
    Tipo_transporte = models.ForeignKey(Tipo_transporte,on_delete=models.CASCADE,null=True)
    co2_tramo = models.FloatField()
    nox_tramo = models.FloatField()
    pm_tramo = models.FloatField()
    