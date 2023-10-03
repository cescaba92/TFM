from django.shortcuts import (render, redirect)
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView,DeleteView)
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from django.db.models import Max
import logging 
from produccion_app.forms import (OrdenVentaForm,OrdenVentaDetalleFormSet,OrdenProduccionForm,SuministroOrdenFormSet,ActividadOrdenFormSet,SuministroViajesOrdenFormSet,
    SuministroEmisionOrdenFormSet,SuministroOrdenProduccionForm,Actividad_OrdenForm,ActividadOrdenFormSet,ActividadEmisionOrdenFormSet,OrdenEntregaForm,Actividad_EnvioForm,ActividadEmision_EnvioForm,
    Tramos_OrdenForm,TramosEnvioFormSet,ActividadEmisionEnvioFormSet,ActividadEnvioFormSet)
from produccion_app.models import (OrdenVenta,DetalleOrdenVenta,OrdenProduccion,OrdenSuministro,SuministroTramos_Orden,SuministroEmision_Orden,Actividad_Orden,ActividadEmision_Orden,
    Actividad_Orden,ActividadEmision_Orden,OrdenEntrega,Tramos_Orden,Actividad_Envio,ActividadEmision_Envio,ProduccionCalculosEndpoint,MidpointEmision_Orden
    ,EnvioCalculosEndpoint,MidpointEmision_Entrega)
from cadena_app.models import (CadenaSuministro,Suministro,Suministro_PlanCadena,SuministroEmision_PlanCadena,SuministroTramos_PlanCadena,Actividad_PlanCadena,ActividadEmision_PlanCadena,
    Categoria_emision,Sustancia_emision,CadenaCalculosEndpoint,Endpoint,MidpointEmision_PlanCadena,Sustancia_Midpoint_emision,MidpointEndpointFactor,CalculosEndpoint,MidpointTramos)
from suministro_app.models import (Suministro, Proveedor)


def calcularEndpoints(orden):

    try:
        cadena_calculos = ProduccionCalculosEndpoint.objects.filter(orden_asociada=orden)

        for cadena_calculo in cadena_calculos:
            cadena_calculo.valor_real = 0.00
            cadena_calculo.save()
    except ProduccionCalculosEndpoint.DoesNotExist:
        print("No existe ninguna cadena asociada")

    try:
        midpointEmisiones = MidpointEmision_Orden.objects.filter(orden_asociada=orden)
        for midpointEmision in midpointEmisiones:
            midpoint = midpointEmision.sustancia_midpoint_asociado.midpoint_emision
            factorEndpoints = MidpointEndpointFactor.objects.filter(midpoint=midpoint)

            for factorx in factorEndpoints:
                calculoendpoint = CalculosEndpoint.objects.get(id=factorx.calculosEndpoint.id)
                cadena_calculo = ProduccionCalculosEndpoint.objects.get(orden_asociada=orden,midpoint_endpoint=calculoendpoint.endpoint)
                valor_anterior = cadena_calculo.valor_real

                valor_agregar = midpointEmision.points_midpoint * factorx.factor
                nuevo_valor = valor_anterior + valor_agregar

                cadena_calculo.valor_real = nuevo_valor
                print(f"valor es: {nuevo_valor}")
                cadena_calculo.save()

    except MidpointEmision_Orden.DoesNotExist:
        print("No existe ninguna emision asociada a la cadena")

def calcularEndpointsEntrega(orden):

    try:
        cadena_calculos = EnvioCalculosEndpoint.objects.filter(envio_asociada=orden)

        for cadena_calculo in cadena_calculos:
            cadena_calculo.valor_real = 0.00
            cadena_calculo.save()
    except EnvioCalculosEndpoint.DoesNotExist:
        print("No existe ninguna cadena asociada")

    try:
        midpointEmisiones = MidpointEmision_Entrega.objects.filter(orden_asociada=orden)
        for midpointEmision in midpointEmisiones:
            midpoint = midpointEmision.sustancia_midpoint_asociado.midpoint_emision
            factorEndpoints = MidpointEndpointFactor.objects.filter(midpoint=midpoint)

            for factorx in factorEndpoints:
                calculoendpoint = CalculosEndpoint.objects.get(id=factorx.calculosEndpoint.id)
                cadena_calculo = EnvioCalculosEndpoint.objects.get(envio_asociada=orden,midpoint_endpoint=calculoendpoint.endpoint)
                valor_anterior = cadena_calculo.valor_real

                valor_agregar = midpointEmision.points_midpoint * factorx.factor
                nuevo_valor = valor_anterior + valor_agregar

                cadena_calculo.valor_real = nuevo_valor
                print(f"valor es: {nuevo_valor}")
                cadena_calculo.save()

    except MidpointEmision_Entrega.DoesNotExist:
        print("No existe ninguna emision asociada a la cadena")

# ============================================================
# Orden de Venta
# ============================================================

class OrdenesVentaListView(ListView):
    context_object_name = 'OrdenVenta_list'
    model = OrdenVenta
    template_name = 'produccion_app/ordenes_ventas.html'


class OrdenesVentaInLine():
    form_class = OrdenVentaForm
    model = OrdenVenta
    template_name = 'produccion_app/orden_venta.html'

    def form_invalid(self,form):
        print("error")

        return redirect('produccion_app:ordenes_venta')


    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("es aqui?")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()
        
        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
           
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        
        messages.success(
            self.request, 'Orden de Venta guardado'
            )
        return redirect('produccion_app:modificar_orden_venta', pk=self.object.id)

    def formset_detalles_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        print("entro aqui - Detalles")
        detalles = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for detalle in detalles:
            detalle.orden_venta_detalle = self.object
            print("entro aqui - xxx")
            detalle.save()


class OrdenesVentaCreateView(OrdenesVentaInLine, CreateView):
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            
            venta_last = OrdenVenta.objects.aggregate(Max('id'))
            numero_como_cadena = str(venta_last['id__max']+1) 
            numero_formateado = numero_como_cadena.zfill(5)
            resultado = "ORD" + numero_formateado

            form.fields['cod_venta'].initial = resultado
            form.estado = "Registrado"
            form.envio = -1

        except:
            form.fields['cod_venta'].initial = "ORD00001"
            form.estado = "Registrado"
            form.envio = -1
        

        return form

    def get_context_data(self, **kwargs):
        ctx = super(OrdenesVentaCreateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'detalles': OrdenVentaDetalleFormSet(prefix='detalles'), 
            }
        else:
            return {
                'detalles': OrdenVentaDetalleFormSet(self.request.POST or None, self.request.FILES or None, prefix='detalles'),
            }

