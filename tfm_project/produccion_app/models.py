from django.db import models
import datetime
from producto_app.models import Producto
from suministro_app.models import (Suministro,Equipos)
from cadena_app.models import (Sustancia_emision,Tipo_transporte,Energia_transporte,Sustancia_Midpoint_emision,Endpoint,FuenteEnergia,MidpointTierra)


# ============================================================
# Cabeceras de Ordenes
# ============================================================

class OrdenVenta(models.Model):
    REGISTRADO = "RE"
    PRODUCCION = "PR"
    ORDEN_ENVIO = "OE" 
    LISTO_ENVIO = "LE"
    ENTREGADO = "EN"
    CANCELADO = "CA"

    TIPOS_ESTADOS = [
        (REGISTRADO, "Registrado"),
        (PRODUCCION, "En Producción"),
        (ORDEN_ENVIO, "Preparando Envio"),
        (LISTO_ENVIO, "Enviado"),
        (ENTREGADO,"Completado"),
        (CANCELADO,"Cancelado")
    ]

    cod_venta =  models.CharField(max_length=50)
    fech_venta = models.DateField(default=datetime.date.today)
    cliente_venta = models.CharField(max_length=264)
    direccion_venta = models.CharField(max_length=264)
    fecha_entrega_venta = models.DateField()
    estado_venta = models.CharField(
        max_length=2,
        choices=TIPOS_ESTADOS,
        default=REGISTRADO,
    )    

class OrdenEntrega(models.Model):
    
    REGISTRADO = "RE"
    PREPARANDO = "PR"
    EN_ENVIO = "ON"
    COMPLETADO = "CO"
    CANCELADO = "CA"

    TIPOS_ESTADOS = [
        (REGISTRADO, "Registrado"),
        (PREPARANDO, "Preparando"),
        (EN_ENVIO, "Enviado"),
        (COMPLETADO, "Completado"),
        (CANCELADO,"Cancelado")
    ]

    orden_venta_entrega = models.ForeignKey(OrdenVenta,on_delete=models.CASCADE,null=True)
    direccion_entrega = models.CharField(max_length=264,null=True)
    fecha_entrega = models.DateField(default=datetime.date.today,null=True)
    contacto_entrega = models.CharField(max_length=264,null=True)
    observaciones_entrega = models.CharField(max_length=264,null=True,blank=True)
    fuente_energia = models.ForeignKey(FuenteEnergia,on_delete=models.CASCADE,null=True)
    estado_entrega  = models.CharField(
        max_length=2,
        choices=TIPOS_ESTADOS,
        default=REGISTRADO,
    )    



class DetalleOrdenVenta(models.Model):
    orden_venta_detalle = models.ForeignKey(OrdenVenta,on_delete=models.CASCADE,null=True)
    producto_detalle = models.ForeignKey(Producto,on_delete=models.CASCADE)
    cantidad_detalle = models.FloatField()

class OrdenProduccion(models.Model):
    REGISTRADO = "RE"
    PREPARANDO = "PR"
    COMPLETADO = "CO"
    CANCELADO = "CA"

    TIPOS_ESTADOS = [
        (REGISTRADO, "Registrado"),
        (PREPARANDO, "En Producción"),
        (COMPLETADO, "Completado"),
        (CANCELADO,"Cancelado")
    ]

    orden_venta_detalle = models.ForeignKey(DetalleOrdenVenta,on_delete=models.CASCADE,null=True)
    fecha_orden = models.DateField(default=datetime.date.today)
    estado_produccion = models.CharField(
        max_length=2,
        choices=TIPOS_ESTADOS,
        default=REGISTRADO,
    )
    fuente_energia = models.ForeignKey(FuenteEnergia,on_delete=models.CASCADE,null=True)
    tierra_ocupada = models.ForeignKey(MidpointTierra,on_delete=models.CASCADE,null=True)
    tierra_m2 = models.FloatField(null=True)



# ============================================================
# Suministros
# ============================================================

