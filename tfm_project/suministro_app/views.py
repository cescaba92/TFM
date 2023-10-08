from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from suministro_app.forms import (ProveedorForm, SuministroForm, SuministroFormSet,EquipoForm,SuministroForm)
from suministro_app.models import (Proveedor, Suministro, Equipos)
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView,DeleteView)
from django.forms.models import inlineformset_factory
from django.contrib import messages

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Create your views here.

class ProveedorInLine():
    form_class = ProveedorForm
    model = Proveedor
    template_name = 'suministro_app/new_update_proveedor.html'

    def form_valid(self,form):
        named_formsets = self.get_named_formsets()

        if not all((x.is_valid() for x in named_formsets.values())):
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

        return redirect('suministro_app:proveedores')

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
            variant.prov_suministro = self.object
            variant.save()

@method_decorator(login_required, name='dispatch')
class ProveedorUpdate(ProveedorInLine, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ProveedorUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'variants': SuministroFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
        }

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        proveedor_id = self.kwargs.get('pk')
        proveedor = Proveedor.objects.get(id=proveedor_id)
        form.proveedor = proveedor.nom_proveedor
        return form

def delete_proveedor(request,pk):
    try:
        proveedor = Proveedor.objects.get(id=pk)
    except Proveedor.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('suministro_app:proveedores')

    proveedor.delete()

    messages.success(
            request, 'Proveedor eliminado.'
            )
    return redirect('suministro_app:proveedores')


def delete_suministro(request, pk):
    try:
        variant = Suministro.objects.get(id=pk)
    except Suministro.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('suministro_app:proveedores', pk=variant.prod_asociado.id)

    variant.delete()
    messages.success(
            request, 'Suministro eliminado.'
            )
    return redirect('suministro_app:proveedores', pk=variant.prod_asociado.id)

@method_decorator(login_required, name='dispatch')
class ProveedoresListView(ListView):
    model = Proveedor
    template_name = 'suministro_app/proveedores.html'

@method_decorator(login_required, name='dispatch')
class ProveedoresCreateView(ProveedorInLine, CreateView):
    
    def get_context_data(self, **kwargs):
        ctx = super(ProveedoresCreateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'variants': SuministroFormSet(prefix='variants'),
            }
        else:
            return {
                'variants': SuministroFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
            }

# ============================================================
# Suministro
# ============================================================
@method_decorator(login_required, name='dispatch')
class SuministroListView(ListView):
    model = Suministro
    template_name = 'suministro_app/suministros.html'

@method_decorator(login_required, name='dispatch')
class SuministroCreateView(CreateView):
    model = Suministro
    template_name='suministro_app/new_update_suministro.html'
    form_class = SuministroForm

    def form_invalid(self, form):

         return redirect('suministro_app:suministros')

    def form_valid(self, form):
        form.save()
        return redirect('suministro_app:suministros')

@method_decorator(login_required, name='dispatch')
class SuministroUpdate(UpdateView):
    model = Suministro
    template_name='suministro_app/new_update_suministro.html'
    form_class = SuministroForm
    
    def form_valid(self, form):
        messages.success(self.request, "The task was updated successfully.")
        form.save()
        return redirect('suministro_app:suministros')

    def get_form(self, form_class=None):
         form = super().get_form(form_class)
         suministro_id = self.kwargs.get('pk')
         suministro = Suministro.objects.get(id=suministro_id)
         form.nombre = suministro.nom_suministro
         return form

def delete_suministro(request,pk):
    try:
        suministro = Suministro.objects.get(id=pk)
    except Suministro.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('suministro_app:suministros')

    suministro.delete()

    messages.success(
            request, 'Suministro eliminado.'
            )
    return redirect('suministro_app:suministros')

# ============================================================
# Equipos
# ============================================================

@method_decorator(login_required, name='dispatch')
class EquipoCreateView(CreateView):
    model = Equipos
    template_name='suministro_app/new_update_equipos.html'
    form_class = EquipoForm

    def form_invalid(self, form):

         return redirect('suministro_app:equipos')

    def form_valid(self, form):
        form.save()
        return redirect('suministro_app:equipos')

@method_decorator(login_required, name='dispatch')
class EquiposListView(ListView):
    model = Equipos
    template_name = 'suministro_app/equipos.html'

@method_decorator(login_required, name='dispatch')
class EquipoUpdate(UpdateView):
    model = Equipos
    template_name='suministro_app/new_update_equipos.html'
    form_class = EquipoForm
    
    def form_valid(self, form):
        messages.success(self.request, "The task was updated successfully.")
        form.save()
        return redirect('suministro_app:equipos')

    def get_form(self, form_class=None):
         form = super().get_form(form_class)
         equipo_id = self.kwargs.get('pk')
         equipo = Equipos.objects.get(id=equipo_id)
         form.nombre = equipo.nom_equipo
         return form

def delete_equipo(request,pk):
    try:
        equipo = Equipos.objects.get(id=pk)
    except Proveedor.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('suministro_app:equipos')

    equipo.delete()

    messages.success(
            request, 'Equipo eliminado.'
            )
    return redirect('suministro_app:equipos')

