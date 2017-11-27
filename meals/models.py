from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator

# Create your models here.

class Macros(models.Model):
	
	user = models.OneToOneField('auth.User',on_delete=models.CASCADE)

	GENDER_CHOICES = (
		('m','Male',),
		('f','Female',),
	)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default='m', blank=False)
	age = models.IntegerField(blank=False)
	weight = models.IntegerField(blank=False)
	height = models.IntegerField(blank=False)
	ACTIVITY_CHOICES = (
		('none','',),
		('light','',),
		('medium','',),
		('high','',),
		('very high','',),
	)

	activity = models.CharField(max_length=9,choices=ACTIVITY_CHOICES,default='none',blank=False)
	DIRECTIONS = (
		('lose','Lose',),
		('maintain','Maintain',),
		('gain','Gain',),
	)
	direction = models.CharField(max_length=8,choices=DIRECTIONS,default='lose',blank=False)	
	change_rate = models.DecimalField(max_digits=4,decimal_places=2,blank=False)
	fat_percent = models.DecimalField(max_digits=4,decimal_places=2,blank=False)
	protein_percent = models.DecimalField(max_digits=4,decimal_places=2,blank=False)
	
class MealTemplate(models.Model):

	user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
	num_per_day = models.IntegerField(blank=False)
	daily_percent = models.DecimalField(max_digits=4,decimal_places=2,blank=False)
	
