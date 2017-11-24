from decimal import *
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError,transaction

from meals.models import Macros

GUEST_USER = User.objects.get(username='guest')
USER = User.objects.get(username='paul')
USERNAME1,PASSWORD1 = 'Joe1','joepass1'
USERNAME2,PASSWORD2 = 'Joe2','joepass2'
MACRO_INIT_FIELD_DICT = {
	'gender':'m',
	'age':35,
	'weight':200,
	'height':70,
	'activity':'none',
	'direction':'lose',
	'change_rate':Decimal('5'),
	'fat_percent':Decimal('35'),
	'protein_percent':Decimal('25')
}
class MacrosTest(TestCase):

	def check_model_validation_error(self,macros,delete_macro=True):
		with self.assertRaises(ValidationError):
			macros.save()
			macros.full_clean()
		if delete_macro:
			macros.user.delete()	

	def check_model_integrity_error(self,macros):
		with transaction.atomic():
			with self.assertRaises(IntegrityError):
				macros.save()
				macros.full_clean()

	def create_broken_macro_field_dict(self,break_field,value):
		broke_macro_dict = MACRO_INIT_FIELD_DICT.copy()
		if User.objects.all().count() != 0:
			User.objects.all()[0].delete()
			
		broke_macro_dict['user'] = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
		if value == 'remove':
			broke_macro_dict.pop(break_field)
		else:
			broke_macro_dict[break_field] = value

		return broke_macro_dict
	
		
	def test_validation_errors_illegal_field_values(self):
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('gender','')))#illegal gender
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('age',0)))#low age
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('weight',0)))#low weight
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('height',0)))#low height
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('age',900)))#high age
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('weight',900)))#high weight
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('height',900)))#high height
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('activity','blah')))#illegal activity
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('direction','blah')))#illegal direction
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('change_rate',Decimal('10.111'))))#illegal(too long)
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('fat_percent',Decimal('10.111'))))#illegal(too long)
		self.check_model_validation_error(Macros(**self.create_broken_macro_field_dict('protein_percent',Decimal('10.111'))))#illegal(too long)
 
		self.assertEqual(Macros.objects.all().count(),0)

	def test_integrity_errors_missing_field_values(self):
		#gender,direction and activity, because the have defaults are not tested on purpose because they are ValidationError
		self.check_model_integrity_error(Macros(**self.create_broken_macro_field_dict('age','remove')))#ow age
		self.check_model_integrity_error(Macros(**self.create_broken_macro_field_dict('weight','remove')))#low weight
		self.check_model_integrity_error(Macros(**self.create_broken_macro_field_dict('height','remove')))#low height
		self.check_model_integrity_error(Macros(**self.create_broken_macro_field_dict('height','remove')))#low height
		self.check_model_integrity_error(Macros(**self.create_broken_macro_field_dict('change_rate','remove')))#illegal(too long)
		self.check_model_integrity_error(Macros(**self.create_broken_macro_field_dict('fat_percent','remove')))#illegal(too long)
		self.check_model_integrity_error(Macros(**self.create_broken_macro_field_dict('protein_percent','remove')))#illegal(too long)
 
		self.assertEqual(Macros.objects.all().count(),0)

	def test_one_to_one_relationship_between_user_and_macro(self):
		#more that one user to macro relation shipe causes and integrity error
		user = User.objects.create_user(username = USERNAME1,password = PASSWORD1)
		MACRO_INIT_FIELD_DICT['user'] = user
		Macros(**MACRO_INIT_FIELD_DICT).save()
		self.check_model_integrity_error(Macros(**MACRO_INIT_FIELD_DICT))
		self.assertEqual(Macros.objects.all().count(),1)

	def test_delete_user_deletes_macro(self):
		user = User.objects.create_user(username = USERNAME1,password = PASSWORD1)
		MACRO_INIT_FIELD_DICT['user'] = user
		Macros(**MACRO_INIT_FIELD_DICT).save()
		self.assertEqual(User.objects.all().count(),1)
		self.assertEqual(Macros.objects.all().count(),1)
		user.delete()
		self.assertEqual(Macros.objects.all().count(),0)

	def test_saving_and_retrieving_macros(self):

		first_user = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
		MACRO_INIT_FIELD_DICT['user'] = first_user
		first_macros = Macros(**MACRO_INIT_FIELD_DICT)
		first_macros.save()

		second_user = User.objects.create_user(username=USERNAME2,password=PASSWORD2)
		MACRO_INIT_FIELD_DICT['user'] = second_user
		second_macros = Macros(**MACRO_INIT_FIELD_DICT)
		second_macros.save()

		saved_macros = Macros.objects.all()
		self.assertEqual(saved_macros.count(),2)

		first_saved_macros = saved_macros[0]
		second_saved_macros = saved_macros[1]

		self.assertEqual(first_saved_macros.gender,MACRO_INIT_FIELD_DICT['gender'])
		self.assertEqual(first_saved_macros.age,MACRO_INIT_FIELD_DICT['age'])
		self.assertEqual(first_saved_macros.weight,MACRO_INIT_FIELD_DICT['weight'])
		self.assertEqual(first_saved_macros.height,MACRO_INIT_FIELD_DICT['height'])
		self.assertEqual(first_saved_macros.user,first_user)

		self.assertEqual(second_saved_macros.gender,MACRO_INIT_FIELD_DICT['gender'])
		self.assertEqual(second_saved_macros.age,MACRO_INIT_FIELD_DICT['age'])
		self.assertEqual(second_saved_macros.weight,MACRO_INIT_FIELD_DICT['weight'])
		self.assertEqual(second_saved_macros.height,MACRO_INIT_FIELD_DICT['height'])
		self.assertEqual(second_saved_macros.user,second_user)
