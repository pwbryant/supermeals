from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator

# Create your models here.

class Macros(models.Model):
	
	user = models.OneToOneField('auth.User',on_delete=models.CASCADE)
	UNIT_CHOICES = (
		('imperial','Imperial',),
		('metric','Metric',),
	)
	unit_type = models.CharField(max_length=8, choices=UNIT_CHOICES,default='imperial', blank=False)

	GENDER_CHOICES = (
		('m','Male',),
		('f','Female',),
	)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=False)
	age = models.IntegerField(blank=False)
	weight = models.DecimalField(max_digits=5,decimal_places=2,blank=False)	
	height = models.DecimalField(max_digits=5,decimal_places=2,blank=False)
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
	change_rate = models.DecimalField(max_digits=9,decimal_places=8,blank=False)
	fat_percent = models.DecimalField(max_digits=4,decimal_places=2,blank=False)
	protein_percent = models.DecimalField(max_digits=4,decimal_places=2,blank=False)

	def calc_tdee(self):
		activity_factor = {
			'none':1.2,
			'light':1.375,
			'medium':1.55,
			'high':1.725,
			'very high':1.9
		}[self.activity]

		direction_factor = {
			 'maintain': 0,
			 'lose': -1,
			 'gain': 1,
		 }[self.direction];
		
		weight_change = self.change_rate / .45359237 * direction_factor * 500 #convert kg to lb by dividing by .45359237
		
		tdee = (10 * self.weight) + (6.25 * self.height) - (5 * self.age)
		if self.gender == 'm':
			tdee += 5 
		else:
			tdee -= 161

		tdee = (tdee * activity_factor) + weight_change

		return tdee
	
class MealTemplate(models.Model):

	user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
	name = models.TextField(blank=False)	
	cals_percent = models.DecimalField(max_digits=4,decimal_places=2,blank=False)
	
