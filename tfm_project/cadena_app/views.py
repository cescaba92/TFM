from django.shortcuts import (render, redirect)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from cadena_app.forms import (CadenaNuevaForm,SuministroPlanFormSet,SuministroPlanCadenaForm,SuministroEmisionPlanFormSet,SuministroTramosPlanFormSet,Actividad_PlanCadenaForm,ActividadPlanFormSet,ActividadEmisionPlanCadenaForm,ActividadEmisionPlanFormSet,SuministroViajesPlanCadenaForm)
from cadena_app.models import (CadenaSuministro, Suministro_PlanCadena,Sustancia_emision,Midpoint_emision,SuministroEmision_PlanCadena,Tramos_PlanCadena,Actividad_PlanCadena,ActividadEmision_PlanCadena,MidpointEmision_PlanCadena,Sustancia_Midpoint_emision,Categoria_emision,MidpointTramos,Categoria_emision)
from cadena_app.models import (MidpointEndpointFactor, CadenaCalculosEndpoint,CalculosEndpoint,Endpoint,SuministroTramos_PlanCadena)
from producto_app.models import (Producto, VariacionProducto)
from suministro_app.models import (Suministro, Proveedor)
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView,DeleteView)
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings

import logging 

# ============================================================
# Proceso de Calculo de Endpoint
# ============================================================

def calcularEndpoints(cadena):

    try:
        cadena_calculos = CadenaCalculosEndpoint.objects.filter(cadena_asociada=cadena)

        for cadena_calculo in cadena_calculos:
            cadena_calculo.valor = 0.00
            cadena_calculo.save()
    except CadenaCalculosEndpoint.DoesNotExist:
        print("No existe ninguna cadena asociada")

    try:
        midpointEmisiones = MidpointEmision_PlanCadena.objects.filter(cadena_asociada=cadena)
        for midpointEmision in midpointEmisiones:
            midpoint = midpointEmision.sustancia_midpoint_asociado.midpoint_emision
            factorEndpoints = MidpointEndpointFactor.objects.filter(midpoint=midpoint)

            for factorx in factorEndpoints:
                calculoendpoint = CalculosEndpoint.objects.get(id=factorx.calculosEndpoint.id)
                cadena_calculo = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena,midpoint_endpoint=calculoendpoint.endpoint)
                valor_anterior = cadena_calculo.valor

                valor_agregar = midpointEmision.points_midpoint * factorx.factor
                nuevo_valor = valor_anterior + valor_agregar

                cadena_calculo.valor = nuevo_valor
                #print(f"valor es: {nuevo_valor}")
                cadena_calculo.save()

    except MidpointEmision_PlanCadena.DoesNotExist:
        print("No existe ninguna emision asociada a la cadena")

def crearVariablesdeCalculo(cadena):
    #codigo = cadena.id
    print(f"cadena es: {cadena}")

    cadena_suministro = CadenaSuministro.objects.get(id=cadena)
    
    print(f"la cadena_suministro es: {cadena_suministro.id}")
    
    cadenaExists = CadenaCalculosEndpoint.objects.filter(cadena_asociada=cadena_suministro)

    if not cadenaExists:
        print("NO EXISTE")
        endpoints = Endpoint.objects.all()

        for endpoint in endpoints:
            cadenacalculosendpoint = CadenaCalculosEndpoint(cadena_asociada=cadena_suministro,midpoint_endpoint=endpoint,valor=0.00)
            cadenacalculosendpoint.save()
    else:
        print("YA EXISTE")

# ============================================================
# Proceso de Calculo de Midpoints
# ============================================================


def calcularemisionesTierra(id_cadena,midpointTierra,cantidad):  

    try:

        cadena = CadenaSuministro.objects.get(id=id_cadena)
        tipo_midpoint = "TI"
        try:
            #categoria = Categoria_emision.objects.get(nom_categoria=midpointTierra.nom_tipouso)
            sustancia = Sustancia_emision.objects.get(componente_emision=midpointTierra.nom_tipouso)
            print(f"Mi sustancia es {sustancia.id}")
            limpiarEmisionesTierra(cadena)
            midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=sustancia)
            for midpoint in midpoints:
                points = midpoint.valor_emision * cantidad
                print(f"Mi midpoint es {midpoint.id}")
                try:
                    midpointEmision = MidpointEmision_PlanCadena.objects.get(cadena_asociada=cadena,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint)
                    midpointEmision.points_midpoint = points
                    midpointEmision.save()

                except MidpointEmision_PlanCadena.DoesNotExist:
                    midpointEmision = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points)
                    midpointEmision.save()

            calcularEndpoints(id_cadena)
        except Sustancia_emision.DoesNotExist:
            print("No se encontro sustancia emision con el nombre de la categoria")
    except CadenaSuministro.DoesNotExist:
        print("aun no hay cadena de Suministro")
    


