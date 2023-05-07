from django.shortcuts import render
from basic_app.forms import UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.




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

def register(request):
	registered = False

	if request.method == "POST":
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save();
			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			profile.save()

			registered = True
		else:
			print(user_form.errors,profile_form.errors)

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request,'basic_app/registration.html',{'user_form':user_form,'profile_form':profile_form,'registered':registered})