from decimal import *
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError,transaction

from meals.models import Macros,Foods, OwnedFoods, Servings, Ingredients

GUEST_USER = User.objects.get(username='guest')
USER = User.objects.get(username='paul')
USERNAME1,PASSWORD1 = 'Joe1','joepass1'
USERNAME2,PASSWORD2 = 'Joe2','joepass2'
MACRO_INIT_FIELD_DICT = {
	'unit_type':'metric',
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
MEAL_TEMPLATE_ARGS = {'user':USER,'name':'breakfast','cals_percent':Decimal('50')}

class BaseTest(TestCase):

	def check_model_validation_error(self,obj,delete_obj=True):
            with self.assertRaises(ValidationError):
                obj.save()
                obj.full_clean()
            if delete_obj:
                obj.user.delete()	

	def check_model_integrity_error(self,obj):
            with transaction.atomic():
                with self.assertRaises(IntegrityError):
                    obj.save()
                    obj.full_clean()

	def create_broken_field_dict(self,break_field,value,master_dict):
            broke_dict = master_dict.copy()
            if User.objects.all().count() != 0:
                    User.objects.all()[0].delete()
                    
            broke_dict['user'] = User.objects.create_user(username=USERNAME1,password=PASSWORD1)
            if value == 'remove':
                    broke_dict.pop(break_field)
            else:
                    broke_dict[break_field] = value

            return broke_dict


class FoodsTest(TestCase):

    def setUp(self):

        self.food1 = Foods.objects.create(
            name='veggie pulled pork',
            cals_per_gram='1.6456',
            fat_per_gram='0.3418',
            carbs_per_gram='0.1519',
            protein_per_gram='1.1646'
        )

        self.srv1 = Servings.objects.create(
            food=self.food1,
            grams=237,
            quantity=1,
            description='bag'
        )

        self.food2 = Foods.objects.create(
            name='bbq sauce',
            cals_per_gram='1.7200',
            fat_per_gram='0.0567', 
            carbs_per_gram='1.6308', 
            protein_per_gram='0.0328' 
        )

        self.srv2 = Servings.objects.create(
            food=self.food2,
            grams=17,
            quantity=1,
            description='tbsp'
        )

        self.empty_food = Foods.objects.create(name='veggie pork with bbq')

        self.ingredient1 = Ingredients.objects.create(
            main_food=self.empty_food,
            ingredient=self.food1,
            serving=self.srv1,
            amount=1
        )

        self.ingredient2 = Ingredients.objects.create(
            main_food=self.empty_food,
            ingredient=self.food2,
            serving=self.srv2,
            amount=4
        )


    def test_saving_and_retrieving_foods(self):
        Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        saved_foods = Foods.objects.filter(name='food name')
        self.assertEqual(saved_foods.count(),1)


    def test_set_macro_per_gram_method(self):
        
        food = self.empty_food
        
        self.assertTrue(food.cals_per_gram is None)

        food.set_macros_per_gram()
        food.save()

        food = Foods.objects.get(name=food.name)
        self.assertEqual(food.cals_per_gram, Decimal('1.6622'))
        self.assertEqual(food.fat_per_gram, Decimal('0.2782'))
        self.assertEqual(food.carbs_per_gram, Decimal('0.4816'))
        self.assertEqual(food.protein_per_gram, Decimal('0.9123'))



c = """
class MacrosTest(BaseTest):
		
    def test_validation_errors_illegal_field_values(self):
        #Integer fields age,height,weight not checked
        self.check_model_validation_error(Macros(**self.create_broken_field_dict('unit_type','schmetric',MACRO_INIT_FIELD_DICT)))#illegal unit_type
        self.check_model_validation_error(Macros(**self.create_broken_field_dict('gender','',MACRO_INIT_FIELD_DICT)))#illegal gender
        self.check_model_validation_error(Macros(**self.create_broken_field_dict('activity','str',MACRO_INIT_FIELD_DICT)))#illegal activity
        self.check_model_validation_error(Macros(**self.create_broken_field_dict('fat_percent',Decimal('10.111'),MACRO_INIT_FIELD_DICT)))#illegal(too long)
        self.check_model_validation_error(Macros(**self.create_broken_field_dict('protein_percent',Decimal('10.111'),MACRO_INIT_FIELD_DICT)))#illegal(too long)

        self.assertEqual(Macros.objects.all().count(),0)

    def test_integrity_errors_missing_field_values(self):
        #unit_type,,direction and activity, because the have defaults are not tested on purpose because they are ValidationError
        self.check_model_integrity_error(Macros(**self.create_broken_field_dict('age','remove',MACRO_INIT_FIELD_DICT)))#no age
        self.check_model_integrity_error(Macros(**self.create_broken_field_dict('weight','remove',MACRO_INIT_FIELD_DICT)))#no weight
        self.check_model_integrity_error(Macros(**self.create_broken_field_dict('height','remove',MACRO_INIT_FIELD_DICT)))#no height
        self.check_model_integrity_error(Macros(**self.create_broken_field_dict('change_rate','remove',MACRO_INIT_FIELD_DICT)))#no chane
        self.check_model_integrity_error(Macros(**self.create_broken_field_dict('fat_percent','remove',MACRO_INIT_FIELD_DICT)))#no fat percent
        self.check_model_integrity_error(Macros(**self.create_broken_field_dict('protein_percent','remove',MACRO_INIT_FIELD_DICT)))#no protein percent

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

        self.assertEqual(first_saved_macros.unit_type,MACRO_INIT_FIELD_DICT['unit_type'])
        self.assertEqual(first_saved_macros.gender,MACRO_INIT_FIELD_DICT['gender'])
        self.assertEqual(first_saved_macros.age,MACRO_INIT_FIELD_DICT['age'])
        self.assertEqual(first_saved_macros.weight,MACRO_INIT_FIELD_DICT['weight'])
        self.assertEqual(first_saved_macros.height,MACRO_INIT_FIELD_DICT['height'])
        self.assertEqual(first_saved_macros.activity,MACRO_INIT_FIELD_DICT['activity'])
        self.assertEqual(first_saved_macros.direction,MACRO_INIT_FIELD_DICT['direction'])
        self.assertEqual(first_saved_macros.change_rate,MACRO_INIT_FIELD_DICT['change_rate'])
        self.assertEqual(first_saved_macros.fat_percent,MACRO_INIT_FIELD_DICT['fat_percent'])
        self.assertEqual(first_saved_macros.protein_percent,MACRO_INIT_FIELD_DICT['protein_percent'])
        self.assertEqual(first_saved_macros.user,first_user)

        self.assertEqual(second_saved_macros.gender,MACRO_INIT_FIELD_DICT['gender'])
        self.assertEqual(second_saved_macros.age,MACRO_INIT_FIELD_DICT['age'])
        self.assertEqual(second_saved_macros.weight,MACRO_INIT_FIELD_DICT['weight'])
        self.assertEqual(second_saved_macros.height,MACRO_INIT_FIELD_DICT['height'])
        self.assertEqual(second_saved_macros.activity,MACRO_INIT_FIELD_DICT['activity'])
        self.assertEqual(second_saved_macros.direction,MACRO_INIT_FIELD_DICT['direction'])
        self.assertEqual(second_saved_macros.change_rate,MACRO_INIT_FIELD_DICT['change_rate'])
        self.assertEqual(second_saved_macros.fat_percent,MACRO_INIT_FIELD_DICT['fat_percent'])
        self.assertEqual(second_saved_macros.protein_percent,MACRO_INIT_FIELD_DICT['protein_percent'])
        self.assertEqual(second_saved_macros.user,second_user)





class OwnedFoodsTest(TestCase):
    
    def test_saving_and_retrieving_owned_foods(self):
        food = Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)

        user = User.objects.create_user(username = USERNAME1,password = PASSWORD1)
        OwnedFoods.objects.create(food=food, user=user)

        saved_owned_foods = OwnedFoods.objects.all()
        self.assertEqual(saved_owned_foods.count(),1)


    def test_delete_user_deletes_owned_foods(self):
        food = Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        user = User.objects.create_user(username = USERNAME1,password = PASSWORD1)
        OwnedFoods.objects.create(food=food, user=user)
        user.delete()
        self.assertEqual(OwnedFoods.objects.all().count(),0)


class ServingsTest(TestCase):
	
    def test_saving_and_retrieving_servings(self):

        food = Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)

        servings = Servings.objects.create(quantity=1,description='cup',grams=100,food=food)

        saved_servings = Servings.objects.all()
        self.assertEqual(saved_servings.count(),1)


    def test_delete_food_deletes_servings(self):
        food = Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        Servings.objects.create(quantity=1,description='cup',grams=100,food=food)
        food.delete()
        self.assertEqual(Servings.objects.all().count(),0)


class IngredientsTest(TestCase):

    def test_saving_and_retrieving_ingrdients(self):

        main_food = Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        food1 = Foods.objects.create(name='food name1',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        food2 = Foods.objects.create(name='food name2',cals_per_gram=2,fat_per_gram=2,carbs_per_gram=2,protein_per_gram=2)

        servings1 = Servings.objects.create(quantity=1,description='cup',grams=100,food=food1)
        servings2 = Servings.objects.create(quantity=2,description='cup',grams=100,food=food2)
        ing1 = Ingredients.objects.create(main_food=main_food,ingredient=food1, serving = servings1, amount=1)
        ing2 = Ingredients.objects.create(main_food=main_food,ingredient=food2, serving = servings2, amount=1)

        saved_ingredients = Ingredients.objects.all()
        self.assertEqual(saved_ingredients.count(),2)

    def test_calc_macros_method(self):
        main_food = Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        food1 = Foods.objects.create(name='food name1',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        food2 = Foods.objects.create(name='food name2',cals_per_gram=2,fat_per_gram=2,carbs_per_gram=2,protein_per_gram=2)

        servings1 = Servings.objects.create(quantity=1,description='cup',grams=100,food=food1)
        servings2 = Servings.objects.create(quantity=2,description='cup',grams=100,food=food2)
        ing1 = Ingredients.objects.create(main_food=main_food,ingredient=food1, serving = servings1, amount=1)
        ing2 = Ingredients.objects.create(main_food=main_food,ingredient=food2, serving = servings2, amount=1)

        saved_ingredients = Ingredients.objects.all()
        self.assertEqual(saved_ingredients.count(),2)
    
    def test_delete_food_deletes_ingredients(self):
        main_food = Foods.objects.create(name='food name',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        food1 = Foods.objects.create(name='food name1',cals_per_gram=1,fat_per_gram=1,carbs_per_gram=1,protein_per_gram=1)
        food2 = Foods.objects.create(name='food name2',cals_per_gram=2,fat_per_gram=2,carbs_per_gram=2,protein_per_gram=2)

        servings1 = Servings.objects.create(quantity=1,description='cup',grams=100,food=food1)
        servings2 = Servings.objects.create(quantity=2,description='cup',grams=100,food=food2)
        ing1 = Ingredients.objects.create(main_food=main_food,ingredient=food1, serving = servings1, amount=1)
        ing2 = Ingredients.objects.create(main_food=main_food,ingredient=food2, serving = servings2, amount=1)

        food1.delete()

        saved_ingredients = Ingredients.objects.all()
        self.assertEqual(saved_ingredients.count(),1)

        food2.delete()

        saved_ingredients = Ingredients.objects.all()
        self.assertEqual(saved_ingredients.count(),0)
"""
