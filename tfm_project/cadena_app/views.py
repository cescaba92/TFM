from django.shortcuts import (render, redirect)
from cadena_app.forms import (CadenaNuevaForm,SuministroPlanFormSet,SuministroPlanCadenaForm,SuministroEmisionPlanFormSet,SuministroTramosPlanFormSet,Actividad_PlanCadenaForm,ActividadPlanFormSet,ActividadEmisionPlanCadenaForm,ActividadEmisionPlanFormSet)
from cadena_app.models import (CadenaSuministro, Suministro_PlanCadena,Sustancia_emision,Midpoint_emision,SuministroEmision_PlanCadena,Tramos_PlanCadena,Actividad_PlanCadena,ActividadEmision_PlanCadena,MidpointEmision_PlanCadena,Sustancia_Midpoint_emision,Categoria_emision,MidpointTramos)
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
# Proceso de Calculo de Midpoints
# ============================================================

def calcularemisionesTierra(id_cadena,midpointTierra,cantidad):    
    points_occ = cantidad * midpointTierra.cfm_tipouso
    points_relax = cantidad * midpointTierra.cfm_relax_tipouso
    tipo_midpoint_occ = "TO"
    tipo_midpoint_rel = "TX"
    midpoints_emision_asociada = Midpoint_emision.objects.get(nom_midpoint='Tierra Utilizada')
    cadena = CadenaSuministro.objects.get(id=id_cadena)
    
    try:
        midpointOcc = MidpointEmision_PlanCadena.objects.get(tipo_midpoint=tipo_midpoint_occ,cadena_asociada=cadena)
        midpointOcc.points_midpoint = points_occ
        midpointOcc.save()

    except MidpointEmision_PlanCadena.DoesNotExist:
        midpointOcc = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint_occ,midpoints_emision_asociada=midpoints_emision_asociada,points_midpoint=points_occ)
        midpointOcc.save()
    try:
        midpointRel = MidpointEmision_PlanCadena.objects.get(tipo_midpoint=tipo_midpoint_rel,cadena_asociada=cadena)
        midpointRel.points_midpoint = points_relax
        midpointRel.save()
    except:
        midpointRel = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint_rel,midpoints_emision_asociada=midpoints_emision_asociada,points_midpoint=points_relax)
        midpointRel.save()


def calcularemisionesSuministro(suministroEmision):
    
    cadena = suministroEmision.sumcadena_asociado.cadena_asociada
    tipo_midpoint = "SU"

    emision_midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=suministroEmision.sustancia_asociada)

    for emision_midpoint in emision_midpoints:
        midpoints_emision_asociada = emision_midpoint.midpoint_emision
        suministroEmision_asociado = suministroEmision
        points = emision_midpoint.valor_emision * suministroEmision.cantidad_sustancia
        print(f"Mi suministroEmision_asociado es {suministroEmision.id}")
        
        try:
            midpoint = MidpointEmision_PlanCadena.objects.get(suministroEmision_asociado=suministroEmision_asociado,midpoints_emision_asociada=midpoints_emision_asociada,tipo_midpoint=tipo_midpoint)
            midpoint.points_midpoint = points
            midpoint.save()

        except MidpointEmision_PlanCadena.DoesNotExist:
            midpoint = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,midpoints_emision_asociada=midpoints_emision_asociada,points_midpoint=points,suministroEmision_asociado=suministroEmision_asociado)
            midpoint.save()



    #midpoints_emision_asociada = suministroEmision.sustancia_asociada.midpoint_emision
    #suministroEmision_asociado = suministroEmision
    #points = suministroEmision.sustancia_asociada.valor_emision * suministroEmision.cantidad_sustancia
    #print(f"Mi suministroEmision_asociado es {suministroEmision.id}")