class OrdenesVentaUpdateView(OrdenesVentaInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(OrdenesVentaUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        formsets = {
        'detalles': OrdenVentaDetalleFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='detalles'),
        }
        print("entro aqui 1")
        for formset_form in formsets['detalles'].forms:
            o_id = formset_form['id'].initial
            print("entro aqui 2")
            if o_id is not None:
                try:
                    orden_produccion = OrdenProduccion.objects.get(orden_venta_detalle=o_id)
                    formset_form.creado = 1
                    print(f"entro aqui 3: {orden_produccion.id}")
                    formset_form.producto = orden_produccion.orden_venta_detalle.producto_detalle.nom_producto
                    formset_form.cantidad = orden_produccion.orden_venta_detalle.cantidad_detalle
                    formset_form.estado = orden_produccion.get_estado_produccion_display()

                except OrdenProduccion.DoesNotExist:
                    formset_form.estado = "Sin Asignar"
                    print("error")

        return formsets


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        orden_id = self.kwargs.get('pk')
        orden = OrdenVenta.objects.get(id=orden_id)
        estado = orden.get_estado_venta_display()
        form.nro = orden.cod_venta
        form.estado = estado

        try:
            ordenEnvio = OrdenEntrega.objects.get(orden_venta_entrega=orden_id)
            form.estado_envio = ordenEnvio.get_estado_entrega_display()
            form.fecha_envio = ordenEnvio.fecha_entrega
            form.direccion_envio = ordenEnvio.direccion_entrega
            form.envio = ordenEnvio.id

        except OrdenEntrega.DoesNotExist:
            form.envio = -1

        return form

def terminar_ProduccionVenta(request,pk):
    try:
        orden = OrdenVenta.objects.get(id=pk)
    except OrdenVenta.DoesNotExist:
        messages.error(
            request, 'No existe la orden de venta. Consultar con el equipo de soporte.'
            )
        return redirect('produccion_app:modificar_orden_venta', pk=orden.id)

    detalles = DetalleOrdenVenta.objects.filter(orden_venta_detalle=orden)

    for detalle in detalles:
        try:
            ordenProduccion = OrdenProduccion.objects.get(orden_venta_detalle=detalle)
            estado = ordenProduccion.get_estado_produccion_display()
            print(f"estado: {estado}")
            if estado != "Completado" and estado != "Cancelado":
                messages.error(request, 'Existe ordenes de producción pendientes')
                return redirect('produccion_app:modificar_orden_venta', pk=orden.id)

        except OrdenProduccion.DoesNotExist:
            print(f"error ubicando la produccion del detalle: {detalle.id}")


    orden.estado_venta = "OE"
    orden.save()

    messages.success(
            request, 'La venta ha cambiado de estado con exito.'
            )
    return redirect('produccion_app:modificar_orden_venta', pk=orden.id)

def delete_DetalleOrdenVenta(request, pk):

    try:
        variant = DetalleOrdenVenta.objects.get(id=pk)
    except DetalleOrdenVenta.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:modificar_orden_venta', pk=variant.orden_venta_detalle.id)

    variant.delete()
    messages.success(
            request, 'Variant deleted successfully'
            )
    return redirect('produccion_app:modificar_orden_venta', pk=variant.orden_venta_detalle.id)

def delete_OrdenVenta(request,pk):
    try:
        orden = OrdenVenta.objects.get(id=pk)
    except OrdenVenta.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:ordenes_venta')

    detalles_venta = DetalleOrdenVenta.objects.filter(orden_venta_detalle=orden)
    
    for detalle in detalles_venta:
        try:
            ordenProduccion = OrdenProduccion.objects.get(orden_venta_detalle=detalle)
        except OrdenProduccion.DoesNotExist:
            messages.success(request, 'Orden de Producción no se encontro. Consultar con el soporte de la aplicacion.')
            return redirect('produccion_app:ordenes_venta')

        ordenesSuministro = OrdenSuministro.objects.filter(orden_produccion=ordenProduccion)
        for ordenSuministro in ordenesSuministro:
            suministroEmisiones = SuministroEmision_Orden.objects.filter(ordensuministro_asociado=ordenSuministro)    
            for emision in suministroEmisiones:
                emision.delete()

            suministroTramos = SuministroTramos_Orden.objects.filter(ordensuministro_asociado=ordenSuministro)
            for tramo in suministroTramos:
                tramo.delete()

            ordenSuministro.estado_pedido_suministro = "CA"
            ordenSuministro.save()

        actividades = Actividad_Orden.objects.filter(produccion_asociada=ordenProduccion)
        for actividad in actividades:
            actividadEmisiones = ActividadEmision_Orden.objects.filter(actividadorden_asociado=actividad)
            for emision in actividadEmisiones:
                emision.delete()

            actividad.delete()

        ordenProduccion.estado_produccion = "CA"
        ordenProduccion.save()
    
    ordenEntrega = OrdenEntrega.objects.get(orden_venta_entrega=orden)

    tramos = Tramos_Orden.objects.filter(orden_envio_asociada=ordenEntrega)
    for tramo in tramos:
        tramo.delete()

    actividades = Actividad_Envio.objects.filter(entrega_asociada=ordenEntrega)

    for actividad in actividades:
        actividadEmision = ActividadEmision_Envio.objects.filter(actividadenvio_asociado=actividad)
        for emision in actividadEmision:
            emision.delete()

        actividad.delete()

    ordenEntrega.estado_entrega = "CA"
    ordenEntrega.save()

    orden.estado_venta = "CA"
    orden.save()

    messages.success(
            request, 'Orden de Venta Cancelada'
            )
    return redirect('produccion_app:ordenes_venta')

def consultar_ordenProducción(request,pk):
    # try:
    #     detalle = DetalleOrdenVenta.objects.get(id=pk)
    #     orden = OrdenProduccion.objects.get(orden_venta_detalle=detalle)
    #     if orden is not None:
    #         return redirect(reverse('produccion_app:modificar_produccion', kwargs={'pk': orden.id}))

    # except OrdenProduccion.DoesNotExist:
    #     print("Error")

    detalle = DetalleOrdenVenta.objects.get(id=pk)
    orden = OrdenProduccion.objects.get(orden_venta_detalle=detalle)
    if orden is not None:
        return redirect(reverse('produccion_app:modificar_produccion', kwargs={'pk': orden.id}))

# ============================================================
# Orden de Produccion
# ============================================================
def limpiarEmisionesSuministro(suministroEmision):
    midpointsEmision = MidpointEmision_Orden.objects.filter(suministroEmision_asociado=suministroEmision)

    for midpointEmision in midpointsEmision:
        midpointEmision.delete()

def calcularemisionesSuministro(suministroEmision):
    
    orden = suministroEmision.ordensuministro_asociado.orden_produccion
    tipo_midpoint = "SU"
    suministroEmision_asociado = suministroEmision
    midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=suministroEmision.sustancia_asociada)
    
    limpiarEmisionesSuministro(suministroEmision_asociado)
    
    for midpoint in midpoints:
        #midpoints_emision_asociada = emision_midpoint.midpoint_emision
        points = midpoint.valor_emision * suministroEmision.cantidad_sustancia
        #print(f"Mi suministroEmision_asociado es {suministroEmision.id}")
        
        try:
            midpointEmision = MidpointEmision_Orden.objects.get(orden_asociada=orden,suministroEmision_asociado=suministroEmision_asociado,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint)
            midpointEmision.points_midpoint = points
            midpointEmision.save()

        except MidpointEmision_Orden.DoesNotExist:
            midpointEmision = MidpointEmision_Orden(orden_asociada=orden,suministroEmision_asociado=suministroEmision_asociado,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,points_midpoint=points)
            midpointEmision.save()

    calcularEndpoints(orden)     

def calcularemisionesTierra(id_cadena,midpointTierra,cantidad):  

    try:

        orden = OrdenProduccion.objects.get(id=id_cadena)
        tipo_midpoint = "TI"
        try:
            #categoria = Categoria_emision.objects.get(nom_categoria=midpointTierra.nom_tipouso)
            sustancia = Sustancia_emision.objects.get(componente_emision=midpointTierra.nom_tipouso)
            print(f"Mi sustancia es {sustancia.id}")
            limpiarEmisionesTierra(orden)
            midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=sustancia)
            for midpoint in midpoints:
                points = midpoint.valor_emision * cantidad
                print(f"Mi midpoint es {midpoint.id}")
                try:
                    midpointEmision = MidpointEmision_Orden.objects.get(orden_asociada=orden,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint)
                    midpointEmision.points_midpoint = points
                    midpointEmision.save()

                except MidpointEmision_Orden.DoesNotExist:
                    midpointEmision = MidpointEmision_Orden(orden_asociada=orden,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points)
                    midpointEmision.save()

            calcularEndpoints(orden)
        except Sustancia_emision.DoesNotExist:
            print("No se encontro sustancia emision con el nombre de la categoria")

    except CadenaSuministro.DoesNotExist:
        print("aun no hay cadena de Suministro")
    
def limpiarEmisionesTierra(orden):
    midpointsEmision = MidpointEmision_Orden.objects.filter(tipo_midpoint="TI",orden_asociada=orden)

    for midpointEmision in midpointsEmision:
        midpointEmision.delete()

