from django.test import TestCase
from django import forms

# from meals.forms import SignUpForm, MakeMacrosForm, MacroMealForm, \
#         EMPTY_USERNAME_ERROR, EMPTY_PASSWORD_ERROR, EMPTY_AGE_ERROR, \
#         EMPTY_WEIGHT_ERROR, EMPTY_HEIGHT_ERROR, EMPTY_MACRO_ERROR, \
#         INVALID_POST_ERROR, DEFAULT_INVALID_INT_ERROR, EMPTY_RATE_ERROR, \
#         INVALID_MACRO_ERROR, OUT_OF_RANGE_MACRO_ERROR, MACROS_DONT_ADD_UP_ERROR

from meals.forms import  MacroMealForm, MacroIngredientForm
from meals.models import Foods, Ingredients, Servings

class MacroMealAndIngredientFormTest(TestCase):


    def setUp(self):

        self.ingredient1 = Foods.objects.create(
            name='veggie pulled pork',
            cals_per_gram='1.6456',
            fat_per_gram='0.3418',
            carbs_per_gram='0.1519',
            protein_per_gram='1.1646'
        )

        self.srv1 = Servings.objects.create(
            food=self.ingredient1,
            grams=237,
            quantity=1,
            description='bag'
        )

        self.ingredient2 = Foods.objects.create(
            name='bbq sauce',
            cals_per_gram='1.7200',
            fat_per_gram='0.0567', 
            carbs_per_gram='1.6308', 
            protein_per_gram='0.0328' 
        )

        self.srv2 = Servings.objects.create(
            food=self.ingredient2,
            grams=17,
            quantity=1,
            description='tbsp'
        )

        self.ingredient_form_factory = forms.formset_factory(
            MacroIngredientForm, extra=2
        )

        self.post = {
            # added long decimals to test that they get rounded
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
            'name': 'veggie_pulled_pork_with_bbq_sauce',
            'notes': 'broil in the oven',
            'form-0-ingredient_id': self.ingredient1.pk,
            'form-0-amount': '1',
            'form-0-ingredient_unit': 'bag',
            'form-1-ingredient_id': self.ingredient2.pk,
            'form-1-amount': '4',
            'form-1-ingredient_unit': 'tbsp'
        }

        self.bad_post = {
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
            'name': '',
            'notes': 'broil in the oven',
            'form-0-ingredient_id': self.ingredient1.pk,
            'form-0-amount': 'str',
            'form-0-ingredient_unit': 'bag',
            'form-1-ingredient_id': self.ingredient2.pk,
            'form-1-amount': 'str',
            'form-1-ingredient_unit': 'tbsp'
        }

        # k[-1] is the ingredient number
        self.ingredient_count = len(set(
            [k[-1] for k in self.post if 'ingredient' in k]
        ))

    def test_MacroMealForm_valid(self):

        form = MacroMealForm(self.post)
        self.assertTrue(form.is_valid())


    def test_MacroMealForm_invalid(self):
        form = MacroMealForm(self.bad_post)
        self.assertFalse(form.is_valid())


    def test_MacroIngredientForm_valid(self):

        form_set = self.ingredient_form_factory(self.post)
        self.assertTrue(form_set.is_valid())


    def test_MacroIngredientForm_invalid(self):

        form = self.ingredient_form_factory(self.bad_post)
        self.assertFalse(form.is_valid())