def calcularemisionEquipos(actividad_PlanCadena):
    print("entro a calcularemisionEquipos")
    uso_horas = actividad_PlanCadena.tiempo_equipo_asociado
    potencia = actividad_PlanCadena.equipo_asociado.potencia_equipo
    kilo_vatios_hora = (potencia/1000.0)*uso_horas

    fuente_energia = actividad_PlanCadena.cadena_asociada.fuente_energia
    co2_equipo_point = fuente_energia.co2_energia * kilo_vatios_hora
    nox_equipo_point = fuente_energia.nox_energia * kilo_vatios_hora
    so2_equipo_point = fuente_energia.so2_energia  * kilo_vatios_hora
    pm_equipo_point = fuente_energia.pm_energia * kilo_vatios_hora
    co60_equipo_point = fuente_energia.co60_energia * kilo_vatios_hora

    puntos_a_revisar = [(settings.CODIGO_C02,co2_equipo_point),(settings.CODIGO_NOX,nox_equipo_point),(settings.CODIGO_SO2,so2_equipo_point),(settings.CODIGO_PM,pm_equipo_point),(settings.CODIGO_CO60,co60_equipo_point)]

    cadena = actividad_PlanCadena.cadena_asociada
    actividad = actividad_PlanCadena
    tipo_midpoint = "CE"

    for dupla in puntos_a_revisar:
        midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=dupla[0])

        for midpoint in midpoints:
            midpoints_emision_asociada = midpoint.midpoint_emision
            points = dupla[1] * midpoint.valor_emision

            try:
                midpointEmision = MidpointEmision_PlanCadena.objects.get(sustancia_midpoint_asociado=midpoint,cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,actividad_asociada=actividad)
                midpointEmision.points_midpoint = points
                midpointEmision.save()
            except MidpointEmision_PlanCadena.DoesNotExist:
                midpointEmision = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,sustancia_midpoint_asociado=midpoint,points_midpoint=points,actividad_asociada=actividad)
                midpointEmision.save()

 

