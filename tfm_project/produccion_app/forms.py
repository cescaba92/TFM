from django import forms
#from cadena_app.models import (Suministro_PlanCadena)
from suministro_app.models import (Proveedor, Suministro)
from produccion_app.models import (OrdenVenta,DetalleOrdenVenta,OrdenProduccion,OrdenSuministro,SuministroEmision_Orden,SuministroTramos_Orden,Actividad_Orden,ActividadEmision_Orden,
    OrdenEntrega,Tramos_Orden,Actividad_Envio,ActividadEmision_Envio)
from cadena_app.models import (Categoria_emision)
from django.forms import inlineformset_factory
from datetime import date  # Importa el módulo date de datetime

# ============================================================
# Cabeceras de Ordenes
# ============================================================

class OrdenVentaForm(forms.ModelForm):
    class Meta():
        model = OrdenVenta
        fields = {'cod_venta','cliente_venta','direccion_venta','fecha_entrega_venta'}
        
        widgets = {
            'cod_venta':forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
            'cliente_venta':forms.TextInput(attrs={'class':'form-control'}),
            'direccion_venta':forms.TextInput(attrs={'class':'form-control'}),
            'fecha_entrega_venta': forms.DateInput(
        format=('%Y-%m-%d'),
        attrs={'class': 'form-control', 
               'placeholder': 'Select a date',
               'type': 'date'
              }),
            #'estado_venta': forms.Select(attrs={'class':'form-control','readonly':'readonly'}),
        };

        labels = {
            'cod_venta': 'Cód. Venta',
            'cliente_venta': 'Cliente',
            'direccion_venta': 'Dirección Envio',
            'fecha_entrega_venta': 'Fecha Entrega Propuesta',
        }

    def __init__(self, *args, **kwargs):
        super(OrdenVentaForm, self).__init__(*args, **kwargs)
        # Establece el valor mínimo como la fecha actual
        self.fields['fecha_entrega_venta'].widget.attrs['min'] = date.today()


class DetalleOrdenVentaForm(forms.ModelForm):
    class Meta():
        model = DetalleOrdenVenta
        fields = {'orden_venta_detalle','producto_detalle','cantidad_detalle'}
        widgets = {
            'orden_venta_detalle':forms.Select(attrs={'class':'form-control'}),
            'producto_detalle':forms.Select(attrs={'class':'form-control'}),
            'cantidad_detalle':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        };

        labels = {
            'orden_venta_detalle': 'Orden Venta',
            'producto_detalle': 'Producto',
            'cantidad_detalle': 'Cantidad'
        }


OrdenVentaDetalleFormSet = inlineformset_factory(OrdenVenta, DetalleOrdenVenta,form=DetalleOrdenVentaForm,extra=1,can_delete=False,can_delete_extra=True)

# ============================================================
# Orden de Producción
# ============================================================

class OrdenProduccionForm(forms.ModelForm):
    class Meta():
        model = OrdenProduccion
        fields = {'orden_venta_detalle','fuente_energia','tierra_ocupada','tierra_m2'}
        
        widgets = {
            'orden_venta_detalle':forms.Select(attrs={'class':'form-control'}),
            'fuente_energia':forms.Select(attrs={'class':'form-control'}),
            'tierra_ocupada':forms.Select(attrs={'class':'form-control'}),
            'tierra_m2': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        };

        labels = {
            'orden_venta_detalle':'Orden de Venta Detalle',
            'fuente_energia': 'Fuente de Energia',
            'tierra_ocupada': 'Tipo de Tierra Ocupada',
            'tierra_m2': 'm2 de uso',
        }


