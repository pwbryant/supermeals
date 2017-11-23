from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator

# Create your models here.

class Macros(models.Model):
	
	GENDER_CHOICES = (
		('m','Male',),
		('f','Female',),
	)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=False)

	age = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(120)], blank=False)

	weight = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(300)], blank=False)

	height = models.IntegerField(validators=[MinValueValidator(30),MaxValueValidator(250)], blank=False)
	user = models.OneToOneField('auth.User',on_delete=models.CASCADE)
