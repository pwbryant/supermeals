from django.test import TestCase

# from meals.forms import SignUpForm, MakeMacrosForm, MacroMealForm, \
#         EMPTY_USERNAME_ERROR, EMPTY_PASSWORD_ERROR, EMPTY_AGE_ERROR, \
#         EMPTY_WEIGHT_ERROR, EMPTY_HEIGHT_ERROR, EMPTY_MACRO_ERROR, \
#         INVALID_POST_ERROR, DEFAULT_INVALID_INT_ERROR, EMPTY_RATE_ERROR, \
#         INVALID_MACRO_ERROR, OUT_OF_RANGE_MACRO_ERROR, MACROS_DONT_ADD_UP_ERROR

from meals.forms import  MacroMealForm

class SignUpFormTest(TestCase):


    def setUp(self):
        self.post = {
            # added long decimals to test that they get rounded
            'name': 'veggie_pulled_pork_with_bbq_sauce',
            'cals_per_gram': '1.6622001',
            'fat_per_gram': '0.2782001',
            'carbs_per_gram': '0.4816001',
            'protein_per_gram': '0.9123001',
            'ingredient_id_0': '7133',
            'ingredient_amt_0': '1',
            'ingredient_unit_0': 'bag',
            'ingredient_id_1': '6014',
            'ingredient_amt_1': '4',
            'ingredient_unit_1': 'tbsp'
        }

        self.bad_post = {
            'name': '',
            'cals_per_gram': 'str',
            'fat_per_gram': 'str',
            'carbs_per_gram': 'str',
            'protein_per_gram': 'str',
            'ingredient_id_0': 'str',
            'ingredient_amt_0': 'str',
            'ingredient_unit_0': '0',
            'ingredient_id_1': 'str',
            'ingredient_amt_1': 'str',
            'ingredient_unit_1': '0'
        }
        # k[-1] is the ingredient number
        self.ingredient_count = len(set(
            [k[-1] for k in self.post if 'ingredient' in k]
        ))

    def test_MacroMealFome_valid(self):

        form = MacroMealForm(self.post, ingredient_count=self.ingredient_count)
        self.assertTrue(form.is_valid())


    def test_MacroMealFome_invalid(self):
        form = MacroMealForm(self.bad_post, ingredient_count=self.ingredient_count)
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
