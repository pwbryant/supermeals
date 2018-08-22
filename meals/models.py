from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
from decimal import Decimal
# Create your models here.

class Macros(models.Model):
	
    user = models.OneToOneField('auth.User',on_delete=models.CASCADE)
    UNIT_CHOICES = (
            ('imperial','Imperial',),
            ('metric','Metric',),
    )
    unit_type = models.CharField(max_length=8, choices=UNIT_CHOICES,default='imperial', blank=False)

    GENDER_CHOICES = (
            ('male','Male',),
            ('female','Female',),
    )
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=False)
    age = models.IntegerField(blank=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=False)	
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
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
    direction = models.CharField(max_length=8, choices=DIRECTIONS, default='lose', blank=False)	
    change_rate = models.DecimalField(max_digits=9, decimal_places=8, blank=False)
    fat_percent = models.DecimalField(max_digits=4, decimal_places=2 ,blank=False)
    protein_percent = models.DecimalField(max_digits=4, decimal_places=2, blank=False)

    def calc_tdee(self):
        activity_factor = {
            'none':Decimal('1.2'),
            'light':Decimal('1.375'),
            'medium':Decimal('1.55'),
            'high':Decimal('1.725'),
            'very high':Decimal('1.9')
        }[self.activity]

        direction_factor = {
                 'maintain': Decimal('0'),
                 'lose': Decimal('-1'),
                 'gain': Decimal('1'),
         }[self.direction];
        
        weight_change = self.change_rate / Decimal('.45359237') * direction_factor * 500 #convert kg to lb by dividing by .45359237
        
        tdee = (Decimal('10') * self.weight) + (Decimal('6.25') * self.height) - (Decimal('5') * self.age)
        if self.gender == 'male':
                tdee += 5 
        else:
                tdee -= 161

        tdee = (tdee * activity_factor) + weight_change

        return tdee


class MealTemplate(models.Model):

    user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    name = models.TextField(blank=False)	
    cals_percent = models.DecimalField(max_digits=4,decimal_places=2,blank=False)
    

class OwnedFoods(models.Model):

    food = models.ForeignKey('Foods',on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    

class Foods(models.Model):

    name = models.TextField(blank=False, unique=True)
    cals_per_gram = models.DecimalField(max_digits=6,decimal_places=4,blank=False)
    fat_per_gram = models.DecimalField(max_digits=6,decimal_places=4,blank=False)
    carbs_per_gram = models.DecimalField(max_digits=6,decimal_places=4,blank=False)
    protein_per_gram = models.DecimalField(max_digits=6,decimal_places=4,blank=False)

    def as_dict(self):
        return {
            "name":self.name,
            "cals_per_gram":self.cals_per_gram,
            "fat_per_gram":self.fat_per_gram,
            "carbs_per_gram":self.carbs_per_gram,
            "protein_per_gram":self.protein_per_gram
        }

    def __str__(self):
        return '{}'.format(self.name)


class Servings(models.Model):

    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=200)
    grams = models.DecimalField(max_digits=6, decimal_places=2)
    food = models.ForeignKey(
        'Foods',
        on_delete=models.CASCADE,
        null=True
        )

    def __str__(self):
        if self.food:
            return '{0} - {1}'.format(self.food.name, self.description)
        return '{0}'.format(self.description)
    

class Ingredients(models.Model):
    
    main_food = models.ForeignKey(
            'Foods',
            on_delete=models.CASCADE,
            related_name='main_food',
            )

    ingredient = models.ForeignKey(
            'Foods',
            on_delete=models.CASCADE,
            related_name='ingredient',
            )

    serving = models.ForeignKey(
            'Servings',
            on_delete=models.CASCADE,
            )

    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return '{0} - {1}'.format(
            self.main_food.name, self.ingredient.name
        )


class Temp(models.Model):

    field1 = models.TextField(blank=False)
    field2 = models.TextField(blank=False)
