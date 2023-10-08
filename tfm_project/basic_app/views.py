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
from produccion_app.models import (OrdenVenta,DetalleOrdenVenta,OrdenProduccion,OrdenEntrega,ProduccionCalculosEndpoint,MidpointEmision_Orden
    ,EnvioCalculosEndpoint,MidpointEmision_Entrega,Endpoint)
from producto_app.models import Producto
from datetime import datetime
from django.db.models import Q

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
				#return render(request,'home',{'username':user.username})
				return redirect('index')
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


	## Valores activos 
	mes_actual = datetime.now().month
	año_actual = datetime.now().year
	print(f"hizo algo?{mes_actual}")
	ordenes = OrdenVenta.objects.filter(fech_venta__year=año_actual,fech_venta__month=mes_actual)
	# salud_humana = 0
    # eco_terrestre = 1
    # eco_aguadulce = 2
    # eco_marino = 03
    # escase_recursos = 4
	emisiones = [0,0,0,0,0]
	emisiones_planificada = [0,0,0,0,0]
	alerta = [1,1,1,1,1]

	productosr = []
	productosp = []
	productosf = []
	productos = Producto.objects.all()

	for producto in productos:
		productosf.append([producto,"","","","","",0,0,0,0,0])
		productosr.append([producto,0,0,0,0,0])
		productosp.append([producto,0,0,0,0,0])

	for orden in ordenes:
		#print("entro?")
		try:
			ordenEnvio = OrdenEntrega.objects.get(orden_venta_entrega=orden.id)
			emisiones_entrega = emisionesValoresEntrega(ordenEnvio)
		except OrdenEntrega.DoesNotExist:
			print("error")
			emisiones_entrega = [0,0,0,0,0]

		for i in range(5):
			emisiones[i] = emisiones[i] + emisiones_entrega[i]

		detalles = DetalleOrdenVenta.objects.filter(orden_venta_detalle=orden)

		for detalle in detalles:
			j = 0
			for productof in productosf:
				if productof[0] == detalle.producto_detalle:

					try:
						try:
							ordenProduccion = OrdenProduccion.objects.get(orden_venta_detalle=detalle)

							for i in range(5):
								x = i+1
								endpoint = Endpoint.objects.get(id=x)
								produ_calculo = ProduccionCalculosEndpoint.objects.get(orden_asociada=ordenProduccion,midpoint_endpoint=endpoint)
								emisiones[i] = emisiones[i] + produ_calculo.valor_real
								productosr[j][x] = productosr[j][x] + produ_calculo.valor_real

								emisiones_planificada[i] = emisiones_planificada[i] + (produ_calculo.valor_pla*detalle.cantidad_detalle)
								productosp[j][x] = productosp[j][x] + (produ_calculo.valor_pla*detalle.cantidad_detalle)

						except OrdenProduccion.DoesNotExist:
							print("no se encontro valores")
					except ProduccionCalculosEndpoint.DoesNotExist:
						print("no se encontro valores")
				j = j+1

	for i in range(5):
		if emisiones[i] <=  1.1*emisiones_planificada[i]:
			alerta[i] = 1
		elif emisiones[i] <  1.4*emisiones_planificada[i]:
			alerta[i] = 0
		else:
			alerta[i] = -1
  		
	salud_humana = "{0:.3E}".format(emisiones[0])
	eco_terrestre = "{0:.3E}".format(emisiones[1])
	eco_aguadulce = "{0:.3E}".format(emisiones[2])
	eco_marino = "{0:.3E}".format(emisiones[3])
	escase_recursos = "{0:.3E}".format(emisiones[4])

	j = 0
	for productof in productosf:

		for i in range(5):
			productof[i+1] = "{0:.3E}".format(productosr[j][i+1])

			if productosr[j][i+1] <=  1.1*productosp[j][i+1]:
				productof[i+6] = 1
			elif productosr[j][i+1] <  1.4*productosp[j][i+1]:
				productof[i+6] = 0
			else:
				productof[i+6] = -1

		j = j + 1



	my_dict = {'salud_humana':salud_humana,'eco_terrestre':eco_terrestre,'eco_aguadulce':eco_aguadulce,'eco_marino':eco_marino,'escase_recursos':escase_recursos,'alertax':alerta,'productos':productosf}

	return render(request,'basic_app/index.html',context=my_dict)


def emisionesValoresEntrega(orden):
    emisiones = []
    for i in range(5):
        x = i+1
        endpoint = Endpoint.objects.get(id=x)
        produ_calculo = EnvioCalculosEndpoint.objects.get(envio_asociada=orden,midpoint_endpoint=endpoint)
        emisiones.append(produ_calculo.valor_real)

    return emisiones

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