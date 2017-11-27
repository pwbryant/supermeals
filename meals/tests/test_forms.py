from django.test import TestCase

from meals.forms import LoginForm,SignUpForm,MyMacrosForm,EMPTY_USERNAME_ERROR, EMPTY_PASSWORD_ERROR,EMPTY_AGE_ERROR,EMPTY_WEIGHT_ERROR,EMPTY_HEIGHT_ERROR,EMPTY_MACRO_ERROR,INVALID_POST_ERROR,DEFAULT_INVALID_INT_ERROR

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


class MyMacrosFormTest(TestCase):

	def test_my_macros_form_has_placeholder_values_and_css_classes(self):
		form = MyMacrosForm()
		self.assertIn('value="m"', form.as_p())
		self.assertIn('value="f"', form.as_p())
		self.assertIn('placeholder="Age"', form.as_p())
		self.assertIn('placeholder="Weight(lbs)"', form.as_p())
		self.assertIn('placeholder="Height(in)"', form.as_p())
		self.assertIn('value="none"', form.as_p())
		self.assertIn('value="lose"', form.as_p())
		self.assertIn('value="30_20_50"', form.as_p())
		self.assertIn('value="40_40_20"', form.as_p())
		self.assertIn('value="30_35_35"', form.as_p())
		self.assertIn('class="form-control input-sm"', form.as_p())
	
	def test_form_validation_for_blank_inputs(self):
		form = MyMacrosForm(data={'gender':'','age':'','weight':'','height':'','activity':'','direction':'','macro_ratios':''})
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
			form.errors['macro_ratios'],
			[INVALID_POST_ERROR]
		)

	def test_form_validation_for_illegal_inputs(self):
		form = MyMacrosForm(data={'gender':0,'age':'str','weight':'str','height':'str','activity':'blah','direction':'blah','macro_ratios':'str'})
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
			form.errors['macro_ratios'],
			[INVALID_POST_ERROR]
		)