class OrdenSuministro(models.Model):
    REGISTRADO = "RE"
    PEDIDO = "PE"
    COMPLETADO = "CO"
    CANCELADO = "CA"

    TIPOS_ESTADOS = [
        (REGISTRADO, "Registrado"),
        (PEDIDO, "Pedido"),
        (COMPLETADO, "Completado"),
        (CANCELADO,"Cancelado")
    ]
    suministro_asociado = models.ForeignKey(Suministro,on_delete=models.CASCADE)
    orden_produccion = models.ForeignKey(OrdenProduccion,on_delete=models.CASCADE)
    cantidad_suministro = models.FloatField()
    estado_pedido_suministro = models.CharField(
        max_length=2,
        choices=TIPOS_ESTADOS,
        default=REGISTRADO,
    ) 

class SuministroEmision_Orden(models.Model):
    ordensuministro_asociado = models.ForeignKey(OrdenSuministro,on_delete=models.CASCADE)
    sustancia_asociada = models.ForeignKey(Sustancia_emision, on_delete=models.CASCADE)
    cantidad_sustancia = models.FloatField()


class SuministroTramos_Orden(models.Model):
    ordensuministro_asociado = models.ForeignKey(OrdenSuministro,on_delete=models.CASCADE)
    tipo_tramo = models.ForeignKey(Tipo_transporte,on_delete=models.CASCADE,null=True)
    energia_tramo = models.ForeignKey(Energia_transporte,on_delete=models.CASCADE,null=True)
    descripcion_tramo = models.CharField(max_length=264,null=True)
    km_tramo = models.FloatField()

# ============================================================
# Actividades
# ============================================================

class Actividad_Orden(models.Model):

    PLANIFICADO = "PL"
    EN_EJECUCION = "EN"
    CERRADO = "CO"

    ESTADO_ACTIVIDAD = [(PLANIFICADO,"Planificado"),(EN_EJECUCION,"En ejecución"),(CERRADO,"Completado")]

    produccion_asociada = models.ForeignKey(OrdenProduccion,on_delete=models.CASCADE,null=True)
    estado_actividad = models.CharField(
        max_length=2,
        choices=ESTADO_ACTIVIDAD,
        default=PLANIFICADO,
    )
    nom_actividad = models.CharField(max_length=264,null=True)
    equipo_asociado = models.ForeignKey(Equipos,on_delete=models.CASCADE,null=True,blank=True)
    tiempo_equipo_asociado = models.FloatField()

class ActividadEmision_Orden(models.Model):
    actividadorden_asociado = models.ForeignKey(Actividad_Orden,on_delete=models.CASCADE)
    sustancia_asociada = models.ForeignKey(Sustancia_emision, on_delete=models.CASCADE)
    cantidad_sustancia = models.FloatField()


# ============================================================
# Orden de Envio
# ============================================================

class Tramos_Orden(models.Model):

    INTERNO = "IN"
    EXTERNO = "EX"
    ENVIO = "EN"

    TIPO_TRANSPORTE = [(INTERNO,"Interno"),(EXTERNO,"Suministro"),(ENVIO,"Envio")]
 
    orden_envio_asociada = models.ForeignKey(OrdenEntrega,on_delete=models.CASCADE,null=True)
    tipo_tramoexterno = models.ForeignKey(Tipo_transporte,on_delete=models.CASCADE,null=True)
    energia_tramoexterno = models.ForeignKey(Energia_transporte,on_delete=models.CASCADE,null=True)
    descripcion_tramoexterno = models.CharField(max_length=264,null=True)
    km_tramoexterno = models.FloatField()

class Actividad_Envio(models.Model):

    PLANIFICADO = "PL"
    EN_EJECUCION = "EN"
    CERRADO = "CO"

    ESTADO_ACTIVIDAD = [(PLANIFICADO,"Planificado"),(EN_EJECUCION,"En ejecución"),(CERRADO,"Completado")]

    entrega_asociada = models.ForeignKey(OrdenEntrega,on_delete=models.CASCADE,null=True)
    estado_actividad = models.CharField(
        max_length=2,
        choices=ESTADO_ACTIVIDAD,
        default=PLANIFICADO,
    )
    nom_actividad = models.CharField(max_length=264,null=True)
    equipo_asociado = models.ForeignKey(Equipos,on_delete=models.CASCADE,null=True,blank=True)
    tiempo_equipo_asociado = models.FloatField()

