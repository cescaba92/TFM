from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from producto_app import views

app_name = 'producto_app'

urlpatterns = [
    #path("registerproducto/", views.producto_register,name='producto_register'),
    #path("user_login/",views.user_login,name='user_login'),
    path('productos/',views.ProductosListView.as_view(),name='productos'),
    path('productos/nuevo/',views.ProductosCreateView.as_view(),name='add_producto'),
    path('update/<int:pk>',views.ProductoUpdate.as_view(),name='update_producto'),
   path('delete-variant/<int:pk>/', views.delete_variant, name='delete_variant'),
   path('delete/<int:pk>',views.delete_producto,name='delete_producto'),

]
