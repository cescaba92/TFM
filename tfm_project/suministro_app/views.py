from django.shortcuts import render, redirect
from suministro_app.forms import ProveedorForm, SuministroForm,SuministroFormSet
from suministro_app.models import (Proveedor, Suministro)
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView,DeleteView)
from django.forms.models import inlineformset_factory
from django.contrib import messages

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Create your views here.

class ProveedorInLine():
    form_class = ProveedorForm
    model = Proveedor
    template_name = 'suministro_app/new_update_suministro.html'

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

    def formset_suministro_valid(self,formset):
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




class ProveedoresListView(ListView):
    model = Proveedor
    template_name = 'suministro_app/proveedores.html'

class ProveedoresCreateView(ProveedorInLine, CreateView):
    
    def get_context_data(self, **kwargs):
        ctx = super(ProductosCreateView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'variants': VariationFormSet(prefix='variants'),
            }
        else:
            return {
                'variants': VariationFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
            }