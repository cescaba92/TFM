from django.urls import path
from prueba_app import views


urlpatterns = [
	path("",views.index, name="index"),
]