def limpiarEmisionesSuministro(suministroEmision):
    midpointsEmision = MidpointEmision_PlanCadena.objects.filter(suministroEmision_asociado=suministroEmision)

    for midpointEmision in midpointsEmision:
        midpointEmision.delete()

def limpiarEmisionesTierra(cadena):
    midpointsEmision = MidpointEmision_PlanCadena.objects.filter(tipo_midpoint="TI",cadena_asociada=cadena)

    for midpointEmision in midpointsEmision:
        midpointEmision.delete()

def limpiarEmisionesActividades(actividadEmision):
    midpointsEmision = MidpointEmision_PlanCadena.objects.filter(actividademision_asociado=actividadEmision)

    for midpointEmision in midpointsEmision:
        midpointEmision.delete()

def calcularemisionesSuministro(suministroEmision):
    
    cadena = suministroEmision.sumcadena_asociado.cadena_asociada
    tipo_midpoint = "SU"
    suministroEmision_asociado = suministroEmision
    midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=suministroEmision.sustancia_asociada)
    
    limpiarEmisionesSuministro(suministroEmision_asociado)
    
    for midpoint in midpoints:
        #midpoints_emision_asociada = emision_midpoint.midpoint_emision
        points = midpoint.valor_emision * suministroEmision.cantidad_sustancia
        #print(f"Mi suministroEmision_asociado es {suministroEmision.id}")
        
        try:
            midpointEmision = MidpointEmision_PlanCadena.objects.get(cadena_asociada=cadena,suministroEmision_asociado=suministroEmision_asociado,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint)
            midpointEmision.points_midpoint = points
            midpointEmision.save()

        except MidpointEmision_PlanCadena.DoesNotExist:
            midpointEmision = MidpointEmision_PlanCadena(cadena_asociada=cadena,suministroEmision_asociado=suministroEmision_asociado,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,points_midpoint=points)
            midpointEmision.save()

    calcularEndpoints(cadena)        

    #midpoints_emision_asociada = suministroEmision.sustancia_asociada.midpoint_emision
    #suministroEmision_asociado = suministroEmision
    #points = suministroEmision.sustancia_asociada.valor_emision * suministroEmision.cantidad_sustancia
    #print(f"Mi suministroEmision_asociado es {suministroEmision.id}")

def calcularemisionEquipos(actividad_PlanCadena):
    print("entro a calcularemisionEquipos")
    uso_horas = actividad_PlanCadena.tiempo_equipo_asociado
    cadena = actividad_PlanCadena.cadena_asociada

    if actividad_PlanCadena.equipo_asociado is not None:

        potencia = actividad_PlanCadena.equipo_asociado.potencia_equipo

        kilo_vatios_hora = (potencia/1000.0)*uso_horas

        fuente_energia = actividad_PlanCadena.cadena_asociada.fuente_energia
        co2_equipo_point = fuente_energia.co2_energia * kilo_vatios_hora
        nox_equipo_point = fuente_energia.nox_energia * kilo_vatios_hora
        so2_equipo_point = fuente_energia.so2_energia  * kilo_vatios_hora
        pm_equipo_point = fuente_energia.pm_energia * kilo_vatios_hora
        co60_equipo_point = fuente_energia.co60_energia * kilo_vatios_hora

    else:
        co2_equipo_point = 0.00
        nox_equipo_point = 0.00
        so2_equipo_point = 0.00
        pm_equipo_point = 0.00
        co60_equipo_point = 0.00


    puntos_a_revisar = [(settings.CODIGO_C02,co2_equipo_point),(settings.CODIGO_NOX,nox_equipo_point),(settings.CODIGO_SO2,so2_equipo_point),(settings.CODIGO_PM,pm_equipo_point),(settings.CODIGO_CO60,co60_equipo_point)]

        
    actividad = actividad_PlanCadena
    tipo_midpoint = "CE"

    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])

        for midpoint in midpoints:
            #midpoints_emision_asociada = midpoint.midpoint_emision
            points = dupla[1] * midpoint.valor_emision

            try:
                midpointEmision = MidpointEmision_PlanCadena.objects.get(sustancia_midpoint_asociado=midpoint,cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,actividad_asociada=actividad)
                midpointEmision.points_midpoint = points
                midpointEmision.save()
            except MidpointEmision_PlanCadena.DoesNotExist:
                midpointEmision = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points,actividad_asociada=actividad)
                midpointEmision.save()

    
    calcularEndpoints(cadena) 

