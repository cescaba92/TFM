from django import forms
from cadena_app.models import (CadenaSuministro,Suministro_PlanCadena)
#from cadena_app.models import Suministro_PlanCadena
from suministro_app.models import (Proveedor, Suministro)
from django.forms import inlineformset_factory

class CadenaNuevaForm(forms.ModelForm):
    class Meta():
        model = CadenaSuministro
        fields = {'prod_asociado','fuente_energia','tierra_ocupada','tierra_m2'}
        
        widgets = {
            'prod_asociado':forms.Select(attrs={'class':'form-control'}),
            #'prod_asociado':forms.Select(attrs={'class':'form-control'}),
            'fuente_energia':forms.Select(attrs={'class':'form-control'}),
            'tierra_ocupada':forms.Select(attrs={'class':'form-control'}),
            'tierra_m2': forms.NumberInput(attrs={'class':'form-control'}),
        };

        labels = {
            'prod_asociado': 'Producto Asociado',
            'fuente_energia': 'Fuente de Energia',
            'tierra_ocupada': 'Tipo de Tierra Ocupada',
            'tierra_m2': 'm2 de uso',
        }

class SuministroPlanCadenaForm(forms.ModelForm):
    proveedor_suministro = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'proveedor-select form-control','onchange':'cargarProductos(this);'}))

    class Meta():
        model = Suministro_PlanCadena
        fields = {'proveedor_suministro','suministro_asociado','cadena_asociada','unidad_suministro','cantidad_suministro'}

        widgets = {
            'proveedor_suministro':forms.Select(attrs={'class':'proveedor-select'}),
            'suministro_asociado':forms.Select(attrs={'class':'suministro-select form-control'}),
            'cadena_asociada':forms.Select(attrs={'class':'form-control'}),
            'unidad_suministro': forms.Select(attrs={'class':'form-control'}),
            'cantidad_suministro': forms.NumberInput(attrs={'class':'form-control'})
        };

    
    field_order = ['proveedor_suministro', 'suministro_asociado', 'cadena_asociada','unidad_suministro','cantidad_suministro']

    def __init__(self, *args, **kwargs):
        super(SuministroPlanCadenaForm, self).__init__(*args, **kwargs)

        #cadenaSuministro = CadenaSuministro.objects.value_list('id',flat=True).distinct()
        #suministro = Suministro.objects.get(id=1)
        proveedores = Proveedor.objects.all();

        self.fields['proveedor_suministro'].choices =[('', '---------')]+[(proveedor.id,proveedor) for proveedor in proveedores]


SuministroPlanFormSet = inlineformset_factory(CadenaSuministro, Suministro_PlanCadena,form=SuministroPlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)

