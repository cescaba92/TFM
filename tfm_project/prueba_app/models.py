from django.db import models

# Create your models here.
class Usuario(models.Model):
	user_id = models.AutoField(primary_key=True)
	user_mail = models.CharField(max_length=264)
	user_name = models.CharField(max_length=264)
	user_lastname = models.CharField(max_length=264)
	user_rol = models.CharField(max_length=264)
	user_phone = models.CharField(max_length=264)
	user_state = models.BooleanField()
	user_lastLogin = models.DateField()

class Rol(models.Model):
	id_rol = models.AutoField(primary_key=True)
	nom_rol = models.CharField(max_length=264)


class RolxUsuario(models.Model):
	user_id = models.ForeignKey(Usuario,
    on_delete=models.CASCADE)
	id_rol = models.ForeignKey(Rol,
    on_delete=models.CASCADE)