def calcularemisionesActividades(actividadEmision):
    cadena = actividadEmision.actividadplan_asociado.cadena_asociada
    tipo_midpoint = "AC"
    midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=actividadEmision.sustancia_asociada)
    actividademision_asociado = actividadEmision
    limpiarEmisionesActividades(actividademision_asociado)

    for midpoint in midpoints:
        #midpoint_emision_asociada = midpoint.midpoint_emision
        points = midpoint.valor_emision * actividadEmision.cantidad_sustancia

        try:
            midpointEmision = MidpointEmision_PlanCadena.objects.get(cadena_asociada=cadena,sustancia_midpoint_asociado=midpoint,actividademision_asociado=actividademision_asociado,tipo_midpoint=tipo_midpoint)
            midpointEmision.points_midpoint = points
            midpointEmision.save()

        except MidpointEmision_PlanCadena.DoesNotExist:
            midpointEmision = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points,actividademision_asociado=actividademision_asociado)
            midpointEmision.save()

    calcularEndpoints(cadena) 

def calcularEmisionesTramos(tramos_PlanCadena):
    print(f"Mi tramos_PlanCadena es {tramos_PlanCadena.id}")
    km_recorridos = tramos_PlanCadena.km_tramoexterno
    
    try:
        midpointTramos = MidpointTramos.objects.get(energia_transporte=tramos_PlanCadena.energia_tramoexterno,Tipo_transporte=tramos_PlanCadena.tipo_tramoexterno)
        co2_tramo_point = midpointTramos.co2_tramo*km_recorridos
        nox_tramo_point = midpointTramos.nox_tramo*km_recorridos
        pm_tramo_point = midpointTramos.pm_tramo*km_recorridos

    except MidpointTramos.DoesNotExist:
        co2_tramo_point = 0.0
        nox_tramo_point = 0.0
        pm_tramo_point = 0.0

    puntos_a_revisar= [(settings.CODIGO_C02,co2_tramo_point),(settings.CODIGO_NOX,nox_tramo_point),(settings.CODIGO_PM,pm_tramo_point)]

    print("Genero duplas")
    cadena = tramos_PlanCadena.cadena_asociada
    tramo_PlanCadena = tramos_PlanCadena
    tipo_midpoint = "TR"


    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])
        print("entro a la dupla")
        for midpoint in midpoints:
            points = dupla[1]*midpoint.valor_emision

            try:
                midpointEmision = MidpointEmision_PlanCadena.objects.get(cadena_asociada=cadena,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,tramos_PlanCadena=tramos_PlanCadena)
                midpointEmision.points_midpoint = points
                midpointEmision.save()

            except MidpointEmision_PlanCadena.DoesNotExist:
                midpointEmision = MidpointEmision_PlanCadena(cadena_asociada=cadena,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,tramos_PlanCadena=tramos_PlanCadena,points_midpoint=points)
                midpointEmision.save()

    calcularEndpoints(cadena) 

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
    cadena = suministroTramos.sumcadena_asociado.cadena_asociada
    #tramo_PlanCadena = tramos_PlanCadena
    tipo_midpoint = "TS"


    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])
        print("entro a la dupla")
        for midpoint in midpoints:
            points = dupla[1]*midpoint.valor_emision
            print(f"esta aqui: {cadena}")
            try:
                midpointEmision = MidpointEmision_PlanCadena.objects.get(cadena_asociada=cadena,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,suministroTramos_PlanCadena=suministroTramos)
                midpointEmision.points_midpoint = points
                midpointEmision.save()

            except MidpointEmision_PlanCadena.DoesNotExist:
                midpointEmision = MidpointEmision_PlanCadena(cadena_asociada=cadena,sustancia_midpoint_asociado=midpoint,tipo_midpoint=tipo_midpoint,suministroTramos_PlanCadena=suministroTramos,points_midpoint=points)
                midpointEmision.save()

    calcularEndpoints(cadena) 


# ============================================================
# Cadena de Suministro Principal
# ============================================================

