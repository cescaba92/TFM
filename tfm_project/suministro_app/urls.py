from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from suministro_app import views

app_name = 'suministro_app'

urlpatterns = [
    path('proveedores/',views.ProveedoresListView.as_view(),name='proveedores'),
    path('proveedores/nuevo/',views.ProveedoresCreateView.as_view(),name='add_proveedor'),
    path('update/<int:pk>',views.ProveedorUpdate.as_view(),name='update_proveedor'),
   path('delete-suministro/<int:pk>/', views.delete_suministro, name='delete_suministro'),
   path('delete/<int:pk>',views.delete_proveedor,name='delete_proveedor'),
   path('equipos/',views.EquiposListView.as_view(),name='equipos'),
   path('equipos/nuevo/',views.EquipoCreateView.as_view(),name='add_equipo'),
   path('equipos/update/<int:pk>',views.EquipoUpdate.as_view(),name='update_equipo'),
   path('equipos/delete/<int:pk>',views.delete_equipo,name='delete_equipo'),
]
