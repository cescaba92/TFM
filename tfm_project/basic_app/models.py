from django.db import models
from django.contrib.auth.models	import User
# Create your models here.


class Rol(models.Model):
	id_rol = models.AutoField(primary_key=True)
	nom_rol = models.CharField(max_length=264)

	def __str__(self): return "%s" % (self.nom_rol)

class UserProfile(models.Model):

	user = models.OneToOneField(User,
    on_delete=models.CASCADE)
	user_job = models.CharField(max_length=264)
	user_phone = models.CharField(max_length=264)
	user_rol = models.ForeignKey(Rol,
    on_delete=models.CASCADE)
