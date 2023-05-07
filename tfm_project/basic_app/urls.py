from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from basic_app import views

app_name = 'basic_app'

urlpatterns = [
    path("register/", views.register,name='register'),
    path("user_login/",views.user_login,name='user_login'),
    path("logout/",views.user_logout, name='user_logout'),

]