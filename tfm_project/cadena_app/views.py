from django.shortcuts import (render, redirect)
from cadena_app.forms import CadenaNuevaForm
from cadena_app.models import CadenaSuministro
from producto_app.models import (Producto, VariacionProducto)
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView,DeleteView)
from django.forms.models import inlineformset_factory
from django.contrib import messages

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
import logging


class CadenaSuministroUpdate(UpdateView):
    model = CadenaSuministro
    template_name='cadena_app/new_cadena_suministro.html'
    form_class = CadenaNuevaForm
    
    def form_valid(self, form):
        messages.success(self.request, "The task was updated successfully.")
        form.save()
        return redirect('producto_app:productos')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

    
        try:
            cadena_id = self.kwargs.get('pk')
            cadena_name = CadenaSuministro.objects.get(id=cadena_id)
            #producto = Producto.objects.get(id=cadena_name.prod_asociado.id)
            #print(f"Mi nombre es {producto.sku_producto} y tengo {producto.nom_producto} años.")
            form.productonombre = cadena_name.prod_asociado.nom_producto

        except Producto.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form
    

# Create your views here.
class CadenaSuministroView(CreateView):
    model = CadenaSuministro
    template_name='cadena_app/new_cadena_suministro.html'
    form_class = CadenaNuevaForm
    #producto = Producto

    def get(self,request,*args,**kwards):
        producto_id = self.kwargs.get('producto')
        print(f"Mi nombre es {producto_id}")

        try:
            producto = Producto.objects.get(id=producto_id)
            cadena = CadenaSuministro.objects.get(prod_asociado=producto.id)
            print(f"Mi nombre es {cadena.id}")
            #return UpdateView.as_view(model=MiModelo, template_name='mi_template.html')(request, *args, **kwargs)

        except CadenaSuministro.DoesNotExist:
             return super().get(request)

        return redirect(reverse('cadena_app:update_cadena1', kwargs={'pk': cadena.id}))

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        producto_id = self.kwargs.get('producto')
        print(f"Mi nombre es {producto_id}")

        try:
            producto = Producto.objects.get(id=producto_id)
            print(f"Mi nombre es {producto.sku_producto} y tengo {producto.nom_producto} años.")
            form.fields['prod_asociado'].initial = producto
            form.productonombre = producto.nom_producto

        except Producto.DoesNotExist:
            messages.success(request, 'Object Does not exit')

        return form
    


    def form_invalid(self, form):
        print("error")

        return redirect('producto_app:productos')

    def form_valid(self, form):
        print("aqui")
        form.save()


        return redirect('producto_app:productos')

  