class CadenaSuministroInLine():
    form_class = CadenaNuevaForm
    model = CadenaSuministro
    template_name = 'cadena_app/update_suministro_cadena.html'

    def form_invalid(self,form):
        print("error")

        return redirect('producto_app:productos')


    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        cadena = self.kwargs['pk']
        midpointTierra = form.cleaned_data['tierra_ocupada']
        cantidad = form.cleaned_data['tierra_m2']

        print(f"Mi cadena es {self.object.id}")
        crearVariablesdeCalculo(self.object.id)

        calcularemisionesTierra(self.object.id,midpointTierra,cantidad)
        

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
           
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()


        messages.success(
            self.request, 'Cadena de Suministros guardado'
            )

        return redirect('cadena_app:update_cadena1',pk=cadena)

    def formset_variants_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        print("entro aqui - Variant")
        variants = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for variant in variants:
            variant.cadena_asociada = self.object
            variant.save()

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
            tramo.cadena_asociada = self.object
            tramo.save()
            calcularEmisionesTramos(tramo)


    def formset_actividades_valid(self,formset):
        print("entro aqui - Actividades")
        actividades = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()
        for actividad in actividades:
            actividad.cadena_asociada = self.object
            actividad.save()
            calcularemisionEquipos(actividad)
            
@method_decorator(login_required, name='dispatch')
class CadenaSuministroCreateView(CadenaSuministroInLine, CreateView):
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        producto_id = self.kwargs.get('pk')
        print(f"Mi nombre es {producto_id}")

        try:
            producto = Producto.objects.get(id=producto_id)
            print(f"Mi nombre es {producto.sku_producto} y tengo {producto.nom_producto} años.")
            form.fields['prod_asociado'].initial = producto
            form.productonombre = producto.nom_producto

        except Producto.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form


    def get(self,request,*args,**kwards):
        producto_id = self.kwargs.get('pk')
        print(f"Mi nombre es {producto_id}")

        try:
            producto = Producto.objects.get(id=producto_id)
            cadena = CadenaSuministro.objects.get(prod_asociado=producto.id)
            print(f"Mi nombre es {cadena.id}")
            #return UpdateView.as_view(model=MiModelo, template_name='mi_template.html')(request, *args, **kwargs)

        except CadenaSuministro.DoesNotExist:
             return super().get(request)

        return redirect(reverse('cadena_app:update_cadena1', kwargs={'pk': cadena.id}))

    def get_context_data(self, **kwargs):
        ctx = super(CadenaSuministroCreateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'tramos': SuministroTramosPlanFormSet(prefix='tramos'),
                'variants': SuministroPlanFormSet(prefix='variants'),
                'actividades': ActividadPlanFormSet(prefix='actividades')
                
            }
        else:
            return {
                'variants': SuministroPlanFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
                'tramos': SuministroTramosPlanFormSet(self.request.POST or None, self.request.FILES or None, prefix='tramos'),
                'actividades': ActividadPlanFormSet(self.request.POST or None, self.request.FILES or None, prefix='actividades'),
            }

@method_decorator(login_required, name='dispatch')
class CadenaSuministroUpdateView(CadenaSuministroInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(CadenaSuministroUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        formsets = {
        'variants': SuministroPlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
        'tramos': SuministroTramosPlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='tramos'),
        'actividades': ActividadPlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='actividades'),
        }

        for formset_form in formsets['variants'].forms:
            suministro_id = formset_form['suministro_asociado'].initial
            if suministro_id is not None:
                try:
                    suministro = Suministro.objects.get(id=suministro_id)
                    proveedor = Proveedor.objects.get(nom_proveedor=suministro.prov_suministro)
                    #print(f"get_form: {proveedor.id}")
                    formset_form['proveedor_suministro'].initial = proveedor.id
                    formset_form.unidad = suministro.get_unidad_suministro_display()
                except:
                    print("error")

        return formsets

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            cadena_id = self.kwargs.get('pk')
            cadena_name = CadenaSuministro.objects.get(id=cadena_id)
            form.productonombre = cadena_name.prod_asociado.nom_producto
            form.existe = True

            try:
                endpoint = Endpoint.objects.get(id=1)
                salud_humana = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=2)
                eco_terrestre = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=3)
                eco_aguadulce = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=4)
                eco_marino = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)
                endpoint = Endpoint.objects.get(id=5)
                escase_recursos = CadenaCalculosEndpoint.objects.get(cadena_asociada=cadena_name,midpoint_endpoint=endpoint)

                form.salud_humana = "{0:.3E}".format(salud_humana.valor)
                form.eco_terrestre = "{0:.3E}".format(eco_terrestre.valor)
                form.eco_aguadulce = "{0:.3E}".format(eco_aguadulce.valor)
                form.eco_marino = "{0:.3E}".format(eco_marino.valor)
                form.escase_recursos = "{0:.3E}".format(escase_recursos.valor)

            except CadenaCalculosEndpoint.DoesNotExist:
                form.existe = False


            # for form_in_formset in self.get_named_formsets()['variants'].forms:
            #     suministro_id = form_in_formset.fields['suministro_asociado'].initial

            #     print(f"Valor: {suministro_id}")

            #     suministro = Suministro.objects.get(id=suministro_id)
                
            #     proveedor_id = Proveedor.objects.get(id=suministro.prov_suministro)
            #     form_in_formset.fields['proveedor_suministro'].initial = proveedor_id

        except CadenaSuministro.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form

