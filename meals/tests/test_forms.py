from django.test import TestCase

from meals.forms import LoginForm,SignUpForm,MakeMacrosForm,EMPTY_USERNAME_ERROR, EMPTY_PASSWORD_ERROR,EMPTY_AGE_ERROR,EMPTY_WEIGHT_ERROR,EMPTY_HEIGHT_ERROR,EMPTY_MACRO_ERROR,INVALID_POST_ERROR,DEFAULT_INVALID_INT_ERROR,EMPTY_RATE_ERROR,INVALID_MACRO_ERROR,OUT_OF_RANGE_MACRO_ERROR

class LoginFormTest(TestCase):

	def test_form_login_has_placeholder_and_css_classes(self):
		form = LoginForm()
		self.assertIn('placeholder="Username"', form.as_p())
		self.assertIn('placeholder="Password"', form.as_p())
		self.assertIn('class="form-control input-sm"', form.as_p())

	def test_form_validation_for_blank_inputs(self):
		form = LoginForm(data={'username':'','password':''})
		self.assertFalse(form.is_valid())
		self.assertEqual(
			form.errors['username'],
			[EMPTY_USERNAME_ERROR]
		)
		self.assertEqual(
			form.errors['password'],
			[EMPTY_PASSWORD_ERROR]
		)

class SignUpFormTest(TestCase):

	def test_form_sign_up_has_placeholder_and_css_classes(self):
		form = SignUpForm()
		self.assertIn('placeholder="Username"', form.as_p())
		self.assertIn('placeholder="Email"', form.as_p())
		self.assertIn('placeholder="Password"', form.as_p())
		self.assertIn('class="form-control input-sm"', form.as_p())

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
		form = MakeMacrosForm()
		self.assertIn('value="m"', form.as_p())
		self.assertIn('value="f"', form.as_p())
		self.assertIn('placeholder="Age"', form.as_p())
		self.assertIn('value="none"', form.as_p())
		self.assertIn('value="lose"', form.as_p())
		self.assertIn('class="form-control input-sm"', form.as_p())
	
	def test_form_validation_for_blank_inputs(self):
		form = MakeMacrosForm(data={'gender':'','age':'','weight':'','height':'','activity':'','direction':'','change_rate':'','protein_percent':'','protein_g':'','fat_percent':'','fat_g':'','carbs_percent':'','carbs_g':''})
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
		form = MakeMacrosForm(data={'gender':0,'age':'str','weight':'str','height':'str','activity':'str','direction':'str','change_rate':'str','protein_percent':'str','protein_g':'str','fat_percent':'str','fat_g':'str','carbs_percent':'str','carbs_g':'str'})
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
		form = MakeMacrosForm(data={'protein_percent':'1000','fat_percent':'1000','carbs_percent':'1000'})
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

		form = MakeMacrosForm(data={'protein_percent':'-1000','fat_percent':'-1000','carbs_percent':'-1000'})
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