class SuministroOrdenProduccionForm(forms.ModelForm):
    proveedor_suministro = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'proveedor-select form-control','onchange':'cargarProductos(this);'}))

    class Meta():
        model = OrdenSuministro
        fields = {'proveedor_suministro','suministro_asociado','orden_produccion','cantidad_suministro'}

        widgets = {
            'proveedor_suministro':forms.Select(attrs={'class':'proveedor-select'}),
            'suministro_asociado':forms.Select(attrs={'class':'suministro-select form-control'}),
            'orden_produccion':forms.Select(attrs={'class':'form-control'}),
            'cantidad_suministro': forms.NumberInput(attrs={'class':'form-control','min':0}), 

        };

        labels = {
            'cantidad_suministro': 'Cantidad Solicitada'
        };
    
    field_order = ['proveedor_suministro', 'suministro_asociado', 'orden_produccion','cantidad_suministro']

    def __init__(self, *args, **kwargs):
        super(SuministroOrdenProduccionForm, self).__init__(*args, **kwargs)

        #cadenaSuministro = CadenaSuministro.objects.value_list('id',flat=True).distinct()
        #suministro = Suministro.objects.get(id=1)
        proveedores = Proveedor.objects.all();

        self.fields['proveedor_suministro'].choices =[('', '---------')]+[(proveedor.id,proveedor) for proveedor in proveedores]


