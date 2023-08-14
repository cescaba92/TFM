from django.contrib import admin
from cadena_app.models import FuenteEnergia
from cadena_app.models import MidpointTierra
from cadena_app.models import sustancia_emision
from cadena_app.models import Midpoint_emision
# Register your models here.
admin.site.register(FuenteEnergia)
admin.site.register(MidpointTierra)
admin.site.register(sustancia_emision)
admin.site.register(Midpoint_emision)