@login_required
def delete_CadenaSuministro(request, pk):

    try:
        variant = Suministro_PlanCadena.objects.get(id=pk)
    except CadenaSuministro.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('cadena_app:update_cadena1', pk=variant.cadena_asociada.id)

    variant.delete()
    messages.success(
            request, 'Suministro eliminado correctamente.'
            )
    return redirect('cadena_app:update_cadena1', pk=variant.cadena_asociada.id)

@login_required
def delete_CadenaActividad(request, pk):

    try:
        variant = Actividad_PlanCadena.objects.get(id=pk)
    except Actividad_PlanCadena.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('cadena_app:update_cadena1', pk=variant.cadena_asociada.id)

    variant.delete()
    messages.success(
            request, 'Actividad eliminada correctamente.'
            )
    return redirect('cadena_app:update_cadena1', pk=variant.cadena_asociada.id)

def cargar_suministros(request):
    proveedor_id = request.GET.get('proveedor_id')
    suministros = Suministro.objects.filter(prov_suministro=proveedor_id)
    data = [{'id':suministro.id,'nom_suministro':suministro.nom_suministro,'unidad_suministro':suministro.unidad_suministro} for suministro in suministros]
    return JsonResponse(data,safe=False)

# ============================================================
# Generales para Emisiones
# ============================================================
def cargar_midpoints(request):
    midpoint_id = request.GET.get('midpoint_id')
    tipo_id = request.GET.get('tipo_id')
    print(f"Tipo es {tipo_id}")

    sustancias = Sustancia_emision.objects.filter(categoria_asociada_id=midpoint_id,tipo_emision=tipo_id)
    data = [{'id':sustancia.id,'componente_emision':sustancia.componente_emision} for sustancia in sustancias]
    return JsonResponse(data,safe=False)

# ============================================================
# Emisiones de Actividades
# ============================================================

class Actividades_PlanCadenaInLine():
    form_class = Actividad_PlanCadenaForm
    model = Actividad_PlanCadena
    template_name = 'cadena_app/update_actividades_emisiones.html'

    def form_invalid(self,form):
        print("error")
        return redirect('cadena_app:update_cadena1', pk=form.cleaned_data['cadena_asociada'].id)

    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error")
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

        return redirect('cadena_app:update_cadena1', pk=form.cleaned_data['cadena_asociada'].id)

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