class SuministroEmision_OrdenForm(forms.ModelForm):
    categoria_asociada = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'midpoint-select form-control','onchange':'cargarEmisiones(this);'}))
    tipo_emision = forms.ChoiceField(choices=[],widget=forms.Select(attrs={'class':'tipo-select form-control','onchange':'cargarTipo(this);'}))

    class Meta():
        model = SuministroEmision_Orden
        fields={'tipo_emision','categoria_asociada','ordensuministro_asociado','sustancia_asociada','cantidad_sustancia'}

        widgets = {
            'tipo_emision':forms.Select(attrs={'class':'tipo-select form-control'}),
            'categoria_asociada':forms.Select(attrs={'class':'midpoint-select'}),
            'sumcadena_asociado':forms.Select(attrs={'class':'form-control'}),
            'sustancia_asociada':forms.Select(attrs={'class':'sustancia-select form-control'}),
            'cantidad_sustancia': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

        

        field_order = ['tipo_emision','categoria_asociada','sustancia_asociada','cantidad_sustancia','ordensuministro_asociado']

    def __init__(self, *args, **kwargs):
        super(SuministroEmision_OrdenForm, self).__init__(*args, **kwargs)

        #emisiones = Sustancia_emision.objects.all();
        categorias_emision = Categoria_emision.objects.all();
        #self.fields['sustancia_asociada'].choices = [('', '---------')]
        self.fields['categoria_asociada'].choices =[('', '---------')]+[(categoria_emision.id,categoria_emision) for categoria_emision in categorias_emision]
        self.fields['tipo_emision'].choices = [('', '---------')]+[('AT', 'Atmósfera')]+[('TI', 'Tierra')]+[('AD', 'Agua Dulce')]+[('AS', 'Océanos')]+[('RF', 'Recursos Fosiles')]+[('CR', 'Consumo Recursos')]

class SuministroTramos_OrdenForm(forms.ModelForm):
    class Meta():
        model= SuministroTramos_Orden
        fields={'ordensuministro_asociado','tipo_tramo','energia_tramo','descripcion_tramo','km_tramo'}

        widgets = {
            'ordensuministro_asociado':forms.Select(attrs={'class':'form-control'}),
            'tipo_tramo':forms.Select(attrs={'class':'form-control'}),
            'energia_tramo':forms.Select(attrs={'class':'form-control'}),
            'descripcion_tramo':forms.TextInput(attrs={'class':'form-control'}),
            'km_tramo':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

SuministroViajesOrdenFormSet = inlineformset_factory(OrdenSuministro, SuministroTramos_Orden,form=SuministroTramos_OrdenForm,extra=1,can_delete=False,can_delete_extra=True)
SuministroEmisionOrdenFormSet = inlineformset_factory(OrdenSuministro, SuministroEmision_Orden,form=SuministroEmision_OrdenForm,extra=1,can_delete=False,can_delete_extra=True)
SuministroOrdenFormSet = inlineformset_factory(OrdenProduccion, OrdenSuministro,form=SuministroOrdenProduccionForm,extra=1,can_delete=False,can_delete_extra=True)


#Actividades
class Actividad_OrdenForm(forms.ModelForm):

    class Meta():
        model = Actividad_Orden
        fields = {'produccion_asociada','nom_actividad','equipo_asociado','tiempo_equipo_asociado'}

        widgets = {
            'produccion_asociada':forms.Select(attrs={'class':'form-control'}),
            #'tipo_actividad':forms.Select(attrs={'class':'form-control'}),
            'nom_actividad':forms.TextInput(attrs={'class':'form-control'}),
            'equipo_asociado':forms.Select(attrs={'class':'form-control'}),
            'tiempo_equipo_asociado':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

        labels = {
            'nom_actividad':'Descripción de la Actividad',
            'equipo_asociado': 'Equipo Utilizado',
            'tiempo_equipo_asociado': 'Tiempo de Uso',
        }

class ActividadEmision_OrdenForm(forms.ModelForm):

    categoria_asociada = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'midpoint-select form-control','onchange':'cargarEmisiones(this);'}))
    tipo_emision = forms.ChoiceField(choices=[],widget=forms.Select(attrs={'class':'tipo-select form-control','onchange':'cargarTipo(this);'}))

    class Meta():
        model = ActividadEmision_Orden
        fields={'tipo_emision','categoria_asociada','actividadorden_asociado','sustancia_asociada','cantidad_sustancia'}

        widgets = {
            'tipo_emision':forms.Select(attrs={'class':'tipo-select form-control'}),
            'categoria_asociada':forms.Select(attrs={'class':'midpoint-select'}),
            'actividadorden_asociado':forms.Select(attrs={'class':'form-control'}),
            'sustancia_asociada':forms.Select(attrs={'class':'sustancia-select form-control'}),
            'cantidad_sustancia': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

        field_order = ['tipo_emision','categoria_asociada','actividadorden_asociado','cantidad_sustancia','sumcadena_asociado']

    def __init__(self, *args, **kwargs):
        super(ActividadEmision_OrdenForm, self).__init__(*args, **kwargs)

        #emisiones = Sustancia_emision.objects.all();
        categorias_emision = Categoria_emision.objects.all();
        #self.fields['sustancia_asociada'].choices = [('', '---------')]
        self.fields['categoria_asociada'].choices =[('', '---------')]+[(categoria_emision.id,categoria_emision) for categoria_emision in categorias_emision]
        self.fields['tipo_emision'].choices = [('', '---------')]+[('AT', 'Atmósfera')]+[('TI', 'Tierra')]+[('AD', 'Agua Dulce')]+[('AS', 'Océanos')]+[('RF', 'Recursos Fosiles')]+[('CR', 'Consumo Recursos')]

ActividadOrdenFormSet = inlineformset_factory(OrdenProduccion, Actividad_Orden,form=Actividad_OrdenForm,extra=1,can_delete=False,can_delete_extra=True)
ActividadEmisionOrdenFormSet = inlineformset_factory(Actividad_Orden, ActividadEmision_Orden,form=ActividadEmision_OrdenForm,extra=1,can_delete=False,can_delete_extra=True)

# ============================================================
# Orden de Entrega
# ============================================================

class OrdenEntregaForm(forms.ModelForm):

    class Meta():
        model = OrdenEntrega
        fields ={'orden_venta_entrega','direccion_entrega','fecha_entrega','contacto_entrega','observaciones_entrega','fuente_energia'}

        widgets = {
            'orden_venta_entrega':forms.Select(attrs={'class':'tipo-select form-control'}),
            'direccion_entrega':forms.TextInput(attrs={'class':'form-control'}),
            'fecha_entrega':forms.DateInput(
        format=('%Y-%m-%d'),
        attrs={'class': 'form-control', 
               'placeholder': 'Select a date',
               'type': 'date'
              }),
            'contacto_entrega':forms.TextInput(attrs={'class':'form-control'}),
            'observaciones_entrega':forms.TextInput(attrs={'class':'form-control'}),
            'fuente_energia':forms.Select(attrs={'class':'tipo-select form-control'}),
        }
        
        labels = {
            'direccion_entrega':'Dirección de Entrega',
            'fecha_entrega': 'Fecha de Entrega',
            'contacto_entrega': 'Contacto de Entrega',
            'observaciones_entrega': 'Observaciones',
            'fuente_energia':'Fuente Energia'
        }

    def __init__(self, *args, **kwargs):
        super(OrdenEntregaForm, self).__init__(*args, **kwargs)
        # Establece el valor mínimo como la fecha actual
        self.fields['fecha_entrega'].widget.attrs['min'] = date.today()

class Actividad_EnvioForm(forms.ModelForm):

    class Meta():
        model = Actividad_Envio
        fields = {'entrega_asociada','nom_actividad','equipo_asociado','tiempo_equipo_asociado'}

        widgets = {
            'entrega_asociada':forms.Select(attrs={'class':'form-control'}),
            #'tipo_actividad':forms.Select(attrs={'class':'form-control'}),
            'nom_actividad':forms.TextInput(attrs={'class':'form-control'}),
            'equipo_asociado':forms.Select(attrs={'class':'form-control'}),
            'tiempo_equipo_asociado':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

        labels = {
            'nom_actividad':'Descripción de la Actividad',
            'equipo_asociado': 'Equipo Utilizado',
            'tiempo_equipo_asociado': 'Tiempo de Uso',
        }

class ActividadEmision_EnvioForm(forms.ModelForm):

    categoria_asociada = forms.ChoiceField(choices=[],widget= forms.Select(attrs={'class':'midpoint-select form-control','onchange':'cargarEmisiones(this);'}))
    tipo_emision = forms.ChoiceField(choices=[],widget=forms.Select(attrs={'class':'tipo-select form-control','onchange':'cargarTipo(this);'}))

    class Meta():
        model = ActividadEmision_Envio
        fields={'tipo_emision','categoria_asociada','actividadenvio_asociado','sustancia_asociada','cantidad_sustancia'}

        widgets = {
            'tipo_emision':forms.Select(attrs={'class':'tipo-select form-control'}),
            'categoria_asociada':forms.Select(attrs={'class':'midpoint-select'}),
            'actividadenvio_asociado':forms.Select(attrs={'class':'form-control'}),
            'sustancia_asociada':forms.Select(attrs={'class':'sustancia-select form-control'}),
            'cantidad_sustancia': forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }

    def __init__(self, *args, **kwargs):
        super(ActividadEmision_EnvioForm, self).__init__(*args, **kwargs)

        #emisiones = Sustancia_emision.objects.all();
        categorias_emision = Categoria_emision.objects.all();
        #self.fields['sustancia_asociada'].choices = [('', '---------')]
        self.fields['categoria_asociada'].choices =[('', '---------')]+[(categoria_emision.id,categoria_emision) for categoria_emision in categorias_emision]
        self.fields['tipo_emision'].choices = [('', '---------')]+[('AT', 'Atmósfera')]+[('TI', 'Tierra')]+[('AD', 'Agua Dulce')]+[('AS', 'Océanos')]+[('RF', 'Recursos Fosiles')]+[('CR', 'Consumo Recursos')]

ActividadEnvioFormSet = inlineformset_factory(OrdenEntrega, Actividad_Envio,form=Actividad_EnvioForm,extra=1,can_delete=False,can_delete_extra=True)
ActividadEmisionEnvioFormSet = inlineformset_factory(Actividad_Envio,ActividadEmision_Envio,form=ActividadEmision_EnvioForm,extra=1,can_delete=False,can_delete_extra=True)

class Tramos_OrdenForm(forms.ModelForm):

    class Meta():
        model= Tramos_Orden
        fields={'orden_envio_asociada','tipo_tramoexterno','energia_tramoexterno','descripcion_tramoexterno','km_tramoexterno'}

        widgets = {
            'orden_envio_asociada':forms.Select(attrs={'class':'form-control'}),
            'tipo_tramoexterno':forms.Select(attrs={'class':'form-control'}),
            'energia_tramoexterno':forms.Select(attrs={'class':'form-control'}),
            'descripcion_tramoexterno':forms.TextInput(attrs={'class':'form-control'}),
            'km_tramoexterno':forms.NumberInput(attrs={'class':'form-control','min':0}), 
        }


TramosEnvioFormSet = inlineformset_factory(OrdenEntrega, Tramos_Orden,form=Tramos_OrdenForm,extra=1,can_delete=False,can_delete_extra=True)