def calcularEmisionesTramosSuministro(suministroTramos):
    print(f"Mi SuministroTramos_PlanCadena es {suministroTramos.id}")
    km_recorridos = suministroTramos.km_tramo
    
    try:
        midpointTramos = MidpointTramos.objects.get(energia_transporte=suministroTramos.energia_tramo,Tipo_transporte=suministroTramos.tipo_tramo)
        co2_tramo_point = midpointTramos.co2_tramo*km_recorridos
        nox_tramo_point = midpointTramos.nox_tramo*km_recorridos
        pm_tramo_point = midpointTramos.pm_tramo*km_recorridos

    except MidpointTramos.DoesNotExist:
        co2_tramo_point = 0.0
        nox_tramo_point = 0.0
        pm_tramo_point = 0.0

    puntos_a_revisar= [(settings.CODIGO_C02,co2_tramo_point),(settings.CODIGO_NOX,nox_tramo_point),(settings.CODIGO_PM,pm_tramo_point)]

    print("Genero duplas")
    orden = suministroTramos.ordensuministro_asociado.orden_produccion
    #tramo_PlanCadena = tramos_PlanCadena
    tipo_midpoint = "TS"


    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])
        print("entro a la dupla")
        for midpoint in midpoints:
            points = dupla[1]*midpoint.valor_emision
            print(f"esta aqui: {orden}")
            try:
                midpointEmision = MidpointEmision_Orden.objects.get(orden_asociada=orden,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,suministroTramos_asociado=suministroTramos)
                midpointEmision.points_midpoint = points
                midpointEmision.save()

            except MidpointEmision_Orden.DoesNotExist:
                midpointEmision = MidpointEmision_Orden(orden_asociada=orden,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,suministroTramos_asociado=suministroTramos,points_midpoint=points)
                midpointEmision.save()

    calcularEndpoints(orden) 

def calcularemisionEquipos(actividad_orden):
    print("entro a calcularemisionEquipos")
    uso_horas = actividad_orden.tiempo_equipo_asociado
    potencia = actividad_orden.equipo_asociado.potencia_equipo
    kilo_vatios_hora = (potencia/1000.0)*uso_horas

    fuente_energia = actividad_orden.produccion_asociada.fuente_energia
    co2_equipo_point = fuente_energia.co2_energia * kilo_vatios_hora
    nox_equipo_point = fuente_energia.nox_energia * kilo_vatios_hora
    so2_equipo_point = fuente_energia.so2_energia  * kilo_vatios_hora
    pm_equipo_point = fuente_energia.pm_energia * kilo_vatios_hora
    co60_equipo_point = fuente_energia.co60_energia * kilo_vatios_hora

    puntos_a_revisar = [(settings.CODIGO_C02,co2_equipo_point),(settings.CODIGO_NOX,nox_equipo_point),(settings.CODIGO_SO2,so2_equipo_point),(settings.CODIGO_PM,pm_equipo_point),(settings.CODIGO_CO60,co60_equipo_point)]

    orden = actividad_orden.produccion_asociada
    actividad = actividad_orden
    tipo_midpoint = "CE"

    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])

        for midpoint in midpoints:
            #midpoints_emision_asociada = midpoint.midpoint_emision
            points = dupla[1] * midpoint.valor_emision

            try:
                midpointEmision = MidpointEmision_Orden.objects.get(sustancia_midpoint_asociado=midpoint,orden_asociada=orden,tipo_midpoint=tipo_midpoint,actividad_asociada=actividad)
                midpointEmision.points_midpoint = points
                midpointEmision.save()
            except MidpointEmision_Orden.DoesNotExist:
                midpointEmision = MidpointEmision_Orden(orden_asociada=orden,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points,actividad_asociada=actividad)
                midpointEmision.save()

    calcularEndpoints(orden) 

def limpiarEmisionesActividades(actividadEmision):
    midpointsEmision = MidpointEmision_Orden.objects.filter(actividademision_asociado=actividadEmision)

    for midpointEmision in midpointsEmision:
        midpointEmision.delete()

def calcularemisionesActividades(actividadEmision):
    orden = actividadEmision.actividadorden_asociado.produccion_asociada
    tipo_midpoint = "AC"
    midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=actividadEmision.sustancia_asociada)
    actividademision_asociado = actividadEmision
    limpiarEmisionesActividades(actividademision_asociado)

    for midpoint in midpoints:
        #midpoint_emision_asociada = midpoint.midpoint_emision
        points = midpoint.valor_emision * actividadEmision.cantidad_sustancia

        try:
            midpointEmision = MidpointEmision_Orden.objects.get(orden_asociada=orden,sustancia_midpoint_asociado=midpoint,actividademision_asociado=actividademision_asociado,tipo_midpoint=tipo_midpoint)
            midpointEmision.points_midpoint = points
            midpointEmision.save()

        except MidpointEmision_Orden.DoesNotExist:
            midpointEmision = MidpointEmision_Orden(orden_asociada=orden,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points,actividademision_asociado=actividademision_asociado)
            midpointEmision.save()

    calcularEndpoints(orden) 

def nueva_ordenProduccion(request,pk):
    orden = DetalleOrdenVenta.objects.get(id=pk)
    print(f"Mi producto es {orden.producto_detalle}")

    try:
        cadena = CadenaSuministro.objects.get(prod_asociado=orden.producto_detalle)
        ordenProduccion = OrdenProduccion(orden_venta_detalle=orden,fuente_energia=cadena.fuente_energia,tierra_ocupada=cadena.tierra_ocupada,tierra_m2=cadena.tierra_m2)
        ordenProduccion.save()
        print(f"Mi cadena es {cadena.id}")
        #try:
        suministros = Suministro_PlanCadena.objects.filter(cadena_asociada=cadena)

        for suministro in suministros:
            print('entro al for')
            ordenSuministro = OrdenSuministro(suministro_asociado=suministro.suministro_asociado,orden_produccion=ordenProduccion,cantidad_suministro=suministro.cantidad_suministro*orden.cantidad_detalle)
            ordenSuministro.save()
            emisionesSuministro = SuministroEmision_PlanCadena.objects.filter(sumcadena_asociado=suministro)

            for emisiones in emisionesSuministro:
                
                suministroEmision_Orden = SuministroEmision_Orden(ordensuministro_asociado=ordenSuministro,sustancia_asociada=emisiones.sustancia_asociada,cantidad_sustancia=emisiones.cantidad_sustancia*orden.cantidad_detalle)
                suministroEmision_Orden.save()
            
            emisionesTramos = SuministroTramos_PlanCadena.objects.filter(sumcadena_asociado=suministro)
            for tramos in emisionesTramos:
                tramosSuministro = SuministroTramos_Orden(ordensuministro_asociado=ordenSuministro,tipo_tramo=tramos.tipo_tramo,energia_tramo=tramos.energia_tramo,descripcion_tramo=tramos.descripcion_tramo,km_tramo=tramos.km_tramo)
                tramosSuministro.save()
        #except:
        #    print("error al grabar interno")      

        actividades = Actividad_PlanCadena.objects.filter(cadena_asociada=cadena)  

        for actividad in actividades:
            print('entro a actividades')
            ordenActividad = Actividad_Orden(produccion_asociada=ordenProduccion,
                nom_actividad=actividad.nom_actividad,equipo_asociado=actividad.equipo_asociado,tiempo_equipo_asociado=actividad.tiempo_equipo_asociado*orden.cantidad_detalle)
            ordenActividad.save()
            emisionesActividad = ActividadEmision_PlanCadena.objects.filter(actividadplan_asociado=actividad)

            for emision in emisionesActividad:
                print('entro al for interno')
                actividademision = ActividadEmision_Orden(actividadorden_asociado=ordenActividad,sustancia_asociada=emision.sustancia_asociada,cantidad_sustancia=emision.cantidad_sustancia*orden.cantidad_detalle)
                actividademision.save()
        print('PASO a actividades')

    except CadenaSuministro.DoesNotExist:
        ordenProduccion = OrdenProduccion(orden_venta_detalle=orden)
        ordenProduccion.save()
        print('se quedo aqui')

    print('llego aqui')
    
    orden_venta = OrdenVenta.objects.get(id=orden.orden_venta_detalle.id)
    orden_venta.estado_venta = "PR"
    orden_venta.save()
    
    
    calculos_cadena = CadenaCalculosEndpoint.objects.filter(cadena_asociada=cadena)

    for calculo in calculos_cadena:
        plan = calculo.valor
        calculo_orden = ProduccionCalculosEndpoint(orden_asociada=ordenProduccion,midpoint_endpoint=calculo.midpoint_endpoint,valor_real=0.00,valor_pla=plan)
        calculo_orden.save()

    # try:
    #     midpointEmisiones = MidpointEmision_PlanCadena.objects.filter(cadena_asociada=cadena)
    #     for midpointEmision in midpointEmisiones:

    #         if midpointEmision.tipo_midpoint == "AC" and midpointEmision.actividadplan_asociado.tipo_actividad == "EN":
    #             print("no actualizar")
    #         else:
    #             midpoint = midpointEmision.sustancia_midpoint_asociado.midpoint_emision
    #             factorEndpoints = MidpointEndpointFactor.objects.filter(midpoint=midpoint)

    #             for factorx in factorEndpoints:
    #                 calculoendpoint = CalculosEndpoint.objects.get(id=factorx.calculosEndpoint.id)
    #                 #cadena_calculo = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena,midpoint_endpoint=calculoendpoint.endpoint)
    #                 orden_calculo = ProduccionCalculosEndpoint.objects.get(orden_asociada=ordenProduccion,midpoint_endpoint=calculoendpoint.endpoint)
    #                 valor_anterior = orden_calculo.valor_pla

    #                 valor_agregar = midpointEmision.points_midpoint * factorx.factor
    #                 nuevo_valor = valor_anterior + valor_agregar

    #                 orden_calculo.valor_pla = nuevo_valor
    #                 print(f"valor es: {nuevo_valor}")
    #                 orden_calculo.save()

    # except MidpointEmision_PlanCadena.DoesNotExist:
    #     print("No existe ninguna emision asociada a la cadena")
    

    print('llego HASTA AQUI')
    
    messages.success(
            request, 'Orden de Producción Creada'
            )
    return redirect('produccion_app:modificar_produccion',pk=ordenProduccion.id)


