from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
	my_dict = {'SCMSostenible':"Empresa 1"}
	return render(request, 'login.html',context=my_dict)


