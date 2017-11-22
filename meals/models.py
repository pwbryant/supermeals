from django.db import models
from django.core.validators import MaxValueValidator,MinValueValidator

# Create your models here.

class Macros(models.Model):
	
	GENDER_CHOICES = (
		('m','Male',),
		('f','Female',),
	)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='m', blank=False)

	age = models.IntegerField(validators=[MaxValueValidator(120)], blank=False)

	weight = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(300)], blank=False)

	height = models.IntegerField(validators=[MinValueValidator(30),MaxValueValidator(250)], blank=False)