def cancelar_ordenProduccion(request,pk):
    print("entro aqui")
    
    try:
        ordenProduccion = OrdenProduccion.objects.get(id=pk)
    except OrdenProduccion.DoesNotExist:
        messages.success(request, 'Orden de Producción no se encontro. Consultar con el soporte de la aplicacion.')
        return redirect('produccion_app:ordenes_produccion')

    ordenesSuministro = OrdenSuministro.objects.filter(orden_produccion=ordenProduccion)
    for ordenSuministro in ordenesSuministro:
        suministroEmisiones = SuministroEmision_Orden.objects.filter(ordensuministro_asociado=ordenSuministro)    
        for emision in suministroEmisiones:
            emision.delete()

        suministroTramos = SuministroTramos_Orden.objects.filter(ordensuministro_asociado=ordenSuministro)
        for tramo in suministroTramos:
            tramo.delete()

        ordenSuministro.estado_pedido_suministro = "CA"
        ordenSuministro.save()

    actividades = Actividad_Orden.objects.filter(produccion_asociada=ordenProduccion)
    for actividad in actividades:
        actividadEmisiones = ActividadEmision_Orden.objects.filter(actividadorden_asociado=actividad)
        for emision in actividadEmisiones:
            emision.delete()

        actividad.delete()

    ordenProduccion.estado_produccion = "CA"
    ordenProduccion.save()
    messages.success(
            request, 'Orden de Producción Cancelada'
            )
    return redirect('produccion_app:ordenes_produccion')

class OrdenesProduccionListView(ListView):
    context_object_name = 'Ordenproduccion_list'
    model = OrdenProduccion
    template_name = 'produccion_app/ordenes_produccion.html'

class OrdendeProduccionInLine():
    form_class = OrdenProduccionForm
    model = OrdenProduccion
    template_name = 'produccion_app/orden_produccion.html'

    def form_invalid(self,form):
        print("esta diciendo que el formulario es invalido")

        return redirect('produccion_app:ordenes_produccion')


    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error valid")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        orden = self.kwargs['pk']
        midpointTierra = form.cleaned_data['tierra_ocupada']
        cantidad = form.cleaned_data['tierra_m2']

        print(f"Mi orden es {self.object.id}")
        #crearVariablesdeCalculo(self.object.id)

        calcularemisionesTierra(self.object.id,midpointTierra,cantidad)
        

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
           
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        return redirect('produccion_app:modificar_produccion',pk=self.object.pk)

    def formset_suministros_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        print("entro aqui - Suministros")
        suministros = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for suministro in suministros:
            suministro.orden_produccion = self.object
            suministro.save()

    def formset_actividades_valid(self,formset):
        print("entro aqui - Actividades")
        actividades = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()
        for actividad in actividades:
            actividad.produccion_asociada = self.object
            actividad.save()
            calcularemisionEquipos(actividad)
            
class OrdendeProduccionUpdateView(OrdendeProduccionInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(OrdendeProduccionUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        formsets = {
        'suministros': SuministroOrdenFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='suministros'),
        'actividades': ActividadOrdenFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='actividades'),
        }

        for formset_form in formsets['suministros'].forms:
            suministro_id = formset_form['suministro_asociado'].initial
            if suministro_id is not None:
                try:
                    suministro = Suministro.objects.get(id=suministro_id)
                    proveedor = Proveedor.objects.get(nom_proveedor=suministro.prov_suministro)
                    #print(f"get_form: {proveedor.id}")
                    formset_form['proveedor_suministro'].initial = proveedor.id
                    ordenSuministro = OrdenSuministro.objects.get(id=formset_form['id'].initial)
                    formset_form.estado_pedido = valor_estado(ordenSuministro.estado_pedido_suministro)
                    formset_form.proveedor = proveedor.nom_proveedor
                    formset_form.suministro = suministro.nom_suministro + "-(" + suministro.unidad_suministro + ")"
                    formset_form.cantidad = formset_form['cantidad_suministro'].initial
                except:
                    print("error 3")

        for formset_form in formsets['actividades'].forms:
            actividad_id = formset_form['id'].initial
            print(f"id de actividad:{actividad_id}")
            if actividad_id is not None:
                try:
                    actividad = Actividad_Orden.objects.get(id=actividad_id)
                    est = actividad.estado_actividad
                    if est == "PL" :
                        estado = "Planificado"
                    elif est == "EN" :
                        estado = "En ejecución"
                    else:
                        estado = "Completado"
                    
                    formset_form.estado = estado
                    formset_form.nombre = actividad.nom_actividad
                    formset_form.equipo = actividad.equipo_asociado.nom_equipo
                    formset_form.tiempo = actividad.tiempo_equipo_asociado
                
                except:
                    print("error en actividad")

        return formsets

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            orden_id = self.kwargs.get('pk')
            orden = OrdenProduccion.objects.get(id=orden_id)
            form.productonombre = orden.orden_venta_detalle.producto_detalle.nom_producto
            form.existe = True
            form.estado = orden.get_estado_produccion_display()
            form.fecha_orden = orden.fecha_orden
            form.cantidad = orden.orden_venta_detalle.cantidad_detalle
            form.fuente = orden.fuente_energia.nom_energia
            form.tierra = orden.tierra_ocupada.nom_tipouso
            form.m2 = orden.tierra_m2

            if form.estado == "Completado" or form.estado == "Cancelado":
                form.fields['fuente_energia'].widget.attrs['disabled'] = 'disabled'
                form.fields['tierra_ocupada'].widget.attrs['disabled'] = 'disabled'
                form.fields['tierra_m2'].widget.attrs['disabled'] = 'disabled'

            try:
                endpoint = Endpoint.objects.get(id=1)
                salud_humana = ProduccionCalculosEndpoint.objects.get(orden_asociada=orden,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=2)
                eco_terrestre = ProduccionCalculosEndpoint.objects.get(orden_asociada=orden,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=3)
                eco_aguadulce = ProduccionCalculosEndpoint.objects.get(orden_asociada=orden,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=4)
                eco_marino = ProduccionCalculosEndpoint.objects.get(orden_asociada=orden,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=5)
                escase_recursos = ProduccionCalculosEndpoint.objects.get(orden_asociada=orden,midpoint_endpoint=endpoint)

                form.salud_humana = "{0:.3E}".format(salud_humana.valor_real)
                form.eco_terrestre = "{0:.3E}".format(eco_terrestre.valor_real)
                form.eco_aguadulce = "{0:.3E}".format(eco_aguadulce.valor_real)
                form.eco_marino = "{0:.3E}".format(eco_marino.valor_real)
                form.escase_recursos = "{0:.3E}".format(escase_recursos.valor_real)

            except ProduccionCalculosEndpoint.DoesNotExist:
                form.existe = False


    #         # for form_in_formset in self.get_named_formsets()['variants'].forms:
    #         #     suministro_id = form_in_formset.fields['suministro_asociado'].initial

    #         #     print(f"Valor: {suministro_id}")

    #         #     suministro = Suministro.objects.get(id=suministro_id)
                
    #         #     proveedor_id = Proveedor.objects.get(id=suministro.prov_suministro)
    #         #     form_in_formset.fields['proveedor_suministro'].initial = proveedor_id

        except OrdenProduccion.DoesNotExist:
            messages.error(request, 'No se encontro la orden de producción. Contacta al Soporte')

        return form

