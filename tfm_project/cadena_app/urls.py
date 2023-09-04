from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from cadena_app import views

app_name = 'cadena_app'

urlpatterns = [
    path('plan/nuevo/<int:pk>',views.CadenaSuministroCreateView.as_view(),name='add_cadena'),
    path('plan/update/<int:pk>',views.CadenaSuministroUpdateView.as_view(),name='update_cadena1'),
    path('plan/cargar_suministros/',views.cargar_suministros,name='cargar_suministros'),
    path('plan/cargar_midpoints/',views.cargar_midpoints,name='cargar_midpoints'),
    path('plan/suministros/emisiones/<int:pk>',views.Suministro_PlanCadenaUpdateView.as_view(),name='add_emisionplan'),
    path('plan/suministros/delete/<int:pk>',views.delete_CadenaSuministro,name='delete_cadenasuministro'),
    path('plan/suministros/delete-emision/<int:pk>',views.delete_SuministroEmision,name='delete_suministroEmision'),
    path('plan/tramos/delete/<int:pk>',views.delete_TramoPlan,name='delete_tramoplan'),
    path('plan/actividades/emisiones/<int:pk>',views.Actividades_PlanCadenaUpdateView.as_view(),name='add_emisionact'),
    path('plan/actividades/delete-emision/<int:pk>',views.delete_ActividadesEmision,name='delete_actividadEmision'),
    path('plan/actividades/delete/<int:pk>',views.delete_CadenaActividad,name='delete_actividadcadena'),
    
]