def calcularemisionesActividades(actividadEmision):
    cadena = actividadEmision.actividadplan_asociado.cadena_asociada
    tipo_midpoint = "AC"
    emision_midpoints = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=actividadEmision.sustancia_asociada)
    print("Entro Aqui")
    for emision_midpoint in emision_midpoints:
        midpoint_emision_asociada = emision_midpoint.midpoint_emision
        actividademision_asociado = actividadEmision
        points = emision_midpoint.valor_emision * actividadEmision.cantidad_sustancia

        try:
            midpoint = MidpointEmision_PlanCadena.objects.get(actividademision_asociado=actividademision_asociado,midpoints_emision_asociada=midpoint_emision_asociada,tipo_midpoint=tipo_midpoint)
            midpoint.points_midpoint = points
            midpoint.save()

        except MidpointEmision_PlanCadena.DoesNotExist:
            midpoint = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,midpoints_emision_asociada=midpoint_emision_asociada,points_midpoint=points,actividademision_asociado=actividademision_asociado)
            midpoint.save()

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

    cadena = tramos_PlanCadena.cadena_asociada
    
    tipo_midpoint = "TR"

    #Registro CO2
    codigo_c02 = 35
    emision_midpoints1 = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=codigo_c02)

    for emision_midpoint in emision_midpoints1:
        midpoints_emision_asociada = emision_midpoint.midpoint_emision
        tramos_PlanCadena = tramos_PlanCadena
        points = emision_midpoint.valor_emision * co2_tramo_point
        #print(f"Mi suministroEmision_asociado es {suministroEmision.id}")
        
        try:
            midpoint = MidpointEmision_PlanCadena.objects.get(tramos_PlanCadena=tramos_PlanCadena,midpoints_emision_asociada=midpoints_emision_asociada,tipo_midpoint=tipo_midpoint)
            midpoint.points_midpoint = points
            midpoint.save()

        except MidpointEmision_PlanCadena.DoesNotExist:
            midpoint = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,midpoints_emision_asociada=midpoints_emision_asociada,points_midpoint=points,tramos_PlanCadena=tramos_PlanCadena)
            midpoint.save()

    #Registro NOX
    codigo_nox = 31
    emision_midpoints2 = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=codigo_nox)

    for emision_midpoint in emision_midpoints2:
        midpoints_emision_asociada = emision_midpoint.midpoint_emision
        tramos_PlanCadena = tramos_PlanCadena
        points = emision_midpoint.valor_emision * nox_tramo_point
        #print(f"Mi suministroEmision_asociado es {suministroEmision.id}")
        
        try:
            midpoint = MidpointEmision_PlanCadena.objects.get(tramos_PlanCadena=tramos_PlanCadena,midpoints_emision_asociada=midpoints_emision_asociada,tipo_midpoint="TN")
            midpoint.points_midpoint = points
            midpoint.save()

        except MidpointEmision_PlanCadena.DoesNotExist:
            midpoint = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint="TN",midpoints_emision_asociada=midpoints_emision_asociada,points_midpoint=points,tramos_PlanCadena=tramos_PlanCadena)
            midpoint.save()
    
    #Registro PM
    codigo_pm = 36

    emision_midpoints3 = Sustancia_Midpoint_emision.objects.filter(sustancia_emision=codigo_pm)

    for emision_midpoint in emision_midpoints3:
        midpoints_emision_asociada = emision_midpoint.midpoint_emision
        tramos_PlanCadena = tramos_PlanCadena
        points = emision_midpoint.valor_emision * pm_tramo_point
        #print(f"Mi suministroEmision_asociado es {suministroEmision.id}")
        
        try:
            midpoint = MidpointEmision_PlanCadena.objects.get(tramos_PlanCadena=tramos_PlanCadena,midpoints_emision_asociada=midpoints_emision_asociada,tipo_midpoint=tipo_midpoint)
            midpoint.points_midpoint = points
            midpoint.save()

        except MidpointEmision_PlanCadena.DoesNotExist:
            midpoint = MidpointEmision_PlanCadena(cadena_asociada=cadena,tipo_midpoint=tipo_midpoint,midpoints_emision_asociada=midpoints_emision_asociada,points_midpoint=points,tramos_PlanCadena=tramos_PlanCadena)
            midpoint.save()

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

        #print(f"Mi cadena es {midpointTierra.nom_tipouso}")
        calcularemisionesTierra(cadena,midpointTierra,cantidad)

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
           
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        return redirect('producto_app:productos')

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
                except:
                    print("error")


        return formsets

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        try:
            cadena_id = self.kwargs.get('pk')
            cadena_name = CadenaSuministro.objects.get(id=cadena_id)
            form.productonombre = cadena_name.prod_asociado.nom_producto


            # for form_in_formset in self.get_named_formsets()['variants'].forms:
            #     suministro_id = form_in_formset.fields['suministro_asociado'].initial

            #     print(f"Valor: {suministro_id}")

            #     suministro = Suministro.objects.get(id=suministro_id)
                
            #     proveedor_id = Proveedor.objects.get(id=suministro.prov_suministro)
            #     form_in_formset.fields['proveedor_suministro'].initial = proveedor_id

        except CadenaSuministro.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form

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
            request, 'Variant deleted successfully'
            )
    return redirect('cadena_app:update_cadena1', pk=variant.cadena_asociada.id)

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
            request, 'Variant deleted successfully'
            )
    return redirect('cadena_app:update_cadena1', pk=variant.cadena_asociada.id)

def cargar_suministros(request):
    proveedor_id = request.GET.get('proveedor_id')
    suministros = Suministro.objects.filter(prov_suministro=proveedor_id)
    data = [{'id':suministro.id,'nom_suministro':suministro.nom_suministro} for suministro in suministros]
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
            request, 'Variant deleted successfully'
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

        return redirect('cadena_app:update_cadena1', pk=form.cleaned_data['cadena_asociada'].id)

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
            #print(f"Mi suministroEmision_asociado es {variant}")

class Suministro_PlanCadenaUpdateView(Suministro_PlanCadenaInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(Suministro_PlanCadenaUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        formsets = {
        'variants': SuministroEmisionPlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
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
            request, 'Variant deleted successfully'
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
            request, 'Variant deleted successfully'
            )
    return redirect('cadena_app:update_cadena1', pk=tramo.cadena_asociada.id)



