from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from cadena_app import views

app_name = 'cadena_app'

urlpatterns = [

    #path('productos/',views.ProductosListView.as_view(),name='productos'),
    #path('cadena-suministro/nuevo/<str:producto>',views.CadenaSuministroView.as_view(),name='add_cadena'),
     path('cadena-suministro/nuevo/<int:pk>',views.CadenaSuministroCreateView.as_view(),name='add_cadena'),
    path('update/<int:pk>',views.CadenaSuministroUpdateView.as_view(),name='update_cadena1'),
    path('cargar_suministros/',views.cargar_suministros,name='cargar_suministros'),
   #path('cadena-suministro/suministros/<int:pk>', views.CadenaSumiNuevoForm.as_view(), name='suministro-suministro'),
   path('delete/<int:pk>',views.delete_CadenaSuministro,name='delete_cadenasuministro'),
]
