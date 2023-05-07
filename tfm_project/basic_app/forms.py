from django import forms
from django.contrib.auth.models import User
from basic_app.models import UserProfile


class UserForm(forms.ModelForm):

	password = forms.CharField(widget=forms.PasswordInput(
		attrs={'class':'form-control'}),
	label='Contraseña')

	username = forms.CharField(help_text='',widget=forms.TextInput(
		attrs={'class':'form-control'}),
	label='Usuario')

	email = forms.EmailField(widget=forms.EmailInput(
		attrs={'class':'form-control'}),
	label='Correo Electrónico')

	first_name = forms.CharField(help_text='',widget=forms.TextInput(
		attrs={'class':'form-control'}),
	label='Nombre')

	last_name = forms.CharField(help_text='',widget=forms.TextInput(
		attrs={'class':'form-control'}),
	label='Apellido')

	#is_active = forms.BooleanField(help_text='',label='Activo?',widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))

	class Meta():
		model = User
		#fields = ('username','email','password','first_name','last_name','is_active')
		fields = ('username','email','password','first_name','last_name')

class UserPasswordForm(forms.ModelForm):
			password = forms.CharField(widget=forms.PasswordInput(
				attrs={'class':'form-control'}),
			label='Contraseña')

			username = forms.CharField(help_text='',widget=forms.TextInput(
				attrs={'class':'form-control','readonly':'readonly'}),
			label='Usuario')

			class Meta():
				model = User
				fields = ('username','password')

class UserUpdateForm(forms.ModelForm):

					username = forms.CharField(help_text='',widget=forms.TextInput(
						attrs={'class':'form-control'}),
					label='Usuario')

					email = forms.EmailField(widget=forms.EmailInput(
						attrs={'class':'form-control'}),
					label='Correo Electrónico')

					first_name = forms.CharField(help_text='',widget=forms.TextInput(
						attrs={'class':'form-control'}),
					label='Nombre')

					last_name = forms.CharField(help_text='',widget=forms.TextInput(
						attrs={'class':'form-control'}),
					label='Apellido')

					class Meta():
						model = User
						fields = ('username','email','first_name','last_name')

class UserProfileForm(forms.ModelForm):
							class Meta():
								model = UserProfile
								fields = ('user_job','user_phone','user_rol')

								widgets = {
								'user_job': forms.TextInput(attrs={'class':'form-control'}),
								'user_phone': forms.TextInput(attrs={'class':'form-control'}),
								'user_rol': forms.Select(attrs={'class':'form-control'})
								}

								labels = {
								'user_job': 'Puesto de Trabajo',
								'user_phone': 'Télefono de Contacto',
								'user_rol': 'Rol de Sistema'
								}