c = """
class SignUpFormTest(TestCase):

	def test_form_sign_up_has_placeholder_and_css_classes(self):
		form = SignUpForm()
		self.assertIn('placeholder="Username"', form.as_p())
		self.assertIn('placeholder="Email"', form.as_p())
		self.assertIn('placeholder="Password"', form.as_p())
		self.assertIn('class="input__input input__input--lg"', form.as_p())

	def test_form_validation_for_blank_inputs(self):
		form = SignUpForm(data={'username':'','password':''})
		self.assertFalse(form.is_valid())
		self.assertEqual(
			form.errors['username'],
			[EMPTY_USERNAME_ERROR]
		)
		self.assertEqual(
			form.errors['password'],
			[EMPTY_PASSWORD_ERROR]
		)

class MakeMacrosFormTest(TestCase):

	def test_my_macros_form_has_placeholder_values_and_css_classes(self):
		form = MakeMacrosForm(unit_type='imperial')		
		self.assertIn('value="male"', form.as_p())
		self.assertIn('value="female"', form.as_p())
		self.assertIn('placeholder="Age"', form.as_p())
		self.assertIn('placeholder="lb"', form.as_p())
		self.assertIn('placeholder="ft"', form.as_p())
		self.assertIn('placeholder="in"', form.as_p())
		self.assertIn('placeholder="lb/wk"', form.as_p())
		self.assertIn('placeholder="kg"', form.as_p())
		self.assertIn('placeholder="cm"', form.as_p())
		self.assertIn('placeholder="kg/wk"', form.as_p())
		self.assertIn('placeholder="%"', form.as_p())
		self.assertIn('placeholder="g"', form.as_p())
		self.assertIn('value="none"', form.as_p())
		self.assertIn('value="lose"', form.as_p())
		#self.assertIn('class="form-control input-sm change_rate"', form.as_p())
		self.assertIn('class="form-control input-sm choose_macros"', form.as_p())
		#self.assertIn('class="form-control input-sm"', form.as_p())
			

	def test_form_validation_for_blank_inputs(self):
		form = MakeMacrosForm(data={'gender':'','age':'','weight':'','height':'','activity':'','direction':'','change_rate':'','protein_percent':'','protein_g':'','fat_percent':'','fat_g':'','carbs_percent':'','carbs_g':''},unit_type='imperial')
		self.assertFalse(form.is_valid())
		self.assertEqual(
			form.errors['gender'],
			[INVALID_POST_ERROR]
		)
		self.assertEqual(
			form.errors['age'],
			[EMPTY_AGE_ERROR]
		)
		self.assertEqual(
			form.errors['weight'],
			[EMPTY_WEIGHT_ERROR]
		)
		self.assertEqual(
			form.errors['height'],
			[EMPTY_HEIGHT_ERROR]
		)
		self.assertEqual(
			form.errors['activity'],
			[INVALID_POST_ERROR]
		)
		self.assertEqual(
			form.errors['direction'],
			[INVALID_POST_ERROR]
		)
		self.assertEqual(
			form.errors['change_rate'],
			[EMPTY_RATE_ERROR]
		)
		self.assertEqual(
			form.errors['protein_percent'],
			[EMPTY_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['protein_g'],
			[EMPTY_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['fat_percent'],
			[EMPTY_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['fat_g'],
			[EMPTY_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['carbs_percent'],
			[EMPTY_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['carbs_g'],
			[EMPTY_MACRO_ERROR]
		)

	def test_form_validation_for_illegal_inputs(self):
		form = MakeMacrosForm(data={'gender':0,'age':'str','weight':'str','height':'str','activity':'str','direction':'str','change_rate':'str','protein_percent':'str','protein_g':'str','fat_percent':'str','fat_g':'str','carbs_percent':'str','carbs_g':'str'},unit_type='imperial')
		self.assertFalse(form.is_valid())
		self.assertEqual(
			form.errors['gender'],
			[INVALID_POST_ERROR]
		)
		self.assertEqual(
			form.errors['age'],
			[DEFAULT_INVALID_INT_ERROR]
		)
		self.assertEqual(
			form.errors['weight'],
			[DEFAULT_INVALID_INT_ERROR]
		)
		self.assertEqual(
			form.errors['height'],
			[DEFAULT_INVALID_INT_ERROR]
		)
		self.assertEqual(
			form.errors['activity'],
			[INVALID_POST_ERROR]
		)
		self.assertEqual(
			form.errors['direction'],
			[INVALID_POST_ERROR]
		)
		self.assertEqual(
			form.errors['change_rate'],
			[DEFAULT_INVALID_INT_ERROR]
		)
		self.assertEqual(
			form.errors['protein_percent'],
			[INVALID_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['protein_g'],
			[INVALID_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['fat_percent'],
			[INVALID_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['fat_g'],
			[INVALID_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['carbs_percent'],
			[INVALID_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['carbs_g'],
			[INVALID_MACRO_ERROR]
		)

	def test_form_validation_for_out_of_range_inputs(self):
		form = MakeMacrosForm(data={'protein_percent':'1000','fat_percent':'1000','carbs_percent':'1000'},unit_type='imperial')
		self.assertFalse(form.is_valid())

		self.assertEqual(
			form.errors['protein_percent'],
			[OUT_OF_RANGE_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['fat_percent'],
			[OUT_OF_RANGE_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['carbs_percent'],
			[OUT_OF_RANGE_MACRO_ERROR]
		)

		form = MakeMacrosForm(data={'protein_percent':'-1000','fat_percent':'-1000','carbs_percent':'-1000','total_macro_percent':'101'},unit_type='imperial')
		self.assertFalse(form.is_valid())

		self.assertEqual(
			form.errors['protein_percent'],
			[OUT_OF_RANGE_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['fat_percent'],
			[OUT_OF_RANGE_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['carbs_percent'],
			[OUT_OF_RANGE_MACRO_ERROR]
		)
		self.assertEqual(
			form.errors['total_macro_percent'],
			[MACROS_DONT_ADD_UP_ERROR]
		)
"""
