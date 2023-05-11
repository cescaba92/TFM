from django import forms
from producto_app.models import Producto
from producto_app.models import VariacionProducto
from django.forms import inlineformset_factory




class ProductoForm(forms.ModelForm):

    class Meta():
        model = Producto
        #fields = ('username','email','password','first_name','last_name','is_active')
        fields = ('sku_producto','nom_producto','des_producto','canal_producto','tip_producto')

        widgets = {
            'sku_producto': forms.TextInput(attrs={'class':'form-control'}),
            'nom_producto': forms.TextInput(attrs={'class':'form-control'}),
            'canal_producto': forms.TextInput(attrs={'class':'form-control'}),
            'tip_producto': forms.Select(attrs={'class':'form-control'}),
            'des_producto': forms.TextInput(attrs={'class':'form-control'}),
        }

        labels = {
            'sku_producto': 'SKU',
            'nom_producto': 'Nombre',
            'canal_producto': 'Canal de Venta',
            'tip_producto': 'Tipo de Producto',
            'des_producto':'Descripción'
        }

class ProductoVariacionForm(forms.ModelForm):

    class Meta():
        model = VariacionProducto
        fields = ('sku_producto','nom_producto','pes_producto','lar_producto','anc_producto','prof_producto')

        widgets = {
            'sku_producto': forms.TextInput(attrs={'class':'form-control'}),
            'nom_producto': forms.TextInput(attrs={'class':'form-control'}),
            'pes_producto': forms.TextInput(attrs={'class':'form-control'}),
            'lar_producto': forms.TextInput(attrs={'class':'form-control'}),
            'anc_producto': forms.TextInput(attrs={'class':'form-control'}),
            'prof_producto': forms.TextInput(attrs={'class':'form-control'}),
        }

        labels = {
            'sku_producto': 'SKU',
            'nom_producto': 'Nombre',
            'pes_producto': 'Peso',
            'lar_producto': 'Largo',
            'anc_producto': 'Ancho',
            'prof_producto': 'Profundidad',
        }


VariationFormSet = inlineformset_factory(Producto, VariacionProducto,form=ProductoVariacionForm,extra=1,can_delete=False,can_delete_extra=True)