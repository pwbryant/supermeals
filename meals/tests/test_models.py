from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError,transaction

from meals.models import Macros

USERNAME1,PASSWORD1 = 'Joe1','joepass1'
USERNAME2,PASSWORD2 = 'Joe2','joepass2'
class MacrosTest(TestCase):

	def check_for_model_save_validation_error(self,macros,delete_macro=True):
		with self.assertRaises(ValidationError):
			macros.save()
			macros.full_clean()
		if delete_macro:
			macros.delete()	

	def check_for_model_save_integrity_error(self,macros):
		with transaction.atomic():
			with self.assertRaises(IntegrityError):
				macros.save()
				macros.full_clean()

	def test_validation_errors_illegal_field_values(self):
		user = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
		self.check_for_model_save_validation_error(Macros(user=user,gender='',age=33,weight=100,height=100))#blank gender
		self.check_for_model_save_validation_error(Macros(user=user,gender='male',age=33,weight=100,height=100))#illegal value
		self.check_for_model_save_validation_error(Macros(user=user,gender='m',age=0,weight=60,height=60))#low age
		self.check_for_model_save_validation_error(Macros(user=user,gender='m',age=10,weight=0,height=50))#low weight
		self.check_for_model_save_validation_error(Macros(user=user,gender='m',age=50,weight=50,height=0))#low height
		self.check_for_model_save_validation_error(Macros(user=user,gender='m',age=200,weight=60,height=60))#high age
		self.check_for_model_save_validation_error(Macros(user=user,gender='m',age=10,weight=900,height=50))#high weight
		self.check_for_model_save_validation_error(Macros(user=user,gender='m',age=50,weight=50,height=900))#high height
		self.assertEqual(Macros.objects.all().count(),0)

	def test_integrity_errors_missing_field_values(self):
		#gender is not tested on purpose because it is an ValidationError
		user = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
		self.check_for_model_save_integrity_error(Macros(gender='m',age=50,weight=50,height=90))#missing user
		self.check_for_model_save_integrity_error(Macros(user=user,gender='m',weight=50,height=90))#missing age
		self.check_for_model_save_integrity_error(Macros(user=user,gender='m',age=50,height=90))#missing weight
		self.check_for_model_save_integrity_error(Macros(user=user,gender='m',age=50,weight=50))#missing height
		self.assertEqual(Macros.objects.all().count(),0)

	def test_one_to_one_relationship_between_user_and_macro(self):
		#more that one user to macro relation shipe causes and integrity error
		user = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
		Macros(user=user,gender='m',age=50,weight=50,height=90).save()
		self.check_for_model_save_integrity_error(Macros(user=user,gender='m',age=50,weight=50,height=90))
		self.assertEqual(Macros.objects.all().count(),1)

	def test_delete_user_deletes_macro(self):
		user = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
		Macros(user=user,gender='m',age=50,weight=50,height=90).save()
		self.assertEqual(User.objects.all().count(),1)
		self.assertEqual(Macros.objects.all().count(),1)
		user.delete()
		self.assertEqual(Macros.objects.all().count(),0)

	def test_saving_and_retrieving_macros(self):

		first_user = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
		first_macros = Macros()
		first_macros.gender = 'm'
		first_macros.age = 33
		first_macros.weight = 210
		first_macros.height = 90
		first_macros.user = first_user
		first_macros.save()

		second_user = User.objects.create_user(username=USERNAME2,password=PASSWORD2)
		second_macros = Macros()
		second_macros.gender = 'f'
		second_macros.age = 23
		second_macros.weight = 100
		second_macros.height = 100
		second_macros.user = second_user
		second_macros.save()

		saved_macros = Macros.objects.all()
		self.assertEqual(saved_macros.count(),2)

		first_saved_macros = saved_macros[0]
		second_saved_macros = saved_macros[1]
		self.assertEqual(first_saved_macros.gender,'m')
		self.assertEqual(first_saved_macros.age,33)
		self.assertEqual(first_saved_macros.weight,210)
		self.assertEqual(first_saved_macros.height,90)
		self.assertEqual(first_saved_macros.user,first_user)

		self.assertEqual(second_saved_macros.gender,'f')
		self.assertEqual(second_saved_macros.age,23)
		self.assertEqual(second_saved_macros.weight,100)
		self.assertEqual(second_saved_macros.height,100)
		self.assertEqual(second_saved_macros.user,second_user)
