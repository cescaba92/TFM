from django import forms
from cadena_app.models import CadenaSuministro

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

        