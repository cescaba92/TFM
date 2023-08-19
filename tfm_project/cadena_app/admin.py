from django.contrib import admin
from cadena_app.models import FuenteEnergia
from cadena_app.models import MidpointTierra
from cadena_app.models import Sustancia_emision
from cadena_app.models import Midpoint_emision
from cadena_app.models import Energia_transporte
from cadena_app.models import Tipo_transporte

# Register your models here.
admin.site.register(FuenteEnergia)
admin.site.register(MidpointTierra)
admin.site.register(Sustancia_emision)
admin.site.register(Midpoint_emision)
admin.site.register(Energia_transporte)
admin.site.register(Tipo_transporte)
