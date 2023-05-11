from django import forms
from suministro_app.models import Proveedor
from suministro_app.models import Suministro
from django.forms import inlineformset_factory


class ProveedorForm(forms.ModelForm):

    class Meta():
        model = Proveedor
        #fields = ('username','email','password','first_name','last_name','is_active')
        fields = ('nom_proveedor','dir_proveedor','cont_nom_proveedor','cont_tel_proveedor','cont_mai_proveedor','tip_proveedor','com_proveedor')

        widgets = {
            'nom_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'dir_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'cont_nom_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'cont_tel_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'cont_mai_proveedor': forms.EmailInput(attrs={'class':'form-control'}),
            'tip_proveedor': forms.Select(attrs={'class':'form-control'}),
            'com_proveedor': forms.Textarea(attrs={'class':'form-control'}),
        }

        labels = {
            'nom_proveedor': 'Nombre',
            'dir_proveedor': 'Dirección',
            'cont_nom_proveedor': 'Nombre',
            'cont_tel_proveedor': 'Teléfono',
            'cont_mai_proveedor':'Correo Electrónico',
            'tip_proveedor': 'Tipo',
            'com_proveedor':'Comentarios'
        }

class SuministroForm(forms.ModelForm):

    class Meta():
        model = Suministro
        fields = ('sku_suministro','nom_suministro','tip_suministro')

        widgets = {
            'sku_suministro': forms.TextInput(attrs={'class':'form-control'}),
            'nom_suministro': forms.TextInput(attrs={'class':'form-control'}),
            'tip_suministro': forms.Select(attrs={'class':'form-control'}),
        }

        labels = {
            'sku_suministro': 'SKU',
            'nom_suministro': 'Nombre',
            'tip_suministro': 'Tipo',
        }


SuministroFormSet = inlineformset_factory(Proveedor, Suministro,form=SuministroForm,extra=1,can_delete=False,can_delete_extra=True)