def actualizar_produccion(request,pk):
    try:
        ordenProduccion = OrdenProduccion.objects.get(id=pk)
        

    except OrdenProduccion.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:ordenes_produccion')

    ordenProduccion.estado_produccion = "PR"
    ordenProduccion.save()
    messages.success(
            request, 'Variant deleted successfully'
            )
    return redirect('produccion_app:modificar_produccion', pk=ordenProduccion.id)

def completar_produccion(request,pk):

    try:
        ordenProduccion = OrdenProduccion.objects.get(id=pk)

    except OrdenProduccion.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:ordenes_produccion', pk=ordenProduccion.id)


    ordenSuministro = OrdenSuministro.objects.filter(orden_produccion=ordenProduccion,estado_pedido_suministro__in=['RE','PE']).count()

    if ordenSuministro > 0:
        messages.error(
            request, 'Hay ordenes de suministros pendientes'
            )
        return redirect('produccion_app:modificar_produccion', pk=ordenProduccion.id)

    ordenActividades = Actividad_Orden.objects.filter(produccion_asociada=ordenProduccion,estado_actividad__in=['PL','EN']).count()

    if ordenActividades > 0:
        messages.error(
            request, 'Hay actividades sin completar'
            )
        return redirect('produccion_app:modificar_produccion', pk=ordenProduccion.id)


    ordenProduccion.estado_produccion = "CO"
    ordenProduccion.save()

    messages.success(
            request, 'La orden de producción ha finalizado.'
            )
    return redirect('produccion_app:modificar_produccion', pk=ordenProduccion.id)



# ============================================================
# Orden de Suministro
# ============================================================

def valor_estado(corto):

    valor = ""
    match corto:
        case "RE":
            valor = "Registrado"
        case "PE":
            valor = "Pedido"
        case "CO":
            valor = "Completado"
        case "CA":
            valor = "Cancelado"

    return valor

def cancelar_Suministro(request,pk):
    try:
        ordenSuministro = OrdenSuministro.objects.get(id=pk)

    except OrdenSuministro.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:ordenes_produccion')

    suministroEmisiones = SuministroEmision_Orden.objects.filter(ordensuministro_asociado=ordenSuministro)

    for emision in suministroEmisiones:
        emision.delete()

    suministroTramos = SuministroTramos_Orden.objects.filter(ordensuministro_asociado=ordenSuministro)

    for tramo in suministroTramos:
        tramo.delete()
    
    ordenSuministro.estado_pedido_suministro = "CA"
    ordenSuministro.save()

    messages.success(
            request, 'Orden de Suministro Cancelado.'
            )
    return redirect('produccion_app:modificar_produccion', pk=ordenSuministro.orden_produccion.id)

def completar_OrdenSuministro(request,pk):
    try:
        ordenSuministro = OrdenSuministro.objects.get(id=pk)

    except OrdenSuministro.DoesNotExist:
        messages.error(
            request, 'No existe una orden de suministro asociada con el código. Consulta con el soporte.'
            )
        return redirect('produccion_app:ordenes_produccion')

    ordenSuministro.estado_pedido_suministro = "CO"
    ordenSuministro.save()

    messages.success(
            request, 'Orden de Suministro Completada.'
            )
    return redirect('produccion_app:modificar_produccion', pk=ordenSuministro.orden_produccion.id)


def enviar_orden(request,pk):

    try:
        ordenSuministro = OrdenSuministro.objects.get(id=pk)

    except OrdenSuministro.DoesNotExist:
        messages.error(
            request, 'No existe una orden de suministro asociada con el código. Consulta con el soporte.'
            )
        return redirect('produccion_app:modificar_suministro', pk=ordenSuministro.id)

    ordenSuministro.estado_pedido_suministro = "PE"
    ordenSuministro.save()
    messages.success(
            request, 'Actualización de la Orden de Suministro.'
            )
    return redirect('produccion_app:modificar_suministro', pk=ordenSuministro.id)


class OrdenSuministroInLine():
    form_class = SuministroOrdenProduccionForm
    model = OrdenSuministro
    template_name = 'produccion_app/orden_suministro_emisiones.html'

    def form_invalid(self,form):
        print("error")
        return redirect('produccion_app:modificar_produccion',pk=form.cleaned_data['orden_produccion'].id)

    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error grabando hijos")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        messages.success(
            self.request, 'Orden de Suministro actualizado.'
            )

        return redirect('produccion_app:modificar_suministro',pk=self.object.id)

    def formset_emisiones_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        emisiones = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for emision in emisiones:
            emision.ordensuministro_asociado = self.object
            emision.save()
            calcularemisionesSuministro(emision)
            #print(f"Mi suministroEmision_asociado es {variant}")

    def formset_tramos_valid(self,formset):
        print("Entro aqui - Tramos")
        tramos = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for tramo in tramos:
            tramo.ordensuministro_asociado = self.object
            tramo.save()
            calcularEmisionesTramosSuministro(tramo)