class ActividadEmision_Envio(models.Model):
    actividadenvio_asociado = models.ForeignKey(Actividad_Envio,on_delete=models.CASCADE)
    sustancia_asociada = models.ForeignKey(Sustancia_emision, on_delete=models.CASCADE)
    cantidad_sustancia = models.FloatField()

# ============================================================
# Evaluacion de Impacto Orden de Producción
# ============================================================

class MidpointEmision_Orden(models.Model):
    TIERRA = "TI"
    SUMINISTRO = "SU"
    TRAMOS  = "TR"
    TRAMO_SUMINISTRO  = "TS"
    ACTIVIDADES = "AC"
    CONSUMO_EQUIPO = "CE"

    TIPO_MIDPOINT = [(TRAMO_SUMINISTRO,"Tramo Sumininstro"),(TIERRA,"Tierra"),(SUMINISTRO,"Suministro"),(TRAMOS,"Tramos"),(ACTIVIDADES,"Actividades"),(CONSUMO_EQUIPO,"Consumo de Equipo")]

    orden_asociada = models.ForeignKey(OrdenProduccion,on_delete=models.CASCADE,null=True)
    tipo_midpoint = models.CharField(
        max_length=2,
        choices=TIPO_MIDPOINT,
        default=SUMINISTRO,
    )
    #midpoints_emision_asociada = models.ForeignKey(Midpoint_emision,on_delete=models.CASCADE,null=True)
    suministroEmision_asociado = models.ForeignKey(SuministroEmision_Orden,on_delete=models.CASCADE,null=True)
    suministroTramos_asociado = models.ForeignKey(SuministroTramos_Orden,on_delete=models.CASCADE,null=True)
    tramos_envio = models.ForeignKey(Tramos_Orden,on_delete=models.CASCADE,null=True)
    actividademision_asociado = models.ForeignKey(ActividadEmision_Orden,on_delete=models.CASCADE,null=True)
    sustancia_midpoint_asociado = models.ForeignKey(Sustancia_Midpoint_emision,on_delete=models.CASCADE,null=True)
    actividad_asociada = models.ForeignKey(Actividad_Orden,on_delete=models.CASCADE,null=True)
    points_midpoint = models.FloatField()


class ProduccionCalculosEndpoint(models.Model):
    orden_asociada = models.ForeignKey(OrdenProduccion,on_delete=models.CASCADE,null=True)
    midpoint_endpoint = models.ForeignKey(Endpoint,on_delete=models.CASCADE,null=True)
    valor_real = models.FloatField()
    valor_pla  = models.FloatField()



# ============================================================
# Evaluacion de Impacto Orden de Envio
# ============================================================

class MidpointEmision_Entrega(models.Model):

    TRAMOS  = "TR"
    ACTIVIDADES = "AC"
    CONSUMO_EQUIPO = "CE"

    TIPO_MIDPOINT = [(TRAMOS,"Tramos"),(ACTIVIDADES,"Actividades"),(CONSUMO_EQUIPO,"Consumo de Equipo")]

    orden_asociada = models.ForeignKey(OrdenEntrega,on_delete=models.CASCADE,null=True)
    tipo_midpoint = models.CharField(
        max_length=2,
        choices=TIPO_MIDPOINT,
        default=TRAMOS,
    )
    tramos_envio = models.ForeignKey(Tramos_Orden,on_delete=models.CASCADE,null=True)
    actividademision_asociado = models.ForeignKey(ActividadEmision_Envio,on_delete=models.CASCADE,null=True)
    sustancia_midpoint_asociado = models.ForeignKey(Sustancia_Midpoint_emision,on_delete=models.CASCADE,null=True)
    actividad_asociada = models.ForeignKey(Actividad_Envio,on_delete=models.CASCADE,null=True)
    points_midpoint = models.FloatField()

class EnvioCalculosEndpoint(models.Model):
    envio_asociada = models.ForeignKey(OrdenEntrega,on_delete=models.CASCADE,null=True)
    midpoint_endpoint = models.ForeignKey(Endpoint,on_delete=models.CASCADE,null=True)
    valor_real = models.FloatField()
    valor_pla  = models.FloatField()



