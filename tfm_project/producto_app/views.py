from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from producto_app.forms import ProductoForm, ProductoVariacionForm,VariationFormSet
from producto_app.models import (Producto, VariacionProducto)
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView,DeleteView)
from django.forms.models import inlineformset_factory
from django.contrib import messages

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Create your views here.

class ProductoInLine():
    form_class = ProductoForm
    model = Producto
    template_name = 'producto_app/nuevoproducto.html'

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
            variant.prod_asociado = self.object
            variant.save()

@method_decorator(login_required, name='dispatch')
class ProductosListView(ListView):
    model = Producto
    template_name = 'producto_app/productos.html'

@method_decorator(login_required, name='dispatch')
class ProductosCreateView(CreateView):
    model = Producto
    template_name='producto_app/nuevoproducto.html'
    form_class = ProductoForm

    def form_invalid(self, form):

        return redirect('producto_app:productos')

    def form_valid(self, form):
        form.save()
        return redirect('producto_app:productos')

@method_decorator(login_required, name='dispatch')
class ProductoUpdate(UpdateView):
    model = Producto
    template_name='producto_app/nuevoproducto.html'
    form_class = ProductoForm
    
    def form_valid(self, form):
        messages.success(self.request, "The task was updated successfully.")
        form.save()
        return redirect('producto_app:productos')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        producto_id = self.kwargs.get('pk')
        producto = Producto.objects.get(id=producto_id)
        form.producto = producto.nom_producto
        return form

# class ProductosCreateView(ProductoInLine, CreateView):
    
#     def get_context_data(self, **kwargs):
#         ctx = super(ProductosCreateView, self).get_context_data(**kwargs)
#         ctx['named_formsets'] = self.get_named_formsets()
#         return ctx

#     def get_named_formsets(self):
#         if self.request.method == "GET":
#             return {
#                 'variants': VariationFormSet(prefix='variants'),
#             }
#         else:
#             return {
#                 'variants': VariationFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
#             }


# class ProductoUpdate(ProductoInLine, UpdateView):

#     def get_context_data(self, **kwargs):
#         ctx = super(ProductoUpdate, self).get_context_data(**kwargs)
#         ctx['named_formsets'] = self.get_named_formsets()
#         return ctx

#     def get_named_formsets(self):
#         return {
#             'variants': VariationFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
#         }

   

def delete_producto(request,pk):
    try:
        producto = Producto.objects.get(id=pk)
    except Producto.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('producto_app:productos')

    producto.delete()

    messages.success(
            request, 'Producto Eliminado.'
            )
    return redirect('producto_app:productos')


def delete_variant(request, pk):
    try:
        variant = VariacionProducto.objects.get(id=pk)
    except VariacionProducto.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('producto_app:update_producto', pk=variant.prod_asociado.id)

    variant.delete()
    messages.success(
            request, 'Variante Eliminado'
            )
    return redirect('producto_app:update_producto', pk=variant.prod_asociado.id)


