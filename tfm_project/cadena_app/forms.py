from django import forms
from cadena_app.models import (CadenaSuministro,Suministro_PlanCadena,SuministroEmision_PlanCadena,Midpoint_emision,Sustancia_emision,TramosExternos_PlanCadena)
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


#Suministro y Emisiones

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

class SuministroEmisionPlanCadenaForm(forms.ModelForm):
    midpoint_emision = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'midpoint-select form-control','onchange':'cargarEmisiones(this);'}))
    tipo_emision = forms.ChoiceField(choices=[],widget=forms.Select(attrs={'class':'tipo-select form-control','onchange':'cargarTipo(this);'}))

    class Meta():
        model = SuministroEmision_PlanCadena
        fields={'tipo_emision','midpoint_emision','sumcadena_asociado','sustancia_asociada','cantidad_sustancia'}

        widgets = {
            'tipo_emision':forms.Select(attrs={'class':'tipo-select form-control'}),
            'midpoint_emision':forms.Select(attrs={'class':'midpoint-select'}),
            'sumcadena_asociado':forms.Select(attrs={'class':'form-control'}),
            'sustancia_asociada':forms.Select(attrs={'class':'sustancia-select form-control'}),
            'cantidad_sustancia': forms.NumberInput(attrs={'class':'form-control'})
        }

        field_order = ['tipo_emision','midpoint_emision','sustancia_asociada','cantidad_sustancia','sumcadena_asociado']

    def __init__(self, *args, **kwargs):
        super(SuministroEmisionPlanCadenaForm, self).__init__(*args, **kwargs)

        #emisiones = Sustancia_emision.objects.all();
        midpoints_emision = Midpoint_emision.objects.all();
        #self.fields['sustancia_asociada'].choices = [('', '---------')]
        self.fields['midpoint_emision'].choices =[('', '---------')]+[(midpoint_emision.id,midpoint_emision) for midpoint_emision in midpoints_emision]
        self.fields['tipo_emision'].choices = [('', '---------')]+[('AT', 'Atmósfera')]+[('TI', 'Tierra')]+[('AD', 'Agua Dulce')]+[('AS', 'Océanos')]+[('RF', 'Recursos Fosiles')]+[('CR', 'Consumo Recursos')]

SuministroEmisionPlanFormSet = inlineformset_factory(Suministro_PlanCadena, SuministroEmision_PlanCadena,form=SuministroEmisionPlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)
SuministroPlanFormSet = inlineformset_factory(CadenaSuministro, Suministro_PlanCadena,form=SuministroPlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)


#Tramos de Viaje
class TramosExternos_PlanCadenaForm(forms.ModelForm):

    class Meta():
        model= TramosExternos_PlanCadena
        fields={'tipo_tramoexterno','energia_tramoexterno','km_tramoexterno'}

        widgets = {
            'tipo_tramoexterno':forms.Select(attrs={'class':'form-control'}),
            'energia_tramoexterno':forms.Select(attrs={'class':'form-control'}),
            'km_tramoexterno':forms.NumberInput(attrs={'class':'form-control'})
        }

SuministroPlanFormSet = inlineformset_factory(CadenaSuministro, TramosExternos_PlanCadena,form=TramosExternos_PlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)
