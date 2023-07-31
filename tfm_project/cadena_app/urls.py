from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from cadena_app import views

app_name = 'cadena_app'

urlpatterns = [

    #path('productos/',views.ProductosListView.as_view(),name='productos'),
    path('cadena-suministro/nuevo/<str:producto>',views.CadenaSuministroView.as_view(),name='add_cadena'),
    path('update/<int:pk>',views.CadenaSuministroUpdate.as_view(),name='update_cadena1'),
   #path('delete-variant/<int:pk>/', views.delete_variant, name='delete_variant'),
   #path('delete/<int:pk>',views.delete_producto,name='delete_producto'),
]
