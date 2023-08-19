from django.shortcuts import (render, redirect)
from cadena_app.forms import (CadenaNuevaForm,SuministroPlanFormSet,SuministroPlanCadenaForm,SuministroEmisionPlanFormSet)
#from cadena_app.forms import CadenaSumiNuevoForm
from cadena_app.models import (CadenaSuministro, Suministro_PlanCadena,Sustancia_emision,Midpoint_emision,SuministroEmision_PlanCadena)
from producto_app.models import (Producto, VariacionProducto)
from suministro_app.models import (Suministro, Proveedor)
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView,DeleteView)
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
import logging

def cargar_midpoints(request):
    midpoint_id = request.GET.get('midpoint_id')
    tipo_id = request.GET.get('tipo_id')
    print(f"Tipo es {tipo_id}")

    sustancias = Sustancia_emision.objects.filter(midpoint_emision=midpoint_id,tipo_emision=tipo_id)
    data = [{'id':sustancia.id,'componente_emision':sustancia.componente_emision} for sustancia in sustancias]
    return JsonResponse(data,safe=False)



class Suministro_PlanCadenaInLine():
    form_class = SuministroPlanCadenaForm
    model = Suministro_PlanCadena
    template_name = 'cadena_app/update_suministro_emisiones.html'

    def form_invalid(self,form):
        print("error")

        return redirect('producto_app:productos')


    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
            print("error")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            print("entro aqui")
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            print("entro aqui 2")
            if formset_save_func is not None:
                formset_save_func(formset)
                print("entro aqui 3")
            else:
                print("entro aqui 4")
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
                    midpoint = Midpoint_emision.objects.get(id=sustancia.midpoint_emision.id)
                    print(f"get_form: {midpoint.id}")
                    formset_form['midpoint_emision'].initial = midpoint.id
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



def cargar_suministros(request):
    proveedor_id = request.GET.get('proveedor_id')
    suministros = Suministro.objects.filter(prov_suministro=proveedor_id)
    data = [{'id':suministro.id,'nom_suministro':suministro.nom_suministro} for suministro in suministros]
    return JsonResponse(data,safe=False)

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

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            print("entro aqui")
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            print("entro aqui 2")
            if formset_save_func is not None:
                formset_save_func(formset)
                print("entro aqui 3")
            else:
                print("entro aqui 4")
                formset.save()

        return redirect('producto_app:productos')

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
            variant.cadena_asociada = self.object
            variant.save()

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
                'variants': SuministroPlanFormSet(prefix='variants'),
            }
        else:
            return {
                'variants': SuministroPlanFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
            }


class CadenaSuministroUpdateView(CadenaSuministroInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(CadenaSuministroUpdateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
 

    def get_named_formsets(self):

        formsets = {
        'variants': SuministroPlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
        }

        for formset_form in formsets['variants'].forms:
            suministro_id = formset_form['suministro_asociado'].initial
            if suministro_id is not None:
                try:
                    suministro = Suministro.objects.get(id=suministro_id)
                    proveedor = Proveedor.objects.get(nom_proveedor=suministro.prov_suministro)
                    print(f"get_form: {proveedor.id}")
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



