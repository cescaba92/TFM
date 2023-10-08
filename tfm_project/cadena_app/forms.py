from django import forms
from cadena_app.models import (CadenaSuministro,Suministro_PlanCadena,SuministroEmision_PlanCadena,Midpoint_emision,Sustancia_emision,Tramos_PlanCadena,Actividad_PlanCadena,ActividadEmision_PlanCadena,Categoria_emision,SuministroTramos_PlanCadena)
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
            'tierra_m2': forms.NumberInput(attrs={'class':'form-control','min':0}), 
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
            'cantidad_suministro': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        };

    
    field_order = ['proveedor_suministro', 'suministro_asociado', 'cadena_asociada','unidad_suministro','cantidad_suministro']

    def __init__(self, *args, **kwargs):
        super(SuministroPlanCadenaForm, self).__init__(*args, **kwargs)

        #cadenaSuministro = CadenaSuministro.objects.value_list('id',flat=True).distinct()
        #suministro = Suministro.objects.get(id=1)
        proveedores = Proveedor.objects.all();

        self.fields['proveedor_suministro'].choices =[('', '---------')]+[(proveedor.id,proveedor) for proveedor in proveedores]

class SuministroEmisionPlanCadenaForm(forms.ModelForm):
    categoria_asociada = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'midpoint-select form-control','onchange':'cargarEmisiones(this);'}))
    tipo_emision = forms.ChoiceField(choices=[],widget=forms.Select(attrs={'class':'tipo-select form-control','onchange':'cargarTipo(this);'}))

    class Meta():
        model = SuministroEmision_PlanCadena
        fields={'tipo_emision','categoria_asociada','sumcadena_asociado','sustancia_asociada','cantidad_sustancia'}

        widgets = {
            'tipo_emision':forms.Select(attrs={'class':'tipo-select form-control'}),
            'categoria_asociada':forms.Select(attrs={'class':'midpoint-select'}),
            'sumcadena_asociado':forms.Select(attrs={'class':'form-control'}),
            'sustancia_asociada':forms.Select(attrs={'class':'sustancia-select form-control'}),
            'cantidad_sustancia': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

        field_order = ['tipo_emision','categoria_asociada','sustancia_asociada','cantidad_sustancia','sumcadena_asociado']

    def __init__(self, *args, **kwargs):
        super(SuministroEmisionPlanCadenaForm, self).__init__(*args, **kwargs)

        #emisiones = Sustancia_emision.objects.all();
        categorias_emision = Categoria_emision.objects.all();
        #self.fields['sustancia_asociada'].choices = [('', '---------')]
        self.fields['categoria_asociada'].choices =[('', '---------')]+[(categoria_emision.id,categoria_emision) for categoria_emision in categorias_emision]
        self.fields['tipo_emision'].choices = [('', '---------')]+[('AT', 'Atmósfera')]+[('TI', 'Tierra')]+[('AD', 'Agua Dulce')]+[('AS', 'Océanos')]+[('RF', 'Recursos Fosiles')]+[('CR', 'Consumo Recursos')]

class SuministroViajesPlanCadenaForm(forms.ModelForm):
    class Meta():
        model= SuministroTramos_PlanCadena
        fields={'sumcadena_asociado','tipo_tramo','energia_tramo','descripcion_tramo','km_tramo'}

        widgets = {
            'sumcadena_asociado':forms.Select(attrs={'class':'form-control'}),
            'tipo_tramo':forms.Select(attrs={'class':'form-control'}),
            'energia_tramo':forms.Select(attrs={'class':'form-control'}),
            'descripcion_tramo':forms.TextInput(attrs={'class':'form-control'}),
            'km_tramo':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

SuministroViajesPlanCadenaForm = inlineformset_factory(Suministro_PlanCadena, SuministroTramos_PlanCadena,form=SuministroViajesPlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)
SuministroEmisionPlanFormSet = inlineformset_factory(Suministro_PlanCadena, SuministroEmision_PlanCadena,form=SuministroEmisionPlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)
SuministroPlanFormSet = inlineformset_factory(CadenaSuministro, Suministro_PlanCadena,form=SuministroPlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)


#Tramos de Viaje
class Tramos_PlanCadenaForm(forms.ModelForm):

    class Meta():
        model= Tramos_PlanCadena
        #fields={'cadena_asociada','tipo_transporte','tipo_tramoexterno','energia_tramoexterno','km_tramoexterno','descripcion_tramoexterno'}
        fields={'cadena_asociada','tipo_tramoexterno','energia_tramoexterno','km_tramoexterno','descripcion_tramoexterno'}

        widgets = {
            'cadena_asociada':forms.Select(attrs={'class':'form-control'}),
            #'tipo_transporte':forms.Select(attrs={'class':'form-control'}),
            'tipo_tramoexterno':forms.Select(attrs={'class':'form-control'}),
            'energia_tramoexterno':forms.Select(attrs={'class':'form-control'}),
            'descripcion_tramoexterno':forms.TextInput(attrs={'class':'form-control'}),
            'km_tramoexterno':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

SuministroTramosPlanFormSet = inlineformset_factory(CadenaSuministro, Tramos_PlanCadena,form=Tramos_PlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)

#Actividades
class Actividad_PlanCadenaForm(forms.ModelForm):

    class Meta():
        model = Actividad_PlanCadena
        fields = {'cadena_asociada','tipo_actividad','nom_actividad','equipo_asociado','tiempo_equipo_asociado'}

        widgets = {
            'cadena_asociada':forms.Select(attrs={'class':'form-control'}),
            'tipo_actividad':forms.Select(attrs={'class':'form-control'}),
            'nom_actividad':forms.TextInput(attrs={'class':'form-control'}),
            'equipo_asociado':forms.Select(attrs={'class':'form-control'}),
            'tiempo_equipo_asociado':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

ActividadPlanFormSet = inlineformset_factory(CadenaSuministro, Actividad_PlanCadena,form=Actividad_PlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)

class ActividadEmisionPlanCadenaForm(forms.ModelForm):

    categoria_asociada = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'midpoint-select form-control','onchange':'cargarEmisiones(this);'}))
    tipo_emision = forms.ChoiceField(choices=[],widget=forms.Select(attrs={'class':'tipo-select form-control','onchange':'cargarTipo(this);'}))

    class Meta():
        model = ActividadEmision_PlanCadena
        fields={'tipo_emision','categoria_asociada','actividadplan_asociado','sustancia_asociada','cantidad_sustancia'}

        widgets = {
            'tipo_emision':forms.Select(attrs={'class':'tipo-select form-control'}),
            'categoria_asociada':forms.Select(attrs={'class':'midpoint-select'}),
            'actividadplan_asociado':forms.Select(attrs={'class':'form-control'}),
            'sustancia_asociada':forms.Select(attrs={'class':'sustancia-select form-control'}),
            'cantidad_sustancia': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

        field_order = ['tipo_emision','categoria_asociada','actividadplan_asociado','cantidad_sustancia','sumcadena_asociado']

    def __init__(self, *args, **kwargs):
        super(ActividadEmisionPlanCadenaForm, self).__init__(*args, **kwargs)

        #emisiones = Sustancia_emision.objects.all();
        categorias_emision = Categoria_emision.objects.all();
        #self.fields['sustancia_asociada'].choices = [('', '---------')]
        self.fields['categoria_asociada'].choices =[('', '---------')]+[(categoria_emision.id,categoria_emision) for categoria_emision in categorias_emision]
        self.fields['tipo_emision'].choices = [('', '---------')]+[('AT', 'Atmósfera')]+[('TI', 'Tierra')]+[('AD', 'Agua Dulce')]+[('AS', 'Océanos')]+[('RF', 'Recursos Fosiles')]+[('CR', 'Consumo Recursos')]

ActividadEmisionPlanFormSet = inlineformset_factory(Actividad_PlanCadena, ActividadEmision_PlanCadena,form=ActividadEmisionPlanCadenaForm,extra=1,can_delete=False,can_delete_extra=True)