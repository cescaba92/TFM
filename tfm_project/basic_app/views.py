from django.shortcuts import render, redirect
from basic_app.forms import UserForm, UserProfileForm, UserPasswordForm, UserUpdateForm

from django.contrib.auth.models import User
from basic_app.models import UserProfile

from django.views.generic import (TemplateView,ListView)

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def user_list(request):
	
	if request.user.is_active:
		users = UserProfile.objects.all()
		return render(request,'basic_app/usuarios.html',{'users':users})
	else:
		return render(request,'basic_app/login.html')
 

@login_required
def user_logout(request):
	logout(request)
	#my_dict = {'alerta':"false"}

	return render(request,'basic_app/login.html')
	#return HttpResponseRedirect(reverse('basic_app/login.html'))
	#return render(request, 'login.html',context=my_dict)

def user_login(request):

	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')

		user=authenticate(username=username,password=password)
		my_dict = {'alerta':"false"}

		if user:
			if user.is_active:
				login(request,user)
				return render(request,'basic_app/index.html',{'username':user.username})
			else:
				my_dict = {'alerta':"La cuenta no esta activa. porfavor contactarse con sistemas."}
				return render(request, 'basic_app/login.html',context=my_dict)
		else:
			print("Usuario no registrado")
			my_dict = {'alerta':"Inicio de sesión fallido. Verifique credenciales."}
			return render(request, 'basic_app/login.html',context=my_dict)
	else:
		return render(request,'basic_app/login.html')


def login_page(request):
	return render(request,'basic_app/login.html')

@login_required
def index(request):
	return render(request,'basic_app/index.html')

def user_desactivar(request,id):
	user=User.objects.get(id=id)

	if request.method == "GET":
		user.is_active = False
		user.save()

	else:
		print("error al desactivar")

	return redirect('basic_app:user_list')


def user_activar(request,id):
	user=User.objects.get(id=id)

	if request.method == "GET":
		user.is_active = True
		user.save()
	else:
		print("error al activar")	
	return redirect('basic_app:user_list')


def user_password(request,id):
	user = User.objects.get(id=id)

	if request.method == "POST":
		user_form = UserPasswordForm(data=request.POST,instance=user)

		if user_form.is_valid():

			user = user_form.save()
			user.set_password(user.password)
			user.save()

		else:
			print(user_form.errors,profile_form.errors)	

	else:
		user_form = UserPasswordForm(initial={'username':user.username})
		return render(request,'basic_app/updatepassuser.html',{'user_form':user_form})

	return redirect('basic_app:user_list') 

def register(request):
	registered = False

	if request.method == "POST":
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save();
			user.set_password(user.password)
			user.save()

			profile = profile_form.save()
			profile.user = user

			profile.save()

			registered = True
		else:
			print(user_form.errors,profile_form.errors)

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request,'basic_app/registration.html',{'user_form':user_form,'profile_form':profile_form,'registered':registered})

def user_update(request,id):
	userx = UserProfile.objects.get(id=id)

	if request.method == "POST":
		user_form = UserUpdateForm(data=request.POST,instance=userx.user)
		profile_form = UserProfileForm(data=request.POST,instance=userx)

		if user_form.is_valid() and profile_form.is_valid():

			user = user_form.save();
			#user.set_password(user.password)
			user.save()

			profile = profile_form.save()
			profile.user = user

			profile.save()

		else:
			print(user_form.errors,profile_form.errors)

	else:
		user_form = UserUpdateForm(initial={'username':userx.user.username,'email':userx.user.email,'first_name':userx.user.first_name,'last_name':userx.user.last_name})
		profile_form = UserProfileForm(initial={'user_job':userx.user_job,'user_phone':userx.user_phone,'user_rol':userx.user_rol})
		return render(request,'basic_app/updateuser.html',{'user_form':user_form,'profile_form':profile_form})

	return redirect('basic_app:user_list')