@method_decorator(login_required, name='dispatch')
class Actividades_PlanCadenaUpdateView(Actividades_PlanCadenaInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(Actividades_PlanCadenaUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        formsets = {
        'emisiones': ActividadEmisionPlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='emisiones'),
        }

        for formset_form in formsets['emisiones'].forms:
            sustancia_id = formset_form['sustancia_asociada'].initial
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
            suministro_plancadena_id = self.kwargs.get('pk')
            actividad_plancadena = Actividad_PlanCadena.objects.get(id=suministro_plancadena_id)
            form.productonombre = actividad_plancadena.cadena_asociada.prod_asociado
            form.indice = actividad_plancadena.cadena_asociada.id
            #form.actividad = actividad_plancadena.nom_actividad

        except Actividad_PlanCadena.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form

def delete_ActividadesEmision(request, pk):

    try:
        emision = ActividadEmision_PlanCadena.objects.get(id=pk)
    except ActividadEmision_PlanCadena.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('cadena_app:add_emisionact', pk=emision.actividadplan_asociado.id)

    emision.delete()
    messages.success(
            request, 'Emision eliminada correctamente.'
            )
    return redirect('cadena_app:add_emisionact', pk=emision.actividadplan_asociado.id)

# ============================================================
# Emisiones de Suministro
# ============================================================


class Suministro_PlanCadenaInLine():
    form_class = SuministroPlanCadenaForm
    model = Suministro_PlanCadena
    template_name = 'cadena_app/update_suministro_emisiones.html'

    def form_invalid(self,form):
        print("error")

        return redirect('cadena_app:update_cadena1', pk=form.cleaned_data['cadena_asociada'].id)


    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error")
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
            self.request, 'Suministro Guardado exitosamente.'
            )

        return redirect('cadena_app:add_emisionplan', pk=self.object.pk)

    def formset_variants_valid(self,formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        variants = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for variant in variants:
            variant.sumcadena_asociado = self.object
            variant.save()
            calcularemisionesSuministro(variant)
            print(f"Mi suministroEmision_asociado es {variant}")

    def formset_tramos_valid(self,formset):
        print("Entro aqui - Tramos")
        tramos = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for tramo in tramos:
            tramo.sumcadena_asociado = self.object
            tramo.save()
            calcularEmisionesTramosSuministro(tramo)

@method_decorator(login_required, name='dispatch')
class Suministro_PlanCadenaUpdateView(Suministro_PlanCadenaInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(Suministro_PlanCadenaUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        formsets = {
        'variants': SuministroEmisionPlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
        'tramos': SuministroViajesPlanCadenaForm(self.request.POST or None,self.request.FILES or None,instance=self.object,prefix='tramos')
        }

        for formset_form in formsets['variants'].forms:
            sustancia_id = formset_form['sustancia_asociada'].initial
            if sustancia_id is not None:
                try:
                    sustancia = Sustancia_emision.objects.get(id=sustancia_id)
                    #print(f"get_form: {sustancia.midpoint_emision.id}")
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
            suministro_plancadena_id = self.kwargs.get('pk')
            suministro_plancadena = Suministro_PlanCadena.objects.get(id=suministro_plancadena_id)
            form.productonombre = suministro_plancadena.cadena_asociada.prod_asociado
            form.suministronombre = suministro_plancadena.suministro_asociado.nom_suministro
            form.fields['proveedor_suministro'].initial = suministro_plancadena.suministro_asociado.prov_suministro.id
            form.indice = suministro_plancadena.cadena_asociada.id

            #print(f"get_form: {suministro_plancadena.suministro_asociado.nom_suministro}")
            # for form_in_formset in self.get_named_formsets()['variants'].forms:
            #     suministro_id = form_in_formset.fields['suministro_asociado'].initial

            #     print(f"Valor: {suministro_id}")

            #     suministro = Suministro.objects.get(id=suministro_id)
                
            #     proveedor_id = Proveedor.objects.get(id=suministro.prov_suministro)
            #     form_in_formset.fields['proveedor_suministro'].initial = proveedor_id

        except SuministroEmision_PlanCadena.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form


def delete_SuministroEmision(request, pk):

    try:
        variant = SuministroEmision_PlanCadena.objects.get(id=pk)
    except SuministroEmision_PlanCadena.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('cadena_app:add_emisionplan', pk=variant.sumcadena_asociado.id)

    variant.delete()
    messages.success(
            request, 'Emision eliminada correctamente'
            )
    return redirect('cadena_app:add_emisionplan', pk=variant.sumcadena_asociado.id)

def delete_SuministroViaje(request,pk):
    try:
        variant = SuministroTramos_PlanCadena.objects.get(id=pk)
    except SuministroTramos_PlanCadena.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('cadena_app:add_emisionplan', pk=variant.sumcadena_asociado.id)

    variant.delete()
    messages.success(
            request, 'Tramo de Viaje eliminado correctamente'
            )
    return redirect('cadena_app:add_emisionplan', pk=variant.sumcadena_asociado.id)

# ============================================================
# Tramos Plan
# ============================================================


def delete_TramoPlan(request, pk):

    try:
        tramo = Tramos_PlanCadena.objects.get(id=pk)
    except Tramos_PlanCadena.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('cadena_app:update_cadena1', pk=tramo.cadena_asociada.id)

    tramo.delete()
    messages.success(
            request, 'Tramo de viaje eliminado correctamente.'
            )
    return redirect('cadena_app:update_cadena1', pk=tramo.cadena_asociada.id)



