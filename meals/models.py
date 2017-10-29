from django.db import models

# Create your models here.

class User(models.Model):

	username = models.TextField(default='')	
	email = models.TextField(default='')	
	password = models.TextField(default='')	