class OrdenSuministroUpdateView(OrdenSuministroInLine,UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(OrdenSuministroUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):

        form = super().get_form()
        suministro_id = self.kwargs.get('pk')
        suministro = OrdenSuministro.objects.get(id=suministro_id)
        estado = suministro.get_estado_pedido_suministro_display()
        print(f"valro estado: {estado}")

        formsets = {
        'emisiones': SuministroEmisionOrdenFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='emisiones'),
        'tramos': SuministroViajesOrdenFormSet(self.request.POST or None,self.request.FILES or None,instance=self.object,prefix='tramos')
        }

        for formset_form in formsets['emisiones'].forms:
            sustancia_id = formset_form['sustancia_asociada'].initial

            if estado == "Completado" or estado == "Cancelado":
                formset_form.fields['tipo_emision'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['categoria_asociada'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['sustancia_asociada'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['cantidad_sustancia'].widget.attrs['disabled'] = 'disabled'

            if sustancia_id is not None:
                try:
                    sustancia = Sustancia_emision.objects.get(id=sustancia_id)
                    #print(f"get_form: {sustancia.midpoint_emision.id}")
                    categoria_asociada = Categoria_emision.objects.get(id=sustancia.categoria_asociada.id)
                    print(f"get_form: {categoria_asociada.id}")
                    formset_form['categoria_asociada'].initial = categoria_asociada.id
                    formset_form['tipo_emision'].initial = sustancia.tipo_emision;

                except Sustancia_emision.DoesNotExist:
                    print("error")


        for formset_form in formsets['tramos'].forms:
            if estado == "Completado" or estado == "Cancelado":
                formset_form.fields['tipo_tramo'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['energia_tramo'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['descripcion_tramo'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['km_tramo'].widget.attrs['disabled'] = 'disabled'

        return formsets


    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            suministro_id = self.kwargs.get('pk')
            print(f"Mi nombre es {suministro_id}")
            suministro = OrdenSuministro.objects.get(id=suministro_id)
            form.productonombre = suministro.orden_produccion.orden_venta_detalle.producto_detalle.nom_producto
            form.suministronombre = suministro.suministro_asociado.nom_suministro
            form.fields['proveedor_suministro'].initial = suministro.suministro_asociado.prov_suministro.id
            form.proveedor = suministro.suministro_asociado.prov_suministro.nom_proveedor
            form.estado = suministro.get_estado_pedido_suministro_display()
            form.unidad = suministro.suministro_asociado.unidad_suministro
            form.orden = suministro.orden_produccion.id
            form.cantidad = suministro.cantidad_suministro


        except OrdenSuministro.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form


def delete_SuministroEmision(request, pk):

    try:
        variant = SuministroEmision_Orden.objects.get(id=pk)
    except SuministroEmision_Orden.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:modificar_suministro', pk=variant.ordensuministro_asociado.id)

    variant.delete()
    messages.success(
            request, 'Variant deleted successfully'
            )
    return redirect('produccion_app:modificar_suministro', pk=variant.ordensuministro_asociado.id)


def delete_SuministroViaje(request,pk):
    try:
        variant = SuministroTramos_Orden.objects.get(id=pk)
    except SuministroTramos_Orden.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:modificar_suministro', pk=variant.ordensuministro_asociado.id)

    variant.delete()
    messages.success(
            request, 'Variant deleted successfully'
            )
    return redirect('produccion_app:modificar_suministro', pk=variant.ordensuministro_asociado.id)

# ============================================================
# Actividades Orden de Producción
# ============================================================

class ActividadesProduccionInLine():
    form_class = Actividad_OrdenForm
    model = Actividad_Orden
    template_name = 'produccion_app/orden_actividades_emisiones.html'

    def form_invalid(self,form):
        print("error formulario invalido")
        return redirect('produccion_app:modificar_produccion',pk=form.cleaned_data['produccion_asociada'].id)

    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error en validacion de hijos")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()
        calcularemisionEquipos(self.object)
        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:
                formset_save_func(formset)
                
            else:
               
                formset.save()

        messages.success(
            self.request, 'Actividad de Producción actualizado.'
            )

        return redirect('produccion_app:modificar_actividad_orden',pk=self.object.id)

    def formset_emisiones_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        emisiones = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
            print("Entro al delete")
        for emision in emisiones:
            emision.actividadplan_asociado = self.object
            print("Entro en esta parte")
            emision.save()
            calcularemisionesActividades(emision)

class ActividadesProduccionInLineUpdateView(ActividadesProduccionInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ActividadesProduccionInLineUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        form = super().get_form()
        id_actividad = self.kwargs.get('pk')
        actividad = Actividad_Orden.objects.get(id=id_actividad)
        estado = actividad.get_estado_actividad_display()

        formsets = {
        'emisiones': ActividadEmisionOrdenFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='emisiones'),
        }

        for formset_form in formsets['emisiones'].forms:
            sustancia_id = formset_form['sustancia_asociada'].initial

            if estado == "Completado" or estado == "Cancelado":
                formset_form.fields['tipo_emision'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['categoria_asociada'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['sustancia_asociada'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['cantidad_sustancia'].widget.attrs['disabled'] = 'disabled'

            if sustancia_id is not None:
                try:
                    sustancia = Sustancia_emision.objects.get(id=sustancia_id)
                    categoria_asociada = Categoria_emision.objects.get(id=sustancia.categoria_asociada.id)
                    print(f"get_form: {categoria_asociada.id}")
                    formset_form['categoria_asociada'].initial = categoria_asociada.id
                    formset_form['tipo_emision'].initial = sustancia.tipo_emision;

                except:
                    print("error")

        return formsets

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            id_actividad = self.kwargs.get('pk')
            actividad = Actividad_Orden.objects.get(id=id_actividad)
            form.productonombre = actividad.produccion_asociada.orden_venta_detalle.producto_detalle.nom_producto
            form.estado = actividad.get_estado_actividad_display()
            form.nombre = actividad.nom_actividad
            form.equipo = actividad.equipo_asociado.nom_equipo
            form.tiempo = actividad.tiempo_equipo_asociado
            form.orden = actividad.produccion_asociada.id
            #form.actividad = actividad_plancadena.nom_actividad

        except Actividad_Orden.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form

def delete_ActividadEmision(request, pk):

    try:
        emision = ActividadEmision_Orden.objects.get(id=pk)
    except ActividadEmision_Orden.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:modificar_actividad_orden', pk=emision.actividadorden_asociado.id)

    emision.delete()
    messages.success(
            request, 'Emision eliminada con exito'
            )
    return redirect('produccion_app:modificar_actividad_orden', pk=emision.actividadorden_asociado.id)

def delete_OrdenActividad(request, pk):

    try:
        variant = Actividad_Orden.objects.get(id=pk)
    except Actividad_Orden.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:modificar_produccion', pk=variant.produccion_asociada.id)

    variant.delete()
    messages.success(
            request, 'Actividad eliminada con exito'
            )
    return redirect('produccion_app:modificar_produccion', pk=variant.produccion_asociada.id)



def iniciar_ActividadProduccion(request,pk):
    try:
        variant = Actividad_Orden.objects.get(id=pk)
    except Actividad_Orden.DoesNotExist:
        print("error 1")
        return redirect('produccion_app:modificar_actividad_orden', pk=variant.id)

    variant.estado_actividad = "EN"
    variant.save()

    try:
        orden = OrdenProduccion.objects.get(id=variant.produccion_asociada.id)
    except OrdenProduccion.DoesNotExist:
        print("no hay orden de producción")

    orden.estado_produccion = "PR"
    orden.save()
    
    messages.success(
            request, 'La actividad se encuentra en ejecución'
            )

    return redirect('produccion_app:modificar_actividad_orden', pk=variant.id)

def terminar_ActividadProduccion(request,pk):
    try:
        variant = Actividad_Orden.objects.get(id=pk)
    except Actividad_Orden.DoesNotExist:
        print("error 1")
        return redirect('produccion_app:modificar_actividad_orden', pk=variant.id)

    variant.estado_actividad = "CO"
    variant.save()
    
    messages.success(
            request, 'La actividad se ha completado.'
            )

    return redirect('produccion_app:modificar_actividad_orden', pk=variant.id)

# ============================================================
# Orden de Entrega
# ============================================================

def calcularEmisionesTramosEntrega(suministroTramos):
    print(f"Mi SuministroTramos_PlanCadena es {suministroTramos.id}")
    km_recorridos = suministroTramos.km_tramoexterno
    
    try:
        midpointTramos = MidpointTramos.objects.get(energia_transporte=suministroTramos.energia_tramoexterno,Tipo_transporte=suministroTramos.tipo_tramoexterno)
        co2_tramo_point = midpointTramos.co2_tramo*km_recorridos
        nox_tramo_point = midpointTramos.nox_tramo*km_recorridos
        pm_tramo_point = midpointTramos.pm_tramo*km_recorridos

    except MidpointTramos.DoesNotExist:
        co2_tramo_point = 0.0
        nox_tramo_point = 0.0
        pm_tramo_point = 0.0

    puntos_a_revisar= [(settings.CODIGO_C02,co2_tramo_point),(settings.CODIGO_NOX,nox_tramo_point),(settings.CODIGO_PM,pm_tramo_point)]

    print("Genero duplas")
    orden = suministroTramos.orden_envio_asociada
    #tramo_PlanCadena = tramos_PlanCadena
    tipo_midpoint = "TR"


    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])
        print("entro a la dupla")
        for midpoint in midpoints:
            points = dupla[1]*midpoint.valor_emision
            print(f"esta aqui: {orden}")
            try:
                midpointEmision = MidpointEmision_Entrega.objects.get(orden_asociada=orden,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,tramos_envio=suministroTramos)
                midpointEmision.points_midpoint = points
                midpointEmision.save()

            except MidpointEmision_Entrega.DoesNotExist:
                midpointEmision = MidpointEmision_Entrega(orden_asociada=orden,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,tramos_envio=suministroTramos,points_midpoint=points)
                midpointEmision.save()

    calcularEndpointsEntrega(orden) 

def calcularemisionEquiposEntrega(actividad_orden):
    print("entro a calcularemisionEquipos")
    uso_horas = actividad_orden.tiempo_equipo_asociado
    potencia = actividad_orden.equipo_asociado.potencia_equipo
    kilo_vatios_hora = (potencia/1000.0)*uso_horas


    fuente_energia = actividad_orden.entrega_asociada.fuente_energia
    co2_equipo_point = fuente_energia.co2_energia * kilo_vatios_hora
    nox_equipo_point = fuente_energia.nox_energia * kilo_vatios_hora
    so2_equipo_point = fuente_energia.so2_energia  * kilo_vatios_hora
    pm_equipo_point = fuente_energia.pm_energia * kilo_vatios_hora
    co60_equipo_point = fuente_energia.co60_energia * kilo_vatios_hora



    puntos_a_revisar = [(settings.CODIGO_C02,co2_equipo_point),(settings.CODIGO_NOX,nox_equipo_point),(settings.CODIGO_SO2,so2_equipo_point),(settings.CODIGO_PM,pm_equipo_point),(settings.CODIGO_CO60,co60_equipo_point)]

    orden = actividad_orden.entrega_asociada
    actividad = actividad_orden
    tipo_midpoint = "CE"

    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])

        for midpoint in midpoints:
            #midpoints_emision_asociada = midpoint.midpoint_emision
            points = dupla[1] * midpoint.valor_emision

            try:
                midpointEmision = MidpointEmision_Entrega.objects.get(sustancia_midpoint_asociado=midpoint,orden_asociada=orden,tipo_midpoint=tipo_midpoint,actividad_asociada=actividad)
                midpointEmision.points_midpoint = points
                midpointEmision.save()
            except MidpointEmision_Entrega.DoesNotExist:
                midpointEmision = MidpointEmision_Entrega(orden_asociada=orden,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points,actividad_asociada=actividad)
                midpointEmision.save()

    calcularEndpointsEntrega(orden) 

def limpiarEmisionesActividadesEntrega(actividadEmision):
    midpointsEmision = MidpointEmision_Entrega.objects.filter(actividademision_asociado=actividadEmision)

    for midpointEmision in midpointsEmision:
        midpointEmision.delete()

def calcularemisionesActividadesEntrega(actividadEmision):
    orden = actividadEmision.actividadenvio_asociado.entrega_asociada
    tipo_midpoint = "AC"
    midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=actividadEmision.sustancia_asociada)
    actividademision_asociado = actividadEmision
    limpiarEmisionesActividadesEntrega(actividademision_asociado)

    for midpoint in midpoints:
        #midpoint_emision_asociada = midpoint.midpoint_emision
        points = midpoint.valor_emision * actividadEmision.cantidad_sustancia

        try:
            midpointEmision = MidpointEmision_Entrega.objects.get(orden_asociada=orden,sustancia_midpoint_asociado=midpoint,actividademision_asociado=actividademision_asociado,tipo_midpoint=tipo_midpoint)
            midpointEmision.points_midpoint = points
            midpointEmision.save()

        except MidpointEmision_Entrega.DoesNotExist:
            midpointEmision = MidpointEmision_Entrega(orden_asociada=orden,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points,actividademision_asociado=actividademision_asociado)
            midpointEmision.save()

    calcularEndpointsEntrega(orden) 

class OrdenEntregaInLine():
    form_class = OrdenEntregaForm
    model = OrdenEntrega
    template_name = 'produccion_app/orden_envio.html'

    def form_invalid(self,form):
        print("esta diciendo que el formulario es invalido")

        return redirect('produccion_app:ordenes_produccion')


    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error valid")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        orden = self.kwargs['pk']

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
           
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()



        messages.success(
            self.request, 'La Orden de Entrega se ha actualizado.'
            )
        return redirect('produccion_app:editar_orden_entrega',pk=orden)

    def formset_tramos_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        print("entro aqui - Tramos")
        tramos = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for tramo in tramos:
            tramo.orden_envio_asociada = self.object
            tramo.save()
            calcularEmisionesTramosEntrega(tramo)

    def formset_actividades_valid(self,formset):
        print("entro aqui - Actividades")
        actividades = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()
        for actividad in actividades:
            actividad.entrega_asociada = self.object
            actividad.save()
            calcularemisionEquiposEntrega(actividad)

def delete_ActividadEntrega(request, pk):

    try:
        variant = Actividad_Envio.objects.get(id=pk)
    except Actividad_Envio.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:modificar_produccion', pk=variant.produccion_asociada.id)

    variant.delete()
    messages.success(
            request, 'Actividad eliminada con exito'
            )
    return redirect('produccion_app:modificar_produccion', pk=variant.produccion_asociada.id)


def OrdenEntregaCreate(request,pk):
    
    try:
        ordenVenta = OrdenVenta.objects.get(id=pk)
    except OrdenVenta.DoesNotExist:
        messages.error(
            request, 'La Orden de Entrega no se ha podido crear. Consulta con el equipo de soporte.'
            )
        return redirect('produccion_app:ordenes_venta')

    ordenEntrega = OrdenEntrega(orden_venta_entrega=ordenVenta,fecha_entrega=ordenVenta.fecha_entrega_venta,direccion_entrega=ordenVenta.direccion_venta)
    ordenEntrega.save()

    
    existe = EnvioCalculosEndpoint.objects.filter(envio_asociada=ordenEntrega)

    if not existe:
        print("NO EXISTE")
        endpoints = Endpoint.objects.all()

        for endpoint in endpoints:
            cadenacalculosendpoint = EnvioCalculosEndpoint(envio_asociada=ordenEntrega,midpoint_endpoint=endpoint,valor_real=0.00,valor_pla=0.00)
            cadenacalculosendpoint.save()
    else:
        print("YA EXISTE")


    messages.success(
            request, 'La Orden de Entrega se ha creado.'
            )

    return redirect('produccion_app:editar_orden_entrega',pk=ordenEntrega.id)


class OrdenEntregaUpdateView(OrdenEntregaInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(OrdenEntregaUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        entrega_id = self.kwargs.get('pk')
        entrega = OrdenEntrega.objects.get(id=entrega_id)
        estadox = entrega.get_estado_entrega_display()

        formsets = {
        'tramos': TramosEnvioFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='tramos'),
        'actividades': ActividadEnvioFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='actividades'),
        }

        for formset_form in formsets['actividades'].forms:
            actividad_id = formset_form['id'].initial
            print(f"id de actividad:{actividad_id}")
            if actividad_id is not None:
                try:
                    actividad = Actividad_Envio.objects.get(id=actividad_id)
                    est = actividad.estado_actividad
                    if est == "PL" :
                        estado = "Planificado"
                    elif est == "EN" :
                        estado = "En ejecución"
                    else:
                        estado = "Completado"
                    
                    formset_form.estado = estado
                    formset_form.nombre = actividad.nom_actividad
                    formset_form.equipo = actividad.equipo_asociado.nom_equipo
                    formset_form.tiempo = actividad.tiempo_equipo_asociado
                
                except:
                    print("error en actividad")

        for formset_form in formsets['tramos'].forms:
            if estadox == "Completado" or estadox == "Cancelado":
                formset_form.fields['tipo_tramoexterno'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['energia_tramoexterno'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['descripcion_tramoexterno'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['km_tramoexterno'].widget.attrs['disabled'] = 'disabled'

        return formsets

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            orden_id = self.kwargs.get('pk')
            orden = OrdenEntrega.objects.get(id=orden_id)
            form.ordenventa = orden.orden_venta_entrega.cod_venta
            form.codventa = orden.orden_venta_entrega.id
            form.estado = orden.get_estado_entrega_display()
            form.fecha = orden.fecha_entrega
            form.contacto = orden.contacto_entrega
            form.direccion = orden.direccion_entrega
            form.observacion = orden.observaciones_entrega
            form.fuente = orden.fuente_energia

        except:
            print("error en actividad")

    #         try:
    #             endpoint = Endpoint.objects.get(id=1)
    #             salud_humana = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
    #             endpoint = Endpoint.objects.get(id=2)
    #             eco_terrestre = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
    #             endpoint = Endpoint.objects.get(id=3)
    #             eco_aguadulce = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
    #             endpoint = Endpoint.objects.get(id=4)
    #             eco_marino = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
    #             endpoint = Endpoint.objects.get(id=5)
    #             escase_recursos = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)

    #             form.salud_humana = "{0:.3E}".format(salud_humana.valor)
    #             form.eco_terrestre = "{0:.3E}".format(eco_terrestre.valor)
    #             form.eco_aguadulce = "{0:.3E}".format(eco_aguadulce.valor)
    #             form.eco_marino = "{0:.3E}".format(eco_marino.valor)
    #             form.escase_recursos = "{0:.3E}".format(escase_recursos.valor)

        # except CadenaCalculosEndpoint.DoesNotExist:
        #     form.existe = False


    #         # for form_in_formset in self.get_named_formsets()['variants'].forms:
    #         #     suministro_id = form_in_formset.fields['suministro_asociado'].initial

    #         #     print(f"Valor: {suministro_id}")

    #         #     suministro = Suministro.objects.get(id=suministro_id)
                
    #         #     proveedor_id = Proveedor.objects.get(id=suministro.prov_suministro)
    #         #     form_in_formset.fields['proveedor_suministro'].initial = proveedor_id

        return form


class Actividad_EnvioInLine():
    form_class = Actividad_EnvioForm
    model = Actividad_Envio
    template_name = 'produccion_app/orden_actividades_emisiones_envio.html'

    def form_invalid(self,form):
        print("error formulario invalido")

        return redirect('produccion_app:modificar_actividad_entrega',pk=self.object.id)

    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error en validacion de hijos")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()
        calcularemisionEquiposEntrega(self.object)

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:
                formset_save_func(formset)
                
            else:
               
                formset.save()

        messages.success(
            self.request, 'Actividad de Entrega actualizado.'
            )

        return redirect('produccion_app:modificar_actividad_entrega',pk=self.object.id)

    def formset_emisiones_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        emisiones = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
            print("Entro al delete")
        for emision in emisiones:
            emision.actividadplan_asociado = self.object
            print("Entro en esta parte")
            emision.save()
            calcularemisionesActividadesEntrega(emision)

class Actividad_EnvioInLineUpdateView(Actividad_EnvioInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(Actividad_EnvioInLineUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        form = super().get_form()
        id_actividad = self.kwargs.get('pk')
        actividad = Actividad_Envio.objects.get(id=id_actividad)
        estado = actividad.get_estado_actividad_display()

        formsets = {
        'emisiones': ActividadEmisionEnvioFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='emisiones'),
        }

        for formset_form in formsets['emisiones'].forms:
            sustancia_id = formset_form['sustancia_asociada'].initial

            if estado == "Completado" or estado == "Cancelado":
                formset_form.fields['tipo_emision'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['categoria_asociada'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['sustancia_asociada'].widget.attrs['disabled'] = 'disabled'
                formset_form.fields['cantidad_sustancia'].widget.attrs['disabled'] = 'disabled'

            if sustancia_id is not None:
                try:
                    sustancia = Sustancia_emision.objects.get(id=sustancia_id)
                    categoria_asociada = Categoria_emision.objects.get(id=sustancia.categoria_asociada.id)
                    print(f"get_form: {categoria_asociada.id}")
                    formset_form['categoria_asociada'].initial = categoria_asociada.id
                    formset_form['tipo_emision'].initial = sustancia.tipo_emision;

                except:
                    print("error")

        return formsets

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            id_actividad = self.kwargs.get('pk')
            actividad = Actividad_Envio.objects.get(id=id_actividad)
            #form.productonombre = actividad.produccion_asociada.orden_venta_detalle.producto_detalle.nom_producto
            form.estado = actividad.get_estado_actividad_display()
            form.nombre = actividad.nom_actividad
            form.equipo = actividad.equipo_asociado.nom_equipo
            form.tiempo = actividad.tiempo_equipo_asociado
            form.orden = actividad.entrega_asociada.id
            form.ordenventa = actividad.entrega_asociada.orden_venta_entrega.cod_venta
            #form.actividad = actividad_plancadena.nom_actividad

        except Actividad_Orden.DoesNotExist:
            messages.success(self.request, 'Object Does not exit')

        return form

def delete_ActividadEntregaEmision(request, pk):

    try:
        emision = ActividadEmision_Envio.objects.get(id=pk)
    except ActividadEmision_Envio.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:modificar_actividad_entrega', pk=emision.actividadenvio_asociado.id)

    emision.delete()
    messages.success(
            request, 'Emision eliminada con exito'
            )
    return redirect('produccion_app:modificar_actividad_entrega', pk=emision.actividadenvio_asociado.id)

def delete_OrdenEntregaActividad(request, pk):

    try:
        variant = Actividad_Envio.objects.get(id=pk)
    except Actividad_Envio.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=variant.entrega_asociada.id)

    variant.delete()
    messages.success(
            request, 'Actividad eliminada con exito'
            )
    return redirect('produccion_app:editar_orden_entrega', pk=variant.entrega_asociada.id)

def enviar_OrdenEntregaActividad(request,pk):
    try:
        orden = OrdenEntrega.objects.get(id=pk)
    except OrdenEntrega.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=orden.id)

    ordenActividades = Actividad_Envio.objects.filter(entrega_asociada=orden,estado_actividad__in=['PL','EN']).count()

    if ordenActividades > 0:
        messages.error(
            request, 'Hay actividades sin completar'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=orden.id)

    tramosActividado = Tramos_Orden.objects.filter(orden_envio_asociada=orden).count()
    if tramosActividado <= 0:
        messages.error(
            request, 'Debe existir al menos un tramo en la orden de entrega'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=orden.id)

    orden.estado_entrega = "ON"
    orden.save()
    print(f"Llega aqui{orden.orden_venta_entrega}")
    ordenventa = OrdenVenta.objects.get(id=orden.orden_venta_entrega.id)
    ordenventa.estado_venta = "LE"
    ordenventa.save()

    messages.success(
            request, 'Orden de Entrega actualizado con exito.'
            )
    return redirect('produccion_app:editar_orden_entrega', pk=orden.id)


def recepcion_OrdenEntregaActividad(request,pk):
    try:
        orden = OrdenEntrega.objects.get(id=pk)
    except OrdenEntrega.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=orden.id)

    ordenActividades = Actividad_Envio.objects.filter(entrega_asociada=orden,estado_actividad__in=['PL','EN']).count()

    if ordenActividades > 0:
        messages.error(
            request, 'Hay actividades sin completar'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=orden.id)

    tramosActividado = Tramos_Orden.objects.filter(orden_envio_asociada=orden).count()
    if tramosActividado <= 0:
        messages.error(
            request, 'Debe existir al menos un tramo en la orden de entrega'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=orden.id)

    orden.estado_entrega = "CO"
    orden.save()
    print(f"Llega aqui{orden.orden_venta_entrega}")
    ordenventa = OrdenVenta.objects.get(id=orden.orden_venta_entrega.id)
    ordenventa.estado_venta = "EN"
    ordenventa.save()

    messages.success(
            request, 'Orden de Entrega actualizado con exito.'
            )
    return redirect('produccion_app:editar_orden_entrega', pk=orden.id)

def iniciar_ActividadEntrega(request,pk):
    try:
        variant = Actividad_Envio.objects.get(id=pk)
    except Actividad_Envio.DoesNotExist:
        print("error 1")
        return redirect('produccion_app:modificar_actividad_entrega', pk=variant.id)

    variant.estado_actividad = "EN"
    variant.save()

    try:
        orden = OrdenEntrega.objects.get(id=variant.entrega_asociada.id)
    except OrdenProduccion.DoesNotExist:
        print("no hay orden de producción")

    orden.estado_entrega = "PR"
    orden.save()
    
    messages.success(
            request, 'La actividad se encuentra en ejecución'
            )

    return redirect('produccion_app:modificar_actividad_entrega', pk=variant.id)

def terminar_ActividadEntrega(request,pk):
    try:
        variant = Actividad_Envio.objects.get(id=pk)
    except Actividad_Envio.DoesNotExist:
        print("error 1")
        return redirect('produccion_app:modificar_actividad_entrega', pk=variant.id)

    variant.estado_actividad = "CO"
    variant.save()
    
    messages.success(
            request, 'La actividad se ha completado.'
            )

    return redirect('produccion_app:modificar_actividad_entrega', pk=variant.id)

def delete_EntregaViaje(request,pk):
    try:
        variant = Tramos_Orden.objects.get(id=pk)
    except Tramos_Orden.DoesNotExist:
        messages.success(
            request, 'No se encontro el tramo para eliminar. Contactar al equipo de soporte.'
            )
        return redirect('produccion_app:editar_orden_entrega', pk=variant.orden_envio_asociada.id)

    variant.delete()
    messages.success(
            request, 'Tramo eliminado con exito'
            )
    return redirect('produccion_app:editar_orden_entrega', pk=variant.orden_envio_asociada.id)

class OrdenEntregaListView(ListView):
    context_object_name = 'Ordenentregas_list'
    model = OrdenEntrega
    template_name = 'produccion_app/ordenes_envio.html'