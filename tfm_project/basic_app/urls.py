from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from basic_app import views
from django.contrib.auth import views as auth_views

app_name = 'basic_app'

urlpatterns = [
    path("register/", views.register,name='register'),
    path("user_login/",views.user_login,name='user_login'),
    path("logout/",views.user_logout, name='user_logout'),
    path("usuarios",views.user_list,name="user_list"),
    path("user_password/<int:id>",views.user_password,name="user_password"),
    path("user_update/<int:id>",views.user_update,name="user_update"),
    path("user_desactivar/<int:id>",views.user_desactivar,name="user_desactivar"),
    path("user_activar/<int:id>",views.user_activar,name="user_activar"),
    path("change_password",
        auth_views.PasswordChangeView.as_view(
            template_name='basic_app/change-password.html',
            success_url = '/'
        ),
        name='change_password'
    ),

]