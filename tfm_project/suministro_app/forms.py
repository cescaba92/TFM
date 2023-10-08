from django import forms
from suministro_app.models import Proveedor
from suministro_app.models import Suministro
from suministro_app.models import Equipos
from django.forms import inlineformset_factory
from datetime import date  # Importa el módulo date de datetime

class EquipoForm(forms.ModelForm):

    class Meta():
        model = Equipos
        fields = {'nom_equipo','fabr_equipo','ser_equipo','fec_adqui_equipo','vida_equipo','est_equipo','ubi_equipo','gar_equipo','prov_equipo','potencia_equipo'}

        widgets = {
            'nom_equipo': forms.TextInput(attrs={'class':'form-control'}),
            'fabr_equipo': forms.TextInput(attrs={'class':'form-control'}),
            'ser_equipo': forms.TextInput(attrs={'class':'form-control'}),
            'fec_adqui_equipo':forms.DateInput(
        format=('%Y-%m-%d'),
        attrs={'class': 'form-control', 
               'placeholder': 'Select a date',
               'type': 'date'
              }),
            'vida_equipo': forms.NumberInput(attrs={'class':'form-control','min':0}), 
            'est_equipo': forms.Select(attrs={'class':'form-control'}),
            'ubi_equipo': forms.TextInput(attrs={'class':'form-control'}),
            'gar_equipo': forms.NumberInput(attrs={'class':'form-control','min':0}), 
            'prov_equipo': forms.Select(attrs={'class':'form-control'}),
            'potencia_equipo': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

        labels = {
            'nom_equipo': 'Nombre',
            'fabr_equipo': 'Fabricante',
            'ser_equipo': 'Cod. de Serie',
            'fec_adqui_equipo': 'Fecha Adquisición',
            'vida_equipo': 'Vida Útil (Años)',
            'est_equipo':'Estado',
            'ubi_equipo': 'Ubicación',
            'gar_equipo':'Garantia (Años)',
            'prov_equipo':'Proveedor',
            'potencia_equipo':'Potencia (W)'
        }
        
    def __init__(self, *args, **kwargs):
        super(EquipoForm, self).__init__(*args, **kwargs)
        self.fields['fec_adqui_equipo'].widget.attrs['max'] = date.today()


class ProveedorForm(forms.ModelForm):

    class Meta():
        model = Proveedor
        #fields = ('username','email','password','first_name','last_name','is_active')
        fields = ('nif_proveedor','nom_proveedor','dir_proveedor','cont_nom_proveedor','cont_tel_proveedor','cont_mai_proveedor','tip_proveedor','com_proveedor')

        widgets = {
            'nif_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'nom_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'dir_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'cont_nom_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'cont_tel_proveedor': forms.TextInput(attrs={'class':'form-control'}),
            'cont_mai_proveedor': forms.EmailInput(attrs={'class':'form-control'}),
            'tip_proveedor': forms.Select(attrs={'class':'form-control'}),
            'com_proveedor': forms.Textarea(attrs={'class':'form-control'}),
        }

        labels = {
            'nif_proveedor': 'NIF',
            'nom_proveedor': 'Nombre',
            'dir_proveedor': 'Dirección',
            'cont_nom_proveedor': 'Nombre',
            'cont_tel_proveedor': 'Teléfono',
            'cont_mai_proveedor':'Correo Electrónico',
            'tip_proveedor': 'Tipo',
            'com_proveedor':'Comentarios'
        }

class SuministroSoloForm(forms.ModelForm):
    class Meta():
        Model = Suministro
        fields = ('sku_suministro','nom_suministro','tip_suministro','prov_suministro','unidad_suministro')

        widgets = {
            'sku_suministro': forms.TextInput(attrs={'class':'form-control'}),
            'nom_suministro': forms.TextInput(attrs={'class':'form-control'}),
            'tip_suministro': forms.Select(attrs={'class':'form-control'}),
            'prov_suministro': forms.Select(attrs={'class':'form-control'}),
            'unidad_suministro':forms.Select(attrs={'class':'form-control'}),
        }

        labels = {
            'sku_suministro': 'SKU',
            'nom_suministro': 'Nombre',
            'tip_suministro': 'Tipo',
            'prov_suministro': 'Proveedor',
            'unidad_suministro': 'Unidad'
        }

class SuministroForm(forms.ModelForm):

    class Meta():
        model = Suministro
        fields = ('sku_suministro','nom_suministro','tip_suministro','prov_suministro','unidad_suministro')

        widgets = {
            'sku_suministro': forms.TextInput(attrs={'class':'form-control'}),
            'nom_suministro': forms.TextInput(attrs={'class':'form-control'}),
            'tip_suministro': forms.Select(attrs={'class':'form-control'}),
            'prov_suministro': forms.Select(attrs={'class':'form-control'}),
            'unidad_suministro':forms.Select(attrs={'class':'form-control'}),
        }

        labels = {
            'sku_suministro': 'SKU',
            'nom_suministro': 'Nombre',
            'tip_suministro': 'Tipo',  
            'prov_suministro': 'Proveedor',
            'unidad_suministro': 'Unidad'
        }


SuministroFormSet = inlineformset_factory(Proveedor, Suministro,form=SuministroForm,extra=1,can_delete=False,can_delete_extra=True)